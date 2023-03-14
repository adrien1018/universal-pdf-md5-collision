# Universal PDF MD5 collision

This project enables one to generate virtually any single-page PDF MD5 collisions **without any additional collision computation**.

## How does it work?

A PDF file mainly consists of a hierarchy of *objects*. A page in a PDF file is represented by a [*page object*](https://opensource.adobe.com/dc-acrobat-sdk-docs/pdfstandards/PDF32000_2008.pdf#G6.1956489), and its content is specified by the `Contents` key in the page object, which normally references a [*content stream*](https://opensource.adobe.com/dc-acrobat-sdk-docs/pdfstandards/PDF32000_2008.pdf#G6.1913072) (which is also a type of object). There are some useful properties that make precomputing a multi-way PDF collision possible:

- The `Contents` can be an array containing multiple content streams, and it is equivalent to concatenating all the content streams in the array together to form a single stream.
- The format of a reference (specifically, an *indirect reference*) in the `Contents` array is `[object-id] [generation] R`, where `[generation]` can be fixed to `0` in our use case.
- The references can be separated by spaces or newlines.
- PDF files can contain comments, which starts with a `%` character and ends with a new line (CR or LF) or a NUL byte.
- The order of objects in a file is arbitrary. When reading a file, objects are found using the [*cross-reference table*](https://opensource.adobe.com/dc-acrobat-sdk-docs/pdfstandards/PDF32000_2008.pdf#G6.1839814) located at the end of the file.

Thus, we can construct a PDF file where the target page object is the first page object, and put the `Contents` key at first. After that, thanks to [HashClash](https://github.com/cr-marcstevens/hashclash)'s identical-prefix attack that produces a single-bit difference at the LSB of the 10-th byte, a collision like this can be precomputed:

```
(file 1)
      1000 1 R %[a bunch of collision bytes]
0123456789abcdef
      1001 1 R %[a bunch of collision bytes]
(file 2)
```

If the collision bytes does not contain the three characters that ends a comment, this will be a valid reference. This will give us a MD5 collision pair where the one file having the contents of object 1000 and the other having the contents of object 1001. We can repeat this process on objects (1002, 1003), (1004, 1005) and so on to construct a multi-way collision.

After precomputing the collision blocks, constructing arbitrary PDF collision is easy: just put the content that we wish to collide in the content streams with the corresponding object ID, and finally reconstruct a valid cross-reference table.

With N pairs of collision blocks, up to 2<sup>N</sup> different files with the same MD5 collision can be constructed, although it depends heavily on the use case. For example, to construct a MD5 quine that displays its MD5 hash in hexadecimal format, we need 16x32=512 pairs of collision blocks; if instead the hash should be displayed in binary format, only 128 collision blocks is needed.

