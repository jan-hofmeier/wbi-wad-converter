#!/usr/bin/env python3
"""
Worms: Battle Islands - Standalone WAD Channel Converter (CLI)
Converts retail Wii disc / WBFS copies of Worms Battle Islands into a standalone WAD channel.
"""

import os, sys, shutil, argparse, subprocess, struct
from scripts.keys import get_common_key
from scripts.extract_game import extract_game
from scripts.pack_content2 import pack_content2
from scripts.pack_wad import create_wad

def align64(n):
    return (n + 63) & ~63

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def ensure_lz11_compress():
    """Ensures a working lz11_compress tool exists (compiles from src if needed)."""
    tool_path = os.path.join(SCRIPT_DIR, "tools", "lz11_compress")
    if os.path.isfile(tool_path) and os.access(tool_path, os.X_OK):
        return tool_path
    
    # Try compiling from src/lz11_compress.c
    src_c = os.path.join(SCRIPT_DIR, "src", "lz11_compress.c")
    if os.path.isfile(src_c) and shutil.which("gcc"):
        os.makedirs(os.path.join(SCRIPT_DIR, "tools"), exist_ok=True)
        print("Compiling native LZ11 compressor...")
        res = subprocess.run(["gcc", "-O3", src_c, "-o", tool_path])
        if res.returncode == 0 and os.path.isfile(tool_path):
            return tool_path

    # Fallback to local executable if present
    local_tool = os.path.join(SCRIPT_DIR, "lz11_compress")
    if os.path.isfile(local_tool) and os.access(local_tool, os.X_OK):
        return local_tool

    return None

def build_shim_from_source(devkitpro_path=None, enable_debug_flash=False):
    """Compiles dvd_nand_shim.bin from source using devkitPPC."""
    devkitpro = devkitpro_path or os.environ.get("DEVKITPRO", "/opt/devkitpro")
    gcc_path = os.path.join(devkitpro, "devkitPPC", "bin", "powerpc-eabi-gcc")
    objcopy_path = os.path.join(devkitpro, "devkitPPC", "bin", "powerpc-eabi-objcopy")

    if not os.path.isfile(gcc_path) or not os.path.isfile(objcopy_path):
        if shutil.which("powerpc-eabi-gcc") and shutil.which("powerpc-eabi-objcopy"):
            gcc_path = shutil.which("powerpc-eabi-gcc")
            objcopy_path = shutil.which("powerpc-eabi-objcopy")
        else:
            raise FileNotFoundError(f"devkitPPC not found at {gcc_path}. Please install devkitPPC or use precompiled binaries.")

    src_dir = os.path.join(SCRIPT_DIR, "src")
    out_dir = os.path.join(SCRIPT_DIR, "precompiled")
    os.makedirs(out_dir, exist_ok=True)

    elf_path = os.path.join(out_dir, "dvd_nand_shim.elf")
    map_path = os.path.join(out_dir, "dvd_nand_shim.elf.map")
    bin_path = os.path.join(out_dir, "dvd_nand_shim.bin")

    flash_flag = "-DENABLE_SENSOR_FLASH=1" if enable_debug_flash else "-DENABLE_SENSOR_FLASH=0"
    print(f"Compiling DVD-NAND shim from source (Debug Flash: {'ON' if enable_debug_flash else 'OFF'})...")
    cflags = [
        "-O2", "-Wall", "-m32", "-mhard-float", "-meabi", "-mno-sdata",
        "-nostartfiles", "-nodefaultlibs", "-fno-builtin", "-fno-tree-loop-distribute-patterns",
        flash_flag,
        "-T", os.path.join(src_dir, "shim.ld"),
        f"-Wl,-Map={map_path}",
        "-o", elf_path,
        os.path.join(src_dir, "dvd_nand_shim.c"),
        os.path.join(src_dir, "trampoline.S")
    ]
    subprocess.run([gcc_path] + cflags, check=True)
    subprocess.run([objcopy_path, "-O", "binary", elf_path, bin_path], check=True)
    if os.path.isfile(elf_path): os.remove(elf_path)
    print(f"Successfully compiled: {bin_path}")
    return bin_path

