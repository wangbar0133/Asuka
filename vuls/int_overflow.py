from ast_scanner.ast_scanner import Scanner
from .vul import Vul, Vuls
from .utils import check_solc_version

INVAILD_OP = ["+", "-", "/", "*", "+=", "-=", "*="]

NAME = "int overflow"

ID = 101

DESCREIBE = "Integer Overflow and Underflow"

ADVICE = "It is recommended to use vetted safe math libraries for arithmetic operations consistently throughout the smart contract system."

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
                                locList=[pragma.loc ,op["loc"]]
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
    






