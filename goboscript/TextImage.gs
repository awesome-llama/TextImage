# https://github.com/awesome-llama/TextImage/

hide;

costumes 
"costumes/TextImage/icon.svg" as "icon",
"costumes/blank.svg" as "@ascii/";


list layers;
list image_buffer;
list data_stream_list;
list source_data_stream_list;
list hash_table; # hash operation

list volumes "data/TextImage_volumes.txt"; # similarity volume data
list op_sizes "data/TextImage_operation_sizes.txt"; # number of characters for each operation, for RLE


# The following lists and variables are used as inputs/outputs:
list TI_1_r;
list TI_2_g;
list TI_3_b;
list TI_4_a;
list TI_header;
var TextImage_file;
var TI_image_size_x;
var TI_image_size_y;


################################
#         Example usage        #
################################


onkey "i" {
    ask "paste image";
    read_TextImage answer();
    debug_draw_image 0, 0, 1;
}


onkey "e" {
    write_TextImage;
    log TextImage_file;
}



################################
#        TextImage read        #
################################

# Read a TextImage file.
proc read_TextImage TextImage_file {
    clear_all_shared_data;
    add "" to TI_header;
    delete layers;
    local str = "";
    i = 1;
    repeat (length $TextImage_file) {
        if ($TextImage_file[i] == ",") {
            add str to TI_header;
            str = "";
        } elif ($TextImage_file[i] == ":") {
            add ("!" & str) to TI_header;
            str = "";
        } elif ($TextImage_file[i] == "|") {
            add str to TI_header;
            str = "";
            if (TI_header[2] == "txtimg") {
                if (TI_header[1+("!v" in TI_header)] == 0) {
                    # read header
                    TI_image_size_x = floor(TI_header[1+("!x" in TI_header)]);
                    TI_image_size_y = floor(TI_header[1+("!y" in TI_header)]);
                    # convert header and data streams into a list of layers
                    i++;
                    j = (1+("!p" in TI_header));
                    repeat (TI_header[j]/4) {
                        # sets of 6 items... !purpose, purpose, type, version, length, index_start
                        add ("!" & TI_header[j+1]) to layers;
                        add TI_header[j+1] to layers;
                        add TI_header[j+2] to layers;
                        add TI_header[j+3] to layers;
                        add TI_header[j+4] to layers;
                        add i to layers;
                        i += TI_header[j+4];
                        j += 4;
                    }
                    # now load data streams based on purpose
                    # this part is for the user to modify for their use case
                    read_layer_from_TextImage $TextImage_file, "main", "RGB";
                    read_layer_from_TextImage $TextImage_file, "alpha", "A";
                    delete layers;
                    data_stream = "";
                } else {
                    error "unknown version";
                }
            } else {
                error "invalid magic number";
            }
            stop_this_script;
        } else {
            str &= $TextImage_file[i];
        }
        i++;
    }
    error "datastream not found";
}



# Takes the layer data (sets of 5 items) and decodes them.
# Decoded result stored in the temporary buffer is then outputted into desired lists.
# If the desired lists are something else, you may want to modify the script(s).
proc read_layer_from_TextImage TextImage_file, purpose, buffer_target_list {
    i = (("!" & $purpose) in layers);
    if (i > 0) {
        # get data stream from TextImage
        data_stream = "";
        j = layers[i+5];
        repeat layers[i+4] {
            data_stream = (data_stream & $TextImage_file[j]);
            j++;
        }
        # process data stream
        if ((layers[i+2] == "RGB8") and (layers[i+3] == 0)) {
            _decompress_RGB8 data_stream, TI_image_size_x;
            if ($buffer_target_list == "RGB") {
                _rgb_unpack_from_image_buffer 3, 1, 2, 3;
            } elif ($buffer_target_list == "A") {
                _a_unpack_from_image_buffer 3, 2;
            } else {
                error "buffer target list does not exist";
            }
            delete image_buffer;
            stop_this_script;
        } else {
            if ((layers[i+2] == "A8") and (layers[i+3] == 0)) {
                _decompress_A8 data_stream, TI_image_size_x;
                if ($buffer_target_list == "RGB") {
                    _rgb_unpack_from_image_buffer 1, 1, 1, 1;
                } elif ($buffer_target_list == "A") {
                    _a_unpack_from_image_buffer 1, 1;
                } else {
                    error "buffer target list does not exist";
                }
                delete image_buffer;
                stop_this_script;
            } else {
                warn "unknown data stream type and/or version";
            }
        }
    }
    # defaults
    if ($buffer_target_list == "RGB") {
        _rgb_unpack_from_image_buffer 1, 1, 1, 1;
    } else {
        if ($buffer_target_list == "A") {
            _a_unpack_from_image_buffer 1, 1;
        }
    }
}


