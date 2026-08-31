#!/usr/bin/env python3
"""
Pure Python Nintendo LZ11 (Type 0x11) Compressor
Used as a portable fallback when native C compiler is not present.
"""

import struct, sys

def compress_lz11(in_data):
    in_size = len(in_data)
    out = bytearray([0x11])
    
    if in_size <= 0xFFFFFF:
        out.extend(struct.pack('<I', in_size)[:3])
    else:
        out.extend(b'\x00\x00\x00')
        out.extend(struct.pack('<I', in_size))

    head = {}
    prev = {}
    in_pos = 0

    while in_pos < in_size:
        flag_pos = len(out)
        out.append(0)
        flag_byte = 0

        for bit in range(7, -1, -1):
            if in_pos >= in_size: break

            best_len = 0
            best_disp = 0

            if in_pos + 3 <= in_size:
                h = (in_data[in_pos], in_data[in_pos+1], in_data[in_pos+2])
                match_pos = head.get(h, -1)
                chain = 64

                while match_pos >= 0 and chain > 0:
                    chain -= 1
                    disp = in_pos - match_pos
                    if disp > 4096 or disp == 0: break

                    max_l = min(in_size - in_pos, 0x10110)
                    match_l = 0
                    while match_l < max_l and in_data[in_pos + match_l] == in_data[match_pos + match_l]:
                        match_l += 1

                    if match_l >= 3 and match_l > best_len:
                        best_len = match_l
                        best_disp = disp
                        if best_len >= 0x10110: break

                    match_pos = prev.get(match_pos, -1)

            if best_len >= 3:
                flag_byte |= (1 << bit)
                d = best_disp - 1

                if best_len <= 16:
                    out.append(((best_len - 1) << 4) | ((d >> 8) & 0x0F))
                    out.append(d & 0xFF)
                elif best_len <= 0x110:
                    l = best_len - 0x11
                    out.append((l >> 4) & 0x0F)
                    out.append(((l & 0x0F) << 4) | ((d >> 8) & 0x0F))
                    out.append(d & 0xFF)
                else:
                    l = best_len - 0x111
                    out.append(0x10 | ((l >> 12) & 0x0F))
                    out.append((l >> 4) & 0xFF)
                    out.append(((l & 0x0F) << 4) | ((d >> 8) & 0x0F))
                    out.append(d & 0xFF)

                for i in range(best_len):
                    if in_pos + i + 3 <= in_size:
                        sub_h = (in_data[in_pos+i], in_data[in_pos+i+1], in_data[in_pos+i+2])
                        prev[in_pos + i] = head.get(sub_h, -1)
                        head[sub_h] = in_pos + i
                in_pos += best_len
            else:
                out.append(in_data[in_pos])
                if in_pos + 3 <= in_size:
                    sub_h = (in_data[in_pos], in_data[in_pos+1], in_data[in_pos+2])
                    prev[in_pos] = head.get(sub_h, -1)
                    head[sub_h] = in_pos
                in_pos += 1

        out[flag_pos] = flag_byte

    return bytes(out)

def compress_file(in_path, out_path):
    with open(in_path, 'rb') as f:
        data = f.read()
    compressed = compress_lz11(data)
    with open(out_path, 'wb') as f:
        f.write(compressed)
    print(f"Compressed {len(data)} -> {len(compressed)} bytes ({(len(compressed)/len(data))*100:.1f}%)")

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: compress_lz11.py <in_file> <out_lz11>")
        sys.exit(1)
    compress_file(sys.argv[1], sys.argv[2])
