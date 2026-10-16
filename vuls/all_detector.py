"""Detector registry: importing this module imports every detector.

Each detector module exposes NAME / ID / DESCREIBE / ADVICE / RISK / check().
To add a new detector, create vuls/<name>.py and import it at the bottom.
"""

from . import (
    access_of_uninitialized_pointer,  # noqa: F401
    arbitrary_call,  # noqa: F401
    delegatecall,  # noqa: F401
    function_default_visibility,  # noqa: F401
    int_overflow,  # noqa: F401
    msgvalue_in_loop,  # noqa: F401
    reentrancy,  # noqa: F401
    tx_origin,  # noqa: F401
    unchecked_return_value,  # noqa: F401
)