proc _rgb_unpack_from_image_buffer step, ri, gi, bi {
    delete TI_1_r;
    delete TI_2_g;
    delete TI_3_b;
    i = 0;
    repeat (TI_image_size_x * TI_image_size_y) {
        add round(image_buffer[i+$ri]) to TI_1_r;
        add round(image_buffer[i+$gi]) to TI_2_g;
        add round(image_buffer[i+$bi]) to TI_3_b;
        i += $step;
    }
}


proc _a_unpack_from_image_buffer step, i {
    # REQUIRES (image size x) (image size y) [4 a]
    delete TI_4_a;
    i = 0;
    repeat (TI_image_size_x * TI_image_size_y) {
        if (image_buffer[i+$i] == "") {
            add 255 to TI_4_a;
        } else {
            add round(image_buffer[i+$i]) to TI_4_a;
        }
        i += $step;
    }
}


proc _decompress_RGB8 data_stream, width {
    _get_character_codes_from_data_stream $data_stream;
    delete image_buffer;
    delete hash_table;
    repeat 94 { add 0 to hash_table; }
    
    _repeat = 0; # counter for how many times an op should be run (RLE)
    op_size = 0;
    i = 1;
    until (i > (length data_stream_list)) {
        if (_repeat > 0) {
            # RLE uses the previously found op and decrements repeat
            _repeat += -1;
        } else {
            op_index = data_stream_list[i];
        }

        if (op_index < 21) {
            # raw
            dec = ((830584*op_index)+((8836*data_stream_list[i+1])+((94*data_stream_list[i+2])+data_stream_list[i+3])));
            _add_RGB floor((dec/65536)), (floor((dec/256))%256), (dec % 256);
            op_size = 3;
        } elif (op_index == 22) {
            # prev
            _add_RGB round(image_buffer[(length image_buffer)-2]), round(image_buffer[(length image_buffer)-1]), round(image_buffer["last"]);
            op_size = 0;
        } elif (op_index < 26) {
            # copy vert fwd/mid/back
            _add_RGB round(image_buffer[(3*((((length image_buffer)/3)-$width) + (25-op_index))) - 2]), round(image_buffer[((3*((((length image_buffer)/3)-$width)+(25-op_index)))-1)]), round(image_buffer[(3*((((length image_buffer)/3)-$width) + (25-op_index))) - 0]);
            op_size = 0;
        } elif (op_index == 26) {
            # hash
            dec = hash_table[1+data_stream_list[i+1]];
            _add_RGB floor((dec/65536)), (floor((dec/256))%256), (dec%256);
            op_size = 1;
        } elif (op_index == 27) {
            # RLE
            op_index = data_stream_list[i+1];
            _repeat = data_stream_list[i+2];
            op_size = 2;
        } elif (op_index < 91) {
            # vol
            vol_index = (1+((op_index-28)*8));
            if (op_index < 73) {
                _vol_index_to_col data_stream_list[i+1], volumes[1+vol_index], volumes[2+vol_index], volumes[3+vol_index], 5, 4, 4;
                op_size = 1;
            } else {
                _vol_index_to_col ((94*data_stream_list[i+1])+data_stream_list[i+2]), volumes[1+vol_index], volumes[2+vol_index], volumes[3+vol_index], 21, 20, 20;
                op_size = 2;
            }
            _add_RGB (image_buffer[(length image_buffer)-2]+(return_v+return_Y_)), (image_buffer[(length image_buffer)-1]+return_Y_), (image_buffer["last"]+(return_u+return_Y_));

        } else {
            error "unknown chunk";
            stop_this_script;
        }
        i += ((_repeat == 0)+op_size);
    }
    delete data_stream_list;
    delete hash_table;
}



proc _add_RGB r, g, b {
    add $r to image_buffer;
    add $g to image_buffer;
    add $b to image_buffer;
    hash_table[1+((((3*$r)+(5*$g))+(7*$b))%94)] = (((65536*$r)+(256*$g))+$b);
}


