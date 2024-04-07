# Save and load images

from PIL import Image
import numpy as np
import layer_A8
import layer_RGB8
import layer_utils as lu
import cskv_utils as cskv

class TextImage:
    def __init__(self, size: tuple):
        """A TextImage object representing the conceptual structure of an image."""
        
        self.magic_num = 'txtimg'
        self.version = '0'
        
        self.size = (max(0, int(size[0])), max(0, int(size[1]))) # 2-tuple for width and height
        self.layers = {} # dict containing all the layers keyed by purpose
        self.custom_attributes = {} # for the user to store additional data. Ignored by a reference decoder.

    def __str__(self):
        return f'TextImage v{self.version} {self.size[0]}x{self.size[1]} with {len(self.layers)} layers: {','.join([f'{k}:{str(ds)}' for k, ds in self.layers.items()])}'

    def set_layer(self, purpose: str, encoded_data_stream: lu.DataStream):
        """Add a layer to the image or replace an existing one. Purpose should be `main` for the main colour layer or `alpha` for transparency. Purpose will be converted to a lowercase string."""
        purpose = str(purpose).lower()
        if not isinstance(encoded_data_stream, lu.DataStream): raise Exception('encoded_data_stream is not a DataStream object')
        self.layers[purpose] = encoded_data_stream
    
    def text(self) -> str:
        """Get the image as text"""
        file = []

        header = {
            'v':self.version,
            'x':self.size[0],
            'y':self.size[1],
            'p':[], # layer properties
            }

        # custom attributes
        for k,v in self.custom_attributes.items():
            if k not in header: header[k] = v
        
        # layers
        layer_data_streams = [] # the actual data streams
        for k,l in self.layers.items():
            l: lu.DataStream
            header['p'].extend([str(k), l.type, l.version, str(len(l.data_stream)),])
            layer_data_streams.append(l.data_stream)
        
        # concatenate everything into a single string...
        file = cskv.CSKV_write(header, magic_number=self.magic_num, append_comma=False)
        file = file + '|' + ''.join(layer_data_streams)

        return file

    def save(self, path):
        """Save the image to a file"""
        with open(path, 'w') as f:
            f.write(self.text())

    def to_pillow_image(self, main_layer='main', alpha_layer='alpha', require_alpha=False, debug=False) -> Image.Image:
        """Return a Pillow image object"""

        # get main:
        if main_layer not in self.layers: raise Exception('main layer not found')
        
        if self.layers[main_layer].type == 'RGB8':
            main_array = layer_RGB8.decompress(self.layers[main_layer].data_stream, self.size, debug=debug)
            main_array = np.array(main_array, np.uint8)
            main_array = np.flip(main_array.reshape(self.size[1], self.size[0], 3), 0)
        elif self.layers[main_layer].type == 'A8':
            main_array = layer_A8.decompress(self.layers[main_layer].data_stream, self.size, debug=debug)
            main_array = np.array(main_array, np.uint8)
            main_array = np.repeat(main_array, 3)
            main_array = np.flip(main_array.reshape(self.size[1], self.size[0], 3), 0)
        else: 
            raise Exception('Layer type unknown for main')
        
        # get alpha:
        if alpha_layer in self.layers:
            if self.layers[alpha_layer].type != 'A8':
                raise Exception('alpha layer must be single channel')
            
            alpha_array = layer_A8.decompress(self.layers[alpha_layer].data_stream, self.size, debug=debug)
            alpha_array = np.array(alpha_array, np.uint8)
            alpha_array = np.flip(alpha_array.reshape(self.size[1], self.size[0], 1), 0)
            
            image = Image.fromarray(obj=np.concatenate((main_array, alpha_array), axis=-1), mode='RGBA')
        
        elif require_alpha: 
            raise Exception('alpha layer not found, if you do not need alpha in the result, set `require_alpha` to False.')
    
        else: # no alpha
            image = Image.fromarray(obj=main_array, mode='RGB')

        return image


def load_from_pillow_image(image, debug=False) -> TextImage:
    """Load a Pillow image object and return a TextImage object"""

    def asarray(image, size: tuple, channels: int = 1):
        """Convert Pillow object into flattened array"""
        arr = np.asarray(image)
        arr = np.flip(arr, 0)
        arr = np.reshape(arr, (size[0]*size[1], channels), 'A')
        return arr
    
    txtimg = TextImage(image.size)

    # RGB main
    if image.mode == 'L':
        image_array = asarray(image, image.size, 1)
        ds = layer_A8.compress(image_array, image.size, debug=debug)
        txtimg.set_layer('main', ds)
    else:
        image_array = asarray(image.convert('RGB'), image.size, 3)
        ds = layer_RGB8.compress(image_array, image.size, debug=debug)
        txtimg.set_layer('main', ds)

    # alpha channel
    if image.mode == 'RGBA':
        image_array = asarray(image.split()[-1], image.size, 1)
        ds = layer_A8.compress(image_array, image.size, debug=debug)
        txtimg.set_layer('alpha', ds)

    return txtimg


def load_from_text(text: str) -> TextImage:
    """Load a TextImage from text, return a TextImage object"""

    header, layer_data_streams = str(text).split('|', 1) # split at first bar character
    
    # read header
    header = cskv.CSKV_read(header, remove_end_comma=False)

    # format validity
    if header[None] != 'txtimg': raise Exception('Unknown magic number')
    if header['v'] != '0': raise Exception('Incompatible version number, expected 0')
    if int(header['p'][0])+1 != len(header['p']): raise Exception('layer properties invalid length')
    
    header['p'].pop(0)

    txtimg = TextImage((header['x'], header['y']))
    txtimg.version = header['v']

    # reformat layers
    layer_properties = []
    lengths = []
    for i in range(0, len(header['p']), 4):
        layer_properties.append(header['p'][i:i+3])
        lengths.append(int(header['p'][i+3]))
    layer_data_streams = split_by_lengths(layer_data_streams, lengths)
    
    # add all the layers to the object
    for p,ds in zip(layer_properties, layer_data_streams):
        txtimg.set_layer(p[0], lu.DataStream(ds, p[1], p[2])) 

    return txtimg


def load_from_text_file(path) -> TextImage:
    """Load a TextImage from text file, return a TextImage object"""

    with open(path, 'r') as f:
        file: str = f.read()

    return load_from_text(file)


def split_by_lengths(data, lengths:list) -> list:
    """Split indexable data by a list of desired resulting lengths."""
    result = []
    start = 0
    for length in lengths:
        result.append(data[start:start+length])
        start += length

    return result

    

if __name__ == '__main__':
    pass
