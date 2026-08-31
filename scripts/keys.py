#!/usr/bin/env python3
"""
Wii Key Management Utility
Supports loading the Wii Common Key from:
- CLI argument (--key)
- OTP dump from Wii or Wii U vWii (--otp otp.bin)
- Key file (--keyfile common.key / key.bin)
- Environment variable (WII_COMMON_KEY)
- Interactive prompt
"""

import os, sys, hashlib

WII_COMMON_KEY_SHA1 = "ebeae6d2762d4d3ea160a6d8327fac9a25f8062b"

def get_common_key(key_arg=None, otp_path=None, keyfile_path=None):
    """
    Locates, extracts, and validates the 16-byte Wii Common Key.
    Returns 16-byte bytes object or None if unavailable.
    """
    key_bytes = None

    # 1. Direct hex key string
    if key_arg:
        try:
            key_bytes = bytes.fromhex(key_arg.strip())
        except ValueError:
            print("Error: Invalid hex string provided for key.")
            return None

    # 2. Environment variable
    if not key_bytes and 'WII_COMMON_KEY' in os.environ:
        try:
            key_bytes = bytes.fromhex(os.environ['WII_COMMON_KEY'].strip())
        except ValueError:
            pass

    # 3. Explicit key file or common.key / key.bin in working directory or input/ folder
    candidate_keyfiles = [keyfile_path] if keyfile_path else []
    candidate_keyfiles.extend([
        os.path.join('input', 'common.key'),
        os.path.join('input', 'key.bin'),
        os.path.join('input', 'keys.bin'),
        'common.key', 'key.bin', 'keys.bin'
    ])

    for kf in candidate_keyfiles:
        if kf and os.path.isfile(kf):
            try:
                with open(kf, 'rb') as f:
                    data = f.read().strip()
                if len(data) == 16:
                    key_bytes = data
                    break
                elif len(data) == 32:
                    key_bytes = bytes.fromhex(data.decode('ascii'))
                    break
            except Exception:
                continue

    # 4. OTP dump from Wii (512 bytes) or Wii U vWii (1024 bytes)
    candidate_otps = [otp_path] if otp_path else []
    candidate_otps.extend([
        os.path.join('input', 'otp.bin'),
        'otp.bin', 'keys/otp.bin'
    ])

    for otp in candidate_otps:
        if otp and os.path.isfile(otp):
            try:
                with open(otp, 'rb') as f:
                    data = f.read()
                if len(data) in (512, 1024, 2048):
                    # Scan for the Wii Common Key across the OTP dump (supports Wii & Wii U dumps)
                    for off in range(0, len(data) - 15):
                        candidate = data[off:off+16]
                        if hashlib.sha1(candidate).hexdigest().lower() == WII_COMMON_KEY_SHA1:
                            key_bytes = candidate
                            print(f"Extracted Wii Common Key from OTP dump ({otp} at offset 0x{off:03X})")
                            break
                    if key_bytes:
                        break
            except Exception:
                continue

    # 5. Interactive prompt if in an interactive terminal
    if not key_bytes and sys.stdin.isatty():
        print("\nWii Common Key is required to encrypt the WAD channel.")
        print("Please provide the 32-character hex key, or path to otp.bin / common.key:")
        user_input = input("Wii Common Key / Path: ").strip()
        if os.path.isfile(user_input):
            return get_common_key(otp_path=user_input, keyfile_path=user_input)
        elif len(user_input) == 32:
            try:
                key_bytes = bytes.fromhex(user_input)
            except ValueError:
                pass

    if key_bytes and len(key_bytes) == 16:
        # Validate SHA-1
        actual_hash = hashlib.sha1(key_bytes).hexdigest().lower()
        if actual_hash == WII_COMMON_KEY_SHA1:
            return key_bytes
        else:
            print(f"Warning: Key provided does not match known Wii Common Key hash (SHA1: {actual_hash}).")
            return key_bytes

    return None

if __name__ == '__main__':
    key = get_common_key()
    if key:
        print(f"Valid Wii Common Key located (SHA1: {hashlib.sha1(key).hexdigest()})")
    else:
        print("Error: No valid Wii Common Key found.")
        sys.exit(1)
