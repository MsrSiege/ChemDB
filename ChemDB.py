#!/usr/bin/env python
# +-----------------------------------------------------------------------------------------------------------------------+#
# ++ DEVELOPMENT FLAG, PREVENTs __pycache__ CREATION
# +-----------------------------------------------------------------------------------------------------------------------+#
import sys

sys.dont_write_bytecode = True

# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ Imports
# ++---------------------------------------------------------------------------------------------------------------------++#
from logging import DEBUG, FileHandler

from src.fctlib.configfile import GetConfig, GetConfigValue
from src.fctlib.logging import LogLOGGER, SetHandlerLevel
from src.fctlib.quit import QuitExecution
from src.fctlib.threads import RerouteThreadingExcepthook
from src.gui import GuiInitConfig, StartGui
from src.test.unittest import RunUnitTests


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-02-01    fJ      0.1     Created
# ++---------------------------------------------------------------------------------------------------------------------++#
def main():
    LogLOGGER.info(f"\n#++{'-'*114}++#\nStarted execution ...")

    GuiInitConfig()

    # Set logfile logging level according to debug mode switch
    if GetConfigValue("DEBUG", "debug_mode"):
        SetHandlerLevel(ClsHandler=FileHandler, log_level=DEBUG)
    LogLOGGER.info(GetConfig())

    RerouteThreadingExcepthook()

    StartGui()

    LogLOGGER.info(f"\nEnded execution!\n#++{'-'*114}++#")
    QuitExecution()


# +-----------------------------------------------------------------------------------------------------------------------+#
# ++ Software main entrypoint
# +-----------------------------------------------------------------------------------------------------------------------+#
if __name__ == "__main__":
    main()

    # # NOTE: Uncomment sys.excepthook injection under scr.fctlib.logging for unit tests!
    # RunUnitTests()


# +-----------------------------------------------------------------------------------------------------------------------+#
# TODO v1.1:
# +-----------------------------------------------------------------------------------------------------------------------+#
# Implement "Cancel" for threading
# Improve "Cancel" handling in general
# Prevent crashing threads as result of StaleElement errors
# Implement help label and mouseover for all elements
# Change threaded number to don't allow higher than cpu_count()
