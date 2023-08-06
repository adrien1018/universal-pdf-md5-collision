#!/usr/bin/env python3

for i in range(32):
    for j in range(16):
        obj_id = (i * 16 + j) * 2 + 1002
        ch = hex(j)[-1]
        content = f'({ch})Tj '
        print(f'''{obj_id} 0 obj
<</Length {len(content)}>>stream
{content}
endstream
endobj
{obj_id+1} 0 obj
<</Length 0>>stream
endstream
endobj''')
