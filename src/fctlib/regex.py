# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ Imports
# ++---------------------------------------------------------------------------------------------------------------------++#
from collections import OrderedDict
from re import Pattern, compile, findall, match

# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ Module variables
# ++---------------------------------------------------------------------------------------------------------------------++#
# Valid CAS number pattern
RepCASNUMBER = compile(r"^\d{1,7}-\d{1,2}-\d{1}$")
# Valid decimal pattern
RepDECIMALCOMMA = compile(r".*\d*,\d+.*")
# Valid hazard statements pattern
RepHAZARDS = compile(r"H\d{3}(?:\s*\+\s*H\d{3})*")
# Valid precautionary statements pattern
RepPRECAUTIONARIES = compile(r"P\d{3}(?:\s*\+\s*P\d{3})*")


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-02-16    fJ      2.0     Unit test: passed
# ++ 24-02-16    fJ      1.1     Added actual CAS checksum checking
# ++ 24-02-12    fJ      1.0     Unit test: passed
# ++ 24-02-06    fJ      0.2     Added docstring
# ++ 24-02-01    fJ      0.1     Created
# ++---------------------------------------------------------------------------------------------------------------------++#
def CheckCasNo(str_input: str) -> bool:
    """Checks if a string represents a valid CAS pattern including CAS checksum check.\n
    - -> | <str_input> String to check\n
    - <- | <return> Boolean CAS number validity"""

    if not isinstance(str_input, str):
        return False

    if not RepCASNUMBER.match(str_input):
        return False

    # Check for CAS checksum correctness
    cas_string = "".join(filter(str.isdigit, str_input))
    return sum(int(char) * (i) for i, char in enumerate(reversed(cas_string))) % 10 == int(cas_string[-1])


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-02-12    fJ      1.0     Unit test: passed
# ++ 24-02-06    fJ      0.2     Added docstring
# ++ 24-02-01    fJ      0.1     Created
# ++---------------------------------------------------------------------------------------------------------------------++#
def GetDelocalisedDecimals(str_input: str) -> str:
    """Returns a string with decimal separators replaced by dots.\n
    - -> | <str_input> String possibly with comma as decimal separators\n
    - <- | <return> String with replaced decimal separators"""

    return str_input.replace(",", ".") if match(RepDECIMALCOMMA, str_input) else str_input


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-02-12    fJ      1.0     Unit test: passed
# ++ 24-02-12    fJ      0.4     Prevent duplicate collection
# ++ 24-02-12    fJ      0.3     Merged H and P statement getter
# ++ 24-02-06    fJ      0.2     Added docstring
# ++ 24-02-03    fJ      0.1     Created
# ++---------------------------------------------------------------------------------------------------------------------++#
def GetGhsStatements(str_input: str, RePattern: Pattern) -> str:
    """Returns a string of all unique whitespace-free GHS' statements found in the input string according to the pattern.\n
    - -> | <str_input> String to get GHS statements\n
    - -> | <RePattern> Regex pattern to find GHS statements with\n
    - <- | <return> String with GHS statements"""

    # Get unique whitespace-free matches from the input string
    matches: list[str] = findall(RePattern, str_input)
    no_whitespace_matches = [match.replace(" ", "") for match in matches]
    unique_matches = list(OrderedDict.fromkeys(no_whitespace_matches))

    return "|".join(unique_matches)
