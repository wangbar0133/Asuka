"""Detector registry: the single source of loaded detectors.

To add a new detector: create vuls/<name>.py with a Detector subclass,
then import it and add the class to DETECTOR_CLASSES below. The CLI and
the Asuka core both read ALL_DETECTORS / DETECTOR_IDS from here - never
re-implement detector discovery elsewhere.
"""
from .access_of_uninitialized_pointer import AccessOfUninitializedPointer
from .arbitrary_call import ArbitraryCall
from .delegatecall import Delegatecall
from .detector import Detector
from .function_default_visibility import FunctionDefaultVisibility
from .int_overflow import IntOverflow
from .msgvalue_in_loop import MsgValueInLoop
from .reentrancy import Reentrancy
from .tx_origin import TxOrigin
from .unchecked_return_value import UncheckedReturnValue

DETECTOR_CLASSES: list[type[Detector]] = [
    AccessOfUninitializedPointer,
    ArbitraryCall,
    Delegatecall,
    FunctionDefaultVisibility,
    IntOverflow,
    MsgValueInLoop,
    Reentrancy,
    TxOrigin,
    UncheckedReturnValue,
]

# SWC id -> singleton instance (detectors are stateless)
ALL_DETECTORS: dict[int, Detector] = {cls.ID: cls() for cls in DETECTOR_CLASSES}
DETECTOR_IDS: list[int] = sorted(ALL_DETECTORS)
