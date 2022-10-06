from ast_scanner.ast_scanner import Scanner
from .vul import Vul, Vuls

NAME = "Access of Uninitialized Pointer"

ID = 109

DESCREIBE = ""

ADVICE = ""

RISK = 3

def check(scan: Scanner):
    vul_list = list()
    for function in scan.functions:
        for statement in function.statements:
            if statement.type != "VariableDeclarationStatement":
                continue
            if statement.initialValue:
                continue
            if statement.variables[0].storageLocation != "memory":
                vul_list.append(
                    Vul(
                        fileName=scan.fileName,
                        locList=[statement.loc]
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
    