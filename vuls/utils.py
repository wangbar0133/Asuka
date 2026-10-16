def check_solc_version(pragma: str, version: int) -> bool:
    """Return True if any segment of the pragma allows a compiler below `version`.

    Supports compound pragmas like "^0.4.16 || ^0.5.0": a contract that
    may compile on a pre-0.8 compiler still needs overflow detection.
    """
    for segment in pragma.split("||"):
        if _check_single_pragma(segment.strip(), version):
            return True
    return False


def _check_single_pragma(pragma: str, version: int) -> bool:
    try:
        major, minor, patch = tuple(pragma.split("."))
        prefix = major[:-1]
        if prefix in ["<", "<="]:
            return True
        if int(minor) < version:
            return True
        return False
    except Exception:
        return False
