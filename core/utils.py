import re

def check_address(address: str):
    return re.search("^0[xX][a-fA-F0-9]{40}$", address) != None