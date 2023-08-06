# Creating the MD5 quine

This is a detailed instruction for creating the [text-only MD5 quine](/example/MD5_Quine.pdf). This can serve as a helpful blueprint for constructing your own collision file.

## Overview

To construct an MD5 quine containing the hexadecimal representation of the document's MD5 hash, follow the outlined steps below:

1. Create an initial PDF that includes all elements of the final product except the MD5 hash.
2. Divide the content stream into three parts: the hexadecimal digits themselves, the content preceding them, and the content succeeding them.
3. Generate objects for each possible digit of the MD5 hash.
4. Assemble all blocks into the precomputed page object and modify the references accordingly.
5. Regenerate the cross-reference table.
6. Compute the MD5 digest of the resulting file, and select the appropriate objects to display the correct MD5 text.

A hex editor will come in handy in this process.

## Initial PDF generation

To generate the initial PDF file, use any PDF writer software to generate a normal PDF document for further editing. We will use [this file](/example/original.pdf) in our example. Within this file, the text `0123456789abcdef0123456789abcdef` serves as a placeholder, intended to be substituted with the actual MD5 digest. This placeholder text serves multiple purposes: it guarantees the font will be exported, ensures correct text positioning, and helps us locating the content later.

The PDF can havemultiple pages, but only one page can be make different in the collision. For the sake of simplicity, a single-page PDF is used in this example.

When creating the PDF, it is advisable to **not** generating a linearized PDF (often denoted by a "Fast Web View" option during generation). Linearized PDFs has a more complicated structure, which can complicate the process.

## Split the document section

### Finding the content object

To split the document section, we need to find the `Contents` object. We start by obtaining the objects list using `gen-xref.py`:

```
$ ./gen-xref.py original.py
Object 1 in index 0 of object 26
Object 2 at offset 1100
...
Object 10 in index 1 of object 26
...
Object 25 at offset 61746
Object 26 at offset 16
...
# irrelevant entries are omitted here
```

We then look at the cross-reference object located at the end of the file:

```
```

`/Root 25 0 R` means the ID of root object is 25. Thus, we go to byte 61746 to find object 25:

```
```

