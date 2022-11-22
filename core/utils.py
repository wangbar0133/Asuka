import re

def check_address(address: str) -> bool:
    return re.search("^0[xX][a-fA-F0-9]{40}$", address) != None

def merge_loc_list(locList:list) -> list:
    locListMerged = list()
    locListMerged.append(locList[0])
    for loc in locList[1:]:
        if loc["end"]["line"] - locListMerged[-1]["start"]["line"] <= 3:
            locListMerged[-1]["end"]["line"] = \
                loc["end"]["line"]
        else:
            locListMerged.append(loc)
    return locListMerged
                        