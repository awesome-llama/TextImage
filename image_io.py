# save and load images
# TODO add functions here, replace compress_image.py

from PIL import Image
import numpy as np
import layer_utils as lu
import layer_A8
import layer_RGB8


def compress_img(image_path, output_path='output/', mode='RGBA', debug=False):
    """Open an image and compress it. Save."""
    # TODO: choose where to load and save, specify colour mode, compression, debug
    
    image = Image.open(image_path)

    file = [
        'img', 
        'v:0', 
        f'x:{image.width}',
        f'y:{image.height}',
        ]

    data_streams_props = [] # list of properties
    data_streams = [] # the actual data streams
    
    if mode == 'RGBA' or mode == 'RGB':
        
        image = image.convert('RGB') # TODO detect alpha
        image_array = np.asarray(image)
        image_array = np.flip(image_array, 0)
        image_array = np.reshape(image_array, (image.width*image.height, 3), 'A')
        
        ds = layer_RGB8.compress(image_array, image.size, debug=debug)
        data_streams.append(ds)
        data_streams_props.extend(lu.properties('main', 'RGB8', 0, ds))
    
    # concatenate everything into a single string...
    file.append(f'p:{len(data_streams_props)},{",".join(data_streams_props)}')
    file = ",".join(file)
    file = file + '|' + "".join(data_streams)

    # save file
    with open(output_path + 'compressed.txt', 'w') as f:
        f.write(file)


class TextImage:
    def __init__(self, size: tuple):
        """Text Image object"""
        
        self.magic_num = 'txtimg'
        self.version = '0'
        
        self.size: tuple = size # 2-tuple for width and height
        self.layers: list = [] # a list containing all the layers (properties and data stream)
        self.custom_attributes = {} # for the user to store additional data

    def add_layer(self, data_stream, purpose='main', type='RGB8', version='0'):
        """Add a layer to the image"""
        self.layers.append({
            'purpose':purpose,
            'type':type,
            'version':version,
            'data_stream':data_stream,
        })
    
    def text(self):
        """Get the image as text"""
        file = []
        # essentials
        file.append(str(self.magic_num))
        file.append(f'v:{self.version}')
        file.append(f'x:{self.size[0]}')
        file.append(f'y:{self.size[1]}')

        # custom attributes
        for k,v in self.custom_attributes.items():
            file.append(f'{k}:{v}')
        
        # layers
        layer_props = [] # list of properties
        layer_data_streams = [] # the actual data streams
        for l in self.layers:
            layer_props.extend([
                str(l['purpose']),
                str(l['type']),
                str(l['version']),
                str(len(l['data_stream'])),
            ])
            layer_data_streams.append(l['data_stream'])
        
        file.append(f'p:{len(layer_props)},{','.join(layer_props)}')
        
        # concatenate everything into a single string...
        file = ','.join(file) + '|' + ''.join(layer_data_streams)

        return file

    def save(self, path):
        """Save the image to a file"""
        with open(path, 'w') as f:
            f.write(self.text())

    def to_pillow_image(self):
        """Return a Pillow image object"""
        image = Image.new('RGB', size=self.size)
        return image


def from_image_file(path, debug=False):
    """Load an image file and return a text image object"""

    image = Image.open(path)
    txtimg = TextImage(image.size)

    im = image.convert('RGB')
    image_array = np.asarray(im)
    image_array = np.flip(image_array, 0)
    image_array = np.reshape(image_array, (image.width*image.height, 3), 'A')
    ds = layer_RGB8.compress(image_array, image.size, debug=debug)
    txtimg.add_layer(ds, 'main', 'RGB8', '0')

    if image.mode == 'RGBA':
        alpha = image.split()[-1]
        image_array = np.asarray(alpha)
        image_array = np.flip(image_array, 0)
        image_array = np.reshape(image_array, (image.width*image.height, 1), 'A')
        ds = layer_A8.compress(image_array, image.size, debug=debug)
        txtimg.add_layer(ds, 'alpha', 'A8', '0')

    return txtimg

if __name__ == '__main__':
    print('compress')
    #compress_img('images/beach_15x9.png')

    img = from_image_file('images/alphagrad.png', False)
    img.save('output/compressed2.txt')