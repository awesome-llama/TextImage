# Generic 1 channel 8-bit (known as "A")

import json
import layer_utils as lu

DEFAULT_VAL = 0
OPERATIONS = [["raw",0,1],["raw",1,1],["raw",2,1],["copy_prev",0,0],["copy_vert_fwd",0,0],["copy_vert",0,0],["copy_vert_back",0,0],["repeat_op",0,3],["inc",0,0],["inc",1,0],["inc",2,0],["inc",3,0],["inc",4,0],["inc",5,0],["inc",6,0],["inc",7,0],["inc",8,0],["inc",9,0],["inc",10,0],["inc",11,0],["inc",12,0],["inc",13,0],["inc",14,0],["inc",15,0],["inc",16,0],["inc",17,0],["inc",18,0],["inc",19,0],["inc",20,0],["inc",21,0],["inc",22,0],["inc",23,0],["inc",24,0],["inc",25,0],["inc",26,0],["inc",27,0],["inc",28,0],["inc",29,0],["inc",30,0],["inc",31,0],["inc",32,0],["inc",33,0],["inc",34,0],["inc",35,0],["inc",36,0],["inc",37,0],["inc",38,0],["inc",39,0],["inc",40,0],["inc",41,0],["inc",42,0],["dec",0,0],["dec",1,0],["dec",2,0],["dec",3,0],["dec",4,0],["dec",5,0],["dec",6,0],["dec",7,0],["dec",8,0],["dec",9,0],["dec",10,0],["dec",11,0],["dec",12,0],["dec",13,0],["dec",14,0],["dec",15,0],["dec",16,0],["dec",17,0],["dec",18,0],["dec",19,0],["dec",20,0],["dec",21,0],["dec",22,0],["dec",23,0],["dec",24,0],["dec",25,0],["dec",26,0],["dec",27,0],["dec",28,0],["dec",29,0],["dec",30,0],["dec",31,0],["dec",32,0],["dec",33,0],["dec",34,0],["dec",35,0],["dec",36,0],["dec",37,0],["dec",38,0],["dec",39,0],["dec",40,0],["dec",41,0],["dec",42,0]]

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


def is_similar(a, b, tol=0):
    """Check if two numbers are similar based on a tolerance value."""
    return abs(a-b) <= tol

def limit_A(a):
    """Ensure generic value is an int in the range 0-255."""
    return max(0, min(255, int(a)))


def data_stream_to_chunks(image_array, dimensions:tuple, lossy_tolerance=0):
    def _add_val(colour: tuple):
        col_prev.insert(0, colour)
        col_prev.pop(-1)

    col_prev = [DEFAULT_VAL for _ in range(dimensions[0] + 2)]
    chunks = [] 
    
    for col in image_array:
        col = limit_A(col)

        # find chunk to encode with:
        if is_similar(col, (c:=col_prev[0]), lossy_tolerance):
            chunks.append((('copy_prev',0), ()))
            _add_val(c)
            continue

        if is_similar(col, (c:=col_prev[dimensions[0]-2]), lossy_tolerance):
            chunks.append((('copy_vert_fwd',0), ()))
            _add_val(c)
            continue
        
        if is_similar(col, (c:=col_prev[dimensions[0]-1]), lossy_tolerance):
            chunks.append((('copy_vert',0), ()))
            _add_val(c)
            continue

        if is_similar(col, (c:=col_prev[dimensions[0]]), lossy_tolerance):
            chunks.append((('copy_vert_back',0), ()))
            _add_val(c)
            continue
        
        diff = (((col-col_prev[0])+128)%256-128)
        
        if 0 < diff < 42:
            chunks.append((('inc',diff-1), ()))
            _add_val(col)
            continue
        
        if -42 < diff < 0:
            chunks.append((('dec',-1-diff), ()))
            _add_val(col)
            continue
        
        # raw pixel, do not compress
        if col >= 94*2:
            chunks.append((('raw', 2), (col-(94*2),)))
        elif col >= 94:
            chunks.append((('raw', 1), (col-(94),)))
        else:
            chunks.append((('raw', 0), (col,)))
        _add_val(col)

    return chunks



