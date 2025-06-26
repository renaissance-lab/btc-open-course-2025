#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

CHUNK_SIZE = 520

def build_nft_script(file_path):

    script= [   
#        public_key.to_x_only_hex(),
#        "OP_CHECKSIG",
        "OP_0",
        "OP_IF",
        "6f7264",  # "ord"
        "OP_1", 
    #    INSCRIPTION_CONFIG["content_type_hex"],
    #    "OP_0",
    #    brc20_hex,
    #    "OP_ENDIF"
    ]

    extension = os.path.splitext(file_path)[1]
    if extension:
        content_type = "image/" + extension
        script.append(content_type.encode('utf-8').hex())
    else: # no file extension, return null
        return
    
    script.append("OP_0")

    with open(file_path, 'rb') as file:
        chunk = file.read(CHUNK_SIZE)  
        while chunk:
            script.append(chunk.hex())
            chunk = file.read(CHUNK_SIZE)  
    script.append("OP_ENDIF")

    return script

if __name__ == "__main__":
    scripts = build_nft_script("/home/jfxu/Downloads/good.jpeg")
    for it in scripts:
        print(it)
