from ast_scanner.ast_scanner import Scanner

from .detector import Detector
from .vul import Vul


class DeprecatedStandards(Detector):
    NAME = "Deprecated Solidity Standards"
    ID = 205
    DESCRIPTION = (
        "The code uses constructs removed or deprecated in modern Solidity: "
        "suicide() instead of selfdestruct, sha3() instead of keccak256, or "
        "msg.gas instead of gasleft(). sha3() in old compilers mapped to "
        "Keccak-256, which differs from the SHA-3 standard - a recurring "
        "source of subtle bugs."
    )
    ADVICE = (
        "Replace suicide(x) with selfdestruct(x), sha3(...) with "
        "keccak256(...) and msg.gas with gasleft()."
    )
    RISK = 1

    DEPRECATED_CALLS = ["suicide", "sha3"]
    DEPRECATED_MEMBERS = ["gas"]

    def check(self, scan: Scanner):
        vul_list: list[Vul] = []
        for function in scan.functions:
            for functionCall in function.functionCalls:
                if functionCall.name in self.DEPRECATED_CALLS:
                    vul_list.append(
                        Vul(
                            fileName=scan.fileName,
                            locList=[functionCall.loc]
                        )
                    )
            for expression in function.expressions:
                if expression.type != "MemberAccess":
                    continue
                if expression.name not in self.DEPRECATED_MEMBERS:
                    continue
                if expression.expression and expression.expression.type == "Identifier" \
                        and expression.expression.name == "msg":
                    vul_list.append(
                        Vul(
                            fileName=scan.fileName,
                            locList=[expression.loc]
                        )
                    )

        return self.result(vul_list)