def compress(image_array:list, dimensions:tuple, lossy_tolerance=0, RLE=True, debug=False):
    """Compress generic 8 bit per channel data stream (e.g. alpha)"""

    chunks = data_stream_to_chunks(image_array, dimensions, lossy_tolerance) # get a list of chunks
    #if RLE: chunks = chunk_RLE(chunks) # second pass for RLE

    if debug:
        lu.analyse_chunks(chunks)
        with open('debug/A8_compress_chunks.json', 'w') as f:
            f.write(json.dumps(chunks, indent=2))

    # final pass to convert chunks into strings:
    string_chunks = []
    for chunk_name, chunk_data in chunks:
        string_chunks.append(lu.index_to_txt(get_op_index(chunk_name)) + lu.index_to_txt(chunk_data))

    if debug:
        size_pixels = dimensions[0]*dimensions[1]
        size_compressed = len(''.join(string_chunks))
        print('b64:' , 2*size_pixels, '-> compressed:' , size_compressed)
        print(f'{round(100*size_compressed/(2*size_pixels), 2)}% of original')
    
    return ''.join(string_chunks)



def decompress(stream:str, dimensions:tuple, debug=False):
    """Decompress generic 8 bit per channel data stream (e.g. alpha)"""

    def _add_val(colour, op_name):
        image_array.append(colour)
        col_prev.insert(0, colour)
        col_prev.pop(-1)
    
    def _process_op(op_name, op_data):
        match op_name[0]:
            case 'raw':
                _add_val((op_name[1]*94 + op_data[0]), op_name)

            case 'copy_prev':
                _add_val(col_prev[0], op_name)

            case 'copy_vert_fwd':
                _add_val(col_prev[dimensions[0] - 2], op_name)

            case 'copy_vert':
                _add_val(col_prev[dimensions[0] - 1], op_name)

            case 'copy_vert_back':
                _add_val(col_prev[dimensions[0] + 0], op_name)

            case 'inc':
                c = (col_prev[0] + op_name[1] + 1)%256
                _add_val(c, op_name)
            
            case 'dec':
                c = (col_prev[0] - (op_name[1]+1))%256
                _add_val(c, op_name)

            case _:
                raise Exception(f'Chunk name {op_name} unknown')

    # iterate over entire image to get intermediate format:
    chunks = []
    i = 0
    while i < len(stream):
        if stream[i] == ' ': # ignore spaces
            i += 1
            continue
        
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

        chunks.append((op_name, op_data))
        i += 1

    if debug:
        with open('debug/A8_decompress_chunks.json', 'w') as f:
            f.write(json.dumps(chunks, indent=2))
    
    # read intermediate and emit pixels into output list
    image_array = []
    col_prev = [DEFAULT_VAL for _ in range(dimensions[0] + 2)]
    
    for chunk_name, chunk_data in chunks:
        if chunk_name == ('repeat_op',0):
            op_name = get_op_name(chunk_data[0])
            op_size = get_op_size(op_name)
            repeat = chunk_data[1]

            for i in range(repeat):
                i = i*op_size+2
                _process_op(op_name, chunk_data[i:i+op_size])
        
        else: _process_op(chunk_name, chunk_data)

    if debug:
        with open('debug/A8_decompress_image_array.json', 'w') as f:
            f.write(json.dumps(image_array, indent=2))

    return image_array




if __name__ == '__main__':
    #img_data, img_dimensions = [128, 1, 19, 20], (2,2)
    #img_data, img_dimensions = [0,25,122,256,0,122], (3,2)
    img_data, img_dimensions = [2,3,0,5,10,250,99,45,44,0], (5, 2)
    print(img_data, img_dimensions)
    datastream = compress(img_data, img_dimensions, RLE=False, debug=True)
    print(datastream)
    decompressed_img = decompress(datastream, img_dimensions, debug=True)
    print(decompressed_img, img_data == decompressed_img)


