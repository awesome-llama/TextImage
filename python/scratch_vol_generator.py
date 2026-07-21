# Used to generate volume data readable by Scratch (import into a list from text file).
# Simply run the script.

import layer_RGB8

output_vols = []
for i, vol in enumerate(layer_RGB8.VOLUMES):
    output_vols.append(f'vol{i}\n') # long_name
    output_vols.append(f'{vol[0][0]}\n') # x0
    output_vols.append(f'{vol[0][1]}\n') # y0
    output_vols.append(f'{vol[0][2]}\n') # z0
    output_vols.append(f'{vol[1][0]}\n') # x1
    output_vols.append(f'{vol[1][1]}\n') # y1
    output_vols.append(f'{vol[1][2]}\n') # z1
    output_vols.append(f'{vol[2]}\n') # size

with open('output/RGB8_vols_scratch.txt', 'w') as f:
    f.writelines(output_vols)