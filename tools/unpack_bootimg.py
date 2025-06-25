#!/usr/bin/env python3
import os, sys, struct, argparse

def read_bytes(f, n):
    d = f.read(n)
    if len(d) != n:
        raise ValueError("Unexpected EOF")
    return d

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input', required=True, help='Input boot/recovery image')
parser.add_argument('-o', '--output', required=True, help='Output directory')
args = parser.parse_args()

with open(args.input, 'rb') as f:
    magic = read_bytes(f, 8)
    if magic != b'ANDROID!':
        raise ValueError("Not an Android boot image")

    kernel_size = struct.unpack('<I', read_bytes(f, 4))[0]
    kernel_addr = struct.unpack('<I', read_bytes(f, 4))[0]
    ramdisk_size = struct.unpack('<I', read_bytes(f, 4))[0]
    ramdisk_addr = struct.unpack('<I', read_bytes(f, 4))[0]
    second_size = struct.unpack('<I', read_bytes(f, 4))[0]
    second_addr = struct.unpack('<I', read_bytes(f, 4))[0]
    tags_addr = struct.unpack('<I', read_bytes(f, 4))[0]
    page_size = struct.unpack('<I', read_bytes(f, 4))[0]
    dt_size = struct.unpack('<I', read_bytes(f, 4))[0]
    unused = struct.unpack('<I', read_bytes(f, 4))[0]
    name = read_bytes(f, 16).rstrip(b'\x00').decode()
    cmdline = read_bytes(f, 512).rstrip(b'\x00').decode()

output_dir = args.output
os.makedirs(output_dir, exist_ok=True)

with open(f"{output_dir}/base.txt", 'w') as f:
    base = kernel_addr & 0xfffff000
    f.write(hex(base))

with open(f"{output_dir}/pagesize.txt", 'w') as f:
    f.write(str(page_size))

with open(f"{output_dir}/cmdline.txt", 'w') as f:
    f.write(cmdline)
