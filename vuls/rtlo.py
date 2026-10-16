import re

from ast_scanner.ast_scanner import Scanner

from .detector import Detector
from .vul import Vul

# right-to-left override and other bidi / invisible directional controls
RTLO_PATTERN = re.compile("[\u202a-\u202e\u2066-\u2069\u200e\u200f]")


class RTLO(Detector):
    NAME = "Right-To-Left-Override Character"
    ID = 204
    DESCRIPTION = (
        "The source contains a Unicode right-to-left-override (or another "
        "bidirectional control) character. Such characters make code render "
        "differently from how the compiler sees it and are a known trick to "
        "hide malicious statements during review."
    )
    ADVICE = (
        "Remove the control character and reject any contribution "
        "containing bidi controls (grep for U+202E and friends)."
    )
    RISK = 3

    def check(self, scan: Scanner):
        vul_list: list[Vul] = []
        try:
            with open(scan.fileName, encoding="utf-8") as f:
                lines = f.readlines()
        except OSError:
            return self.result(vul_list)

        for line_number, line in enumerate(lines, start=1):
            match = RTLO_PATTERN.search(line)
            if match:
                vul_list.append(
                    Vul(
                        fileName=scan.fileName,
                        locList=[{
                            "start": {"line": line_number, "column": match.start()},
                            "end": {"line": line_number, "column": match.end()},
                        }]
                    )
                )

        return self.result(vul_list)
