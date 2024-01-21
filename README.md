# TextImage

## Motivations
The image format outlined here was necessitated by the lack of any decent way to store bitmap image data in Scratch. Scratch is limiting in that binary data can not be stored, only strings, booleans, and double floats. Binary data represented using base 64 or hexadecimal numbers have been demonstrated but are suboptimal (there are many unused characters) and use of common binary image formats like BMP, PNG, and JPEG are difficult to read/write using Scratch's limited feature set. Instead, what is more common in Scratch is use of very simple and usually custom-made uncompressed formats, for example, hexadecimal numbers for each pixel concatenated together. Many of these formats lack essential features necessary for adoption and standardisation. 


## Format Outline
- Supports an arbitrary number of colour channels including lossless 8-bits per channel RGB bitmap images and lossless 8-bits per channel generic (e.g. for alpha).
- Uses printable ASCII characters only, no spaces and no newlines.
- Simple enough to implement in Scratch (minimising the number of blocks and variables), enabling it to be more easily used in projects.
- Offers significantly smaller file sizes compared to pre-existing Scratch methods, and in some cases even better than common image formats like PNG.

### Links
- [Example images](images/converted)
- [Scratch Reference Implementation](https://scratch.mit.edu/projects/945312296/)
- [List of projects using TextImage](documentation/adoption.md)


## Format Specifications
This format stores images as printable text using 94 of the 95 printable ASCII characters. The one character excluded is space. In the commonly-used [UTF-8 text encoding](https://en.wikipedia.org/wiki/UTF-8), these characters each have a size of 1 byte.

The full ordered set of characters in use, indexed 0-93:

```!"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz{|}~```

An arbitrary number of "data streams" can be specified. Each data stream has corresponding properties to specify their type and usage. This enables easy expansion to support new methods beyond the 8-bit RGB and 8-bit generic lossless data streams currently implemented.

The image format begins with magic number `txtimg`. This follows with a comma and then these key-value pairs separated by commas. Semicolons go between the key name and value. Identical implementation to [my save code format](https://awesome-llama.github.io/articles/my-save-code-format). This part of the format is known as CSKV or "comma-separated key-values".

- version number `v` (currently `0`)
- image width `x` in pixels 
- image height `y` in pixels
- list of data stream properties `p` containing 4 alternating property values. First value indicates the total number of items in the list. The following properties are (in this order): 
    - purpose within the image (`main`, `alpha`, etc. `main` is the main colour channel and should be highest priority. All images should have one. `alpha` indicates the layer is for transparency. No other purpose is currently defined, it is open to custom use cases where additional layers are needed)
    - data stream type (`RGB8`, `A8`, etc.)
    - data stream version (`0` for all data streams currently)
    - data stream length (number of characters in the data stream by itself)

A vertical bar (`|`) then indicates the data streams will follow, which are all concatenated without any separating character. 

Reserved characters due to their usage as separators: `,` `:` `|` They must not be used within keys or values.

Use of custom key names to store additional data is allowed however to avoid potential future conflicts prefix an underscore to the key name (these are reserved for custom use). 

Data streams use pixels that are ordered left-to-right (x axis), bottom-to-top (y axis).

### Example
The following is an example TextImage file, with explanation for some of the parts:

```
txtimg,v:0,x:14,y:17,p:8,main,RGB8,0,142,alpha,A8,0,101|<7?40vV53c><7)877798<7)877798<7)87779;!7H+B.D`@"Co8787779;j<7)8777953f!=J787;b77987779;!8787;!879877794e6p878787798<7N""?q!(FD<7)877798<7)8<7>!!($/T($,%$%($,%$%($,%$%($,%$%($,%$%($,%$%($,%$%($,%$%($,%$%($,%($&%$$$)($&T($,%$%($,%$%($,%$%($,%($/
```

- `txtimg,v:0,x:14,y:17` TextImage file, version 0, dimensions 14x17
- `p:8,main,RGB8,0,142,alpha,A8,0,101` Properties containing 8 list items to follow, specifying a main RGB8 data stream that is 142 characters long and an alpha A8 data stream that is 101 characters long.
- `|` The concatenated data streams follow, in the order given by the properties (RGB8 and then A8)
- ```<7?40vV53c><7)877798<7)877798<7)87779;!7H+B.D`@"Co8787779;j<7)8777953f!=J787;b77987779;!8787;!879877794e6p878787798<7N""?q!(FD<7)877798<7)8<7>``` RGB8 data stream
- ```!!($/T($,%$%($,%$%($,%$%($,%$%($,%$%($,%$%($,%$%($,%$%($,%$%($,%($&%$$$)($&T($,%$%($,%$%($,%$%($,%($/``` A8 data stream


### Data Streams
See [data_streams.md](documentation/data_streams.md) for detailed information on them.


## Dependencies
- Requires Pillow and numpy.
- pyperclip is used in `quick_preview.py` but not required anywhere else.
- Python 3.10 or newer.


## Usage
### Previewing
For a quick preview of an image that does not require writing your own code, you can run `quick_preview.py` to preview the TextImage stored in your system clipboard.


### Code
Use the methods defined in [image_io.py](image_io.py). An image can be stored as a `TextImage` object.

- To create a TextImage object, use `load_from_pillow_image()` to load from a Pillow Image object. Use Pillow if you want to load an image from a file like PNG or JPG. If you already have a TextImage file, use `load_from_text_file()` or `load_from_text()` if it was a Python string. 
- To convert a TextImage object to a Pillow Image object, use the method `to_pillow_image()` (and from there you can manipulate or save it). 
- To save a TextImage object as a TextImage file, use the `save()` method or `text()` if you want it as a Python string.

If you want more control such as creating arbitrary channels, you can create a blank TextImage object, specifying the image dimensions, and then add channels using `add_layer()`, which gives full control over data stream type, purpose, and of course, the data itself.


## Current Issues
### Performance
The Python reference encoder and decoder is slow however for the resolution of images used in Scratch it's not much of an issue.

