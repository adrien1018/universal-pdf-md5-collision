#!/usr/bin/env python3

import hashlib, sys

with open(sys.argv[1], 'rb') as f: orig_data = f.read()
with open('collisions-1', 'rb') as f: data1 = f.read()
with open('collisions-2', 'rb') as f: data2 = f.read()

nhash = hashlib.md5(orig_data).hexdigest()

offset = 192
blk = 128

data = orig_data[:offset]
for i in range(32):
    res = int(nhash[i], 16)
    for j in range(16):
        pos = i*16+j
        data += (data1 if j == res else data2)[offset+blk*pos : offset+blk*(pos+1)]

data += orig_data[len(data):]

with open(sys.argv[2], 'wb') as f: f.write(data)
