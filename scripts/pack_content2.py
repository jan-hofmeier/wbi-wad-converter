#!/usr/bin/env python3
"""
Packs the 54 Worms Battle Islands assets into content2.bin matching s_FileTable offsets.
"""

import os, sys

FILE_TABLE = [
    ("DataWii/Audio/Atrac/Generic.spd", 10222796, 0x00000000),
    ("DataWii/Audio/Atrac/Generic.spt", 152, 0x009BFD00),
    ("DataWii/Audio/Banks/sfx/FE_Ambient.spd", 2640527, 0x009BFDC0),
    ("DataWii/Audio/Banks/sfx/FE_Ambient.spt", 2076, 0x00C44880),
    ("DataWii/Audio/Banks/sfx/FrontEnd.spd", 39887, 0x00C450C0),
    ("DataWii/Audio/Banks/sfx/FrontEnd.spt", 522, 0x00C4ECC0),
    ("DataWii/Audio/Banks/sfx/Game.spd", 1685760, 0x00C4EF00),
    ("DataWii/Audio/Banks/sfx/Game.spt", 3778, 0x00DEA800),
    ("DataWii/Audio/Banks/landscapeeditor.spd", 122848, 0x00DEB700),
    ("DataWii/Audio/Banks/landscapeeditor.spt", 818, 0x00E09700),
    ("DataWii/Audio/Banks/sfx/Misc.spd", 844772, 0x00E09A40),
    ("DataWii/Audio/Banks/sfx/Misc.spt", 3038, 0x00ED7E40),
    ("DataWii/Audio/Banks/speech/Area51.spd", 363822, 0x00ED8A40),
    ("DataWii/Audio/Banks/speech/Area51.spt", 1854, 0x00F31780),
    ("DataWii/Audio/Banks/speech/CrazedWarVet.spd", 360676, 0x00F31EC0),
    ("DataWii/Audio/Banks/speech/CrazedWarVet.spt", 1854, 0x00F89FC0),
    ("DataWii/Audio/Banks/speech/English.spd", 224683, 0x00F8A700),
    ("DataWii/Audio/Banks/speech/English.spt", 1854, 0x00FC14C0),
    ("DataWii/Audio/Banks/speech/French.spd", 201535, 0x00FC1C00),
    ("DataWii/Audio/Banks/speech/French.spt", 1854, 0x00FF2F40),
    ("DataWii/Audio/Banks/speech/German.spd", 201738, 0x00FF3680),
    ("DataWii/Audio/Banks/speech/German.spt", 1854, 0x01024AC0),
    ("DataWii/Audio/Banks/speech/GuerillaWarfare.spd", 331626, 0x01025200),
    ("DataWii/Audio/Banks/speech/GuerillaWarfare.spt", 1854, 0x01076180),
    ("DataWii/Audio/Banks/speech/Italian.spd", 234358, 0x010768C0),
    ("DataWii/Audio/Banks/speech/Italian.spt", 1854, 0x010AFC40),
    ("DataWii/Audio/Banks/speech/Jarhead.spd", 402743, 0x010B0380),
    ("DataWii/Audio/Banks/speech/Jarhead.spt", 1854, 0x011128C0),
    ("DataWii/Audio/Banks/speech/PresidentBush.spd", 555516, 0x01113000),
    ("DataWii/Audio/Banks/speech/PresidentBush.spt", 1854, 0x0119AA00),
    ("DataWii/Audio/Banks/speech/PreviewWii.spd", 155794, 0x0119B140),
    ("DataWii/Audio/Banks/speech/PreviewWii.spt", 1040, 0x011C1200),
    ("DataWii/Audio/Banks/speech/ReligiousSold.spd", 467310, 0x011C1640),
    ("DataWii/Audio/Banks/speech/ReligiousSold.spt", 1854, 0x012337C0),
    ("DataWii/Audio/Banks/speech/SecretAgent.spd", 423911, 0x01233F00),
    ("DataWii/Audio/Banks/speech/SecretAgent.spt", 1854, 0x0129B700),
    ("DataWii/Audio/Banks/speech/SecretMilitary.spd", 323506, 0x0129BE40),
    ("DataWii/Audio/Banks/speech/SecretMilitary.spt", 1854, 0x012EAE00),
    ("DataWii/Audio/Banks/speech/Spanish.spd", 233597, 0x012EB540),
    ("DataWii/Audio/Banks/speech/Spanish.spt", 1854, 0x013245C0),
    ("DataWii/Audio/Banks/speech/SpecialOps.spd", 295915, 0x01324D00),
    ("DataWii/Audio/Banks/speech/SpecialOps.spt", 1854, 0x0136D100),
    ("DataWii/BuildInfo.txt", 52, 0x0136D840),
    ("DataWii/Default.cfg", 20, 0x0136D880),
    ("DataWii/Modules.rso", 2478912, 0x0136D8C0),
    ("DataWii/Video/T17.thp", 1906912, 0x015CAC00),
    ("DataWii/Video/THQ.thp", 3766656, 0x0179C500),
    ("DataWii/Video/ThpPlayerFiles/2nd_time.mid", 12103, 0x01B33E80),
    ("DataWii/Video/ThpPlayerFiles/gm16adpcm.pcm", 881485, 0x01B36E00),
    ("DataWii/Video/ThpPlayerFiles/gm16adpcm.wt", 193082, 0x01C0E180),
    ("DataWii/Wow3.sel", 44736, 0x01C3D3C0),
    ("DataWii/first.zip", 733221, 0x01C48280),
    ("DataWii/frontend.zip", 4594145, 0x01CFB2C0),
    ("DataWii/game.zip", 8604285, 0x0215CCC0),
]

def pack_content2(game_dir, out_file):
    """
    Packs the assets located in game_dir into out_file (content2.bin).
    """
    total_size = 0x0215CCC0 + 8604285
    # Align to 64 bytes
    total_size = (total_size + 63) & ~63
    
    print(f"Building content2 archive ({total_size} bytes / {total_size/1024/1024:.2f} MB)...")
    buffer = bytearray(total_size)

    for rel_path, expected_size, offset in FILE_TABLE:
        # Search relative to game_dir
        candidates = [
            os.path.join(game_dir, rel_path),
            os.path.join(game_dir, rel_path.lower()),
            os.path.join(game_dir, "files", rel_path),
            os.path.join(game_dir, "DATA", "files", rel_path)
        ]
        
        found_path = None
        for cand in candidates:
            if os.path.isfile(cand):
                found_path = cand
                break
        
        # Case-insensitive and basename fallback
        if not found_path:
            norm_target = rel_path.replace("\\", "/").lower()
            base_name = os.path.basename(rel_path).lower()
            for root, _, files in os.walk(game_dir):
                for f in files:
                    full_p = os.path.join(root, f)
                    rel_p = os.path.relpath(full_p, game_dir).replace("\\", "/").lower()
                    if rel_p == norm_target or rel_p.endswith(norm_target) or f.lower() == base_name:
                        found_path = full_p
                        break
                if found_path: break

        if not found_path:
            raise FileNotFoundError(f"Missing required asset: {rel_path}")

        with open(found_path, "rb") as f:
            data = f.read()

        buffer[offset:offset+len(data)] = data

    with open(out_file, "wb") as f:
        f.write(buffer)

    print(f"Successfully generated {out_file} ({len(buffer)} bytes)")

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: pack_content2.py <game_extracted_dir> <output_content2.bin>")
        sys.exit(1)
    pack_content2(sys.argv[1], sys.argv[2])
