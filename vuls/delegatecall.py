from ast_scanner.ast_scanner import Scanner
from .vul import Vul, Vuls

NAME = "Delegatecall to Untrusted Callee"

ID = 112

DESCREIBE = "There exists a special variant of a message call, named delegatecall which is "
"identical to a message call apart from the fact that the code at the target address is "
"executed in the context of the calling contract and msg.sender and msg.value do not change "
"their values. This allows a smart contract to dynamically load code from a different address "
"at runtime. Storage, current address and balance still refer to the calling contract. \n"
"Calling into untrusted contracts is very dangerous, as the code at the target address can "
"change any storage values of the caller and has full control over the caller's balance."

ADVICE = "Use delegatecall with caution and make sure to never call into untrusted contracts."
"If the target address is derived from user input ensure to check it against a whitelist of trusted contracts."

RISK = 3

def check(scan: Scanner):
    vul_list = list()
    # find all delegatecall in every function
    for function in scan.functions:
        if "onlyOwner" in function.modifiers:
            continue
        if not (
                "external" == function.functionObject.visibility
                or "public" in function.functionObject.visibility
            ):
                continue
        for functionCall in function.functionCalls:
            if functionCall.name != "delegatecall":
                continue
            if not hasattr(functionCall, "expression"):
                continue
            address = functionCall.expression.name
            if address in function.functionObject.declarations.keys():
                if function.functionObject.declarations[address].type == "Parameter":
                    vul_list.append(
                        Vul(
                            fileName=scan.fileName,
                            locList=[
                                functionCall.loc,
                                function.functionObject.declarations[address].loc
                            ]
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