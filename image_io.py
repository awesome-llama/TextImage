# Save and load images

from PIL import Image
import numpy as np
import layer_A8
import layer_RGB8
import cskv_utils as cskv

class TextImage:
    def __init__(self, size: tuple):
        """Text Image object"""
        
        self.magic_num = 'txtimg'
        self.version = '0'
        
        self.size = (max(0, int(size[0])), max(0, int(size[1]))) # 2-tuple for width and height
        self.layers = {} # dict containing all the layers (properties and data stream), key is purpose
        self.custom_attributes = {} # for the user to store additional data

    def __str__(self):
        return f'TextImage v{self.version} {self.size[0]}x{self.size[1]} with {len(self.layers)} layers: {', '.join([k + ' using ' + l['type'] + '_v' + l['version'] for k,l in self.layers.items()])}'

    def add_layer(self, data_stream, purpose='main', type='RGB8', version='0'):
        """Add a layer to the image"""
        self.layers[purpose] = {
            'type':type,
            'version':version,
            'data_stream':data_stream,
        }
    
    def text(self):
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
            header['p'].extend([
                str(k),
                str(l['type']),
                str(l['version']),
                str(len(l['data_stream'])),
            ])
            layer_data_streams.append(l['data_stream'])
        
        # concatenate everything into a single string...
        file = cskv.CSKV_write(header, magic_number=self.magic_num, append_comma=False)
        file = file + '|' + ''.join(layer_data_streams)

        return file

    def save(self, path):
        """Save the image to a file"""
        with open(path, 'w') as f:
            f.write(self.text())

    def to_pillow_image(self, main_layer='main', alpha_layer=None, debug=False):
        """Return a Pillow image object"""

        # get main:
        if main_layer not in self.layers:
            raise Exception('main layer not found')
        
        if self.layers[main_layer]['type'] == 'RGB8':
            main_array = layer_RGB8.decompress(self.layers[main_layer]['data_stream'], self.size, debug=debug)
            main_array = np.array(main_array, np.uint8)
            main_array = np.flip(main_array.reshape(self.size[1], self.size[0], 3), 0)
        elif self.layers[main_layer]['type'] == 'A8':
            main_array = layer_A8.decompress(self.layers[main_layer]['data_stream'], self.size, debug=debug)
            main_array = np.array(main_array, np.uint8)
            main_array = np.repeat(main_array, 3)
            main_array = np.flip(main_array.reshape(self.size[1], self.size[0], 3), 0)
        else: raise Exception('Layer type unknown for main')
        
        
        if alpha_layer is not None:
            # get alpha
            if alpha_layer in self.layers:
                if self.layers[alpha_layer]['type'] != 'A8':
                    raise Exception('alpha layer must be single channel')
                
                alpha_array = layer_A8.decompress(self.layers[alpha_layer]['data_stream'], self.size, debug=debug)
                alpha_array = np.array(alpha_array, np.uint8)
                alpha_array = np.flip(alpha_array.reshape(self.size[1], self.size[0], 1), 0)
                
            else: raise Exception('alpha layer not found')
            
            image = Image.fromarray(obj=np.concatenate((main_array, alpha_array), axis=-1), mode='RGBA')

        else:
            # no alpha
            image = Image.fromarray(obj=main_array, mode='RGB')

        return image


def load_from_image_file(path, debug=False):
    """Load an image file and return a text image object"""

    def asarray(image, size: tuple, channels: int = 1):
        """Convert pillow object into flattened array"""
        arr = np.asarray(image)
        arr = np.flip(arr, 0)
        arr = np.reshape(arr, (size[0]*size[1], channels), 'A')
        return arr
    
    image = Image.open(path)
    txtimg = TextImage(image.size)

    # RGB main
    image_array = asarray(image.convert('RGB'), image.size, 3)
    ds = layer_RGB8.compress(image_array, image.size, debug=debug)
    txtimg.add_layer(ds, 'main', 'RGB8', '0')

    # alpha channel
    if image.mode == 'RGBA':
        image_array = asarray(image.split()[-1], image.size, 1)
        ds = layer_A8.compress(image_array, image.size, debug=debug)
        txtimg.add_layer(ds, 'alpha', 'A8', '0')

    return txtimg


def load_from_text(path):
    """Load a text image from file, return TextImage object"""

    with open(path, 'r') as f:
        file: str = f.read()

    header, layer_data_streams = file.split('|', 1) # split at first bar character
    
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
        txtimg.add_layer(ds, p[0], p[1], p[2]) 

    return txtimg
    
def split_by_lengths(data, lengths:list):
    """Split indexable data by a list of desired resulting lengths."""
    result = []
    start = 0
    for length in lengths:
        result.append(data[start:start+length])
        start += length

    return result

    

if __name__ == '__main__':
    PATH = 'images/alphagrad.png'
    #PATH = 'C:/Users/Atlas/Documents/Scratch/Image Format 2/all images/alltrue_mc_textures.png'
    
    print('COMPRESS')
    txtimg = load_from_image_file(PATH, False)
    print(txtimg)
    txtimg.save('output/compressed2.txt')

    print('')

    print('DECOMPRESS')
    txtimg = load_from_text('output/compressed2.txt')
    print(txtimg)
    img = txtimg.to_pillow_image(alpha_layer='alpha')
    print(img)
    img.show()
    img.save('output/decompressed.png')

    #print(split_by_lengths('abcdefgh', [2, 3, 2, 1]))

    # test: main channel to A8
    """txtimg = load_from_image_file('images/rhodes_transparent.png')
    txtimg.layers['main'] = txtimg.layers['alpha']
    txtimg.layers.pop('alpha')

    txtimg.save('output/compressed2.txt')

    txtimg = load_from_text('output/compressed2.txt')
    print(txtimg)
    img = txtimg.to_pillow_image()
    print(img)
    img.show()
    img.save('output/decompressed.png')"""