`/Pages 10 0 R` means, again, the ID of the [*document catalog object*](https://opensource.adobe.com/dc-acrobat-sdk-docs/pdfstandards/PDF32000_2008.pdf#G6.1926881) (which contains the array of page objects) is 10. Object 10 is inside object 26, which means it is stored inside object 26 (object 26 is an [*object stream*](https://opensource.adobe.com/dc-acrobat-sdk-docs/pdfstandards/PDF32000_2008.pdf#G6.2393289)). Thus, we go to byte 16 to find object 26:

```
```

Looks like it contains a bunch of random bytes. The keyword here is the `/Filter FlateDecode`, which means the content is compressed using DEFLATE and we need to decompress it. Hence, we can extract the bytes between the newline after `stream` and the newline before `endstream`, convert it into hexadecimal, and feed it into `convert.py`:

```
$ ./convert.py <<< '789c33543050303450303751b0b1d177cecf2b49cd2b295630028a06e93be6e5e59714471b1b8078b1fa0189454049906a9064506a717e6951726ab18231981f5259900a54929e6a670736a914a454df3b33a538da10a2df37352533d129bf221a6480a9a5a99e9191828589512c426bb19d1d1700a5382969'
1 0 10 74 <</Contents 2 0 R/Annots[30 0 R]/Parent 10 0 R/Resources 3 0 R/Type/Page>><</Count 1/Kids[1 0 R]/MediaBox[0 0 595.22 842]/Type/Pages>>
```

The second `<<...>>` is our object 10 (the index of `./gen-xref.py` is 0-based). It again points to object 1 (`/Kids[1 0 R]`), which is the first object here. Finally, we see the `/Contents 2 0 R`, which is the object containing the page content. Hence, we go to byte 1100 and decompress its content using the same method:

```
... (content omitted)
16.02 0 0 16.02 156.3 495.5003 Tm
.0003 Tc
-.0002 Tw
[(The MD5 c)28.4(h)4.4(ec)28.4(ks)4.3(um of th)4.4(is do)-24(cu)4.4(men)30.6(t)-1.5( is)4.3(:)3.7( )]TJ
/TT8 1 Tf
.8352 -1.7341 TD
-.0009 Tc
0 Tw
(0123456789abcde)Tj
7.4906 0 TD
-.0011 Tc
(f0123456789abcdef )Tj
/TT6 1 Tf
.4981 -1.6367 TD
... (content omitted)
```

Here we find the placeholder text we want to substitute (`Tj` means the text inside the parenthesis should be inserted at the current location).

### Split the contents

In order to display the actual MD5 hash, we must partition this content into distinct segments. Specifically, we want to concatenate the contents of the following objects:

1. An object containing all the contents before `0 Tw` (inclusive).
2. 16x32=512 pairs of objects to form the digest, each consisting of:
    - An object stream containing `([digit])Tj` to insert a digit
    - An empty object stream to do nothing.
3. An object containing all the contents before `/TT6 1 Tf` (inclusive).

The ID of the precomputed collision pairs start from (1000, 1001). Thus, the initial object should carry the ID 1000, and the object pairs for the digits will utilize IDs (1002, 1003), (1004, 1005), and so forth. The last object can reuse the original object 2.

## Generating the objects

We start from the first object. Run `./convert.py zlib raw` to convert the plain text to hexadecimal format:

```
$ ./convert.py zlib raw < text_before
789c85524b4bc34010bee757cc7157e874dfd9789462411014f7261e6a9bb6d136812655fcf7ceeeb629ea4142b2b3797ccf4ce74f12367d71138a69080a2484752115083a68a90494d6a1f34243d8170236748665bc7c160c7878a37122d142989df6e1eaff81a84ca6522651d1a254e401a74bb42ad3a110c245ba499caac4793fb3f0786cdafa0ce44e9a1d8a93ec344925b072e084462b325c42b1673ca224bc6736afdbfab018ea15bc729220d91727432583051cdbe6832b8f8ad57ca250b343bfd8f19770574802d7ca111bf94eb86ad4e9332e3ccc6e21aa5d76bb5dd3375d0b434730062deb2e283e6b4e93711ebd21cd1ecd98f898b68c867fdb34a541fdc3654e585623749a5455a273609d43ed84b9bc98eaf342fa4b837fa2a43f4083a9ecc8116dead1b0ca86c3b6ce7e6364866db9a16b7ddabdf7b4d5ecb8876e0d437ed6f4b04a89b0e531ddd8d72dd7021d1b6205964193bfbae63a169232a3c67d6e1cbdb62aaa2fb591630fd518d83714959eec
```

Finally, use any hex editor to insert object 1000 into the document. The object should look like this:

```
0001015f: 3130 3030 2030 206f 626a 0d0a 3c3c 2f46  1000 0 obj..<</F
0001016f: 696c 7465 722f 466c 6174 6544 6563 6f64  ilter/FlateDecod
0001017f: 652f 4c65 6e67 7468 2033 3735 3e3e 7374  e/Length 375>>st
0001018f: 7265 616d 0d0a 789c 8552 4b4b c340 10be  ream..x..RKK.@..
0001019f: e757 cc71 57e8 74df d978 9462 4110 14f7  .W.qW.t..x.bA...
000101af: 261e 6a9b b6d1 3681 2655 fcf7 ceee b629  &.j...6.&U.....)
000101bf: ea41 42b2 b379 7ccf 4ce7 4f12 367d 7113  .AB..y|.L.O.6}q.
000101cf: 8a69 080a 2484 7521 1508 3a68 a904 94d6  .i..$.u!..:h....
000101df: a1f3 4243 d817 0236 7486 65bc 7c16 0c78  ..BC...6t.e.|..x
000101ef: 78a3 7122 d142 989d f6e1 eaff 81a8 4ca6  x.q".B........L.
000101ff: 5226 51d1 a254 e401 a74b b42a d3a1 10c2  R&Q..T...K.*....
0001020f: 45ba 499c aac4 793f b3f0 786c dafa 0ce4  E.I...y?..xl....
0001021f: 4e9a 1d8a 93ec 3449 25b0 72e0 8446 2b32  N.....4I%.r..F+2
0001022f: 5c42 b167 3ca2 24bc 6736 afdb fab0 18ea  \B.g<.$.g6......
0001023f: 15bc 7292 20d9 1727 4325 8305 1cdb e683  ..r. ..'C%......
0001024f: 2b8f 8ad5 7ca2 50b3 43bf d8f1 9770 5748  +...|.P.C....pWH
0001025f: 02d7 ca11 1bf9 4eb8 6ad4 e933 2e3c cc6e  ......N.j..3.<.n
0001026f: 21aa 5d76 bb5d d337 5d0b 4347 3006 2deb  !.]v.].7].CG0.-.
0001027f: 2e28 3e6b 4e93 711e bd21 cd1e cd98 f898  .(>kN.q..!......
0001028f: b68c 867f db34 a541 fdc3 654e 5856 2374  .....4.A..eNXV#t
0001029f: 9a54 55a2 7360 9d43 ed84 b9bc 98ea f342  .TU.s`.C.......B
000102af: fa4b 837f a2a4 3f40 83a9 ecc8 116d ead1  .K....?@.....m..
000102bf: b0ca 86c3 b6ce 7e63 6486 6db9 a16b 7dda  ......~cd.m..k}.
000102cf: bdf7 b4d5 ecb8 876e 0d43 7ed6 f4b0 4a89  .......n.C~...J.
000102df: b0e5 31dd d8d7 2dd7 021d 1b62 0596 4193  ..1...-....b..A.
000102ef: bfba e63a 1692 32a3 c67d 6e1c bdb6 2aaa  ...:..2..}n...*.
000102ff: 2fb5 9163 0fd5 18d8 3714 959e ec0d 0a65  /..c....7......e
0001030f: 6e64 7374 7265 616d 0d0a 656e 646f 626a  ndstream..endobj
0001031f: 0a                                       .
```

Note that the `/Length 375` should match the byte length of the object. The last object can be generated similarly by replacing the contents of object 2.

Creating objects for the digits follows a more straightforward process. We designate object 1002 to represent the digit 0 (`(0)Tj`), object 1004 for 1, and continue this pattern up to object 2024. The odd-numbered objects (1003, 1005, and so forth) will all be empty. `gen-objects.py` is written for this task, which outputs all the objects. These objects can then be inserted into the document.
