#!/usr/bin/env python3
"""
Stage 1: Build Release Distribution Package
Compiles the PowerPC DVD-NAND shim and host tools, then creates a clean distribution archive.
"""

import os, sys, shutil, subprocess, zipfile

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def build_all(version="1.0.0"):
    print(f"=== Building Worms Battle Islands WAD Converter v{version} Release ===\n")
    
    src_dir = os.path.join(SCRIPT_DIR, "src")
    precompiled_dir = os.path.join(SCRIPT_DIR, "precompiled")
    os.makedirs(precompiled_dir, exist_ok=True)

    devkitpro = os.environ.get("DEVKITPRO", "/opt/devkitpro")
    gcc_path = os.path.join(devkitpro, "devkitPPC", "bin", "powerpc-eabi-gcc")
    objcopy_path = os.path.join(devkitpro, "devkitPPC", "bin", "powerpc-eabi-objcopy")

    elf_path = os.path.join(precompiled_dir, "dvd_nand_shim.elf")
    map_path = os.path.join(precompiled_dir, "dvd_nand_shim.elf.map")
    bin_path = os.path.join(precompiled_dir, "dvd_nand_shim.bin")

    if os.path.isfile(gcc_path) and os.path.isfile(objcopy_path):
        print("[1/3] Compiling PowerPC DVD-NAND shim...")
        src_dir = os.path.join(SCRIPT_DIR, "src")
        cflags = [
            "-O2", "-Wall", "-m32", "-mhard-float", "-meabi", "-mno-sdata",
            "-nostartfiles", "-nodefaultlibs", "-fno-builtin", "-fno-tree-loop-distribute-patterns",
            "-T", os.path.join(src_dir, "shim.ld"),
            f"-Wl,-Map={map_path}",
            "-o", elf_path,
            os.path.join(src_dir, "dvd_nand_shim.c"),
            os.path.join(src_dir, "trampoline.S")
        ]
        subprocess.run([gcc_path] + cflags, check=True)
        subprocess.run([objcopy_path, "-O", "binary", elf_path, bin_path], check=True)
        if os.path.isfile(elf_path): os.remove(elf_path)
        print(f"  -> Generated {bin_path} ({os.path.getsize(bin_path)} bytes)")
    elif os.path.isfile(bin_path):
        print("[1/3] Using existing precompiled PowerPC DVD-NAND shim...")
    else:
        print(f"Error: devkitPPC gcc not found at {gcc_path} and no precompiled shim available.")
        sys.exit(1)

    # 2. Compile native tools
    print("\n[2/3] Compiling native host LZ11 compressor...")
    tools_dir = os.path.join(SCRIPT_DIR, "tools")
    os.makedirs(tools_dir, exist_ok=True)
    lz11_tool = os.path.join(tools_dir, "lz11_compress")
    if shutil.which("gcc"):
        subprocess.run(["gcc", "-O3", os.path.join(src_dir, "lz11_compress.c"), "-o", lz11_tool], check=True)
        print(f"  -> Generated {lz11_tool}")
    else:
        print("  -> Warning: gcc not found, python fallback compressor will be used.")

    # 3. Create Distribution Archive
    print("\n[3/3] Packaging distribution archive...")
    dist_dir = os.path.join(SCRIPT_DIR, "dist")
    os.makedirs(dist_dir, exist_ok=True)
    zip_path = os.path.join(dist_dir, f"wbi-wad-converter-v{version}.zip")

    files_to_pack = [
        ("convert.py", "convert.py"),
        ("README.md", "README.md"),
        ("Makefile", "Makefile"),
        (os.path.join("precompiled", "dvd_nand_shim.bin"), "precompiled/dvd_nand_shim.bin"),
        (os.path.join("precompiled", "dvd_nand_shim.elf.map"), "precompiled/dvd_nand_shim.elf.map"),
        (os.path.join("src", "dvd_nand_shim.c"), "src/dvd_nand_shim.c"),
        (os.path.join("src", "trampoline.S"), "src/trampoline.S"),
        (os.path.join("src", "shim.ld"), "src/shim.ld"),
        (os.path.join("src", "lz11_compress.c"), "src/lz11_compress.c"),
        (os.path.join("scripts", "keys.py"), "scripts/keys.py"),
        (os.path.join("scripts", "extract_game.py"), "scripts/extract_game.py"),
        (os.path.join("scripts", "patch_dol.py"), "scripts/patch_dol.py"),
        (os.path.join("scripts", "pack_content2.py"), "scripts/pack_content2.py"),
        (os.path.join("scripts", "pack_wad.py"), "scripts/pack_wad.py"),
        (os.path.join("scripts", "compress_lz11.py"), "scripts/compress_lz11.py"),
        (os.path.join("input", "README.txt"), "input/README.txt"),
    ]
    if os.path.isfile(lz11_tool):
        files_to_pack.append((os.path.join("tools", "lz11_compress"), "tools/lz11_compress"))

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for local_p, zip_p in files_to_pack:
            abs_p = os.path.join(SCRIPT_DIR, local_p)
            if os.path.isfile(abs_p):
                zf.write(abs_p, zip_p)

    print(f"  -> Created release package: {zip_path} ({os.path.getsize(zip_path)} bytes)")
    print("\n=== Release Build Finished Successfully ===")

if __name__ == '__main__':
    ver = sys.argv[1] if len(sys.argv) > 1 else "1.0.0"
    build_all(ver)
