# Generic 1 channel 8-bit






def compress(image_array:list, dimensions:tuple, lossy_tolerance=0):
    """Compress generic 8 bit per channel data stream (e.g. alpha)"""


def compress(image_array:list, dimensions:tuple, lossy_tolerance=0):
    """Compress RGB 8 bit per channel data stream"""

    # get a list of chunks:
    chunks = data_stream_to_chunks(image_array, dimensions, lossy_tolerance)

    if True:
        analysis = {}
        for chunk_name, chunk_data in chunks:
            if chunk_name in analysis:
                analysis[chunk_name] += 1
            else:
                analysis[chunk_name] = 1
        print(analysis)
            
    # second pass for RLE
    chunks = chunk_RLE(chunks)


    # final pass to convert chunks into strings:
    string_chunks = []
    for chunk_name, chunk_data in chunks:
        string_chunks.append(lu.index_to_txt(get_op_index(chunk_name)) + lu.index_to_txt(chunk_data))

    if True:
        size_pixels = dimensions[0]*dimensions[1]
        size_compressed = len(''.join(string_chunks))
        print('b64:' , 4*size_pixels, '-> compressed:' , size_compressed)
        print(f'{round(100*size_compressed/(4*size_pixels), 2)}% of original')

    return ''.join(string_chunks)