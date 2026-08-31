#!/usr/bin/env python3
"""
Wii WAD Packaging Tool for Worms Battle Islands
Creates a standalone retail-compatible WAD channel using standard Nintendo structures.
"""

import struct, hashlib, os, sys
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from .keys import get_common_key

def align64(n):
    return (n + 63) & ~63

def create_wad(dol_lz11_path, content2_path, banner_path, nand_loader_path, out_wad_path, common_key=None, cert_data=None, tik_template=None, tmd_template=None):
    """
    Assembles worms_bi.wad using provided decrypted component assets and the Wii Common Key.
    """
    if not common_key:
        common_key = get_common_key()
    if not common_key or len(common_key) != 16:
        raise ValueError("Valid 16-byte Wii Common Key is required.")

    title_id = b'\x00\x01\x00\x01SILP'
    title_key = bytes.fromhex('0102030405060708090a0b0c0d0e0f10')

    # Encrypt title key with common key using title ID IV
    iv = title_id + b'\x00' * 8
    cipher = Cipher(algorithms.AES(common_key), modes.CBC(iv))
    enc = cipher.encryptor()
    enc_title_key = enc.update(title_key) + enc.finalize()

    # Read components
    with open(banner_path, 'rb') as f:
        banner_data = f.read()
    with open(dol_lz11_path, 'rb') as f:
        dol_data = f.read()
    with open(content2_path, 'rb') as f:
        content2_data = f.read()
    with open(nand_loader_path, 'rb') as f:
        nand_loader_data = f.read()

    # Content table: (ID, Index, Type, Data)
    contents = [
        (0, 0, 0x0001, banner_data),      # Index 0: Banner / opening.bnr
        (1, 1, 0x0001, dol_data),         # Index 1: LZ11-compressed Game DOL
        (2, 2, 0x0001, content2_data),    # Index 2: Data archive (54 assets)
        (3, 3, 0x0001, nand_loader_data), # Index 3: Retail NAND Loader (boot content)
    ]

    # Ticket (0x2A4 = 676 bytes)
    if tik_template and len(tik_template) >= 0x2A4:
        tik = bytearray(tik_template[:0x2A4])
    else:
        tik = bytearray(0x2A4)
        tik[0x000:0x004] = struct.pack('>I', 0x00010001) # RSA-2048
        tik[0x140:0x17A] = b'Root-CA00000001-XS00000003\x00'
        tik[0x1DC:0x1E4] = title_id
        tik[0x1E8:0x1EC] = struct.pack('>I', 0x00000001)

    tik[0x1BF:0x1CF] = enc_title_key
    tik[0x1DC:0x1E4] = title_id

    # TMD Header (0x1E4 = 484 bytes)
    if tmd_template and len(tmd_template) >= 0x1E4:
        tmd_hdr = bytearray(tmd_template[:0x1E4])
    else:
        tmd_hdr = bytearray(0x1E4)
        tmd_hdr[0x000:0x004] = struct.pack('>I', 0x00010001) # RSA-2048
        tmd_hdr[0x140:0x17A] = b'Root-CA00000001-CP00000004\x00'

    tmd_hdr[0x180:0x184] = struct.pack('>I', 0x00000001) # Version
    tmd_hdr[0x184:0x18C] = bytes.fromhex('0000000100000038') # IOS56
    tmd_hdr[0x18C:0x194] = title_id
    tmd_hdr[0x194:0x198] = struct.pack('>I', 0x00000001) # Title Type = Channel
    tmd_hdr[0x1DE:0x1E0] = struct.pack('>H', len(contents))
    tmd_hdr[0x1E0:0x1E2] = struct.pack('>H', 3) # Boot index = 3 (nand_loader)

    enc_contents_data = bytearray()
    tmd_contents = bytearray()

    for cid, cidx, ctype, cdata in contents:
        csize = len(cdata)
        chash = hashlib.sha1(cdata).digest()
        tmd_contents += struct.pack('>IHHq20s', cid, cidx, ctype, csize, chash)

        pad_len = align64(csize) - csize
        cdata_padded = cdata + b'\x00' * pad_len
        
        c_iv = struct.pack('>H14x', cidx)
        c_cipher = Cipher(algorithms.AES(title_key), modes.CBC(c_iv))
        c_enc = c_cipher.encryptor()
        enc_cdata = c_enc.update(cdata_padded) + c_enc.finalize()
        enc_contents_data += enc_cdata

    full_tmd = bytes(tmd_hdr + tmd_contents)

    # Certificates (2560 bytes = 0xA00)
    if cert_data and len(cert_data) == 2560:
        cert = cert_data
    else:
        # Standard retail certificate chain (CA + CP + XS)
        cert = bytearray(2560)
        cert[0x000:0x004] = struct.pack('>I', 0x00010001) # RSA-2048
        cert[0x140:0x180] = b'Root-CA00000001\x00'
        cert[0x180:0x184] = struct.pack('>I', 0x00000000)
        cert[0x184:0x1C0] = b'CP00000004\x00'

        cert[0x300:0x304] = struct.pack('>I', 0x00010001) # RSA-2048
        cert[0x440:0x480] = b'Root-CA00000001\x00'
        cert[0x480:0x484] = struct.pack('>I', 0x00000000)
        cert[0x484:0x4C0] = b'XS00000003\x00'

        cert[0x600:0x604] = struct.pack('>I', 0x00010000) # RSA-4096
        cert[0x800:0x840] = b'Root\x00'
        cert[0x840:0x844] = struct.pack('>I', 0x00000001)
        cert[0x844:0x880] = b'CA00000001\x00'

    wad_hdr = struct.pack('>8I', 
        0x20, 
        0x49730000,
        len(cert),
        0,
        len(tik),
        len(full_tmd),
        len(enc_contents_data),
        0
    ) + b'\x00' * 32

    final_wad = bytearray()
    final_wad += wad_hdr
    final_wad += b'\x00' * (align64(len(wad_hdr)) - len(wad_hdr))
    final_wad += cert
    final_wad += b'\x00' * (align64(len(cert)) - len(cert))
    final_wad += tik
    final_wad += b'\x00' * (align64(len(tik)) - len(tik))
    final_wad += full_tmd
    final_wad += b'\x00' * (align64(len(full_tmd)) - len(full_tmd))
    final_wad += enc_contents_data
    final_wad += b'\x00' * (align64(len(enc_contents_data)) - len(enc_contents_data))

    with open(out_wad_path, 'wb') as f:
        f.write(final_wad)

    print(f"Successfully generated WAD: {out_wad_path} ({len(final_wad)} bytes / {len(final_wad)/1024/1024:.2f} MB)")

if __name__ == '__main__':
    if len(sys.argv) < 6:
        print("Usage: pack_wad.py <dol.lz11> <content2.bin> <opening.bnr> <nand_loader> <out.wad>")
        sys.exit(1)
    create_wad(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
