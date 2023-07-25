from ast_scanner.ast_scanner import Scanner
from .vul import Vul, Vuls

NAME = "Arbitrary calls"

ID = 137

DESCREIBE = "The address of the external contract being called can be controlled."

ADVICE = "Verification of external input parameters."

RISK = 3

def check(scan: Scanner):
    vul_list = list()
    for function in scan.functions:
        # the function should be call by external
        if not function.functionObject.node.visibility in ["default", "public", "external"]:
            continue
        # get all member access function call
        for expression in function.functionCalls:
            if not expression.type == "FunctionCall":
                continue
            if "expression" not in expression.keys():
                continue
            member = expression.expression
            if member.type == "FunctionCall":
                # IERC20(token).transferFrom(from, address(this), amount);
                
                if not member.expression.type == "Identifier":
                    continue
                argumens = member.arguments
                if len(argumens) != 1:
                    continue
                argumen = argumens[0]
                if not argumen.type == "Identifier":
                    continue
                argName = argumen.name
                if argName not in function.functionObject.arguments.keys():
                    continue
                arg = function.functionObject.arguments[argName]
                if not arg.typeName.name == "address":
                    continue
                vul_list.append(
                    Vul(
                        fileName=scan.fileName,
                        locList=[function.functionObject.node.loc]
                    )
                )
            elif member.type == "Identifier":
                # (bool success, ) = zeroXExchangeProxy.call(swapData);
                if not expression.name == "call":
                    continue
                argumens = expression.arguments
                if len(argumens) != 1:
                    continue
                argumen = argumens[0]
                if not argumen.type == "Identifier":
                    continue
                argName = argumen.name
                if argName not in function.functionObject.arguments.keys():
                    continue
                arg = function.functionObject.arguments[argName]
                if not arg.typeName.name == "bytes":
                    continue
                vul_list.append(
                    Vul(
                        fileName=scan.fileName,
                        locList=[function.functionObject.node.loc]
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
    