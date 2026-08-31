#!/usr/bin/env python3
"""
patch_dol.py - Injects the DVD-to-NAND shim into main.dol and hooks DVD functions.
"""

import os
import struct
import subprocess
import sys
import shutil


def read_be32(data, offset):
    return struct.unpack(">I", data[offset:offset+4])[0]


def write_be32(data, offset, val):
    struct.pack_into(">I", data, offset, val & 0xFFFFFFFF)


def get_elf_symbols(elf_path=None, map_path=None):
    """Extract symbol addresses from the compiled shim ELF or MAP file."""
    symbols = {
        "Hook_DVDConvertPathToEntrynum": 0x805B0670,
        "Hook_DVDFastOpen": 0x805B0700,
        "Hook_DVDOpen": 0x805B0730,
        "Hook_DVDReadAsyncPrio": 0x805B0740,
        "Hook_DVDClose": 0x805B07D0,
        "Hook_MainTrace_Trampoline": 0x805B0B20,
    }

    # 1. Try reading map file if available
    candidate_maps = [map_path] if map_path else []
    candidate_maps.extend([
        os.path.join(os.path.dirname(__file__), "..", "precompiled", "dvd_nand_shim.elf.map"),
        "precompiled/dvd_nand_shim.elf.map",
        "dvd_nand_shim.elf.map"
    ])

    for mp in candidate_maps:
        if mp and os.path.isfile(mp):
            try:
                import re
                with open(mp, "r", errors="replace") as f:
                    map_txt = f.read()
                matches = re.findall(r'0x([0-9a-fA-F]{8})\s+(Hook_[A-Za-z0-9_]+)', map_txt)
                for addr_s, sym in matches:
                    symbols[sym] = int(addr_s, 16)
                return symbols
            except Exception:
                pass

    # 2. Try nm if ELF is provided
    if elf_path and os.path.isfile(elf_path):
        nm_paths = [
            os.path.join(os.environ.get("DEVKITPRO", "/opt/devkitpro"), "devkitPPC", "bin", "powerpc-eabi-nm"),
            "powerpc-eabi-nm",
        ]
        for nm_bin in nm_paths:
            if shutil.which(nm_bin) or os.path.isfile(nm_bin):
                try:
                    output = subprocess.check_output([nm_bin, elf_path]).decode("ascii", errors="replace")
                    for line in output.splitlines():
                        parts = line.strip().split()
                        if len(parts) >= 3:
                            addr_str, sym_type, name = parts[0], parts[1], parts[2]
                            symbols[name] = int(addr_str, 16)
                    return symbols
                except Exception:
                    pass

    return symbols


