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

usage: asuka [-h] [--version] [-k APIKEY] [-c CHAIN] [-d] [-i INCLUDE] [-e EXCLUDE] [-t THREAD] path

positional arguments:
  path                  Folders or solidity files or address.

optional arguments:
  -h, --help            show this help message and exit
  --version             Show current version
  -k APIKEY, --apikey APIKEY
                        Api key
  -c CHAIN, --chain CHAIN
                        chain type

Check List:
  -d, --detector        Show all detectors

Detect:
  -i INCLUDE, --include INCLUDE
                        Specify the detector
  -e EXCLUDE, --exclude EXCLUDE
                        Exclusion detector
  -t THREAD, --thread THREAD
                        Number of threads
```

Scan all solidity files in the current folder:

```shell
asuka .
```

Scan contract by address chain type and api key:

```shell
asuka 0xdac17f958d2ee523a2206206994597c13d831ec7 -t eth -k xxxxxxxxxxxxxxxxxx
```

Support Ethereum now.

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
| SWC-112     | Delegatecall to Untrusted Callee|
| SWC-115     | Authorization through tx.origin |

More Smart Contract Weakness: <https://swcregistry.io/>

## Welcome to pull request

You can take PR to commit new detector, or take issues when you got trouble.
