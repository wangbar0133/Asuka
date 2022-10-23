from ast_scanner.ast_scanner import Scanner
from .vul import Vul, Vuls

NAME = "Authorization through tx.origin"

ID = 115

DESCREIBE = ""

ADVICE = "Use msg.sender instead."

RISK = 0

def check(scan: Scanner):
    vul_list = list()
    for function in scan.functions:
        for functionCall in function.functionCalls:
            if functionCall.name != "require":
                continue
            argument = functionCall.arguments[0]
            if check_require(argument):
                vul_list.append(
                    Vul(
                        fileName=scan.fileName,
                        locList=[functionCall.loc]
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
    
    
def check_require(argument):
    if argument.type != "BinaryOperation":
        return False
    binary = list()
    for node in [argument.left, argument.right]:
        if node.type == "MemberAccess":
            if node.memberName == "origin" and node.expression.type == "Identifier":
                if node.expression.name == "tx":
                    binary.append("tx.origin")
            elif node.memberName == "sender" and node.expression.type == "Identifier":
                if node.expression.name == "msg":
                    binary.append("msg.sender")        
        else:
            binary.append("Identifier")
    if set(binary) == set(["tx.origin", "msg.sender"]):
        return False
    if "tx.origin" in binary:
        return True
    return False