def extract_nandloader_from_wad(wad_path, common_key, out_path):
    """Extracts the boot content nandloader from a system WAD (e.g. Wii Shop Channel / Mii Channel)."""
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    
    with open(wad_path, 'rb') as f:
        wad = f.read()

    hdr_len, _, cert_len, _, tik_len, tmd_len, data_len, _ = struct.unpack('>8I', wad[:32])
    cert_off = align64(hdr_len)
    cert = wad[cert_off:cert_off+cert_len]
    off = cert_off + align64(cert_len)
    tik = wad[off:off+tik_len]
    off += align64(tik_len)
    tmd = wad[off:off+tmd_len]
    off += align64(tmd_len)
    enc_data = wad[off:off+data_len]

    title_id = tik[0x1DC:0x1E4]
    enc_title_key = tik[0x1BF:0x1CF]

    iv = title_id + b'\x00' * 8
    cipher = Cipher(algorithms.AES(common_key), modes.CBC(iv))
    dec = cipher.decryptor()
    title_key = dec.update(enc_title_key) + dec.finalize()

    boot_idx = struct.unpack('>H', tmd[0x1E0:0x1E2])[0]
    num_contents = struct.unpack('>H', tmd[0x1DE:0x1E0])[0]

    c_off = 0x1E4
    data_cursor = 0
    boot_content_data = None

    for i in range(num_contents):
        cid, cidx, ctype, csize, chash = struct.unpack('>IHHq20s', tmd[c_off:c_off+36])
        c_off += 36

        padded_size = align64(csize)
        c_enc = enc_data[data_cursor:data_cursor+padded_size]
        data_cursor += padded_size

        if cidx == boot_idx:
            c_iv = struct.pack('>H14x', cidx)
            c_cipher = Cipher(algorithms.AES(title_key), modes.CBC(c_iv))
            c_dec = c_cipher.decryptor()
            dec_data = c_dec.update(c_enc) + c_dec.finalize()
            boot_content_data = dec_data[:csize]
            break

    if not boot_content_data:
        raise RuntimeError("Failed to locate boot content inside provided WAD.")

    with open(out_path, 'wb') as f:
        f.write(boot_content_data)
    print(f"Extracted boot nandloader from {wad_path} -> {out_path}")
    return out_path, cert, tik, tmd[:0x1E4]

def auto_discover_inputs():
    """Scans the 'input/' directory and current directory for required assets."""
    search_dirs = [os.path.join(SCRIPT_DIR, "input"), "input", SCRIPT_DIR, "."]
    
    game_path = None
    loader_path = None

    # 1. Search for Game Disc Image or Directory
    for d in search_dirs:
        if not os.path.isdir(d): continue
        for item in os.listdir(d):
            full_p = os.path.join(d, item)
            low = item.lower()
            if os.path.isfile(full_p) and (low.endswith(".wbfs") or low.endswith(".iso")):
                if "worms" in low or "silp" in low or "battle" in low:
                    game_path = full_p
                    break
                elif not game_path:
                    game_path = full_p
            elif os.path.isdir(full_p) and item not in ("scripts", "src", "precompiled", "tools", "dist", "work_temp"):
                if os.path.isfile(os.path.join(full_p, "main.dol")) or os.path.isdir(os.path.join(full_p, "DataWii")):
                    game_path = full_p
                    break
        if game_path: break

    # 2. Search for NAND Bootloader (.app, .dol, or system/WiiWare .wad)
    for d in search_dirs:
        if not os.path.isdir(d): continue
        for item in os.listdir(d):
            full_p = os.path.join(d, item)
            low = item.lower()
            if os.path.isfile(full_p):
                if low.endswith(".app") and (item.startswith("00000060") or "loader" in low):
                    loader_path = full_p
                    break
                elif low.endswith(".dol") and ("loader" in low or "nand" in low):
                    loader_path = full_p
                    break
                elif low.endswith(".wad") and ("shop" in low or "haba" in low or "mii" in low or "haca" in low or "channel" in low or "wiiware" in low):
                    if "worms" not in low and "output" not in low:
                        loader_path = full_p
                        break
        if loader_path: break

    return game_path, loader_path

