Data streams consist of "chunks". Each chunk contains an operation where the first character is the "op code" (op is short for operation). All characters after are "op data". The op codes are indexed from 0. Each op code has a defined size, except for RLE which specifies it as part of its data. The size only counts the op data. The encoder prioritises smaller operations to get the best compression.

Refer to [ops.xlsx](ops.xlsx) for tables of all operations.

# RGB8
*RGB data, 8 bits per channel*
*(although could accept any 3-channel 8-bit data, note that the compression expects minimal luma differences to be common like in photos)*

The compression used here outperforms both QOI and PNG images (when they are represented as base 64). As far as I'm aware, this is the best image compression available for Scratch. 

## Chunks
Index:
- raw RGB value (0-21)
- copy adjacent colour (22-25)
- index into a hash table like QOI (26)
- run-length encoding (RLE) of op codes (27)
- luma difference volumes, size 1 (28-72)
- luma difference volumes, size 2 (73-90)
- unassigned (91-93)

Size:
- copy adjacent colour: 0
- index into a hash table: 1
- luma difference, size 1: 1
- luma difference, size 2: 2
- RLE: 2 or more
- raw RGB value: 3

### Raw RGB Value
With 22 operations, each with 3 data characters, a mixed-base number (a₂₂,b₉₄,c₉₄,d₉₄) can be represented (internally referred to as a "4-tuple"). This can contain all 16,777,216 8-bit per channel RGB colours. 

### Copy Adjacent Colour
Copy previous, vertical-forward, vertical, vertical-back.

### Colour Differences
Adjacent pixels in an image tend to be similar to each other and differences in brightness are usually more significant. Knowing this, a large amount of the operations are assigned to encoding this efficiently through "luma differences". Each luma difference operation represents a rectangular cuboid "volume" where every coordinate inside can be indexed. There are 2 sizes of volumes. Size 1 is 1 data character in length and has 94 indices (one for every character). Size 2 uses 2 data characters and has a total of 94x94=8836 indices. Size 1 has the dimensions of (5,4,4) and size 2 has the dimensions of (21,20,20). Both don't fit perfectly into the total number of indices so some are wasted unfortunately. The volumes are in Y'UV space. RGB values are remapped to Y'UV like QOI (green channel is luma, U and V are the difference from blue and red from green). 

All the volumes are positioned in Y'UV space to best cover the spread of possible colour differences. Size 1 volumes are clustered around the origin of (0,0,0) as smaller differences are much more common. Even more common than that are the same colour repeating and for this, 4 operations are assigned to copying colours.

### RLE
Run-length encoding is handled as a 2nd pass in the encoder. Its goal is to reduce the number of repeating op codes (note: not op data). A single RLE operation consists of 2 fixed data characters, which is the operation it will repeat and then the number of times it will be repeated (0-93 times). This does mean it is possible to specify itself as the character to repeat but this is not implemented due to the complexity it would add.


# A8
*Generic single-channel 8-bit data*
Example use case: transparency
(WIP, not in a usable state yet)

## Chunks
Index:
- raw value (0-2)
- copy adjacent colour (3-6)
- run-length encoding (RLE) of op codes (7)
- increasing difference (8-50)
- decreasing difference (51-93)

Size:
- copy adjacent colour: 0
- increasing difference: 0
- decreasing difference: 0
- RLE: 2 or more
- raw value: 1

### Raw Value
There are 256 values that need to be encoded and these can fit in to 3 operations with 1 data char each. 

raw0 handles 0-93, raw1 handles 94-187, raw2 handles 188-255.

### Copy Adjacent Colour
Copy previous, vertical-forward, vertical, vertical-back.

### Difference
If a value is similar to the previous, it can be encoded as a difference from it. Differences from 1 to 43 and -1 to -43 can be encoded as single operations. A difference of 0 is handled by the copy_prev operation. Differences can wrap. For example, 254 -> 3 can be handled as a difference of -251 or it can be better handled as -5 which can be encoded as it is in the range.

### RLE
Not implemented.
