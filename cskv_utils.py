# Comma-separated key-value pairs... CSKV
# https://awesome-llama.github.io/articles/my-save-code-format

# utilities for reading/writing


def CSKV_write(data:dict, magic_number:str=None, append_comma=True, include_list_length=True) -> str:
    """Write a CSKV string. `append_comma` ensures the final item ends with a comma. `include_list_length` inserts the number of list items immediately after the key name."""

    def valid_string(string:str):
        """Raise exception if string contains invalid character, otherwise return string"""
        string = str(string)
        if ',' in string or ':' in string:
            raise Exception(f'{string} contains an invalid character')
        return string
    
    cskv = []
    if magic_number is not None:
        cskv.append(valid_string(magic_number))

    for k,v in data.items():
        if isinstance(v, list) or isinstance(v, tuple) or isinstance(v, set):
            if include_list_length:
                v = str(len(v)) + ',' + ','.join(map(valid_string, v))
            else:
                v = ','.join(map(valid_string, v))
        else:
            v = valid_string(v)

        cskv.append(f'{valid_string(k)}:{v}')

    cskv = ','.join(cskv)
    if append_comma: cskv = cskv + ',' # include end comma
    
    return cskv


def CSKV_read(data:str, remove_magic_number=False, remove_end_comma=True, remove_list_length=False) -> dict: 
    """Read a CSKV string and return a dictionary. Params make assumptions on the written data as the format does not specify it. See `CSKV_write` for their purpose."""
    
    items = str(data).split(',')
    if remove_magic_number: items.pop(0)
    if remove_end_comma: items.pop(-1) # remove empty string at the end
    
    output = {}
    current_key = None # empty string as key (used by magic number)

    for item in items:
        if ':' in item:
            if len(output.get(current_key, [])) == 1:
                output[current_key] = output[current_key][0] # remove list for single items
            
            k, *v = item.split(':')
            
            if len(v) > 1: 
                raise Exception('unexpected colon')

            output[k] = [] if remove_list_length else v
            current_key = k
        
        elif current_key is None:
            output[None] = item
        
        else:
            output[current_key].append(item)

    return output



if __name__ == '__main__':
    # Tests
    
    # numbers
    temp = {'a':1,'b':2,'c':3,'d':4}
    print(temp)
    temp = CSKV_write(temp)
    print(temp)
    print(CSKV_read(temp))
    print('')

    # lists
    temp = {'a':[555],'b':[100, 'test0'],'c':[],'d':['test2', 'test3']}
    print(temp)
    temp = CSKV_write(temp)
    print(temp)
    print(CSKV_read(temp))
    print('')

    # magic number
    temp = {'a':'apple','b':'banana','c':[]}
    print(temp)
    temp = CSKV_write(temp, magic_number='MAGIC NUM')
    print(temp)
    print(CSKV_read(temp))
    print('')