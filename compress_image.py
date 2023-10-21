# Load an image and compress it into the text-based format.

from PIL import Image
import numpy as np
import layer_utils
import layer_RGB8
#import layer.A8

FILE_PATH = 'C:/Users/Atlas/Documents/Scratch/Image Format 2/image_format'



debug_dimensions = ()



def compress_img(image_name, path=FILE_PATH, lossy_tolerance=0):
    """Open an image and compress it. Save."""
    
    image = Image.open(path+image_name)
    image_array = np.asarray(image)
    image_array = np.flip(image_array, 0)
    image_array = np.reshape(image_array, (image.width*image.height, 3), 'A')
    global debug_dimensions
    debug_dimensions = image.size
    
    data_stream = layer_RGB8.compress(image_array, image.size, lossy_tolerance)

    file = data_stream
    #file = f"img,v:0.1,w:{image.width},h:{image.height},layers:1#len:{len(data_stream)}|{data_stream}"

    with open(f'{path}compressed.txt', 'w') as f:
        f.write(file)


##############

def decompress_img(image_name, path=FILE_PATH):
    
    with open(path+image_name) as f:
        image = f.read()

    
    dimensions = (256, 256)

    print(debug_dimensions)
    dimensions = debug_dimensions
    image_array = layer_RGB8.decompress(image, dimensions)

    # output the image:
    image_array = np.array(image_array, np.uint8)
    image_array = np.flip(image_array.reshape(dimensions[1], dimensions[0], 3), 0)

    image = Image.fromarray(obj=image_array, mode='RGB')
    image.show()
    image.save(path + 'decompressed_test.png')





if __name__ == '__main__':

    #compress_img('images/beach_hq.png', lossy_tolerance=0)
    compress_img('images/beach.png')
    #compress_img('images/test.png')
    #compress_img('images/grad.png', lossy_tolerance=20)
    #compress_img('images/region_landing_pad_night.png', lossy_tolerance=20)
    #compress_img('images/boat.png', lossy_tolerance=1)
    #compress_img('images/testcard.png')
    #compress_img('blender google fail.png', 'C:/Users/Atlas/Documents/HDR/')
    #compress_img('images/breakable_atlas.png')
    #compress_img('images/nprguy.jpg')
    #compress_img('images/rgb8.png')
    #compress_img('images/region_pod.png')
    #compress_img('images/rhodes noisy.png')
    #compress_img('images/alltrue_mc_textures.png')
    #compress_img('images/lvl3.png')
    
    decompress_img('compressed.txt')