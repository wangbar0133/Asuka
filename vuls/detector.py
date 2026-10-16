"""Base class and shared protocol for all Asuka detectors."""
from typing import ClassVar

from ast_scanner.ast_scanner import Scanner

from .vul import Vul, Vuls


class Detector:
    """Base class every detector inherits from.

    Subclasses declare their metadata as class attributes and implement
    check(). Build the return value with result() so every detector
    reports consistent metadata.
    """

    NAME: ClassVar[str] = ""
    ID: ClassVar[int] = 0
    DESCRIPTION: ClassVar[str] = ""
    ADVICE: ClassVar[str] = ""
    RISK: ClassVar[int] = 0

    def check(self, scan: Scanner) -> Vuls:
        raise NotImplementedError("detectors must implement check()")

    def result(self, vul_list: list[Vul]) -> Vuls:
        """Build the standard Vuls result carrying this detector's metadata."""
        return Vuls(
            name=self.NAME,
            id=self.ID,
            description=self.DESCRIPTION,
            advice=self.ADVICE,
            risk=self.RISK,
            vulList=vul_list,
        )
