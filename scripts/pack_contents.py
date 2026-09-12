#!/usr/bin/env python3
"""
Loads the 54 Worms Battle Islands game assets as individual content entries.
Each file becomes its own WAD content rather than being packed into a single blob.
"""

import os, sys

FILE_TABLE = [
    ("DataWii/Audio/Atrac/Generic.spd", 10222796),
    ("DataWii/Audio/Atrac/Generic.spt", 152),
    ("DataWii/Audio/Banks/sfx/FE_Ambient.spd", 2640527),
    ("DataWii/Audio/Banks/sfx/FE_Ambient.spt", 2076),
    ("DataWii/Audio/Banks/sfx/FrontEnd.spd", 39887),
    ("DataWii/Audio/Banks/sfx/FrontEnd.spt", 522),
    ("DataWii/Audio/Banks/sfx/Game.spd", 1685760),
    ("DataWii/Audio/Banks/sfx/Game.spt", 3778),
    ("DataWii/Audio/Banks/landscapeeditor.spd", 122848),
    ("DataWii/Audio/Banks/landscapeeditor.spt", 818),
    ("DataWii/Audio/Banks/sfx/Misc.spd", 844772),
    ("DataWii/Audio/Banks/sfx/Misc.spt", 3038),
    ("DataWii/Audio/Banks/speech/Area51.spd", 363822),
    ("DataWii/Audio/Banks/speech/Area51.spt", 1854),
    ("DataWii/Audio/Banks/speech/CrazedWarVet.spd", 360676),
    ("DataWii/Audio/Banks/speech/CrazedWarVet.spt", 1854),
    ("DataWii/Audio/Banks/speech/English.spd", 224683),
    ("DataWii/Audio/Banks/speech/English.spt", 1854),
    ("DataWii/Audio/Banks/speech/French.spd", 201535),
    ("DataWii/Audio/Banks/speech/French.spt", 1854),
    ("DataWii/Audio/Banks/speech/German.spd", 201738),
    ("DataWii/Audio/Banks/speech/German.spt", 1854),
    ("DataWii/Audio/Banks/speech/GuerillaWarfare.spd", 331626),
    ("DataWii/Audio/Banks/speech/GuerillaWarfare.spt", 1854),
    ("DataWii/Audio/Banks/speech/Italian.spd", 234358),
    ("DataWii/Audio/Banks/speech/Italian.spt", 1854),
    ("DataWii/Audio/Banks/speech/Jarhead.spd", 402743),
    ("DataWii/Audio/Banks/speech/Jarhead.spt", 1854),
    ("DataWii/Audio/Banks/speech/PresidentBush.spd", 555516),
    ("DataWii/Audio/Banks/speech/PresidentBush.spt", 1854),
    ("DataWii/Audio/Banks/speech/PreviewWii.spd", 155794),
    ("DataWii/Audio/Banks/speech/PreviewWii.spt", 1040),
    ("DataWii/Audio/Banks/speech/ReligiousSold.spd", 467310),
    ("DataWii/Audio/Banks/speech/ReligiousSold.spt", 1854),
    ("DataWii/Audio/Banks/speech/SecretAgent.spd", 423911),
    ("DataWii/Audio/Banks/speech/SecretAgent.spt", 1854),
    ("DataWii/Audio/Banks/speech/SecretMilitary.spd", 323506),
    ("DataWii/Audio/Banks/speech/SecretMilitary.spt", 1854),
    ("DataWii/Audio/Banks/speech/Spanish.spd", 233597),
    ("DataWii/Audio/Banks/speech/Spanish.spt", 1854),
    ("DataWii/Audio/Banks/speech/SpecialOps.spd", 295915),
    ("DataWii/Audio/Banks/speech/SpecialOps.spt", 1854),
    ("DataWii/BuildInfo.txt", 52),
    ("DataWii/Default.cfg", 20),
    ("DataWii/Modules.rso", 2478912),
    ("DataWii/Video/ThpPlayerFiles/2nd_time.mid", 12103),
    ("DataWii/Video/ThpPlayerFiles/gm16adpcm.pcm", 881485),
    ("DataWii/Video/ThpPlayerFiles/gm16adpcm.wt", 193082),
    ("DataWii/Wow3.sel", 44736),
    ("DataWii/first.zip", 733221),
    ("DataWii/frontend.zip", 4594145),
    ("DataWii/game.zip", 8604285),
]

INTROS = [
    ("DataWii/Video/T17.thp", 1906912),
    ("DataWii/Video/THQ.thp", 3766656),
]

def load_individual_contents(game_dir, intro=True) -> list:
    """
    Returns a list of (rel_path, raw_bytes) for each of the 54 game assets.
    Each entry will become its own WAD content (indices 3..56).
    """
    result = []
    files = FILE_TABLE
    if intro:
        files += INTROS
    for rel_path, expected_size in files:
        candidates = [
            os.path.join(game_dir, rel_path),
            os.path.join(game_dir, rel_path.lower()),
            os.path.join(game_dir, "files", rel_path),
            os.path.join(game_dir, "DATA", "files", rel_path),
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
                if found_path:
                    break

        if not found_path:
            raise FileNotFoundError(f"Missing required asset: {rel_path}")

        with open(found_path, "rb") as f:
            data = f.read()

        actual_size = len(data)
        if actual_size != expected_size:
            print(f"  [!] Size mismatch for {rel_path}: expected {expected_size}, got {actual_size}")

        result.append((rel_path, data))
        print(f"  [+] {rel_path} ({actual_size} bytes) -> content index {3 + len(result) - 1}")

    return result


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: pack_contents.py <game_extracted_dir>")
        sys.exit(1)
    contents = load_individual_contents(sys.argv[1])
    print(f"\nLoaded {len(contents)} individual content files.")
