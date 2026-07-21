# Quickly preview a TextImage from the system clipboard

import image_io
import pyperclip

pasted = pyperclip.paste()
if pasted[0:6] == 'txtimg':
    txtimg = image_io.load_from_text(pasted)
    img = txtimg.to_pillow_image(require_alpha=False)
    try:
        img.save('output/clipboard.png')
    except Exception as e:
        print(e)
    img.show()
else:
    print('no TextImage detected in clipboard')