proc _vol_index_to_col index, o0, o1, o2, d0, d1, d2 {
    return_Y_ = ($o0+(floor(($index/($d2*$d1)))%$d0));
    return_u = ($o1+(floor(($index/$d2))%$d1));
    return_v = ($o2+($index%$d2));
}


proc _decompress_A8 data_stream, width {
    _get_character_codes_from_data_stream $data_stream;
    delete image_buffer;
    # repeat is a counter for how many times an op should be run (RLE)
    _repeat = 0;
    op_size = 0;
    i = 1;
    until (i > (length data_stream_list)) {
        if (_repeat > 0) {
            # RLE uses the previously found op and decrements repeat
            _repeat -= 1;
        } else {
            op_index = data_stream_list[i];
        }
        
        if (op_index < 3) {
            # raw
            add ((94 * op_index)+data_stream_list[i+1]) to image_buffer;
            op_size = 1;
            
        } elif (op_index == 3) { 
            # prev
            add round(image_buffer["last"]) to image_buffer;
            op_size = 0;

        } elif (op_index < 7) {
            # copy vert fwd/mid/back
            add round(image_buffer[((length image_buffer)-$width) + (6-op_index)]) to image_buffer;
            op_size = 0;

        } elif (op_index == 7) {
            # RLE
            op_index = data_stream_list[i+1];
            _repeat = data_stream_list[i+2];
            op_size = 2;

        } else {
            # diff
            if (op_index < 51) {
                add ((image_buffer["last"]+(op_index-7)) % 256) to image_buffer;
            } else {
                add ((image_buffer["last"]+(50-op_index)) % 256) to image_buffer;
            }
            op_size = 0;
        }
        i += ((_repeat == 0)+op_size);
    }
    delete data_stream_list;
}

proc _get_character_codes_from_data_stream data_stream {
    # iterate over inputted text, convert each to character indices. ! should be index 0.
    delete data_stream_list;
    i = 1;
    repeat (length $data_stream) {
        switch_costume $data_stream[i];
        add (costume_number()-3) to data_stream_list;
        i++;
    }
    switch_costume "icon";
}





################################
#       TextImage write        #
################################


# Write a typical RGBA image
proc write_TextImage {
    TI_image_size_x = floor(TI_image_size_x);
    TI_image_size_y = floor(TI_image_size_y);
    delete layers;
    
    # encode layers, this can be modified to suit the use case
    
    # RGB8:
    delete image_buffer;
    i = 1;
    repeat (TI_image_size_x * TI_image_size_y) {
        add round((255-((255-(TI_1_r[i]*(TI_1_r[i] > 0)))*(TI_1_r[i] < 255)))) to image_buffer;
        add round((255-((255-(TI_2_g[i]*(TI_2_g[i] > 0)))*(TI_2_g[i] < 255)))) to image_buffer;
        add round((255-((255-(TI_3_b[i]*(TI_3_b[i] > 0)))*(TI_3_b[i] < 255)))) to image_buffer;
        i++;
    }
    _data_stream_compress_RGB8_from_buffer TI_image_size_x;
    add_layer "main", "RGB8", 0, data_stream;
    
    # A8:
    delete image_buffer;
    i = 1;
    repeat (TI_image_size_x * TI_image_size_y) {
        add round((255-((255-(TI_4_a[i]*(TI_4_a[i] > 0)))*(TI_4_a[i] < 255)))) to image_buffer;
        i++;
    }
    _data_stream_compress_A8_from_buffer TI_image_size_x;
    add_layer "alpha", "A8", 0, data_stream;
    
    # create file
    TextImage_file = ("txtimg,v:0," & ((("x:" & TI_image_size_x) & (",y:" & TI_image_size_y)) & ","));
    
    # you can define custom properties like this:
    #TextImage_file &= (("_project:" & PROJECT) & ",");
    
    # layers (sets of 6 items)
    TextImage_file &= ("p:" & (4*((length layers)/6)));
    data_stream = "";
    i = 0;
    repeat ((length layers) / 6) {
        TextImage_file &= ("," & layers[i+2]);
        TextImage_file &= ("," & layers[i+3]);
        TextImage_file &= ("," & layers[i+4]);
        TextImage_file &= ("," & layers[i+5]);
        data_stream &= (layers[i+6]);
        i += 6;
    }

    TextImage_file &= ("|" & data_stream);
    data_stream = "";
    delete layers;
}


