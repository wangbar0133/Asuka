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
    if scan.operators:
        for op in scan.operators:
            if op.name in INVAILD_OP:
                vul_list.append(
                    Vul(
                        fileName=scan.fileName,
                        locList=[op["loc"]]
                    )
                )
                
    return Vuls(
            name=NAME,
            id=ID,
            descreibe=DESCREIBE,
            advice=ADVICE,
            risk=RISK,
            vulList=vul_list
        )