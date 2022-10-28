# Asuka

You can use auska to detect any solidity file to find defects. It's base on python3 and antlr4.

## How to install

```shell
git clone git@github.com:wangbar0133/Asuka.git
cd Asuka
python setup.py install
```

## How to use

```shell
asuka --help

usage: asuka [-h] [-d] [-i INCLUDE] [-e EXCLUDE] [-t THREAD] path

optional arguments:
  -h, --help            show this help message and exit

Check List:
  -d, --detector        Show all detectors.

Detect:
  path                  Folders or solidity files.
  -i INCLUDE, --include INCLUDE
                        Specify the detector
  -e EXCLUDE, --exclude EXCLUDE
                        Exclusion detector
  -t THREAD, --thread THREAD
                        Number of threads.
```

Scan all solidity files in the current folder:

```shell
asuka .
```

Scan single solidity file:

```shell
asuka test.sol
```

Specify or exclude detectors, using -i(inclued) or -e(exclude) and the SWC id Should be separated by a comma. SWC id can be start with s or just a number.

```shell
asuka . -i s100,101

```

You can specify threads by using -t.

```shell
asuka . -t 4
```

## Detectors

All detectors are base on SWC.

| ID          | Name                            |
| ----------- | ------------------------------- |
| SWC-100     | Function Default Visibility     |
| SWC-101     | Int Overflow                    |
| SWC-104     | Unchecked Return Value          |
| SWC-107     | Reentrancy                      |
| SWC-109     | Access of Uninitialized Pointer |
| SWC-115     | Authorization through tx.origin |

More Smart Contract Weakness: <https://swcregistry.io/>

## Welcome to pull request

You can take PR to commit new detector, or take issues when you got trouble.
