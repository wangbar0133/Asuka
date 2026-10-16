"""Detector registry: the single source of loaded detectors.

To add a new detector: create vuls/<name>.py with a Detector subclass,
then import it and add the class to DETECTOR_CLASSES below. The CLI and
the Asuka core both read ALL_DETECTORS / DETECTOR_IDS from here - never
re-implement detector discovery elsewhere.

ID policy: use the official SWC id when the registry has one
(https://swcregistry.io/); detectors without an SWC entry use the
custom 2xx range to stay clearly separated.
"""
from .access_of_uninitialized_pointer import AccessOfUninitializedPointer
from .arbitrary_call import ArbitraryCall
from .delegatecall import Delegatecall
from .deprecated_standards import DeprecatedStandards
from .detector import Detector
from .divide_before_multiply import DivideBeforeMultiply
from .function_default_visibility import FunctionDefaultVisibility
from .incorrect_unary import IncorrectUnary
from .int_overflow import IntOverflow
from .msgvalue_in_loop import MsgValueInLoop
from .reentrancy import Reentrancy
from .rtlo import RTLO
from .suicidal import Suicidal
from .tautology import Tautology
from .timestamp import TimestampDependence
from .tx_origin import TxOrigin
from .unchecked_return_value import UncheckedReturnValue
from .unchecked_transfer import UncheckedTransfer
from .weak_prng import WeakPRNG

DETECTOR_CLASSES: list[type[Detector]] = [
    AccessOfUninitializedPointer,
    ArbitraryCall,
    Delegatecall,
    DeprecatedStandards,
    DivideBeforeMultiply,
    FunctionDefaultVisibility,
    IncorrectUnary,
    IntOverflow,
    MsgValueInLoop,
    Reentrancy,
    RTLO,
    Suicidal,
    Tautology,
    TimestampDependence,
    TxOrigin,
    UncheckedReturnValue,
    UncheckedTransfer,
    WeakPRNG,
]

# SWC id -> singleton instance (detectors are stateless)
ALL_DETECTORS: dict[int, Detector] = {cls.ID: cls() for cls in DETECTOR_CLASSES}
DETECTOR_IDS: list[int] = sorted(ALL_DETECTORS)
