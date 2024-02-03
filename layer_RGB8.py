# RGB 8-bit per channel

import json
import layer_utils as lu

DEFAULT_VAL = (0,0,0)
VOLUMES = [[(-2,-1,-1),(5,4,4),1],[(-2,3,-1),(5,4,4),1],[(-2,-5,-1),(5,4,4),1],[(-2,-5,2),(5,4,4),1],[(-2,3,2),(5,4,4),1],[(-2,-1,2),(5,4,4),1],[(-2,-5,-5),(5,4,4),1],[(-2,3,-5),(5,4,4),1],[(-2,-1,-5),(5,4,4),1],[(3,-1,-5),(5,4,4),1],[(3,3,-5),(5,4,4),1],[(3,-5,-5),(5,4,4),1],[(3,-1,2),(5,4,4),1],[(3,3,2),(5,4,4),1],[(3,-5,2),(5,4,4),1],[(3,-5,-1),(5,4,4),1],[(3,3,-1),(5,4,4),1],[(3,-1,-1),(5,4,4),1],[(8,-1,-1),(5,4,4),1],[(8,3,-1),(5,4,4),1],[(8,-5,-1),(5,4,4),1],[(8,-5,2),(5,4,4),1],[(8,3,2),(5,4,4),1],[(8,-1,2),(5,4,4),1],[(8,-5,-5),(5,4,4),1],[(8,3,-5),(5,4,4),1],[(8,-1,-5),(5,4,4),1],[(-7,-1,-5),(5,4,4),1],[(-7,3,-5),(5,4,4),1],[(-7,-5,-5),(5,4,4),1],[(-7,-1,2),(5,4,4),1],[(-7,3,2),(5,4,4),1],[(-7,-5,2),(5,4,4),1],[(-7,-5,-1),(5,4,4),1],[(-7,3,-1),(5,4,4),1],[(-7,-1,-1),(5,4,4),1],[(-12,-1,-1),(5,4,4),1],[(-12,3,-1),(5,4,4),1],[(-12,-5,-1),(5,4,4),1],[(-12,-5,2),(5,4,4),1],[(-12,3,2),(5,4,4),1],[(-12,-1,2),(5,4,4),1],[(-12,-5,-5),(5,4,4),1],[(-12,3,-5),(5,4,4),1],[(-12,-1,-5),(5,4,4),1],[(-10,7,-9),(21,20,20),2],[(-10,-25,-9),(21,20,20),2],[(-10,-9,7),(21,20,20),2],[(-10,-9,-24),(21,20,20),2],[(11,-9,-8),(21,20,20),2],[(-31,-9,-8),(21,20,20),2],[(32,-9,-8),(21,20,20),2],[(-52,-9,-8),(21,20,20),2],[(53,-9,-8),(21,20,20),2],[(-73,-9,-8),(21,20,20),2],[(11,-9,-24),(21,20,20),2],[(11,-9,7),(21,20,20),2],[(11,-25,-9),(21,20,20),2],[(11,7,-9),(21,20,20),2],[(-31,7,-9),(21,20,20),2],[(-31,-25,-9),(21,20,20),2],[(-31,-9,7),(21,20,20),2],[(-10,11,-29),(21,20,20),2]]

OPERATIONS = [["raw",0,3],["raw",1,3],["raw",2,3],["raw",3,3],["raw",4,3],["raw",5,3],["raw",6,3],["raw",7,3],["raw",8,3],["raw",9,3],["raw",10,3],["raw",11,3],["raw",12,3],["raw",13,3],["raw",14,3],["raw",15,3],["raw",16,3],["raw",17,3],["raw",18,3],["raw",19,3],["raw",20,3],["unassigned",3,0],["copy_prev",0,0],["copy_vert_fwd",0,0],["copy_vert",0,0],["copy_vert_back",0,0],["hash_table",0,1],["repeat_op",0,None],["vol",0,1],["vol",1,1],["vol",2,1],["vol",3,1],["vol",4,1],["vol",5,1],["vol",6,1],["vol",7,1],["vol",8,1],["vol",9,1],["vol",10,1],["vol",11,1],["vol",12,1],["vol",13,1],["vol",14,1],["vol",15,1],["vol",16,1],["vol",17,1],["vol",18,1],["vol",19,1],["vol",20,1],["vol",21,1],["vol",22,1],["vol",23,1],["vol",24,1],["vol",25,1],["vol",26,1],["vol",27,1],["vol",28,1],["vol",29,1],["vol",30,1],["vol",31,1],["vol",32,1],["vol",33,1],["vol",34,1],["vol",35,1],["vol",36,1],["vol",37,1],["vol",38,1],["vol",39,1],["vol",40,1],["vol",41,1],["vol",42,1],["vol",43,1],["vol",44,1],["vol",45,2],["vol",46,2],["vol",47,2],["vol",48,2],["vol",49,2],["vol",50,2],["vol",51,2],["vol",52,2],["vol",53,2],["vol",54,2],["vol",55,2],["vol",56,2],["vol",57,2],["vol",58,2],["vol",59,2],["vol",60,2],["vol",61,2],["vol",62,2],["unassigned",0,0],["unassigned",1,0],["unassigned",2,0]]

