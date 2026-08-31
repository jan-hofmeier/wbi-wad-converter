# Worms: Battle Islands - Standalone WAD Channel Converter

A standalone converter and runtime shim engine that transforms retail disc copies of **Worms: Battle Islands** (Wii / RVL) into an official-style, fully self-contained **Wii Channel WAD** (`SILP`) bootable directly from the Wii System Menu on retail Wii, vWii (Wii U), and the Dolphin Emulator.

## Human Remark

This was created using Sonnet and Gemini, but wouldn't have been possible without the amazing work of the community reverse engeniering the system and file formats.

Why does this even exist? you might ask. There is not much reason to do this as USB loaders work perfectly fine and the NAND very is limited. I was just suprised how small the game was when I dumped it and later learned that it was orginally intented as a Wii Ware release. So this is just how the Developers intended the game to be played. I just wondered if it was possible and what it would and had some tokens left at the end of the month. There is a noticable improvment in loading times compared to a USB Loader tho.

I let the AI work mostly on its own with only minimal input regarding the goal and architecture descisions and a few nudges when it drifted off / fell into a rabit hole, just so see where it would get. To my suprise it was very good at reverse engineering the binaries and produces a working wad at the end (tested on Dolphin and vWii).
But use this at your own risk. Apart from skimming through the code, there was no review.

---

## Features

- **100% Standalone Channel**: The resulting WAD contains the executable, banner, bootloader, and all 54 game assets (`content2.bin`) in a native multi-content WAD format (`~44.3 MB`).
- **No SD Card or Loose Files Required**: Everything installs directly into the NAND filesystem as standard channel contents.
- **Stock IOS Compatibility**: Runs on unmodified retail **`IOS56`** without requiring `HW_AHBPROT`, cIOS, or custom system patches.
- **Official NAND Bootloader Support**: Compatible with official unpatched retail Nintendo NAND loaders (e.g. from the Wii Shop Channel v21 or Mii Channel).
- **On-Demand Dynamic Streaming**: Transparently streams THP intro videos, audio banks, dynamic RSO modules (`Modules.rso`), and compressed `.zip` packages on the fly using native synchronous NAND calls with minimal RAM overhead.
- **Clean & Legal**: Contains only custom reverse-engineered shim source code and tooling. No proprietary game assets, Nintendo binaries, or encryption keys are distributed in this repository.

---

## Two-Stage Workflow

This project is organized into two stages:

1. **Stage 1 (Build / Developer)**: Compiles the PowerPC DVD-NAND redirection shim and native tools into precompiled release binaries.
2. **Stage 2 (Conversion / User)**: Takes the user's legally dumped game (`.wbfs` / `.iso`), extracts assets, patches the DOL, compresses it to LZ11, and packages the final WAD channel.

---

## Prerequisites

- **Python 3.8+** with `cryptography` package:
  
  ```bash
  pip install cryptography
  ```
- **GCC** (optional, for compiling the native fast LZ11 compressor; a pure Python fallback is included).
- **devkitPPC** (optional, only needed if modifying and recompiling the PowerPC shim from source).

---

## User Guide: Building the WAD (Stage 2)

### Quick Start (Double-Click / Drag & Drop):

1. Drop your files into the **`input/`** folder:
   
   - **Game**: `Worms Battle Island.wbfs` (or `.iso`)
   
   - **Bootloader**: `00000060.app` (from Wii Shop v21) **OR** `Shopping-Channel-HABA-v21-Wii.wad` **OR** `nand_loader.dol`
   
   - **Key**: `otp.bin` (from Wii / Wii U) **OR** `common.key`
2. **Double-click `convert.py`** (or run `python3 convert.py`).
3. The script automatically detects the files, builds `worms_bi.wad`, and reports the result!

---

### Command-Line Usage (CLI):

```bash
# Automatic discovery mode (scans 'input/' and current directory):
python3 convert.py

# Explicit paths:
python3 convert.py -i "Worms Battle Island.wbfs" -l "Shopping-Channel-HABA-v21-Wii.wad" -o "worms_bi.wad" --otp "otp.bin"

# Using a decrypted nandloader .app directly:
python3 convert.py -i "Worms Battle Island.wbfs" -l "00000060.app" -o "worms_bi.wad"

# Developer mode (recompiling the shim from source with devkitPPC):
python3 convert.py -i "Worms Battle Island.wbfs" -l "00000060.app" --build-shim -o "worms_bi.wad"
```

---

## Developer Guide: Building from Source (Stage 1)

If you are developing or modifying the shim code:

```bash
# 1. Compile the PowerPC shim and native tools
make all

# 2. Package a release distribution archive (saved in dist/)
make release
```

---

## Technical Architecture

