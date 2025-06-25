#!/usr/bin/env python3
import os, sys, struct, argparse

def hex_or_int(x):
    return int(x, 0)

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input', required=True, help='Input boot image')
parser.add_argument('-o', '--output', required=True, help='Output directory')
args = parser.parse_args()

with open(args.input, 'rb') as f:
    data = f.read()

# Unpack Android boot image header (version 0)
hdr_format = '8s10I16s512s'
hdr_size = struct.calcsize(hdr_format)
hdr = struct.unpack(hdr_format, data[:hdr_size])

magic, kernel_size, kernel_addr, ramdisk_size, ramdisk_addr, \
second_size, second_addr, tags_addr, page_size, _, name, cmdline = hdr

if magic != b'ANDROID!':
    raise ValueError("Not a valid Android boot image")

os.makedirs(args.output, exist_ok=True)

def write_file(name, value):
    with open(os.path.join(args.output, name), 'w') as f:
        f.write(str(value))

write_file('kernel_size.txt', kernel_size)
write_file('ramdisk_size.txt', ramdisk_size)
write_file('base.txt', hex(kernel_addr & 0xfffff000))
write_file('kernel_offset.txt', hex(kernel_addr - (kernel_addr & 0xfffff000)))
write_file('ramdisk_offset.txt', hex(ramdisk_addr - (kernel_addr & 0xfffff000)))
write_file('second_offset.txt', hex(second_addr - (kernel_addr & 0xfffff000)))
write_file('tags_offset.txt', hex(tags_addr - (kernel_addr & 0xfffff000)))
write_file('pagesize.txt', page_size)
write_file('cmdline.txt', cmdline.decode('ascii').strip('\x00'))
