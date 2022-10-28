from ast_scanner.ast_scanner import Scanner
from .vul import Vul, Vuls

NAME = "Access of Uninitialized Pointer"

ID = 109

DESCREIBE = "Uninitialized local storage variables can point to unexpected storage locations in the contract, which can lead to intentional or unintentional vulnerabilities."

ADVICE = """Check if the contract requires a storage object as in many situations this is actually not the case. If a local variable is sufficient, mark the storage location of the variable explicitly with the memory attribute. If a storage variable is needed then initialise it upon declaration and additionally specify the storage location storage."""

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
    