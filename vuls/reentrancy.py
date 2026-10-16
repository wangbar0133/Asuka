from ast_scanner.ast_scanner import Scanner

from .detector import Detector
from .vul import Vul

METHODS = ["call", "value", "sendValue"]

STATE = ["=", "+=", "-=", "*=", "/="]


class Reentrancy(Detector):
    NAME = "Reentrancy"
    ID = 107
    DESCRIPTION = """One of the major dangers of calling external contracts is that they can take over the control flow.
In the reentrancy attack (a.k.a. recursive call attack), a malicious contract calls back into the calling contract
before the first invocation of the function is finished. This may cause the different invocations of the function
to interact in undesirable ways."""
    ADVICE = """One of the major dangers of calling external contracts is that they can take over the control flow.
In the reentrancy attack (a.k.a. recursive call attack), a malicious contract calls back into the calling contract
before the first invocation of the function is finished. This may cause the different invocations of the function
to interact in undesirable ways. Or use a reentrancy lock (ie. OpenZeppelin's ReentrancyGuard"""
    RISK = 3

    def check(self, scan: Scanner):
        vul_list: list[Vul] = []
        for contract in scan.contracts:
            for function in contract.functions:
                # view/pure live in stateMutability, not visibility
                if function.functionObject.stateMutability in ["view", "pure"]:
                    continue
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
                functionStorageDeclarations: dict = {}
                for name, declartion in function.functionObject.declarations.items():
                    if not declartion.__hasattr__("storageLocation"):
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

        return self.result(vul_list)


def check_functioncall(functionCalls: list):
    for functionCall in functionCalls:
        if functionCall["name"] in METHODS:
            return functionCall
    return False
