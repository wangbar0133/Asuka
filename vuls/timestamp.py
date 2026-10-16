from ast_scanner.ast_scanner import Scanner, Tools

from .detector import Detector
from .vul import Vul


class TimestampDependence(Detector):
    NAME = "Timestamp Dependence"
    ID = 116
    DESCRIPTION = (
        "block.timestamp (or the deprecated now) is used inside a require/if/"
        "while condition. Block timestamps are set by miners and can drift by "
        "several seconds, so logic depending on them - especially equality "
        "comparisons or short windows - can be manipulated."
    )
    ADVICE = (
        "Do not rely on the exact value of block.timestamp; tolerate drift "
        "(use ranges and inequalities) or avoid timestamps for security "
        "decisions entirely."
    )
    RISK = 1

    def check(self, scan: Scanner):
        vul_list: list[Vul] = []
        for function in scan.functions:
            for statement in function.statements:
                if statement.type not in ("IfStatement", "WhileStatement",
                                          "ForStatement"):
                    continue
                condition = statement.get("condition") or statement.get("conditionExpression")
                if condition and self._uses_timestamp(condition):
                    vul_list.append(
                        Vul(
                            fileName=scan.fileName,
                            locList=[statement.loc]
                        )
                    )
            for functionCall in function.functionCalls:
                if functionCall.name != "require":
                    continue
                if not functionCall.arguments:
                    continue
                if self._uses_timestamp(functionCall.arguments[0]):
                    vul_list.append(
                        Vul(
                            fileName=scan.fileName,
                            locList=[functionCall.loc]
                        )
                    )

        return self.result(vul_list)

    @staticmethod
    def _uses_timestamp(node) -> bool:
        for inner in Tools.iter_nodes(node):
            if inner.get("type") == "Identifier" and inner.get("name") == "now":
                return True
            if inner.get("type") == "MemberAccess" \
                    and inner.get("memberName") == "timestamp" \
                    and inner.get("expression", {}) \
                    and inner["expression"].get("type") == "Identifier" \
                    and inner["expression"].get("name") == "block":
                return True
        return False
