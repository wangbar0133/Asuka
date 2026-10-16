from ast_scanner.ast_scanner import Scanner, Tools

from .detector import Detector
from .vul import Vul

COMPARISON_OPS = ("==", "!=", "<", "<=", ">", ">=")
DANGEROUS_UNARY = ("!", "~")


class IncorrectUnary(Detector):
    NAME = "Dangerous Unary Expression"
    ID = 206
    DESCRIPTION = (
        "A unary ! or ~ is used on one side of a comparison, e.g. !x == y or "
        "~x > y. The unary binds tighter than intended: the comparison is "
        "performed on the boolean/negated value, not on x, which is almost "
        "never what the author meant."
    )
    ADVICE = "Add parentheses to make the precedence explicit: (!x) == y."
    RISK = 1

    def check(self, scan: Scanner):
        vul_list: list[Vul] = []
        seen: set[int] = set()
        for function in scan.functions:
            for statement in function.statements:
                for node in Tools.iter_nodes(statement):
                    if node.get("type") != "BinaryOperation":
                        continue
                    if node.get("operator") not in COMPARISON_OPS or id(node) in seen:
                        continue
                    for side in (node.get("left"), node.get("right")):
                        if side and side.get("type") == "UnaryOperation" \
                                and side.get("operator") in DANGEROUS_UNARY:
                            seen.add(id(node))
                            vul_list.append(
                                Vul(
                                    fileName=scan.fileName,
                                    locList=[node.loc]
                                )
                            )
                            break

        return self.result(vul_list)
