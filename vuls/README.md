# How make a new detector

```python
from ast_scanner.ast_scanner import Scanner
from .vul import Vul, Vuls

NAME = ""

ID = 0

DESCREIBE = ""

ADVICE = ""

RISK = 0

def check(scan: Scanner):
    vul_list = list()
    
    return Vuls(
            name=NAME,
            id=ID,
            descreibe=DESCREIBE,
            advice=ADVICE,
            risk=RISK,
            vulList=vul_list
        )
    
```

Find a new smart contract weakness in <https://swcregistry.io/>
Fill in the NAME, ID, DESCREIBE by <https://swcregistry.io/> or yourself.
Complete the check function.
import this module in all_detector.py.
