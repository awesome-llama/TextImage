# Load an image and compress it into the text-based format.

from PIL import Image
import numpy as np
import layer_RGB8
#import layer_A8

debug_dimensions = () # TESTING ONLY

# TODO: create proper functions for handling file loading and saving, handle the file paths better too

def compress_img(image_path, output_path='output/', lossy_tolerance=0, debug=False):
    """Open an image and compress it. Save."""
    
    image = Image.open(image_path)
    
    image = image.convert('RGB') # TODO detect alpha
    image_array = np.asarray(image)
    image_array = np.flip(image_array, 0)
    image_array = np.reshape(image_array, (image.width*image.height, 3), 'A')
    global debug_dimensions
    debug_dimensions = image.size
    
    data_stream = layer_RGB8.compress(image_array, image.size, lossy_tolerance, debug=debug)

    file = data_stream

    with open(output_path + 'compressed.txt', 'w') as f:
        f.write(file)



def decompress_img(image_path, output_path='output/', debug=False):
    
    with open(image_path) as f:
        image = f.read()

    #dimensions = (256, 256)
    #print(debug_dimensions)
    dimensions = debug_dimensions
    
    image_array = layer_RGB8.decompress(image, dimensions, debug=debug)

    # output the image:
    image_array = np.array(image_array, np.uint8)
    image_array = np.flip(image_array.reshape(dimensions[1], dimensions[0], 3), 0)
    image = Image.fromarray(obj=image_array, mode='RGB')

    image.show()
    image.save(output_path + 'decompressed.png')


if __name__ == '__main__':
    print('compress')

    #compress_img('images/beach.png')
    #compress_img('images/test.png')
    #compress_img('images/grad.png', lossy_tolerance=20)
    #compress_img('images/region_landing_pad_night.png', lossy_tolerance=20)
    #compress_img('images/boat.png', lossy_tolerance=1)
    #compress_img('images/testcard.png')
    #compress_img('images/breakable_atlas.png')
    #compress_img('images/nprguy.jpg')
    #compress_img('C:/Users/Atlas/Downloads/col.bmp')
    #compress_img('images/region_pod.png')
    compress_img('C:/Users/Atlas/Documents/Scratch/Image Format 2/all images/alltrue_mc_textures.png', lossy_tolerance=0, debug=True)
    
    print('decompress')
    decompress_img('output/compressed.txt', debug=True) # decompress the image