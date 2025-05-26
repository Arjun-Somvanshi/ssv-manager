import os
import requests
import json

'''
Expected pubkey file format:
"93247f2209abcacf57b75a51dafae777f9dd38bc7053d1af526f220a7489a6d3a2753e5f3e8b1cfe39b56f43611df74a"
"b8c219e070533344189e8f985209177c2c385177d7bae902d4256388176b5048e33a38ec3a639d0385ad5b3747b1defd"
.
.
.

(OR)

"0x93247f2209abcacf57b75a51dafae777f9dd38bc7053d1af526f220a7489a6d3a2753e5f3e8b1cfe39b56f43611df74a"
"0xb8c219e070533344189e8f985209177c2c385177d7bae902d4256388176b5048e33a38ec3a639d0385ad5b3747b1defd"
'''
# file with pubkeys
pubkeyfile = "./keys6"

# change this if you have 0x prefix
hex_encoded = False

# Beacon Endpoint
url = "https://rpc.ankr.com/premium-http/eth_beacon/8acd28da9232f635bf0baabc21c0fa9a2f6e61aaad6797dcfbd2c058d5a9eb9f/eth/v1/beacon/states/head/validators"

# The status which you want keys of
status="active_ongoing"

def get_pubkeys(hex_encoded):
    with open(pubkeyfile, "r") as f:
        pubkeys = f.readlines()
        if hex_encoded:
            pubkeys = [key.strip()[1:-1] for key in pubkeys]
        else:
            pubkeys = ["0x" + key.strip()[1:-1] for key in pubkeys]
    return pubkeys


def get_status(pubkeys):
    data = { "ids": pubkeys }
    headers = {"accept": "application/json", "Content-Type": "application/json"}
    response = requests.post(url, json=data, headers=headers)
    response_data = response.json()
    with open("result.json", "w") as f:
        json.dump(response_data, f, indent=2)
    return response_data 

def check_status(pubkeys, status):
    response_data = get_status(pubkeys)["data"]
    for validator in response_data:
        if validator["status"] == status:
            print(validator["validator"]["pubkey"])


if __name__ == "__main__":
    pubkeys = get_pubkeys(hex_encoded)
    check_status(pubkeys, status)

