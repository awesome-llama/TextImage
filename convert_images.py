"""Get all images in the images folder, create text images of them and save in the nested converted folder. For demonstration purposes."""

import os
import image_io
from PIL import Image

def list_files(directory):
    # get all files in the directory
    files = os.listdir(directory)
    
    # filter out directories, leaving only files
    files = [file for file in files if os.path.isfile(os.path.join(directory, file))]
    
    return files

USE_A8_MAIN = ['submarine.png', 'tweed volcano.png'] # images that should use A8 for the main purpose

DEBUG = False

# Create txtimg
if True:
    DIRECTORY = 'images/'
    for file_name in list_files(DIRECTORY):
        print(file_name)
        img = Image.open(DIRECTORY+file_name)
        if file_name in USE_A8_MAIN:
            img = img.convert('L') # RGB to L

        txtimg = image_io.load_from_pillow_image(img, debug=DEBUG)
        print(txtimg)
        txtimg.save(DIRECTORY+'converted/'+file_name+'.txt')


# Convert back to image:
if True:
    DIRECTORY = 'images/converted/'
    for file_name in list_files(DIRECTORY):
        txtimg = image_io.load_from_text_file(DIRECTORY+file_name)
        print(txtimg)
        if 'alpha' in txtimg.layers:
            image = txtimg.to_pillow_image(alpha_layer='alpha', debug=DEBUG)
        else:
            image = txtimg.to_pillow_image(debug=DEBUG)
        
        image.save(DIRECTORY+'to_image/'+file_name+'.png', format='png')