def main():
    parser = argparse.ArgumentParser(description="Convert Worms: Battle Islands into a standalone Wii Channel WAD.")
    parser.add_argument("-i", "--input", help="Input Worms Battle Islands disc image (.wbfs, .iso) or extracted folder.")
    parser.add_argument("-l", "--loader", help="Path to NAND bootloader (.dol, .app, or system WAD like Wii Shop / Mii Channel).")
    parser.add_argument("-o", "--output", default="worms_bi.wad", help="Output WAD filename (default: worms_bi.wad).")
    parser.add_argument("--key", help="16-byte hex Wii Common Key.")
    parser.add_argument("--otp", help="Path to otp.bin from Wii or Wii U vWii.")
    parser.add_argument("--keyfile", help="Path to common.key or key.bin.")
    parser.add_argument("--build-shim", action="store_true", help="Recompile the DVD-NAND shim from source with devkitPPC.")
    parser.add_argument("--debug-flash", action="store_true", help="Enable hardware sensor bar LED diagnostic blinking (for debugging boot hangs).")
    parser.add_argument("--devkitpro", help="Custom path to devkitPro directory.")
    parser.add_argument("--work-dir", default="work_temp", help="Temporary working directory.")
    parser.add_argument("--keep-temp", action="store_true", help="Keep temporary working files after completion.")

    args = parser.parse_args()
    is_interactive = sys.stdin.isatty()

    print("=" * 65)
    print(" Worms: Battle Islands - Standalone WAD Channel Converter")
    print("=" * 65)

    # Auto-discovery if arguments omitted (e.g. double-clicked)
    input_game = args.input
    input_loader = args.loader

    if not input_game or not input_loader:
        auto_game, auto_loader = auto_discover_inputs()
        if not input_game: input_game = auto_game
        if not input_loader: input_loader = auto_loader

    # Resolve Key
    common_key = get_common_key(key_arg=args.key, otp_path=args.otp, keyfile_path=args.keyfile)

    # Check for missing prerequisites
    missing = []
    if not input_game:
        missing.append(("Game Disc Image (.wbfs / .iso)", "Place 'Worms Battle Island.wbfs' (or .iso) into the 'input/' folder."))
    if not input_loader:
        missing.append(("NAND Bootloader (.app / .dol / .wad)", "Place '00000060.app' (Wii Shop v21) or a system channel WAD into the 'input/' folder."))
    if not common_key:
        missing.append(("Wii Common Key / OTP", "Place 'otp.bin' (from Wii/vWii) or 'common.key' into the 'input/' folder."))

    if missing:
        print("\nScanning for required files in 'input/' folder and current directory...\n")
        print("Status Checklist:")
        print(f"  [{'✓' if input_game else '✗'}] Game Disc Image : {input_game or 'Missing'}")
        print(f"  [{'✓' if input_loader else '✗'}] NAND Bootloader : {input_loader or 'Missing'}")
        print(f"  [{'✓' if common_key else '✗'}] Wii Common Key  : {'Found / Validated' if common_key else 'Missing'}")
        
        print("\nMissing required components:")
        for name, hint in missing:
            print(f"  • {name}:")
            print(f"    -> {hint}")

        if is_interactive and len(sys.argv) == 1:
            try:
                input("\nPress Enter to exit...")
            except (KeyboardInterrupt, EOFError):
                pass
        sys.exit(1)

    print("\nLocated Files:")
    print(f"  [✓] Game Disc Image : {input_game}")
    print(f"  [✓] NAND Bootloader : {input_loader}")
    print(f"  [✓] Wii Common Key  : Loaded successfully")
    print("-" * 65 + "\n")

    work_dir = os.path.abspath(args.work_dir)
    os.makedirs(work_dir, exist_ok=True)

    try:
        # 2. Resolve Shim
        if args.build_shim or args.debug_flash:
            shim_bin = build_shim_from_source(args.devkitpro, enable_debug_flash=args.debug_flash)
        else:
            shim_bin = os.path.join(SCRIPT_DIR, "precompiled", "dvd_nand_shim.bin")
            if not os.path.isfile(shim_bin):
                print("Precompiled shim not found. Attempting to build from source...")
                try:
                    shim_bin = build_shim_from_source(args.devkitpro, enable_debug_flash=args.debug_flash)
                except FileNotFoundError:
                    print("\nError: 'precompiled/dvd_nand_shim.bin' is not present and devkitPPC was not found.")
                    print("Please either:")
                    print("  1. Download the official release package from GitHub Releases (which includes the prebuilt shim), OR")
                    print("  2. Install devkitPPC and build the shim using 'make all'.\n")
                    sys.exit(1)

        # 3. Extract Game Assets
        extracted_dir = os.path.join(work_dir, "extracted")
        if os.path.isdir(input_game):
            extracted_dir = input_game
        else:
            extract_game(input_game, extracted_dir, common_key=common_key)

        main_dol_path = os.path.join(extracted_dir, "main.dol")
        if not os.path.isfile(main_dol_path):
            main_dol_path = os.path.join(extracted_dir, "sys", "main.dol")
        if not os.path.isfile(main_dol_path):
            raise FileNotFoundError(f"main.dol not found in extracted game assets ({extracted_dir})")

        banner_path = os.path.join(extracted_dir, "opening.bnr")
        if not os.path.isfile(banner_path):
            banner_path = os.path.join(extracted_dir, "files", "opening.bnr")
        if not os.path.isfile(banner_path):
            raise FileNotFoundError(f"opening.bnr not found in extracted game assets ({extracted_dir})")

        # 4. Resolve NAND Loader
        nand_loader_path = input_loader
        cert_data, tik_template, tmd_template = None, None, None
        if not os.path.isfile(nand_loader_path):
            raise FileNotFoundError(f"Specified NAND loader file not found: {input_loader}")

        if nand_loader_path.lower().endswith(".wad"):
            loader_dest = os.path.join(work_dir, "nand_loader.app")
            nand_loader_path, cert_data, tik_template, tmd_template = extract_nandloader_from_wad(nand_loader_path, common_key, loader_dest)

        # 5. Patch main.dol
        patched_dol = os.path.join(work_dir, "main_patched.dol")
        print("Patching main.dol with DVD-NAND redirection shim...")
        from scripts.patch_dol import patch_dol
        patch_dol(main_dol_path, shim_bin, None, patched_dol)

        # 6. Compress DOL with LZ11
        lz11_dol = os.path.join(work_dir, "main_patched.dol.lz11")
        lz11_tool = ensure_lz11_compress()
        if lz11_tool:
            print("Compressing main_patched.dol with LZ11...")
            subprocess.run([lz11_tool, patched_dol, lz11_dol], check=True)
        else:
            print("Warning: Native lz11_compress unavailable. Using Python LZ11 compressor...")
            from scripts.compress_lz11 import compress_file
            compress_file(patched_dol, lz11_dol)

        # 7. Build Content 2 Archive
        content2_path = os.path.join(work_dir, "content2.bin")
        pack_content2(extracted_dir, content2_path)

        # 8. Package Final WAD
        out_wad = os.path.abspath(args.output)
        print(f"Creating standalone WAD channel: {out_wad}...")
        create_wad(lz11_dol, content2_path, banner_path, nand_loader_path, out_wad,
                   common_key=common_key, cert_data=cert_data, tik_template=tik_template, tmd_template=tmd_template)

        print("\n" + "=" * 65)
        print(f" SUCCESS: {os.path.basename(out_wad)} created successfully!")
        print(f" Output Location: {out_wad}")
        print(" You can now install and play this WAD on Wii, vWii, or Dolphin.")
        print("=" * 65 + "\n")

    finally:
        if not args.keep_temp and os.path.isdir(work_dir):
            shutil.rmtree(work_dir, ignore_errors=True)

    if is_interactive and len(sys.argv) == 1:
        try:
            input("Press Enter to exit...")
        except (KeyboardInterrupt, EOFError):
            pass

if __name__ == '__main__':
    main()
