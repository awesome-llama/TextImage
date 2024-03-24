# all utilities for handling layer data streams

# the set of b94 chars
CHARS = '!"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~'

def indices_to_txt(indices: list):
    """Convert a list of indices into a string using the character table"""
    return ''.join([CHARS[i] for i in indices])
    

def txt_to_indices(text: str):
    """Convert string into a list of indices using the character table"""
    return [CHARS.index(char) for char in text]


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
    """ftup, or 4-tuple uses a mixed base of (21,94,94,94) for representing a 3-tuple with bases (256,256,256)."""
    dec = 65536*colour[0] + 256*colour[1] + colour[2]
    return (
        dec // (94*94*94) % 21,
        (dec // (94*94)) % 94,
        (dec // 94) % 94,
        dec % 94
    )


def ftup_to_col(ftup: tuple):
    """ftup, or 4-tuple uses a mixed base of (21,94,94,94) for representing a 3-tuple with bases (256,256,256)."""
    dec = 830584*ftup[0] + 8836*ftup[1] + 94*ftup[2] + ftup[3]
    return (
        (dec // 65536) % 256,
        (dec // 256) % 256,
        dec % 256,
    )


def chunk_RLE(chunks, chunk_class) -> list:
    """Perform run-length encoding on a list of chunks. Replace chunks with repeat_op where applicable and return new list. Requires specifying functions to get operation size and index."""

    output = [] # output list for all chunks

    buffer = []
    buffer_op = None

    def _buffer_contents(buffer):

        repeat_size_chars = 3 + len(buffer) * buffer[0].size # op, op, repeat, (data)...
        buffer_size_chars = len(buffer) * (1 + buffer[0].size) # (op, data)...
    
        if repeat_size_chars < buffer_size_chars: 

            cd = [buffer[0].index, len(buffer)] # op and repeat count
            for elem in buffer: 
                cd.extend(elem.data) # append data for each buffer element
            
            if repeat_size_chars != 1+len(cd):
                raise Exception('mismatch in size measurements for RLE')

            return [chunk_class('repeat_op', 0, list(cd))] 
            
        else: 
            return buffer # dump buffer unaltered
        

    for chunk in chunks:
        chunk: Chunk
        if ((buffer_op != chunk.name) or (len(buffer) >= 93)) and buffer_op != None:
            output.extend(_buffer_contents(buffer))
            buffer = []
        
        buffer_op = chunk.name
        buffer.append(chunk) # add current chunk to buffer

    if buffer_op is not None: # output anything still in the buffer at the end (excl. None)
        output.extend(_buffer_contents(buffer))

    return output


def analyse_chunks(chunks: list):
    """Analyse chunks to find occurences of operations for an understanding of compression effectiveness."""
    analysis = {}
    for chunk in chunks:
        chunk: Chunk
        if chunk.name in analysis:
            analysis[chunk.name] += 1
        else:
            analysis[chunk.name] = 1
    #print(analysis)

    ordered_analysis = [(f'{a[0]}{a[1]}',b) for a,b in analysis.items()]
    ordered_analysis.sort(key=lambda x: x[1], reverse=True)
    ordered_analysis_dict = {a:b for a,b in ordered_analysis}
    print(ordered_analysis_dict)
    return ordered_analysis_dict


class Chunk:
    """A single chunk containing operation name and data"""

    #OPERATIONS = [] # list with short_name, short_index, size
    @classmethod
    def set_operations(cls, operations):
        """Set the class OPERATIONS for use by all instances"""
        cls.OPERATIONS = operations
        cls.OPERATIONS_DICT = {(o[0],o[1]):i for i, o in enumerate(cls.OPERATIONS)}
    
    def __init__(self, short_name: str, short_name_index = 0, op_data = []):
        if short_name is None:
            self.name = (short_name, short_name_index)
            self.index = None
            self.size = None
            self.data = op_data
            return
        
        self.name = (short_name, short_name_index)
        
        if self.name not in self.OPERATIONS_DICT:
            raise Exception(f'Unrecognised operation name: {self.name}')

        self.index = self.OPERATIONS_DICT[self.name]

        self.size = self.OPERATIONS[self.index][2]

        if self.size is not None and len(op_data) != self.size:
            raise Exception(f'Data does not match expected length')
        
        self.data = op_data

    def __str__(self):
        return f'{self.__class__.__name__}({self.name[0]}{self.name[1]} {self.data})'
    
    def indices(self) -> list:
        """Get the chunk as a list of indices"""
        return [self.index] + self.data




if __name__ == '__main__':
    print(indices_to_txt([0]))
    print(txt_to_indices('Hello!'))

    print(col_to_ftup((12,14,16)))

    print(vol_index_to_col(6666))
    