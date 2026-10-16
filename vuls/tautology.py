from ast_scanner.ast_scanner import Scanner, Tools

from .detector import Detector
from .vul import Vul

COMPARISON_OPS = ("==", "!=", "<", "<=", ">", ">=")


class Tautology(Detector):
    NAME = "Tautological Comparison"
    ID = 203
    DESCRIPTION = (
        "A variable is compared to itself (x == x, x < x, ...). The result "
        "is constant, which usually indicates a copy-paste mistake or an "
        "incomplete edit - the intended check never happens."
    )
    ADVICE = "Compare against the intended other operand."
    RISK = 2

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
                    if self._same_operand(node.get("left"), node.get("right")):
                        seen.add(id(node))
                        vul_list.append(
                            Vul(
                                fileName=scan.fileName,
                                locList=[node.loc]
                            )
                        )

        return self.result(vul_list)

    @staticmethod
    def _same_operand(left, right) -> bool:
        if not left or not right:
            return False
        if left.get("type") == "Identifier" and right.get("type") == "Identifier":
            return left.get("name") == right.get("name")
        if left.get("type") == "MemberAccess" and right.get("type") == "MemberAccess":
            if left.get("memberName") != right.get("memberName"):
                return False
            lbase, rbase = left.get("expression"), right.get("expression")
            if lbase and rbase and lbase.get("type") == "Identifier" \
                    and rbase.get("type") == "Identifier":
                return lbase.get("name") == rbase.get("name")
        return False
