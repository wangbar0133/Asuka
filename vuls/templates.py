from ast_scanner.ast_scanner import Scanner
from .vul import Vul, Vuls

NAME = ""

ID = 0

DESCREIBE = ""

ADVICE = ""

RISK = 0

def check(scan: Scanner):
    vul_list = list()
    
    return Vuls(
            name=NAME,
            id=ID,
            descreibe=DESCREIBE,
            advice=ADVICE,
            risk=RISK,
            vulList=vul_list
        )
    