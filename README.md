# Prototype Image Format 2
**Work in progress! Everything subject to change!**

See: https://scratch.mit.edu/discuss/topic/604786/
A successor to the image format used in TM3D available here: https://scratch.mit.edu/projects/788861757/

This format will consist of a container where a number of "layers" can be defined. Each layer can contain a data stream. The only data stream available currently is "RGB8" (RGB 8-bit per channel colour). There is a plan on adding another type for generic single-channel data. 

This project makes use of base 94. All printable ASCII characters except whitespace is in use. The compression used here outperforms both QOI and PNG images (when they are represented as base 64). As far as I'm aware, this is currently the best image compression available for Scratch. 

## Dependencies
- Requires Pillow and numpy.
- Python 3.10 or newer.

## Usage
WIP.
Requires some configuration. See `compress_image.py`.


## RGB8
The data stream consists of "chunks". Each chunk contains an operation where the first character is the "op code". All characters after are "op data". The op codes are indexed from 0 and are the following:
- raw RGB value (0-21)
- copy adjacent colour (22-25)
- use hash table like QOI (26)
- RLE of op codes (27)
- luma diff volumes (28-90)
- unassigned (91-93)

Colours in an image tend to be similar to each other. Luma differences are more common compared to colour. I remap the RGB values to Y'UV like QOI. Then I make use of rectangular cuboid "volumes" of small and large sizes (1 and 2 op data chars, respectively) to cover the spread efficiently and allow for such changes in colour to be encoded by specifying a volume and a location within it. Smaller volumes are centered around the origin since smaller changes are very common. The result is a large majority of the pixels are accounted for with this form of compression.

## Current issues
### Performance
The Python reference encoder and decoder is slow. It should however be OK for Scratch usage with the size of images typically used there.
