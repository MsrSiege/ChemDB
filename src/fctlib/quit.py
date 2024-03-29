# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ Imports
# ++---------------------------------------------------------------------------------------------------------------------++#
from sys import exit

from src.fctlib.selenium import QuitWebDrivers


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-03-04    fJ      1.0     Dev tests: passed ... works as intended
# ++ 24-02-06    fJ      0.2     Added docstring
# ++ 24-02-05    fJ      0.1     Created
# ++---------------------------------------------------------------------------------------------------------------------++#
def QuitExecution():
    """Cleans prior to and terminates app execution."""

    QuitWebDrivers()
    exit()
