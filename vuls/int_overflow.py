from ast_scanner.ast_scanner import Scanner
from .vul import Vul, Vuls

INVAILD_OP = ["+", "-", "/", "*", "+=", "-=", "*="]

NAME = "int overflow"

ID = 101

DESCREIBE = "Integer Overflow and Underflow"

ADVICE = "Using safemath lib"

RISK = 3

def check(scan: Scanner):
    vul_list = list()
    for pragma in scan.sourceUnitObject.pragmas:
        if check_solc_version(pragma.value, 8):
            if scan.operators:
                for op in scan.operators:
                    if op.name in INVAILD_OP:
                        vul_list.append(
                            Vul(
                                fileName=scan.fileName,
                                locList=[op["loc"]]
                            )
                        )
            break
                
    return Vuls(
            name=NAME,
            id=ID,
            descreibe=DESCREIBE,
            advice=ADVICE,
            risk=RISK,
            vulList=vul_list
        )
    

def check_solc_version(pragma: str, version: int):
    try:
        major, minor, patch = tuple(pragma.split("."))
        prefix = major[:-1]
        if prefix in ["<", "<="]:
            return True
        if int(minor) < version:
            return True
        return False
    except:
        return False





