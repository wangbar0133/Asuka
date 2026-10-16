from ast_scanner.ast_scanner import Scanner, Tools

from .detector import Detector
from .vul import Vul

DIVISION_OPS = ("/", "%")


class DivideBeforeMultiply(Detector):
    NAME = "Imprecise Arithmetic Order"
    ID = 202
    DESCRIPTION = (
        "A division (or modulo) is an immediate operand of a multiplication, "
        "e.g. a / b * c. The intermediate result is truncated, losing "
        "precision that the following multiplication cannot recover."
    )
    ADVICE = (
        "Reorder the operations so the multiplication happens first "
        "(a * c / b), or use a precision-preserving library."
    )
    RISK = 2

    def check(self, scan: Scanner):
        vul_list: list[Vul] = []
        seen: set[int] = set()
        for function in scan.functions:
            for statement in function.statements:
                for node in Tools.iter_nodes(statement):
                    if node.get("type") != "BinaryOperation":
                        continue
                    if node.get("operator") != "*" or id(node) in seen:
                        continue
                    for side in (node.get("left"), node.get("right")):
                        if side and side.get("type") == "BinaryOperation" \
                                and side.get("operator") in DIVISION_OPS:
                            seen.add(id(node))
                            vul_list.append(
                                Vul(
                                    fileName=scan.fileName,
                                    locList=[node.loc]
                                )
                            )
                            break

        return self.result(vul_list)
