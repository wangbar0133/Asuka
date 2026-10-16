from ast_scanner.ast_scanner import Scanner

from .detector import Detector
from .vul import Vul


class FunctionDefaultVisibility(Detector):
    NAME = "Function Default Visibility"
    ID = 100
    DESCRIPTION = (
        "Function visibility type specified are public by default, "
        "this may lead to a vulnerability"
    )
    ADVICE = (
        "It is recommended to make a conscious decision on which visibility "
        "type is appropriate for a function."
    )
    RISK = 2

    def check(self, scan: Scanner):
        vul_list: list[Vul] = []
        for function in scan.functions:
            if function.functionObject.visibility == "default":
                vul_list.append(
                    Vul(
                        fileName=scan.fileName,
                        locList=[{
                            "start": function.functionObject.node.loc["start"],
                            "end": function.functionObject.node.loc["start"]
                        }]
                    )
                )

        return self.result(vul_list)