def patch_dol(dol_in_path, shim_bin_path, shim_elf_path, dol_out_path):
    print("=" * 70)
    print(f"PATCHING DOL: {dol_in_path} -> {dol_out_path}")
    print("=" * 70)

    with open(dol_in_path, "rb") as f:
        dol_data = bytearray(f.read())

    with open(shim_bin_path, "rb") as f:
        shim_bin = f.read()

    symbols = get_elf_symbols(shim_elf_path)
    print("Shim Symbols:")
    for name, addr in sorted(symbols.items(), key=lambda x: x[1]):
        if name.startswith("Shim_"):
            print(f"  0x{addr:08X}: {name}")

    # Align current DOL length to 32 bytes
    orig_len = len(dol_data)
    padded_orig_len = (orig_len + 31) & ~31
    if padded_orig_len > orig_len:
        dol_data.extend(b"\x00" * (padded_orig_len - orig_len))

    # Pad shim binary to 32 bytes
    shim_len = len(shim_bin)
    padded_shim_len = (shim_len + 31) & ~31
    padded_shim_bin = shim_bin + (b"\x00" * (padded_shim_len - shim_len))

    # Function to convert mem addr to file offset in dol
    def mem_to_file(maddr):
        # Text sections 0..6
        for i in range(7):
            fo = read_be32(dol_data, i * 4)
            ma = read_be32(dol_data, 0x48 + i * 4)
            sz = read_be32(dol_data, 0x90 + i * 4)
            if ma <= maddr < ma + sz:
                return fo + (maddr - ma)
        # Data sections 0..10
        for i in range(11):
            fo = read_be32(dol_data, 0x1C + i * 4)
            ma = read_be32(dol_data, 0x64 + i * 4)
            sz = read_be32(dol_data, 0xAC + i * 4)
            if ma <= maddr < ma + sz:
                return fo + (maddr - ma)
        return None

    # Append shim binary as Data[8] section at 0x805B0000 (immediately following Data[7])
    shim_mem_addr = 0x805B0000
    shim_file_offset = len(dol_data)
    dol_data.extend(padded_shim_bin)

    # Clear Text[2] in DOL Header (index 2)
    write_be32(dol_data, 0x08, 0)
    write_be32(dol_data, 0x50, 0)
    write_be32(dol_data, 0x98, 0)

    # Register Data[8] in DOL Header (index 8: 0x1C + 8*4=0x3C, 0x64 + 8*4=0x84, 0xAC + 8*4=0xCC)
    write_be32(dol_data, 0x1C + 8 * 4, shim_file_offset)
    write_be32(dol_data, 0x64 + 8 * 4, shim_mem_addr)
    write_be32(dol_data, 0xAC + 8 * 4, padded_shim_len)

    print(f"\nAppended Data[8] shim at 0x{shim_mem_addr:08X} (file offset 0x{shim_file_offset:08X}, size {padded_shim_len} bytes)")

    # Define Hooks to patch
    hooks = [
        {
            "name": "Main_Trace_Hook",
            "orig_addr": 0x8018DC88,
            "target_sym": "Hook_MainTrace_Trampoline",
        },
        {
            "name": "DVDConvertPathToEntrynum",
            "orig_addr": 0x8028B3B0,
            "target_sym": "Hook_DVDConvertPathToEntrynum",
        },
        {
            "name": "DVDFastOpen",
            "orig_addr": 0x8028B6C0,
            "target_sym": "Hook_DVDFastOpen",
        },
        {
            "name": "DVDOpen",
            "orig_addr": 0x8028B730,
            "target_sym": "Hook_DVDOpen",
        },
        {
            "name": "DVDReadAsyncPrio",
            "orig_addr": 0x8028B9A0,
            "target_sym": "Hook_DVDReadAsyncPrio",
        },
        {
            "name": "DVDClose",
            "orig_addr": 0x8028B850,
            "target_sym": "Hook_DVDClose",
        },
        {
            "name": "OSInit_ArenaLo_High",
            "orig_addr": 0x80273678,
            "raw_insn": 0x3C60805D, # lis r3, 0x805D
        },
        {
            "name": "OSInit_ArenaLo_Low",
            "orig_addr": 0x80273680,
            "raw_insn": 0x38630000, # addi r3, r3, 0 -> 0x805D0000
        },
        {
            "name": "OSInit_ArenaLo2_High",
            "orig_addr": 0x802737E0,
            "raw_insn": 0x3C60805D, # lis r3, 0x805D
        },
        {
            "name": "OSInit_ArenaLo2_Low",
            "orig_addr": 0x802737E4,
            "raw_insn": 0x38630000, # addi r3, r3, 0 -> 0x805D0000
        },
        {
            "name": "OSInit_ArenaLo3_High",
            "orig_addr": 0x80273868,
            "raw_insn": 0x3C60805D, # lis r3, 0x805D
        },
        {
            "name": "OSInit_ArenaLo3_Low",
            "orig_addr": 0x8027386C,
            "raw_insn": 0x38630000, # addi r3, r3, 0 -> 0x805D0000
        },
        {
            "name": "OSInit_ArenaLo4_High",
            "orig_addr": 0x8027CA6C,
            "raw_insn": 0x3C60805D, # lis r3, 0x805D
        },
        {
            "name": "OSInit_ArenaLo4_Low",
            "orig_addr": 0x8027CA74,
            "raw_insn": 0x38630000, # addi r3, r3, 0 -> 0x805D0000
        },
        {
            "name": "DBInit_Stub",
            "orig_addr": 0x80004000,
            "raw_insn": 0x4E800020, # blr
        },
        {
            "name": "MetroTRK_Check_Stub1",
            "orig_addr": 0x80004040,
            "raw_insn": 0x38600000, # li r3, 0
        },
        {
            "name": "MetroTRK_Check_Stub2",
            "orig_addr": 0x80004044,
            "raw_insn": 0x4E800020, # blr
        },
        {
            "name": "MetroTRK_Disable",
            "orig_addr": 0x800041A0,
            "raw_insn": 0x60000000,
        },
        {
            "name": "OSInit_DiscVerify_Bypass",
            "orig_addr": 0x80273990,
            "raw_insn": 0x480001D4, # b 0x80273B64 (bypass CheckDisc panic loop)
        },
        {
            "name": "OSInit_PlayRec_Skip",
            "orig_addr": 0x80273BA4,
            "raw_insn": 0x60000000, # nop (skip play_rec.dat write in OSInit)
        },
    ]

    print("\nPatching Hook Entry Points:")
    for h in hooks:
        orig = h["orig_addr"]
        if "raw_insn" in h:
            branch_insn = h["raw_insn"]
            target_str = f"raw 0x{branch_insn:08X}"
        else:
            if "target_addr" in h:
                target = h["target_addr"]
            else:
                sym = h["target_sym"]
                if sym not in symbols:
                    raise ValueError(f"Symbol {sym} not found in ELF symbols!")
                target = symbols[sym]

            offset = target - orig
            if h.get("is_call", False):
                branch_insn = 0x48000001 | (offset & 0x03FFFFFC)
                target_str = f"bl 0x{target:08X}"
            else:
                branch_insn = 0x48000000 | (offset & 0x03FFFFFC)
                target_str = f"b 0x{target:08X}"

        foff = mem_to_file(orig)
        if foff is None:
            raise ValueError(f"Could not map virtual address 0x{orig:08X} to file offset!")

        orig_insn = read_be32(dol_data, foff)
        write_be32(dol_data, foff, branch_insn)

        print(f"  {h['name']:<25} [0x{orig:08X} (file 0x{foff:08X})]: "
              f"0x{orig_insn:08X} -> 0x{branch_insn:08X} ({target_str})")

    # Save output DOL
    with open(dol_out_path, "wb") as f:
        f.write(dol_data)

    print(f"\nSuccessfully wrote patched DOL to {dol_out_path} ({len(dol_data)} bytes).")
    print("=" * 70)


if __name__ == "__main__":
    dol_in = "main.dol"
    shim_bin = "dvd_nand_shim.bin"
    shim_elf = "dvd_nand_shim.elf"
    dol_out = "main_patched.dol"

    if len(sys.argv) >= 2:
        dol_in = sys.argv[1]
    if len(sys.argv) >= 3:
        dol_out = sys.argv[2]

    patch_dol(dol_in, shim_bin, shim_elf, dol_out)
