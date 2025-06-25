#!/usr/bin/env python3

# Minimal mkbootimg port (for AOSP boot images)
# Based on original AOSP sources and osm0sis' tools
# SPDX-License-Identifier: Apache-2.0

import struct
import argparse

def hexint(x):
    return int(x, 16)

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

os_version = parse_os_version(args.os_version)
os_patch_level = parse_os_patch(args.os_patch_level)
header = struct.pack('8s11I16s512s', b'ANDROID!',
    len(kernel_data), len(ramdisk_data), 0, args.pagesize,
    args.base + args.kernel_offset, args.base + args.ramdisk_offset,
    args.base + args.tags_offset, os_version, os_patch_level, 0,
    args.board.encode('utf-8'),
    args.cmdline.encode('utf-8'))

with open(args.output, 'wb') as f:
    f.write(header)
    pad(f, args.pagesize)
    f.write(kernel_data)
    pad(f, args.pagesize)
    f.write(ramdisk_data)
    pad(f, args.pagesize)
