# How to make a new detector

Templates:

```python
from ast_scanner.ast_scanner import Scanner

from .detector import Detector
from .vul import Vul


class MyDetector(Detector):
    NAME = ""

    ID = 0  # SWC id, see https://swcregistry.io/

    DESCRIPTION = ""

    ADVICE = ""

    RISK = 0  # 0=Info, 1=Low, 2=Medium, 3=High

    def check(self, scan: Scanner):
        vul_list: list[Vul] = []

        return self.result(vul_list)
```

You can operate the Scanner object to find vuls.
Check int_overflow.py for a simple example, reentrancy.py for a bigger one.

Then register it in vuls/all_detector.py:

1. import your class,
2. add it to DETECTOR_CLASSES.

Find a new smart contract weakness in <https://swcregistry.io/>,
fill in NAME / ID / DESCRIPTION / ADVICE / RISK, implement check(),
and add expectations to tests/test_detectors.py (EXPECTED_IDS + EXPECTED).
