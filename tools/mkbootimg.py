#!/usr/bin/env python3

import struct
import argparse
import hashlib

def hexint(x): return int(x, 16)

parser = argparse.ArgumentParser()
parser.add_argument('--kernel', required=True)
parser.add_argument('--ramdisk', required=True)
parser.add_argument('--cmdline', default='')
parser.add_argument('--base', type=hexint, required=True)
parser.add_argument('--pagesize', type=int, required=True)
parser.add_argument('--board', default='')
parser.add_argument('--kernel_offset', type=hexint, required=True)
parser.add_argument('--ramdisk_offset', type=hexint, required=True)
parser.add_argument('--tags_offset', type=hexint, required=True)
parser.add_argument('--os_version', default='0.0.0')
parser.add_argument('--os_patch_level', default='0')
parser.add_argument('-o', '--output', required=True)

args = parser.parse_args()

def parse_os_version(ver):
    a, b, c = map(int, ver.split('.'))
    return ((a & 0x7f) << 14) | ((b & 0x3f) << 8) | (c & 0xff)

def parse_os_patch(patch):
    y, m = map(int, patch.split('-'))
    return ((y - 2000) & 0x7f) << 4 | (m & 0xf)

def pad(f, size):
    while f.tell() % size != 0:
        f.write(b'\x00')

with open(args.kernel, 'rb') as f:
    kernel_data = f.read()
with open(args.ramdisk, 'rb') as f:
    ramdisk_data = f.read()

# Calculate header values
os_version = parse_os_version(args.os_version)
os_patch_level = parse_os_patch(args.os_patch_level)
os_version_patch = (os_version << 11) | os_patch_level
kernel_addr = args.base + args.kernel_offset
ramdisk_addr = args.base + args.ramdisk_offset
tags_addr = args.base + args.tags_offset

# Create ID (SHA1 of kernel + ramdisk)
img_id = hashlib.sha1(kernel_data + ramdisk_data).digest().ljust(32, b'\x00')

# Pack header (boot image v0)
header = struct.pack(
    '8s10I16s512s32s',
    b'ANDROID!',                  # magic
    len(kernel_data),             # kernel_size
    kernel_addr,                  # kernel_addr
    len(ramdisk_data),            # ramdisk_size
    ramdisk_addr,                 # ramdisk_addr
    0,                            # second_size
    0,                            # second_addr
    tags_addr,                    # tags_addr
    args.pagesize,                # page_size
    0,                            # dt_size
    os_version_patch,            # os_version & os_patch_level
    args.board.encode('utf-8').ljust(16, b'\x00'),   # name
    args.cmdline.encode('utf-8').ljust(512, b'\x00'), # cmdline
    img_id                        # id
)

# Write boot.img
with open(args.output, 'wb') as f:
    f.write(header)
    pad(f, args.pagesize)
    f.write(kernel_data)
    pad(f, args.pagesize)
    f.write(ramdisk_data)
    pad(f, args.pagesize)