class ChunkRGB8(lu.Chunk):
    pass

ChunkRGB8.set_operations(OPERATIONS)

OP_INDICES = {(op_data[0],op_data[1]):(i,op_data[2]) for i, op_data in enumerate(OPERATIONS)}


def get_op_index(op_name: tuple):
    """Return the op index from a 2-tuple name"""
    return OP_INDICES[op_name][0]

def get_op_size(op_name: tuple):
    """Return the op size from a 2-tuple name"""
    return OP_INDICES[op_name][1]

def get_op_name(index: int):
    """Return the 2-tuple op name of an index"""
    return (OPERATIONS[index][0], OPERATIONS[index][1])


def RGB_to_YUV(rgb: tuple):
    """R'G'B' to Y'UV (g, b-g, r-g)"""
    return ((rgb[1], rgb[2]-rgb[1], rgb[0]-rgb[1]))

def YUV_to_RGB(yuv: tuple):
    """Y'UV to R'G'B' (g, b-g, r-g)"""
    return ((yuv[2]+yuv[0], yuv[0], yuv[1]+yuv[0]))

def is_similar(a: tuple, b: tuple, tol=0):
    """Check if two RGB colours are similar based on a tolerance value."""
    if tol == 0: return a == b
    tol /= 255
    G = 0.45 # gamma
    a2 = ((a[0]/255)**G, (a[1]/255)**G, (a[2]/255)**G)
    b2 = ((b[0]/255)**G, (b[1]/255)**G, (b[2]/255)**G)
    return (abs(a2[0]-b2[0])<=tol) and (abs(a2[1]-b2[1])<=tol) and (abs(a2[2]-b2[2])<=tol)

def similar_in_list(src_list, find, tol=0):
    """Check if an item exists in a source list and return index if so."""
    for i, elem in enumerate(src_list):
        if is_similar(elem, find, tol): return i
    return None

def limit_RGB(col:tuple):
    """Ensure the colour is a 3-tuple of ints in the range 0-255"""
    r = max(0, min(255, int(col[0])))
    g = max(0, min(255, int(col[1])))
    b = max(0, min(255, int(col[2])))
    return (r, g, b)