```
                             worms_bi.wad (~44.3 MB)
   ┌────────────────────────────────────────────────────────────────────────┐
   │ Content 0: opening.bnr      (Channel Banner & Icon)                    │
   │ Content 1: main_patched.dol (Game Executable, ~2.2 MB LZ11 compressed) │
   │ Content 2: 00000002.app     (41.6 MB Encrypted Data Archive, 54 assets)│
   │ Content 3: nand_loader.dol  (Official Retail Nintendo NAND Bootloader) │
   └────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
[Game Engine]                  [NAND Storage]
      │                              │
      │ 1. DVDOpen("first.zip")      │
      ├──────────────────────────────┤
      │ 2. DVDReadAsyncPrio(buf, len)│
      ▼                              │
[dvd_nand_shim]                      │
      │ 3. Match in s_FileTable      │
      │    (offset in content 2)     │
      │                              │
      │ 4. NANDSeek(offset) ─────────┼──► /title/00010001/53494c50/content/00000002.app
      │ 5. NANDRead(buf, 32KB chunks)┼──► Direct streaming into caller buffer
      │ 6. DCFlushRange(buf, len)    │
      │ 7. Set cb.transferredSize    │
      │ 8. Invoke DVD Callback       │
      ▼                              │
[Game Engine continues...]           │
```

### Memory Map (MEM1 & MEM2)

- **MEM1 (`Text[2]`)**: The custom shim is linked into a dedicated section at `0x805B0000`–`0x805B4000`. `ArenaLo` is set to `0x805C0000` to prevent memory heap collisions.
- **MEM2**: Left entirely unburdened for dynamic game allocations (unzipping destructible landscapes, particle textures, and audio mixing).

### Verified Synchronous NAND Functions in RVL SDK

- `NANDOpen`: `0x802AC240` — `(const char* path, NANDFileInfo* info, u8 accType)`
- `NANDClose`: `0x802AC4E0` — `(NANDFileInfo* info)`
- `NANDRead`: `0x802AB360` — `(NANDFileInfo* info, void* buf, u32 len)`
- `NANDSeek`: `0x802AB540` — `(NANDFileInfo* info, s32 offset, s32 whence)`
- `NANDGetLength`: `0x802AC550` — `(NANDFileInfo* info, u32* length)`

---

## Project Structure

```
wbi-wad-converter/
├── convert.py                 # Main CLI converter tool (Stage 2 / All-in-one)
├── build_release.py           # Stage 1 release builder
├── Makefile                   # Automation Makefile
├── README.md                  # Documentation
├── .gitignore                 # Git ignore configuration
├── src/
│   ├── dvd_nand_shim.c        # DVD-to-NAND C shim implementation
│   ├── trampoline.S           # PowerPC assembly hook trampolines
│   ├── shim.ld                # Linker script for Text[2] section
│   └── lz11_compress.c        # Standalone native C Nintendo LZ11 compressor
├── scripts/
│   ├── keys.py                # Wii Common Key & OTP extraction logic
│   ├── extract_game.py        # Pure-Python WBFS/ISO disc image unpacker
│   ├── patch_dol.py           # DOL section injector and SDK branch hooker
│   ├── pack_content2.py       # 54-asset content2.bin concatenator
│   ├── pack_wad.py            # WAD assembler (TMD, Ticket, Certs, Cryptography)
│   └── compress_lz11.py       # Pure-Python LZ11 compressor fallback
└── precompiled/               # Generated during release packaging (or 'make all')
    ├── dvd_nand_shim.bin      # Precompiled PowerPC shim binary
    └── dvd_nand_shim.elf.map  # Symbol map of precompiled shim
```

---

## Credits & Acknowledgments

This project builds upon reverse-engineering research and documentation contributed by the homebrew community:

- **[WiiBrew.org](https://wiibrew.org)**: For comprehensive technical documentation on the Wii WAD container format, Title Metadata (TMD), Ticket encryption, ISFS NAND filesystem architecture, DOL section headers, and OTP memory mapping.
- **[Dolphin Emulator](https://dolphin-emu.org)**: For invaluable open-source IOS filesystem proxy and Bluetooth emulation diagnostics, which enabled precise tracing and verification of NAND streaming and WPAD packet handling.
- **[devkitPro / devkitPPC](https://devkitpro.org)**: For the PowerPC GCC toolchain (`powerpc-eabi-gcc`) used to compile the bare-metal runtime shim.
- **[Wiimms (WIT / Wiimms ISO Tools)](https://wit.wiimm.de)**: For documentation and reverse-engineering of the Wii WBFS disc format and FST filesystem structures.
- **[GBATek](http://problemkaputt.de/gbatek.htm) & [DSiBrew](https://dsibrew.org)**: For specifications and references on the Nintendo LZ77 Type 0x11 (LZ11) compression algorithm.
- **[OpenShopChannel Project](https://github.com/OpenShopChannel)**: For open-source NAND loader research and channel bootstrapping references.

---

## Legal & Clean-Room Notice

This project is created strictly for preservation, conversion, and interoperability purposes. It does not contain copyrighted game data, proprietary Nintendo system binaries, or cryptographic master keys. Users must provide their own legitimately acquired game copy and console dumps.
