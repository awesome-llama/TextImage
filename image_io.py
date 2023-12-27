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



if __name__ == '__main__':
    print('compress')
    compress_img('images/beach_15x9.png')