# Generic 1 channel 8-bit
# WIP

import layer_utils as lu

def compress(image_array:list, dimensions:tuple, lossy_tolerance=0):
    """Compress generic 8 bit per channel data stream (e.g. alpha)"""

    chunks = data_stream_to_chunks(image_array, dimensions, lossy_tolerance) # get a list of chunks
    chunks = chunk_RLE(chunks) # second pass for RLE


    # final pass to convert chunks into strings:
    string_chunks = []
    for chunk_name, chunk_data in chunks:
        string_chunks.append(lu.index_to_txt(get_op_index(chunk_name)) + lu.index_to_txt(chunk_data))


    return ''.join(string_chunks)