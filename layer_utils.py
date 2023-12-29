# all utilities for handling layer data streams

# the set of b94 chars
CHARS = '!"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~'

CHAR_LOOKUP = {char:i for i,char in enumerate(CHARS)}


def index_to_txt(indices):
    """Convert a number or list of numbers into a string of b94 chars"""
    if isinstance(indices, list) or isinstance(indices, tuple):
        return ''.join([CHARS[i] for i in indices])
    return CHARS[indices]


def char_index(char):
    """Get the index of a character"""
    return CHAR_LOOKUP[char]



def col_to_vol_index(colour: tuple, origin=(0,0,0), dimensions=(21,20,20)):
    """Return the index of the colour inside the volume, None if out of bounds"""

    relative_colour = (colour[0]-origin[0], colour[1]-origin[1], colour[2]-origin[2])
    
    if relative_colour[0] >= 0 and relative_colour[0] < dimensions[0] and \
        relative_colour[1] >= 0 and relative_colour[1] < dimensions[1] and \
        relative_colour[2] >= 0 and relative_colour[2] < dimensions[2]:
        
        return dimensions[1]*dimensions[2]*relative_colour[0] + dimensions[2]*relative_colour[1] + relative_colour[2]
    
    return None


def vol_index_to_col(index: int, origin=(0,0,0), dimensions=(21,20,20)):
    """Return the colour inside the volume, None if out of bounds"""
    if index is None: return None

    if index >= 0 or index < (dimensions[2]*dimensions[1]*dimensions[0]):
        relative_colour = (
            index // (dimensions[2]*dimensions[1]) % dimensions[0],
            (index // dimensions[2]) % dimensions[1],
            index % dimensions[2]
        )
        
        return (relative_colour[0]+origin[0], relative_colour[1]+origin[1], relative_colour[2]+origin[2])
    
    return None


def col_to_ftup(colour: tuple):
    """ftup, or 4-tuple uses a mixed base of (22,94,94,94) for representing a 3-tuple with bases (256,256,256)."""
    dec = 65536*colour[0] + 256*colour[1] + colour[2]
    return (
        dec // (94*94*94) % 22,
        (dec // (94*94)) % 94,
        (dec // 94) % 94,
        dec % 94
    )


def ftup_to_col(ftup: tuple):
    """ftup, or 4-tuple uses a mixed base of (22,94,94,94) for representing a 3-tuple with bases (256,256,256)."""
    dec = 830584*ftup[0] + 8836*ftup[1] + 94*ftup[2] + ftup[3]
    return (
        (dec // 65536) % 256,
        (dec // 256) % 256,
        dec % 256,
    )


def chunk_RLE(chunks, func_get_op_size, func_get_op_index):
    """Perform run-length encoding on a list of chunks. Replace chunks with repeat_op where applicable and return new list. Requires specifying functions to get operation size and index."""
    
    chunks_RLE = []
    buffer = [(None, ())]
    buffer_op = buffer[0][0] # cache the first operation name

    def _buffer_contents(buffer, buffer_op):
        buffer_size_chars = len(buffer) * (1 + func_get_op_size(buffer_op)) # (op, data)...
        repeat_size_chars = 3 + len(buffer) * func_get_op_size(buffer_op) # op, op, repeat, (data)...
    
        if buffer_size_chars > repeat_size_chars:
            cd = [func_get_op_index(buffer_op), len(buffer)] # op and repeat count
            for elem in buffer:
                cd.extend(elem[1]) # append data for each buffer element
            
            cd = (('repeat_op',0), tuple(cd))

            if repeat_size_chars != 1+len(cd[1]):
                raise Exception('mismatch in size measurements for RLE')

            return [cd] # buffer replaced by single repeat op
            
        else: return buffer
        

    for chunk in chunks:
        if chunk[0] == buffer_op and len(buffer) < 93: # match op in buffer
            buffer.append(chunk)
        else:
            if buffer_op is not None: chunks_RLE.extend(_buffer_contents(buffer, buffer_op))
            buffer = [chunk]
            buffer_op = buffer[0][0]

    # get anything still in the buffer at the end
    if buffer_op is not None: chunks_RLE.extend(_buffer_contents(buffer, buffer_op))
    
    return chunks_RLE


def analyse_chunks(chunks: list):
    """Analyse chunks to find occurences of operations for an understanding of compression effectiveness."""
    analysis = {}
    for chunk_name, chunk_data in chunks:
        if chunk_name in analysis:
            analysis[chunk_name] += 1
        else:
            analysis[chunk_name] = 1
    #print(analysis)

    ordered_analysis = [(f'{a[0]}{a[1]}',b) for a,b in analysis.items()]
    ordered_analysis.sort(key=lambda x: x[1], reverse=True)
    ordered_analysis_dict = {a:b for a,b in ordered_analysis}
    print(ordered_analysis_dict)
    return ordered_analysis_dict



if __name__ == '__main__':
    print(index_to_txt(0))
    print(char_index('!'))

    print(col_to_ftup((12,14,16)))

    print(vol_index_to_col(6666))
    