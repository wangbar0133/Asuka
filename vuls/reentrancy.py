from ast_scanner.ast_scanner import Scanner
from .vul import Vul, Vuls

NAME = "reentrancy"

ID = 0

DESCREIBE = ""

ADVICE = ""

RISK = 0

METHED = ["call", "transfer", "send", "value"]

STATE = ["=", "+=", "-=", "*=", "/="]


def check(scan: Scanner):
    vul_list = list()
    for contract in scan.contracts:
        for function in contract.functions:
            if "nonReentrant" in function.modifiers:
                continue
            # check call transfer seend low level function call
            lowLevelCall = check_functioncall(function.functionCalls)
            if not lowLevelCall:
                continue
            # get below statements
            below_statements = function.get_below_statements(lowLevelCall)[1:]
            # check contract state vars
            for statement in below_statements:
                if statement.type != "ExpressionStatement":
                    continue
                expression = statement.expression
                if expression.type != "BinaryOperation":
                    continue
                if expression.operator not in STATE:
                    continue
                left = expression.left
                
                if left.type == "IndexAccess":
                    if left.base.name in contract.contractObject.stateVars.keys():
                        vul_list.append(
                            Vul(
                                fileName=scan.fileName,
                                locList=[lowLevelCall.loc, left.loc]
                            )
                        )
                elif left.type == "Identifier":
                    if left.name in contract.contractObject.stateVars.keys():
                        vul_list.append(
                            Vul(
                                fileName=scan.fileName,
                                locList=[lowLevelCall.loc, left.loc]
                            )
                        )
            # check function storage declartions
            functionStorageDeclarations = dict()
            for name, declartion in function.functionObject.declarations.items():
                if not hasattr(declartion, "storageLocation"):
                    continue
                if declartion.storageLocation == "storage":
                    functionStorageDeclarations[name] = declartion
                             
            for statement in below_statements:
                if statement.type != "ExpressionStatement":
                    continue
                expression = statement.expression
                if expression.type != "BinaryOperation":
                    continue
                if expression.operator not in STATE:
                    continue
                left = expression.left
                if left.type != "MemberAccess":
                    continue
                if left.expression.type != "Identifier":
                    continue
                if left.expression.name in functionStorageDeclarations.keys():
                    vul_list.append(
                            Vul(
                                fileName=scan.fileName,
                                locList=[lowLevelCall.loc, left.loc]
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
    

def check_functioncall(functionCalls):
    for functionCall in functionCalls:
        if functionCall["name"] in METHED:
            return functionCall
    return False