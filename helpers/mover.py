import os
import json
import shutil

active_file = "./active6"
keys_dir = "./keys"
dest_dir = "./active6-keystores"

with open(active_file) as f:
    active_keys = [line.strip() for line in f.readlines()]

keyfiles = os.listdir(keys_dir)

for keyfile in keyfiles:
    keyfile_path=os.path.join(keys_dir, keyfile)
    with open(keyfile_path) as f:
        keyfile_data = json.load(f)
    if "0x" + keyfile_data["pubkey"]  in active_keys:
        shutil.copy(keyfile_path, dest_dir)
        