proc add_layer purpose, type, version, data_stream {
    # sets of 6 items... !purpose, purpose, type, version, length, index_start
    add ("!" & $purpose) to layers;
    add $purpose to layers;
    add $type to layers;
    add $version to layers;
    add length $data_stream to layers;
    add $data_stream to layers;
}



proc _data_stream_compress_RGB8_from_buffer width {
    
    delete data_stream_list;
    delete hash_table;
    repeat 94 { add 0 to hash_table; }
    
    i = 0;
    repeat ((length image_buffer)/3) {
        # get current pixel as a single decimal value for faster comparisons
        dec = ((65536*image_buffer[i+1])+((256*image_buffer[i+2])+image_buffer[i+3]));
        if (dec == ((65536*image_buffer[i-2])+((256*image_buffer[i-1])+image_buffer[i+0]))) {
            add 22 to data_stream_list; # prev
            
        } elif (dec == ((65536*image_buffer[(i-(3*$width))+4])+((256*image_buffer[(i-(3*$width))+5])+image_buffer[(i-(3*$width))+6]))) {
            add 23 to data_stream_list; # copy vert fwd

        } elif (dec == ((65536*image_buffer[(i-(3*$width))+1])+((256*image_buffer[(i-(3*$width))+2])+image_buffer[(i-(3*$width))+3]))) {
            add 24 to data_stream_list; # copy vert

        } elif (dec == ((65536*image_buffer[(i-(3*$width))-2])+((256*image_buffer[(i-(3*$width))-1])+image_buffer[(i-(3*$width))+0]))) {
            add 25 to data_stream_list; # copy vert back

        } elif dec in hash_table { #contains(hash_table, dec) { # TODO
            add 26 to data_stream_list; # hash table
            add ((dec in hash_table)-1) to data_stream_list;

        } else {

            return_Y_ = (image_buffer[i+2]-image_buffer[i-1]);
            return_u = ((image_buffer[i+3]-image_buffer[i])-return_Y_);
            return_v = ((image_buffer[i+1]-image_buffer[i-2])-return_Y_);
            
            # convert to vol index for each vol. 
            # this is mostly hard-coded, modification required if the volumes list is changed
            
            vol_index = "";
            j = -8;
            until not ((vol_index == "") and (j < 352)) {
                j += 8;
                _col_to_volume_index return_Y_, return_u, return_v, volumes[j+2], volumes[j+3], volumes[j+4], 5, 4, 4;
            }
            if (vol_index == "") {
                until not ((vol_index == "") and (j < 496)) {
                    j += 8;
                    _col_to_volume_index return_Y_, return_u, return_v, volumes[j+2], volumes[j+3], volumes[j+4], 21, 20, 20;
                }
                if (vol_index == "") {
                    # FALLBACK raw 4-tuple
                    add (floor(dec/830584)%21) to data_stream_list;
                    add (floor(dec/8836)%94) to data_stream_list;
                    add (floor(dec/94)%94) to data_stream_list;
                    add (dec%94) to data_stream_list;
                } else {
                    add (28+(j/8)) to data_stream_list;
                    add floor(vol_index/94) to data_stream_list;
                    add (vol_index%94) to data_stream_list;
                }
            } else {
                add (28+(j/8)) to data_stream_list;
                add vol_index to data_stream_list;
            }
        }
        hash_table[1 + ((((3*image_buffer[i+1])+(5*image_buffer[i+2])) + (7*image_buffer[i+3])) % 94)] = dec;
        i += 3;
    }
    
    _data_stream_process_RLE 27, 0; # RLE
    _chars_from_data_stream; # convert to data stream

    delete data_stream_list;
    delete hash_table;
}


proc _col_to_volume_index c0, c1, c2, o0, o1, o2, d0, d1, d2 {
    if (((not (($c0-$o0) < 0)) and (($c0-$o0) < $d0)) and (((not (($c1-$o1) < 0)) and (($c1-$o1) < $d1)) and ((not (($c2-$o2) < 0)) and (($c2-$o2) < $d2)))) {
        vol_index = ((($d1*$d2)*($c0-$o0))+(($d2*($c1-$o1))+($c2-$o2)));
    } else {
        vol_index = "";
    }
}


