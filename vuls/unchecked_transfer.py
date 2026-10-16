from ast_scanner.ast_scanner import Scanner, Tools

from .detector import Detector
from .vul import Vul

TOKEN_METHODS = ("transfer", "transferFrom", "safeTransfer", "safeTransferFrom")


class UncheckedTransfer(Detector):
    NAME = "Unchecked Token Transfer"
    ID = 201
    DESCRIPTION = (
        "The return value of an ERC20/ERC721 transfer call is discarded. "
        "Token transfers return a boolean that is false on failure (and "
        "non-standard tokens can fail without reverting), so a discarded "
        "result silently loses tokens."
    )
    ADVICE = (
        "Check the return value: require(token.transfer(...)) or handle "
        "the returned boolean explicitly."
    )
    RISK = 3

    def check(self, scan: Scanner):
        vul_list: list[Vul] = []
        for contract in scan.contracts:
            # include state variables inherited from base contracts,
            # which may live in another file
            state_vars = contract.resolved_state_vars()
            for function in contract.functions:
                for statement in function.statements:
                    if statement.type != "ExpressionStatement":
                        continue
                    expression = statement.expression
                    if expression.type != "FunctionCall":
                        continue
                    callee = expression.expression
                    if not callee or callee.type != "MemberAccess":
                        continue
                    if callee.memberName not in TOKEN_METHODS:
                        continue
                    if self._base_is_address(
                            callee.expression, function, state_vars):
                        # address.transfer(x): ether path, covered by the
                        # unchecked-return-value detector
                        continue
                    vul_list.append(
                        Vul(
                            fileName=scan.fileName,
                            locList=[expression.loc]
                        )
                    )

        return self.result(vul_list)

    @staticmethod
    def _base_is_address(base, function, state_vars: dict) -> bool:
        """Best-effort: is the callee receiver an address-typed value?

        Unknown bases are treated as non-address (conservative towards
        reporting), matching how tokens are usually held in variables of
        interface types.
        """
        if not base:
            return False
        if base.type == "Identifier":
            name = base.name
            if name == "this":
                # this.transfer(...) calls our own function, not a token
                return True
            declaration = function.functionObject.declarations.get(name)
            if declaration is None:
                declaration = state_vars.get(name)
            return UncheckedTransfer._declared_as_address(declaration)
        if base.type == "MemberAccess":
            # msg.sender.transfer(...) is an ether transfer
            inner = base.get("expression")
            if inner and inner.get("type") == "Identifier" \
                    and inner.get("name") == "msg" \
                    and base.get("memberName") == "sender":
                return True
            # users[i].addr.transfer(x) style ether payouts: resolve the
            # root of the member chain; report only when it is known to
            # be a non-address (token-like) variable, skip otherwise
            root = base
            while root.get("type") == "MemberAccess" and root.get("expression"):
                root = root["expression"]
            if root.get("type") != "Identifier":
                return True
            declaration = function.functionObject.declarations.get(root.get("name"))
            if declaration is None:
                declaration = state_vars.get(root.get("name"))
            if declaration is None:
                return True
            return UncheckedTransfer._declared_as_address(declaration)
        if base.type == "FunctionCall":
            # IERC20(token).transfer(...) is a token call, while
            # address(this).transfer(...) / payable(x).transfer(...) are
            # ether transfers (owned by the unchecked-return-value
            # detector). The parser drops the callee of a payable cast,
            # so a None expression means an address-like conversion.
            inner = base.get("expression")
            if inner is None:
                return True
            if inner.get("type") == "Identifier" \
                    and inner.get("name") in ("address", "payable"):
                return True
            return False
        return False

    @staticmethod
    def _declared_as_address(declaration) -> bool:
        """True only for address-typed declarations.

        Everything else (contract/interface types, elementary types,
        unknown names) is treated as a token-like receiver and reported:
        for a security scanner the false negative costs more here.
        """
        if declaration is None:
            return False
        return Tools.is_address_type(declaration)
