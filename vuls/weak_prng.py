from ast_scanner.ast_scanner import Scanner, Tools

from .detector import Detector
from .vul import Vul

CHAIN_ATTRIBUTES = ("timestamp", "number", "difficulty", "prevrandao", "gaslimit")
HASH_FUNCTIONS = ("keccak256", "sha3", "sha256", "ripemd160")


class WeakPRNG(Detector):
    NAME = "Weak Sources of Randomness"
    ID = 120
    DESCRIPTION = (
        "Chain attributes (block.timestamp, block.number, blockhash, ...) are "
        "used as a source of randomness inside a hash function. These values "
        "are predictable or manipulable by miners, so the resulting "
        "'randomness' can be anticipated or biased."
    )
    ADVICE = (
        "Use an oracle-based randomness source (e.g. Chainlink VRF) or a "
        "commit-reveal scheme instead of chain attributes."
    )
    RISK = 3

    def check(self, scan: Scanner):
        vul_list: list[Vul] = []
        for function in scan.functions:
            for functionCall in function.functionCalls:
                if functionCall.name not in HASH_FUNCTIONS:
                    continue
                if not functionCall.get("arguments"):
                    continue
                for argument in functionCall.arguments:
                    if self._contains_chain_attribute(argument):
                        vul_list.append(
                            Vul(
                                fileName=scan.fileName,
                                locList=[functionCall.loc]
                            )
                        )
                        break

        return self.result(vul_list)

    @staticmethod
    def _contains_chain_attribute(node) -> bool:
        for inner in Tools.iter_nodes(node):
            if inner.get("type") == "Identifier" and inner.get("name") == "now":
                return True
            if inner.get("type") == "MemberAccess" \
                    and inner.get("memberName") in CHAIN_ATTRIBUTES \
                    and inner.get("expression", {}) \
                    and inner["expression"].get("type") == "Identifier" \
                    and inner["expression"].get("name") == "block":
                return True
            if inner.get("type") == "FunctionCall" \
                    and inner.get("expression", {}) \
                    and inner["expression"].get("name") == "blockhash":
                return True
        return False
