#!/usr/bin/env python3

import re, sys, zlib, itertools

OBJ_PAT = re.compile(rb'(\d+) 0 obj\s.*?endobj', re.DOTALL)
XREF_PAT = re.compile(rb'<<(.*?/Type[^/]*?/XRef.*?)>>.*stream\s+(.*)\s+endstream', re.DOTALL)

with open(sys.argv[1], 'rb') as f: data = f.read()

offset_dict = {}
xref_id, xref_header, xref_format = None, None, None
offset_table = None

for mat in OBJ_PAT.finditer(data):
    if xref_id is not None:
        raise RuntimeError('XRef table must be at the end')
    offset_dict[int(mat[1])] = mat.start()
    xmat = XREF_PAT.search(mat[0])
    if xmat:
        xref_id = int(mat[1])
        predictor = re.search(rb'/Predictor\W+([^/>]*)', xmat[1])
        columns = re.search(rb'/Columns\W+([^/>]*)', xmat[1])
        xref_header = re.sub(rb'/(Size|Length|W|Filter)\W[^/]*', b'', xmat[1])
        xref_header = re.sub(rb'/DecodeParms<<.*?>>', b'', xref_header)
        xref_format = list(map(int, re.findall(rb'/W.*?\[(\d+).*?(\d+).*?(\d+)\]', xmat[1])[0]))
        root_object = re.search(rb'/Root[^/]+', xref_header)[0].decode()
        offset_table = xmat[2]
        if re.search(rb'/Filter.*FlateDecode', xmat[1]):
            offset_table = zlib.decompress(xmat[2])
        if predictor:
            if predictor[1] != b'12':
                raise RuntimeError('Unsupported predictor')
            columns = int(columns[1].decode()) + 1
            offset_table = [offset_table[i:i+columns] for i in range(0, len(offset_table), columns)]
            for i in range(1, len(offset_table)):
                offset_table[i] = bytes((offset_table[i][j] + offset_table[i-1][j]) % 256 for j in range(columns))
            offset_table = b''.join([i[1:] for i in offset_table])

data = data[:offset_dict[xref_id]]
entry_size = sum(xref_format)
format_sum = [0] + list(itertools.accumulate(xref_format))
offset_table = [offset_table[i:i+entry_size] for i in range(0, len(offset_table), entry_size)]
offset_table = [list(map(lambda x: int.from_bytes(i[format_sum[x]:format_sum[x+1]], 'big'), range(3)))
                for i in offset_table]

xref_format[1] = max(xref_format[1], (len(data).bit_length() + 7) // 8)
num_entries = max(len(offset_table), max(offset_dict) + 1)
offset_table += [[0, 0, 65535] for i in range(num_entries - len(offset_table))]
for i, j in offset_dict.items():
    offset_table[i] = [1, j, 0]
if any([i[2] == 65535 for i in offset_table]) and xref_format[2] < 2:
    xref_format[2] = 2

if len(sys.argv) == 2:
    print(root_object)
    for j, i in enumerate(offset_table):
        if i[0] == 0: continue
        if i[0] == 1:
            print(f'Object {j} at offset {i[1]}')
        else:
            print(f'Object {j} in index {i[2]} of object {i[1]}')
    sys.exit(0)

use_predictor = True
offset_data = [bytearray() for i in offset_table]
for i in range(len(offset_table)):
    for j in range(3):
        offset_data[i] += offset_table[i][j].to_bytes(xref_format[j], 'big')

if use_predictor:
    width = sum(xref_format)
    for i in range(len(offset_data) - 1, 0, -1):
        for j in range(width):
            offset_data[i][j] = (256 + offset_data[i][j] - offset_data[i-1][j]) % 256
    for i in range(len(offset_data)):
        offset_data[i] = bytearray([2]) + offset_data[i]

offset_data = b''.join(offset_data)
offset_data = zlib.compress(offset_data, level=9)

data += f'{xref_id} 0 obj\r<<'.encode()
data += xref_header
if use_predictor:
    data += f'/DecodeParms<</Columns {width}/Predictor 12>>'.encode()
data += f'/Filter/FlateDecode/Size {len(offset_table)}/Length {len(offset_data)}/W[{xref_format[0]} {xref_format[1]} {xref_format[2]}]>>stream\r\n'.encode()
data += offset_data
data += f'\r\nendstream\rendobj\rstartxref\r\n{offset_dict[xref_id]}\r\n%%EOF\r\n'.encode()

with open(sys.argv[2], 'wb') as f: f.write(data)
