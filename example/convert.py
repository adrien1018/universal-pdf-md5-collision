#!/usr/bin/env python3

import sys, base64, zlib

inform = 'zlib'
form = 'raw'
if len(sys.argv) > 1: form = sys.argv[1]
if len(sys.argv) > 2: inform = sys.argv[2]

def err():
    print(f'Usage: {sys.argv[0]} [raw/hex/b85/zlib] [zlib/hex/raw]', file=sys.stderr)
    sys.exit(1)

if inform == 'hex':
    data = bytes.fromhex(sys.stdin.read())
elif inform == 'zlib':
    data = bytes.fromhex(sys.stdin.read())
    data = zlib.decompress(data)
elif inform == 'raw':
    data = sys.stdin.buffer.read()
else:
    err()

if form == 'raw':
    print(data.decode())
elif form == 'hex':
    print(data.hex())
elif form == 'b85':
    print(base64.b85encode(data).decode())
elif form == 'zlib':
    print(zlib.compress(data).hex())
else:
    err()
