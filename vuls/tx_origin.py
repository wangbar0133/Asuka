from ast_scanner.ast_scanner import Scanner

from .detector import Detector
from .vul import Vul


class TxOrigin(Detector):
    NAME = "Authorization through tx.origin"
    ID = 115
    DESCRIPTION = """tx.origin is a global variable in Solidity which returns the address of the account that sent the transaction.
Using the variable for authorization could make a contract vulnerable if an authorized account calls into a
malicious contract. A call could be made to the vulnerable contract that passes the authorization check since
tx.origin returns the original sender of the transaction which in this case is the authorized account."""
    ADVICE = "Use msg.sender instead."
    RISK = 3

    def check(self, scan: Scanner):
        vul_list: list[Vul] = []
        for function in scan.functions:
            for functionCall in function.functionCalls:
                if functionCall.name != "require":
                    continue
                # require() may carry no arguments; arguments[0] used to
                # raise IndexError and kill the whole scan
                if not functionCall.arguments:
                    continue
                argument = functionCall.arguments[0]
                if check_require(argument):
                    vul_list.append(
                        Vul(
                            fileName=scan.fileName,
                            locList=[functionCall.loc]
                        )
                    )

        return self.result(vul_list)


def check_require(argument) -> bool:
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
