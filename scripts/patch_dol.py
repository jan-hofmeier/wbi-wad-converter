import os, struct, sys

def read_be32(data, offset): return struct.unpack(">I", data[offset:offset+4])[0]
def write_be32(data, offset, val): struct.pack_into(">I", data, offset, val & 0xFFFFFFFF)

def parse_map_symbols(map_path):
    symbols = {}
    if not os.path.exists(map_path):
        return symbols
    with open(map_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 2:
                if parts[0].startswith("0x805b") or parts[0].startswith("0x805B"):
                    addr = int(parts[0], 16)
                    name = parts[1]
                    symbols[name] = addr
    return symbols

def patch_dol(dol_in_path, shim_bin_path, shim_elf_path, dol_out_path):
    with open(dol_in_path, "rb") as f: dol_data = bytearray(f.read())
    with open(shim_bin_path, "rb") as f: shim_bin = bytearray(f.read())

    map_path = shim_bin_path.replace(".bin", ".elf.map")
    if not os.path.exists(map_path):
        map_path = os.path.join(os.path.dirname(shim_bin_path), "dvd_nand_shim.elf.map")
    if not os.path.exists(map_path):
        map_path = "precompiled/dvd_nand_shim.elf.map"
    
    symbols = parse_map_symbols(map_path)
    print(f"Loaded {len(symbols)} symbols from {map_path}")
    for k in ["M1_Wrapper", "M2_Wrapper", "M3_Wrapper", "Hook_MainTrace_Trampoline", "Hook_DVDConvertPathToEntrynum", "Hook_DVDFastOpen", "Hook_DVDOpen", "Hook_DVDReadAsyncPrio", "Hook_DVDClose"]:
        print(f"  {k:<30}: 0x{symbols.get(k, 0):08X}")

    shim_mem_addr = 0x805B0000

    orig_len = len(dol_data)
    padded_orig_len = (orig_len + 31) & ~31
    if padded_orig_len > orig_len: dol_data.extend(b"\x00" * (padded_orig_len - orig_len))

    shim_len = len(shim_bin)
    padded_shim_len = (shim_len + 31) & ~31
    padded_shim_bin = shim_bin + (b"\x00" * (padded_shim_len - shim_len))

    def mem_to_file(maddr):
        for i in range(7):
            fo = read_be32(dol_data, i * 4); ma = read_be32(dol_data, 0x48 + i * 4); sz = read_be32(dol_data, 0x90 + i * 4)
            if ma <= maddr < ma + sz: return fo + (maddr - ma)
        for i in range(11):
            fo = read_be32(dol_data, 0x1C + i * 4); ma = read_be32(dol_data, 0x64 + i * 4); sz = read_be32(dol_data, 0xAC + i * 4)
            if ma <= maddr < ma + sz: return fo + (maddr - ma)
        return None

    shim_file_offset = len(dol_data)
    dol_data.extend(padded_shim_bin)

    write_be32(dol_data, 0x08, 0); write_be32(dol_data, 0x50, 0); write_be32(dol_data, 0x98, 0)
    write_be32(dol_data, 0x1C + 8 * 4, shim_file_offset)
    write_be32(dol_data, 0x64 + 8 * 4, shim_mem_addr)
    write_be32(dol_data, 0xAC + 8 * 4, padded_shim_len)

    hooks = [
        # Milestone 1: Inside OSInit at DVD check entry (0x80273970) -> bl M1_Wrapper
        {"name": "M1_Hook", "orig_addr": 0x80273970, "target_addr": symbols["M1_Wrapper"], "is_call": True},
        
        # Milestone 2: When OSInit returns to __start (0x80004170) -> b M2_Wrapper
        {"name": "M2_Hook", "orig_addr": 0x80004170, "target_addr": symbols["M2_Wrapper"], "is_call": False},
        
        # Milestone 3: __start calling main (0x800041B0) -> bl M3_Wrapper
        {"name": "M3_Hook", "orig_addr": 0x800041B0, "target_addr": symbols["M3_Wrapper"], "is_call": True},
        
        # Main trace hook in case main is entered directly:
        {"name": "Main_Trace_Hook", "orig_addr": 0x8018DC88, "target_addr": symbols["Hook_MainTrace_Trampoline"]},
        
        # DVD Redirection hooks (Milestone 5 is embedded in Hook_DVDConvertPathToEntrynum)
        {"name": "DVDConvertPathToEntrynum", "orig_addr": 0x8028B3B0, "target_addr": symbols["Hook_DVDConvertPathToEntrynum"]},
        {"name": "DVDFastOpen", "orig_addr": 0x8028B6C0, "target_addr": symbols["Hook_DVDFastOpen"]},
        {"name": "DVDOpen", "orig_addr": 0x8028B730, "target_addr": symbols["Hook_DVDOpen"]},
        {"name": "DVDReadAsyncPrio", "orig_addr": 0x8028B9A0, "target_addr": symbols["Hook_DVDReadAsyncPrio"]}, 
        {"name": "DVDClose", "orig_addr": 0x8028B850, "target_addr": symbols["Hook_DVDClose"]},
        
        # OSInit & Startup Fixes
        {"name": "OSInit_ArenaLo_High", "orig_addr": 0x80273678, "raw_insn": 0x3C60805D},
        {"name": "OSInit_ArenaLo_Low", "orig_addr": 0x80273680, "raw_insn": 0x38630000},
        {"name": "OSInit_ArenaLo2_High", "orig_addr": 0x802737E0, "raw_insn": 0x3C60805D},
        {"name": "OSInit_ArenaLo2_Low", "orig_addr": 0x802737E4, "raw_insn": 0x38630000},
        {"name": "OSInit_ArenaLo3_High", "orig_addr": 0x80273868, "raw_insn": 0x3C60805D},
        {"name": "OSInit_ArenaLo3_Low", "orig_addr": 0x8027386C, "raw_insn": 0x38630000},
        {"name": "OSInit_ArenaLo4_High", "orig_addr": 0x8027CA6C, "raw_insn": 0x3C60805D},
        {"name": "OSInit_ArenaLo4_Low", "orig_addr": 0x8027CA74, "raw_insn": 0x38630000},
        {"name": "DBInit_Stub", "orig_addr": 0x80004000, "raw_insn": 0x4E800020},
        {"name": "MetroTRK_Check_Stub1", "orig_addr": 0x80004040, "raw_insn": 0x38600000},
        {"name": "MetroTRK_Check_Stub2", "orig_addr": 0x80004044, "raw_insn": 0x4E800020},
        {"name": "MetroTRK_Disable", "orig_addr": 0x800041A0, "raw_insn": 0x60000000},
        
        # TOTAL DVD HARDWARE BYPASS: Jump straight from VIInit return to 80273B64
        {"name": "OSInit_DVDHardware_Bypass", "orig_addr": 0x80273974, "raw_insn": 0x480001F0},
        
        # PlayRec Skip: Prevent hang on play_rec.dat
        {"name": "OSInit_PlayRec_Skip", "orig_addr": 0x80273BA4, "raw_insn": 0x60000000},
        
        # KPR Null Checks
        {"name": "KPR_NullCheck_Bypass1", "orig_addr": 0x8033C8E0, "raw_insn": 0x38600004},
        {"name": "KPR_NullCheck_Bypass2", "orig_addr": 0x8033C8E4, "raw_insn": 0x4E800020},
    ]

    print("\nPatching Hook Entry Points:")
    for h in hooks:
        orig = h["orig_addr"]
        if "raw_insn" in h: branch_insn = h["raw_insn"]
        else:
            target = h["target_addr"]
            offset = target - orig
            if h.get("is_call", False): branch_insn = 0x48000001 | (offset & 0x03FFFFFC)
            else: branch_insn = 0x48000000 | (offset & 0x03FFFFFC)
        
        foff = mem_to_file(orig)
        write_be32(dol_data, foff, branch_insn)
        print(f"  {h['name']:<30} [0x{orig:08X}] -> 0x{branch_insn:08X}")

    with open(dol_out_path, "wb") as f: f.write(dol_data)

if __name__ == "__main__":
    patch_dol(sys.argv[1], "precompiled/dvd_nand_shim.bin", None, sys.argv[2] if len(sys.argv) > 2 else "main_patched.dol")
