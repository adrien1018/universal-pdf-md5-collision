#!/usr/bin/env python3

for i in range(32):
    for j in range(16):
        m = (i * 16 + j) * 2 + 1002
        ch = hex(j)[-1]
        if i == 0:
            content = f'BT 16.02 0 0 16.02 169.6799 467.72 Tm ({ch})Tj '
        elif i == 31:
            content = f'({ch})Tj ET'
        else:
            content = f'({ch})Tj '
        print(f'''{m} 0 obj
<</Length {len(content)}>>stream
{content}
endstream
endobj
{m+1} 0 obj
<</Length 0>>stream
endstream
endobj''')
