from ast_scanner.ast_scanner import Scanner
from vuls.int_overflow import ADVICE
from .vul import Vul, Vuls

NAME = "Function Default Visibility"

ID = 100

DESCREIBE = "Function visibility type specified are public by default, this may lead to a vulnerability"

ADVICE = "It is recommended to make a conscious decision on which visibility type is appropriate for a function."

RISK = 2

def check(scan: Scanner):
    vul_list = list()
    for function in scan.functions:
        if function.functionObject.node.visibility == "default":
            vul_list.append(
                Vul(
                    fileName=scan.fileName,
                    locList=[{
                        "start": function.functionObject.node.loc["start"],
                        "end": function.functionObject.node.loc["start"]
                    }]
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