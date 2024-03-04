# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ Imports
# ++---------------------------------------------------------------------------------------------------------------------++#
from collections.abc import Iterable
from typing import Any, Callable


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-02-12    fJ      1.0     Unit test: passed
# ++ 24-02-12    fJ      0.3     Generalised and pythonised
# ++ 24-02-06    fJ      0.2     Added docstring
# ++ 24-02-06    fJ      0.1     Created
# ++---------------------------------------------------------------------------------------------------------------------++#
def DictToSet(dict_input: dict[Any, Any]) -> set[Any]:
    """Converts a dictionary into a set of its values, unpacked if possible.\n
    - -> | <dict_input> Dictionary to convert\n
    - <- | <return> Converted set"""

    if dict_input is None:
        return set()

    set_output = set()
    for values in dict_input.values():
        if isinstance(values, Iterable) and not isinstance(values, (str, bytes)):
            set_output.update(values)
        else:
            set_output.add(values)
    return set_output


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-02-12    fJ      1.0     Unit test: passed
# ++ 24-02-12    fJ      0.3     Generalised and pythonised
# ++ 24-02-06    fJ      0.2     Added docstring
# ++ 24-02-06    fJ      0.1     Created
# ++---------------------------------------------------------------------------------------------------------------------++#
def DictToTuple(dict_input: dict[Any, Any]) -> tuple[Any, ...]:
    """Converts a dictionary into a tuple of its key-value pairs.\n
    - -> | <dict_input> Dictionary to convert\n
    - <- | <return> Converted tuple"""

    if dict_input is None:
        return ()

    return tuple((key, value) for key, value in dict_input.items())


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-02-15    fJ      1.0     Unit test: passed
# ++ 24-02-15    fJ      0.1     Created
# ++---------------------------------------------------------------------------------------------------------------------++#
def TryConvert(value: Any, datatype: Callable[[Any], Any]) -> Any:
    """Tries converting a value (not None) into a given target type.\n
    - -> | <value> Value to convert\n
    - -> | <target_datatype> Datatype to convert the value to\n
    - <- | <return> Converted value or the original value if the conversion failed"""

    if value is None:
        return None

    try:
        return datatype(value)
    except (ValueError, TypeError):
        return value
