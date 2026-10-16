# Asuka

You can use Asuka to detect defects in any Solidity file. It's based on Python 3.11+ and antlr4.

## How to install

Requires Python 3.11 or newer.

```shell
git clone git@github.com:wangbar0133/Asuka.git
cd Asuka
python3.11 -m venv .venv
.venv/bin/pip install -e .
```

## How to use

```shell
asuka --help

usage: asuka [-h] [--version] [-k APIKEY] [-c CHAIN] [-d] [-i INCLUDE] [-e EXCLUDE] [-t THREAD] path

positional arguments:
  path                  Folders or solidity files or address.

options:
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
asuka 0xdac17f958d2ee523a2206206994597c13d831ec7 -c eth -k xxxxxxxxxxxxxxxxxx
```

Support Ethereum now.

Scan single solidity file:

```shell
asuka test.sol
```

Specify or exclude detectors, using -i(include) or -e(exclude) and the SWC id Should be separated by a comma. SWC id can be start with s or just a number.

```shell
asuka . -i s100,101

```

You can specify threads by using -t.

```shell
asuka . -t 4
```

## Cross-file scanning

Local imports (`"./x.sol"`, `"../lib/x.sol"`, `"/contracts/x.sol"`) are resolved
automatically: imported files are parsed and indexed so inheritance chains and
declared types resolve across files.

Imports are **resolution-only** - a dependency is never a scan target, and
package-style paths (`"@openzeppelin/..."`) are recorded but not resolved
(no node_modules/remappings support). A local import that cannot be found is
reported as a warning:

```shell
asuka contracts/
# 2 import(s) not found:
#   contracts/A.sol: ./missing/B.sol
```

Detectors see inherited declarations: a state variable declared in a base
contract (even in another file) is recognised when deciding whether a
`transfer(...)` call is an ether payout or an unchecked token move, and when
checking for reentrancy writes after an external call. Inherited *functions*
are not scanned yet - only functions defined in the files being scanned are
reported (see AGENTS.md).

## Detectors

Most detectors map to an [SWC](https://swcregistry.io/) entry; detectors without
one use the custom 2xx range.

| ID          | Name                             | Basis |
| ----------- | -------------------------------- | ----- |
| SWC-100     | Function Default Visibility      | SWC   |
| SWC-101     | Int Overflow                     | SWC   |
| SWC-104     | Unchecked Return Value           | SWC   |
| SWC-106     | Unprotected Selfdestruct         | SWC   |
| SWC-107     | Reentrancy                       | SWC   |
| SWC-109     | Access of Uninitialized Pointer  | SWC   |
| SWC-112     | Delegatecall to Untrusted Callee | SWC   |
| SWC-115     | Authorization through tx.origin  | SWC   |
| SWC-116     | Timestamp Dependence             | SWC   |
| SWC-120     | Weak Sources of Randomness       | SWC   |
| 137         | Arbitrary calls                  | custom|
| 138         | msg.value in loop                | custom|
| 201         | Unchecked Token Transfer         | custom|
| 202         | Imprecise Arithmetic Order       | custom|
| 203         | Tautological Comparison          | custom|
| 204         | Right-To-Left-Override Character | custom|
| 205         | Deprecated Solidity Standards    | custom|
| 206         | Dangerous Unary Expression       | custom|

More Smart Contract Weakness: <https://swcregistry.io/>

## Development

```shell
python3.11 -m venv .venv
.venv/bin/pip install -e ".[dev]"

.venv/bin/pytest            # run the test suite
.venv/bin/ruff check .      # lint
.venv/bin/asuka test_data/  # try the scanner on the bundled samples
```

CI runs lint plus the test suite on Python 3.11–3.14 for every push and pull request.
See [AGENTS.md](AGENTS.md) for the repository map, conventions, and known pitfalls.

## Welcome to pull request

You can take PR to commit new detector, or take issues when you got trouble.
