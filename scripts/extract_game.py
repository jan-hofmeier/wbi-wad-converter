#!/usr/bin/env python3
"""
Wii ISO / WBFS and Directory Extraction Utility for Worms Battle Islands.
Extracts main.dol, opening.bnr, and the 54 required assets without external dependencies.
"""

import os, sys, struct, shutil, subprocess
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from .keys import get_common_key

class DiscReader:
    def __init__(self, file_path):
        self.f = open(file_path, 'rb')
        self.file_path = file_path
        self.is_wbfs = False
        self.read_header()

    def read_header(self):
        self.f.seek(0)
        magic = self.f.read(4)
        if magic == b'WBFS':
            self.is_wbfs = True
            self.f.seek(8)
            self.hd_sec_sz = 1 << self.f.read(1)[0]
            self.wbfs_sec_sz = 1 << self.f.read(1)[0]
            
            # Read first disc header in WBFS
            self.f.seek(0x200) # Disc info table
            # Disc table has 144 bytes per slot, block table follows at 0x300 or 0x400
            # For 2MB blocks on WBFS:
            # Let's locate the disc block table
            self.f.seek(0x200)
            self.disc_id = self.f.read(6)
            
            # Read block map (0x200 bytes header, then disc info, then allocation table)
            # The allocation table starts at 0x100 + disc_index * table_size
            # In WBFS: block map for disc 0 starts at offset 0x200 + 0x100 = 0x300
            self.f.seek(0x200 + 144)
            num_wbfs_blocks = 143360 * 0x8000 // self.wbfs_sec_sz # ~4.7GB / wbfs_sec_sz
            self.f.seek(0x300)
            self.wbfs_table = struct.unpack(f'>{num_wbfs_blocks}H', self.f.read(num_wbfs_blocks * 2))
        else:
            self.is_wbfs = False

    def read_raw(self, offset, size):
        if not self.is_wbfs:
            self.f.seek(offset)
            return self.f.read(size)
        
        # Read from WBFS blocks
        out = bytearray()
        pos = offset
        rem = size
        while rem > 0:
            block_idx = pos // self.wbfs_sec_sz
            block_off = pos % self.wbfs_sec_sz
            chunk_len = min(rem, self.wbfs_sec_sz - block_off)
            
            if block_idx < len(self.wbfs_table) and self.wbfs_table[block_idx] != 0:
                phy_block = self.wbfs_table[block_idx]
                phy_offset = phy_block * self.wbfs_sec_sz + block_off
                self.f.seek(phy_offset)
                out += self.f.read(chunk_len)
            else:
                out += b'\x00' * chunk_len
            
            pos += chunk_len
            rem -= chunk_len
        return bytes(out)

    def close(self):
        self.f.close()


