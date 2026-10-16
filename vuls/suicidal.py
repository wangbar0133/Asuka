from ast_scanner.ast_scanner import Scanner, Tools

from .detector import Detector
from .vul import Vul


class Suicidal(Detector):
    NAME = "Unprotected Selfdestruct"
    ID = 106
    DESCRIPTION = (
        "The contract can be destructed by anyone. A selfdestruct (or the "
        "deprecated suicide) call reachable from a public or external function "
        "without an authorization modifier lets an attacker destroy the "
        "contract and potentially divert its balance."
    )
    ADVICE = (
        "Protect the selfdestruct path with an authorization modifier "
        "(e.g. onlyOwner) and make the function non-public otherwise."
    )
    RISK = 3

    DESTRUCTORS = ["selfdestruct", "suicide"]

    def check(self, scan: Scanner):
        vul_list: list[Vul] = []
        for function in scan.functions:
            if function.functionObject.visibility not in ["default", "public", "external"]:
                continue
            if Tools.check_modifier(function.functionObject, ["onlyOwner", "onlyGov", "onlyAdmin"]):
                continue
            for functionCall in function.functionCalls:
                if functionCall.name not in self.DESTRUCTORS:
                    continue
                vul_list.append(
                    Vul(
                        fileName=scan.fileName,
                        locList=[functionCall.loc]
                    )
                )

        return self.result(vul_list)
