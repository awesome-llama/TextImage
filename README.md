# Prototype Image Format 2
**Work in progress! Everything subject to change!**

## Motivations
The image format outlined here was necessitated by a lack of any decent way to store image data in Scratch. Scratch is limiting in that it cannot store binary data. Common image formats like PNG and JPEG are unusable without being represented as plain text. This has been done before, commonly using base 64 or hexadecimal but it's not optimal. There are many more characters available but no easy way to fit binary data into them without big inefficiencies. These formats also were not designed to be implemented in Scratch so the scripts end up being quite large, complex, and slow. 

Simpler representations of images exist too but they are usually uncompressed. Colours as hexadecimal numbers concatenated together is commonly used. It's fine for some use cases, but there are many where simply no decent format exists for them. Some examples are listed in this forum topic: https://scratch.mit.edu/discuss/topic/604786/


## Format Introduction
There are 95 printable characters (including whitespace). It was decided that space shouldn't be part of the format so it is excluded, leaving 94. 

The full ordered set of characters this format uses are listed here:
```!"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz{|}~```

"What about Unicode characters? There are so many of them!" 
There are many issues with this common thought. For UTF-8, ASCII characters take up 1 byte each but other characters take multiple. Additionally, it complicates the implementation (note that case detection already requires costumes for each character). Are the characters as widely supported? There is an increased risk of places that will disallow or handle them wrong. These issues significantly outweigh any possible benefit.


## Container
~~The image format is actually a container format. It can specify an arbitrary number of "layers". Each layer contains 1 data stream. The available data streams are listed further below.~~

(WIP)
~~A layer specifies the following data:~~
- purpose (main, alpha, etc.)
- data stream name
- data stream version
- data stream length

(WIP)


## Data Streams
### RGB8
*RGB data, 8 bits per channel*
*(although could accept any 3-channel 8-bit data, just note that the compression expects luma differences to be significant)*

The compression used here outperforms both QOI and PNG images (when they are represented as base 64). As far as I'm aware, this is the best image compression available for Scratch. 

#### Chunks
This data stream consists of "chunks". Each chunk contains an operation where the first character is the "op code" (op is short for operation). All characters after are "op data". The op codes are indexed from 0 and are the following:
- raw RGB value (0-21)
- copy adjacent colour (22-25)
- index into a hash table like QOI (26)
- run-length encoding (RLE) of op codes (27)
- luma difference volumes, size 1 (28-72)
- luma difference volumes, size 2 (73-90)
- unassigned (91-93)

Each op code has a defined size, except for RLE which specifies it as part of its data. The sizes are the following (note that this count excludes the op code itself):
- copy adjacent colour: 0
- index into a hash table: 1
- luma difference, size 1: 1
- luma difference, size 2: 2
- RLE: 2 or more
- raw RGB value: 3

The encoder prioritises smaller operations. The worst operation is a raw RGB value.

#### Raw RGB Value
With 22 operations, each with 3 data characters, a mixed-base number (a₂₂,b₉₄,c₉₄,d₉₄) can be represented (internally referred to as a "4-tuple"). This can contain all 16,777,216 8-bit per channel RGB colours. 

#### Copy Adjacent Colour
Copy previous, vertical-forward, vertical, vertical-back.

#### Colour Differences
Adjacent pixels in an image tend to be similar to each other and differences in brightness are usually more significant. Knowing this, a large amount of the operations are assigned to encoding this efficiently through "luma differences". Each luma difference operation represents a rectangular cuboid "volume" where every coordinate inside can be indexed. There are 2 sizes of volumes. Size 1 is 1 data character in length and has 94 indices (one for every character). Size 2 uses 2 data characters and has a total of 94x94=8836 indices. Size 1 has the dimensions of (5,4,4) and size 2 has the dimensions of (21,20,20). Both don't fit perfectly into the total number of indices so some are wasted unfortunately. The volumes are in Y'UV space. RGB values are remapped to Y'UV like QOI (green channel is luma, U and V are the difference from blue and red from green). 

All the volumes are positioned in Y'UV space to best cover the spread of possible colour differences. Size 1 volumes are clustered around the origin of (0,0,0) as smaller differences are much more common. Even more common than that are the same colour repeating and for this, 4 operations are assigned to copying colours.

#### RLE
Run-length encoding is handled as a 2nd pass in the encoder. Its goal is to reduce the number of repeating op codes (note: not op data). A single RLE operation consists of 2 fixed data characters, which is the operation it will repeat and then the number of times it will be repeated (0-93 times). This does mean it is possible to specify itself as the character to repeat but this is not implemented due to the complexity it would add.


### A8
*Generic single-channel 8-bit data*

~~Like RGB8, this data stream consists of chunks~~
(WIP)


## Dependencies
- Requires Pillow and numpy.
- Python 3.10 or newer.


## Usage
Requires some configuration. See `compress_image.py`.
(WIP)


## Current Issues
### Performance
The Python reference encoder and decoder is slow. It should however be OK for Scratch usage with the size of images typically used there.

