"""Get all images in the images folder, create text images of them and save in the nested converted folder. For demonstration purposes."""

import os
import image_io


def list_files(directory):
    # get all files in the directory
    files = os.listdir(directory)
    
    # filter out directories, leaving only files
    files = [file for file in files if os.path.isfile(os.path.join(directory, file))]
    
    return files


DIRECTORY = 'images/'

for file_name in list_files(DIRECTORY):
    txtimg = image_io.load_from_image_file(DIRECTORY+file_name, debug=False)
    txtimg.save(DIRECTORY+'converted/'+file_name+'.txt')