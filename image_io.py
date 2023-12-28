# save and load images
# TODO add functions here, replace compress_image.py

from PIL import Image
import numpy as np
import layer_A8
import layer_RGB8


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


if __name__ == '__main__':
    print('compress')
    img = from_image_file('images/alphagrad.png', False)
    img.save('output/compressed2.txt')