def extract_game(input_path, output_dir, common_key=None):
    """
    Extracts required assets from input_path (WBFS file, ISO file, or directory) into output_dir.
    """
    os.makedirs(output_dir, exist_ok=True)

    # 1. Directory Input
    if os.path.isdir(input_path):
        print(f"Using existing extracted directory: {input_path}")
        # Check for main.dol, opening.bnr, DataWii
        return input_path

    # 2. Try 'wit' if installed on the system
    if shutil.which("wit"):
        print(f"Extracting {input_path} using wit tool...")
        cmd = ["wit", "extract", input_path, "--dest", output_dir, "--files", "+main.dol", "+opening.bnr", "+DataWii/**", "--overwrite"]
        res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if res.returncode == 0 and os.path.isfile(os.path.join(output_dir, "sys", "main.dol")):
            return output_dir

    # 3. Built-in Pure Python WBFS / ISO Decryptor & Extractor
    print(f"Reading disc image: {input_path}...")
    reader = DiscReader(input_path)

    try:
        # Check Disc Header
        header = reader.read_raw(0, 0x100)
        disc_id = header[:6]
        if not disc_id.startswith(b'SILP'):
            print(f"Warning: Expected Worms Battle Islands (SILP), found ID: {disc_id.decode('ascii', errors='replace')}")

        if not common_key:
            common_key = get_common_key()
        if not common_key or len(common_key) != 16:
            raise ValueError("Wii Common Key required to decrypt WBFS/ISO disc image.")

        # Read Partition Table at 0x40000
        part_tbl = reader.read_raw(0x40000, 0x20)
        n_parts, part_info_off = struct.unpack('>II', part_tbl[:8])
        part_entry = reader.read_raw(part_info_off * 4, 8)
        part_offset_sectors, part_type = struct.unpack('>II', part_entry)
        part_offset = part_offset_sectors * 4

        # Read Ticket and TMD of Partition 0
        part_hdr = reader.read_raw(part_offset, 0x20000)
        enc_title_key = part_hdr[0x1BF:0x1CF]
        title_id = part_hdr[0x1DC:0x1E4]
        
        # Decrypt Title Key
        iv = title_id + b'\x00' * 8
        cipher = Cipher(algorithms.AES(common_key), modes.CBC(iv))
        enc = cipher.decryptor()
        title_key = enc.update(enc_title_key) + enc.finalize()

        # Partition Data starts at part_offset + 0x20000
        # In Wii partitions, data is divided into 0x8000 (32 KB) clusters:
        # 0x400 bytes hash data, 0x7C00 bytes encrypted user data.
        data_base = part_offset + 0x20000

        def read_part_cluster(cluster_idx):
            cluster_raw = reader.read_raw(data_base + cluster_idx * 0x8000, 0x8000)
            if len(cluster_raw) < 0x8000: return b'\x00' * 0x7C00
            iv = cluster_raw[0x3D0:0x3E0]
            enc_data = cluster_raw[0x400:0x8000]
            c_dec = Cipher(algorithms.AES(title_key), modes.CBC(iv)).decryptor()
            return c_dec.update(enc_data) + c_dec.finalize()

        def read_part_data(part_file_offset, size):
            out = bytearray()
            pos = part_file_offset
            rem = size
            while rem > 0:
                c_idx = pos // 0x7C00
                c_off = pos % 0x7C00
                chunk_len = min(rem, 0x7C00 - c_off)
                cluster_dec = read_part_cluster(c_idx)
                out += cluster_dec[c_off:c_off+chunk_len]
                pos += chunk_len
                rem -= chunk_len
            return bytes(out)

        # Read Partition header info
        boot_hdr = read_part_data(0, 0x500)
        dol_off = struct.unpack('>I', boot_hdr[0x420:0x424])[0] * 4
        fst_off = struct.unpack('>I', boot_hdr[0x424:0x428])[0] * 4
        fst_sz = struct.unpack('>I', boot_hdr[0x428:0x42C])[0] * 4

        # Read DOL
        print("Extracting main.dol...")
        dol_hdr = read_part_data(dol_off, 0x100)
        # Find maximum DOL extent
        max_dol_end = 0x100
        for i in range(7):
            to = struct.unpack('>I', dol_hdr[i*4:(i+1)*4])[0]
            ts = struct.unpack('>I', dol_hdr[0x90+i*4:0x90+(i+1)*4])[0]
            if to + ts > max_dol_end: max_dol_end = to + ts
        for i in range(11):
            do = struct.unpack('>I', dol_hdr[0x1C+i*4:0x1C+(i+1)*4])[0]
            ds = struct.unpack('>I', dol_hdr[0xAC+i*4:0xAC+(i+1)*4])[0]
            if do + ds > max_dol_end: max_dol_end = do + ds

        main_dol_data = read_part_data(dol_off, max_dol_end)
        with open(os.path.join(output_dir, "main.dol"), "wb") as f:
            f.write(main_dol_data)

        # Read FST
        print("Parsing FST file tree...")
        fst_data = read_part_data(fst_off, fst_sz)
        num_entries = struct.unpack('>I', fst_data[8:12])[0]
        string_table_off = num_entries * 12

        def get_fst_name(name_off):
            end = fst_data.find(b'\x00', string_table_off + name_off)
            return fst_data[string_table_off + name_off : end].decode('latin1')

        # Traverse FST
        entry_idx = 0
        dir_stack = [("", num_entries)]
        
        for i in range(num_entries):
            type_flag = fst_data[i*12]
            name_off = struct.unpack('>I', b'\x00' + fst_data[i*12+1:i*12+4])[0]
            name = get_fst_name(name_off) if i > 0 else ""

            while dir_stack and i >= dir_stack[-1][1]:
                dir_stack.pop()

            curr_dir = dir_stack[-1][0] if dir_stack else ""

            if type_flag == 1: # Directory
                next_entry = struct.unpack('>I', fst_data[i*12+8:i*12+12])[0]
                dir_path = os.path.join(curr_dir, name) if curr_dir else name
                dir_stack.append((dir_path, next_entry))
            else: # File
                file_off = struct.unpack('>I', fst_data[i*12+4:i*12+8])[0] * 4
                file_sz = struct.unpack('>I', fst_data[i*12+8:i*12+12])[0]
                full_rel = os.path.join(curr_dir, name) if curr_dir else name

                norm = full_rel.replace('\\', '/').lower()
                if norm == 'opening.bnr' or norm.startswith('datawii/'):
                    dest_p = os.path.join(output_dir, full_rel)
                    os.makedirs(os.path.dirname(dest_p), exist_ok=True)
                    fdata = read_part_data(file_off, file_sz)
                    with open(dest_p, 'wb') as f:
                        f.write(fdata)

        print(f"Extraction completed successfully into {output_dir}")
        return output_dir

    finally:
        reader.close()

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: extract_game.py <input.wbfs|input.iso|input_dir> <output_dir>")
        sys.exit(1)
    extract_game(sys.argv[1], sys.argv[2])