def data_stream_to_chunks(image_array, dimensions:tuple, lossy_tolerance=0):
    def _add_colour(colour: tuple):
        col_prev.insert(0, colour)
        col_prev.pop(-1)
        col_table[(colour[0]*3 + colour[1]*5 + colour[2]*7) % 94] = colour # hashed index

    col_prev = [DEFAULT_VAL for _ in range(dimensions[0] + 2)]
    col_table = [DEFAULT_VAL for _ in range(len(lu.CHARS))]
    chunks = [] 
    
    for col in image_array:
        col = limit_RGB(col)  

        # find chunk to encode with:
        if is_similar(col, (c:=col_prev[0]), lossy_tolerance):
            chunks.append(ChunkRGB8('copy_prev'))
            _add_colour(c)
            continue

        if is_similar(col, (c:=col_prev[dimensions[0]-2]), lossy_tolerance):
            chunks.append(ChunkRGB8('copy_vert_fwd'))
            _add_colour(c)
            continue
        
        if is_similar(col, (c:=col_prev[dimensions[0]-1]), lossy_tolerance):
            chunks.append(ChunkRGB8('copy_vert'))
            _add_colour(c)
            continue

        if is_similar(col, (c:=col_prev[dimensions[0]+0]), lossy_tolerance):
            chunks.append(ChunkRGB8('copy_vert_back'))
            _add_colour(c)
            continue
        
        if (si := similar_in_list(col_table, col, lossy_tolerance)) is not None:
            chunks.append(ChunkRGB8('hash_table', 0, [si]))
            _add_colour(col_table[si])
            continue
        
        in_volume = False
        col_diff = (col[0]-col_prev[0][0], col[1]-col_prev[0][1], col[2]-col_prev[0][2])
        YUV_diff = RGB_to_YUV(col_diff)
        for i, volume in enumerate(VOLUMES):
            if (index := lu.col_to_vol_index(YUV_diff, volume[0], volume[1])) is not None:

                if volume[2] == 1:
                    chunks.append(ChunkRGB8('vol', i, [index]))
                elif volume[2] == 2:
                    chunks.append(ChunkRGB8('vol', i, [index//94, index%94]))
                else:
                    raise Exception('Volume size disallowed (waste of space)')
                
                _add_colour(col)
                in_volume = True
                break
        
        # raw pixel, do not compress
        if not in_volume:
            ftup = lu.col_to_ftup(col)
            chunks.append(ChunkRGB8('raw', ftup[0], list(ftup[1:])))
            #chunks.append((('raw', ftup[0]), tuple(ftup[1:])))
            _add_colour(col)

    return chunks



def compress(image_array:list, dimensions:tuple, lossy_tolerance=0, RLE=True, debug=False):
    """Compress RGB 8 bit per channel data stream"""

    chunks = data_stream_to_chunks(image_array, dimensions, lossy_tolerance) # get a list of chunks
    if RLE: chunks = lu.chunk_RLE(chunks, ChunkRGB8) # second pass for RLE

    if debug:
        lu.analyse_chunks(chunks)
        with open('debug/RGB8_compress_chunks.txt', 'w') as f:
            f.writelines(str(c)+'\n' for c in chunks)

    # final pass to convert chunks into strings:
    string_chunks = []
    for chunk in chunks:
        chunk: ChunkRGB8
        string_chunks.append(lu.index_to_txt(chunk.indices()))

    if debug:
        size_pixels = dimensions[0]*dimensions[1]
        size_compressed = len(''.join(string_chunks))
        print('b64:' , 4*size_pixels, '-> compressed:' , size_compressed)
        print(f'{round(100*size_compressed/(4*size_pixels), 2)}% of original')

    return ''.join(string_chunks)





def decompress(stream:str, dimensions:tuple, debug=False):
    """Decompress RGB 8 bit per channel data stream"""

    def _add_colour(colour: tuple, c):
        #image_array.append((c.size*63,c.size*63,c.size*63)) # preview efficiency
        image_array.append(colour)
        col_prev.insert(0, colour)
        col_prev.pop(-1)
        col_table[(colour[0]*3 + colour[1]*5 + colour[2]*7) % 94] = colour

    def _process_chunk(chunk):
        match chunk.name[0]:
            case 'raw':
                _add_colour(lu.ftup_to_col((chunk.name[1], chunk.data[0], chunk.data[1], chunk.data[2])), chunk.name)

            case 'copy_prev':
                _add_colour(col_prev[0], chunk)

            case 'copy_vert_fwd':
                _add_colour(col_prev[dimensions[0] - 2], chunk)

            case 'copy_vert':
                _add_colour(col_prev[dimensions[0] - 1], chunk)

            case 'copy_vert_back':
                _add_colour(col_prev[dimensions[0] + 0], chunk)

            case 'hash_table':
                _add_colour(col_table[chunk.data[0]], chunk)
            
            case 'vol':
                if chunk.size == 1:
                    index = chunk.data[0]
                elif chunk.size == 2:
                    index = 94*chunk.data[0] + chunk.data[1]
                
                YUV_diff = lu.vol_index_to_col(index, VOLUMES[chunk.name[1]][0], VOLUMES[chunk.name[1]][1])
                col_diff = YUV_to_RGB(YUV_diff)
                _add_colour((col_prev[0][0]+col_diff[0], col_prev[0][1]+col_diff[1], col_prev[0][2]+col_diff[2]), chunk)

            case _:
                raise Exception(f'Chunk name {op_name} unknown')


    # iterate over entire image to get intermediate format:
    chunks = []
    i = 0
    while i < len(stream):
        
        op_name = get_op_name(lu.char_index(stream[i]))

        if op_name[0] == 'repeat_op':
            repeat_op_name = get_op_name(lu.char_index(stream[i+1])) # the op that should be repeated
            repeat = 2 + lu.char_index(stream[i+2]) * get_op_size(repeat_op_name)
        else:
            repeat = get_op_size(op_name)
        
        
        op_data = []
        for _ in range(repeat): # add op data
            i += 1
            op_data.append(lu.char_index(stream[i]))

        chunks.append(ChunkRGB8(op_name[0], op_name[1], op_data))
        i += 1

    if debug:
        with open('debug/RGB8_decompress_chunks.txt', 'w') as f:
            f.writelines(str(c)+'\n' for c in chunks)
    
    # read intermediate and emit pixels into output list
    image_array = []
    col_prev = [DEFAULT_VAL for _ in range(dimensions[0] + 2)]
    col_table = [DEFAULT_VAL for _ in range(len(lu.CHARS))]
    
    for chunk in chunks:
        chunk: ChunkRGB8
        if chunk.name[0] == 'repeat_op':
            op_name = get_op_name(chunk.data[0])
            op_size = get_op_size(op_name)
            repeat = chunk.data[1]

            for i in range(repeat):
                i = i*op_size+2
                _process_chunk(ChunkRGB8(op_name[0], op_name[1], chunk.data[i:i+op_size]))
        
        else: _process_chunk(chunk)

    if debug:
        with open('debug/RGB8_decompress_image_array.json', 'w') as f:
            f.write(json.dumps(image_array, indent=2))

    return image_array
    


if __name__ == '__main__':
    print(YUV_to_RGB((16,13,6)))

