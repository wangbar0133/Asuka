from ast_scanner.ast_scanner import Scanner, Tools
from .vul import Vul, Vuls

NAME = "msg.value in loop"

ID = 138

DESCREIBE = "msg.value in loop may cause msg.value reuse."

ADVICE = "using msg.value in just one time."

RISK = 3

def check(scan: Scanner):
    vul_list = list()
    for function in scan.functions:
        forStatements = list()
        for statement in function.statements:
            if statement.type == "ForStatement":
                forStatements.append(statement)
        if len(forStatements) == 0:
            continue
        
        msgValueExpression = list()
        
        for expression in function.expressions:
            if not expression.type == "MemberAccess":
                continue
            if not expression.name == "value":
                continue
            if not expression.expression.type == "Identifier":
                continue
            if expression.expression.name == "msg":
                msgValueExpression.append(expression.expression)       
                
        if len(msgValueExpression) == 0:
            continue
        
        for statement in forStatements:
            for expression in msgValueExpression:
                if Tools.scope_check(statement, expression):
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
    