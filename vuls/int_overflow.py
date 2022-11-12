from ast_scanner.ast_scanner import Scanner
from .vul import Vul, Vuls
from .utils import check_solc_version

INVAILD_OP = ["+", "-", "/", "*", "+=", "-=", "*="]

NAME = "Int Overflow"

ID = 101

DESCREIBE = "Integer Overflow and Underflow"

ADVICE = "It is recommended to use vetted safe math libraries for arithmetic operations consistently throughout the smart contract system."

RISK = 3

def check(scan: Scanner):
    """
        Detector of int overflow vul.
        1. Get solc version by scan.sourceUnitObject.pragmas.
        2. Check the version.
        3. Get all operators by scan.operators
        4. Check the operators is invalid.
        5. Collect all detected vul with file path and code locations.
    """
    vul_list = list()
    for pragma in scan.sourceUnitObject.pragmas:
        if check_solc_version(pragma.value, 8):
            if scan.operators:
                for op in scan.operators:
                    if op.name in INVAILD_OP:
                        vul_list.append(
                            Vul(
                                fileName=scan.fileName,
                                locList=[pragma.loc ,op["loc"]]
                            )
                        )
            break
                
    return Vuls(
            name=NAME,
            id=ID,
            descreibe=DESCREIBE,
            advice=ADVICE,
            risk=RISK,
            vulList=vul_list
        )
    