proc _data_stream_compress_A8_from_buffer width {
    
    delete data_stream_list;
    i = 1;
    repeat (length image_buffer) {
        dec = image_buffer[i];
        if (dec == image_buffer[i-1]) {
            add 3 to data_stream_list; # prev

        } elif (dec == image_buffer[i-($width-1)]) {
            add 4 to data_stream_list; # copy vert fwd

        } elif (dec == image_buffer[i-$width]) {
            add 5 to data_stream_list;# copy vert

        } elif (dec == image_buffer[i-($width+1)]) {
            add 6 to data_stream_list; # copy vert back

        } else {
            
            local diff = ((((dec-image_buffer[i-1])+128)%256)-128);
            
            if ((0 < diff) and (diff < 42)) {
                add (diff+7) to data_stream_list; # inc

            } elif ((-42 < diff) and (diff < 0)) {
                add (50-diff) to data_stream_list; # dec

            } else {
                add (floor((dec/94))%94) to data_stream_list; # raw 2-tuple
                add (dec%94) to data_stream_list;
            }
        }
        i++;
    }
    
    _data_stream_process_RLE 7, 94; # RLE
    _chars_from_data_stream; # convert to data stream
    
    delete data_stream_list;
}


# enumerate over `data_stream` list, convert each to chars
proc _chars_from_data_stream  {
    data_stream = "";
    i = 1;
    repeat (length data_stream_list) {
        switch_costume (data_stream_list[i]+3);
        data_stream &= costume_name();
        i++;
    }
    switch_costume "icon";
}


# RLE index: the index for `repeat_op`  |  op size start index: the index into the [op sizes] list, 0-indexed
proc _data_stream_process_RLE RLE_index, op_size_start_index {
    
    # load data_stream_list into temp list (source_data_stream_list) so it can be written to
    delete source_data_stream_list;
    i = 1;
    repeat (length data_stream_list) {
        add data_stream_list[i] to source_data_stream_list;
        i++;
    }
    delete data_stream_list;
    
    # [image buffer] now will be repurposed to store accumulated op data before being copied to data_stream_list. buffer size is the number of ops in the buffer (not the same as number of items in the buffer list), buffer op is the op code used by all buffer items. (op size) is repurposed.
    i = 1;
    delete image_buffer;
    local buffer_size = 0;
    local buffer_op = source_data_stream_list[i];

    # enumerate over source_data_stream_list
    until (i > (1+(length source_data_stream_list))) {
        if (not ((buffer_op == source_data_stream_list[i]) and (buffer_size < 93))) {
            # check that the buffer is compressible with RLE
            if ((3+(buffer_size*op_size)) < (buffer_size*(1+op_size))) {
                # use RLE
                add $RLE_index to data_stream_list;
                add buffer_op to data_stream_list;
                add buffer_size to data_stream_list;
                j = 1;
                repeat (length image_buffer) {
                    add image_buffer[j] to data_stream_list;
                    j++;
                }
            } else {
                # dump the buffer contents back into the data stream with unaltered chunks
                j = 1;
                repeat buffer_size {
                    add buffer_op to data_stream_list;
                    repeat op_size {
                        add image_buffer[j] to data_stream_list;
                        j++;
                    }
                }
            }
            # next chunk
            delete image_buffer;
            buffer_size = 0;
            buffer_op = source_data_stream_list[i];
        }
        # add current chunk to buffer
        op_size = op_sizes[1 + $op_size_start_index + buffer_op];
        i++;
        repeat op_size {
            add source_data_stream_list[i] to image_buffer;
            i++;
        }
        buffer_size++;
    }
    delete source_data_stream_list;
}



################################
#     TextImage utilities      #
################################


proc clear_all_shared_data {
    TextImage_file = "";
    TI_image_size_x = 0;
    TI_image_size_y = 0;
    delete TI_1_r;
    delete TI_2_g;
    delete TI_3_b;
    delete TI_4_a;
    delete TI_header;
}


proc debug_draw_image x, y, res {
    erase_all;
    set_pen_size $res;
    i = 1;
    set_y $y;
    repeat (TI_image_size_y/$res) {
        set_x $x;
        repeat (TI_image_size_x/$res) {
            if (TI_4_a[i] > 0) {
                set_pen_color (16777216*TI_4_a[i] + 65536*TI_1_r[i] + 256*TI_2_g[i] + TI_3_b[i]);
                pen_down;
                pen_up;
            }
            change_x $res;
            i++;
        }
        change_y $res;
    }
}
