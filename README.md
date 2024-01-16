# TextImage

## Motivations
The image format outlined here was necessitated by a lack of any decent way to store bitmap image data in Scratch. Scratch is limiting in that it cannot store binary data, only strings, booleans, and double floats within variables and lists. Common image formats like PNG and JPEG are unusable without being represented as plain text. This has been done before, commonly using base 64 or hexadecimal but it's not optimal as there are many more characters available but no simple and efficient way to utilise them, and this still ignores the fact that binary image formats are difficult to read/write using the available features of Scratch. Simpler representations of images are very common but are usually uncompressed, for example, hexadecimal numbers concatenated together. These are fine for many use cases but lack of compression and metadata can make them less usable for more complex projects.


## Format Outline
- Supports an arbitrary number of colour channels including lossless 8-bit per channel RGB bitmap images and lossless 8-bit per channel generic (e.g. for alpha).
- Uses printable ASCII characters only, no spaces and no newlines.
- Simple enough to implement in scratch (while also minimising the number of blocks and variables), enabling it to be more easily be used by others.
- Offers significantly smaller file sizes compared to pre-existing Scratch methods.

[TextImage examples](images/converted)


## Format Specifications
This format stores images as printable text using 94 of the 95 printable ASCII characters. The one character excluded is space.

The full ordered set of characters in use, indexed 0-93:

```!"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz{|}~```

An arbitrary number of "data streams" can be specified. Each data stream has corresponding properties to specify their type and usage. This enables easy expansion to support new methods beyond the 8-bit RGB and 8-bit generic lossless data streams currently implemented.

The image format begins with magic number `txtimg`. This follows with a comma and then these key-value pairs separated by commas. Semicolons go between the key name and value. Identical implementation to [my save code format](https://awesome-llama.github.io/articles/my-save-code-format). This part of the format is known as `CSKV` or "comma-separated key-values".

- version number `v` (currently `0`)
- image width `x` in pixels 
- image height `y` in pixels
- list of data stream properties `p` containing 4 alternating property values. First value indicates the total number of items in the list. The following properties are (in this order): 
    - purpose within the image (`main`, `alpha`, etc.)
    - data stream type (`RGB8`, `A8`, etc.)
    - data stream version (`0` for all data streams currently)
    - data stream length (number of characters in the data stream by itself)

A vertical bar (`|`) then indicates the data streams will follow, which are all concatenated without any separating character. 

An example image looks like this (with the concatenated data streams removed):

```txtimg,v:0,x:120,y:80,p:8,main,RGB8,0,22682,alpha,A8,0,523|```

This example is a 120x80 image with 8 bit RGB and alpha channels. The RGB8 data stream is 22682 characters long whereas the alpha channel is 523 characters.

Reserved characters due to their usage as separators: `,:|`

Use of custom key names to store additional data is allowed however to avoid potential future conflicts prefix an underscore to the key name (these are reserved for custom use). 

Pixels are ordered left-to-right (x axis), bottom-to-top (y axis).


### Data Streams
See [data_streams.md](data_streams.md).


## Dependencies
- Requires Pillow and numpy.
- pyperclip is used in `quick_preview.py` but not required anywhere else.
- Python 3.10 or newer.


## Usage
Use the methods defined in [image_io.py](image_io.py). 

An image can be stored as a `TextImage` object. To convert it to a Pillow Image object, use the method `to_pillow_image()` (and from there you can manipulate or save it). To create a TextImage object, use `load_from_pillow_image()` to load from a Pillow Image object or  `load_from_text_file()` to load from a saved TextImage text file. To save a TextImage object as a text file, use the `save()` method.


## Current Issues
### Performance
The Python reference encoder and decoder is slow. It should however be OK for Scratch usage with the size of images typically used there.

