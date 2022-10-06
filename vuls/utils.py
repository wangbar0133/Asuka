def check_solc_version(pragma: str, version: int):
    try:
        major, minor, patch = tuple(pragma.split("."))
        prefix = major[:-1]
        if prefix in ["<", "<="]:
            return True
        if int(minor) < version:
            return True
        return False
    except:
        return False
