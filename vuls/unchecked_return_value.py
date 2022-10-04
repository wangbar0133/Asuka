from ast_scanner.ast_scanner import Scanner
from .vul import Vul, Vuls

NAME = "Unchecked Return Value"

ID = 0

DESCREIBE = "The return value of a message call is not checked."

ADVICE = "Check return values of low-level call methods."

RISK = 0

METHED = ["call", "transfer", "send", "value"]

def check(scan: Scanner):
    vul_list = list()
    for function in scan.functions:
        # check if call() in function
        if not check_functioncall(function.functionCalls):
            continue
        
        for statement in function.statements:
            if statement.type != "ExpressionStatement":
                continue
            if statement.expression.type != "FunctionCall":
                continue
            if statement.expression.expression.type != "MemberAccess":
                continue
            if statement.expression.expression.memberName in METHED:
                vul_list.append(
                    Vul(
                        fileName=scan.fileName,
                        locList=[statement.expression.loc]
                    )
                )
                
        # con't handle address.call{ value: value }()
        returnValueMap = dict()
        for statement in function.statements:
            if statement.type == "VariableDeclarationStatement":
                if not statement.initialValue:
                    continue
                if statement.initialValue.type != "FunctionCall":
                    continue
                if statement.initialValue.expression.type != "MemberAccess":
                    continue
                if statement.initialValue.expression.memberName not in METHED:
                    continue
                returnValueMap[statement.variables[0].name] = statement
            
            elif statement.type == "ExpressionStatement" and returnValueMap:
                if statement.expression.type != "FunctionCall":
                    continue
                if statement.expression.expression.name != "require":
                    continue
                if not statement.expression.arguments:
                    continue
                name = statement.expression.arguments[0].name
                if name in returnValueMap.keys():
                    del returnValueMap[name]  
        
        if returnValueMap:
            for statement in returnValueMap.values():
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
    
    
def check_functioncall(functionCalls):
    for functionCall in functionCalls:
        if functionCall["name"] in METHED:
            return True
    return False