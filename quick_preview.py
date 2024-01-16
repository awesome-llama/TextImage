# Quickly preview a TextImage from the system clipboard

import image_io
from PIL import Image
import pyperclip

pasted = pyperclip.paste()
if pasted[0:6] == 'txtimg':
    txtimg = image_io.load_from_text(pasted)
    img = txtimg.to_pillow_image(require_alpha=False)
    img.show()
else:
    print('no TextImage detected')