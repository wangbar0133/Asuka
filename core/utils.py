import re

def check_address(address: str) -> bool:
    return re.search("^0[xX][a-fA-F0-9]{40}$", address) != None