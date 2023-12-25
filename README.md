# Prototype Image Format 2
**Work in progress! Everything subject to change!**

## Motivations
The image format outlined here was necessitated by a lack of any decent way to store image data in Scratch. Scratch is limiting in that it cannot store binary data. Common image formats like PNG and JPEG are unusable without being represented as plain text. This has been done before, commonly using base 64 or hexadecimal but it's not optimal. There are many more characters available but no easy way to fit binary data into them without big inefficiencies. These formats also were not designed to be implemented in Scratch so the scripts end up being quite large, complex, and slow. 

Simpler representations of images exist too but they are usually uncompressed. Colours as hexadecimal numbers concatenated together is commonly used. It's fine for some use cases, but there are many where simply no decent format exists for them. Some examples are listed in [this forum topic](https://scratch.mit.edu/discuss/topic/604786/). 


## Format Introduction
This format stores images as printable text. There are 95 printable ASCII characters (including whitespace). It was decided that space shouldn't be part of the format so it is excluded, leaving 94. 

The full ordered set of characters in use, indexed from 0:

```!"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz{|}~```




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
See [data_streams.md](data_streams.md).

## Dependencies
- Requires Pillow and numpy.
- Python 3.10 or newer.


## Usage
Requires some configuration. See [compress_image.py](compress_image.py), which demonstrates ways to access the compression and decompression of RGB8. This is all work-in-progress!


## Current Issues
### Performance
The Python reference encoder and decoder is slow. It should however be OK for Scratch usage with the size of images typically used there.

