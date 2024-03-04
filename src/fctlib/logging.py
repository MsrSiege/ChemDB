# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ Imports
# ++---------------------------------------------------------------------------------------------------------------------++#
import logging
import sys
from traceback import extract_tb
from types import TracebackType
from typing import Callable

from src.settings import PthLOGFILE


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-02-13    fJ      1.0     Dev tests: passed ... works as intended
# ++ 24-02-13    fJ      0.1     Created
# ++---------------------------------------------------------------------------------------------------------------------++#
class FunctionHandler(logging.Handler):
    """Custom logging handler for using a function to emit log records."""

    def __init__(self):
        super().__init__()
        self.func = None

    def set_function(self, FunctionInput: Callable):
        """Sets the function to emit the log record to."""
        self.func = FunctionInput

    def emit(self, record: logging.LogRecord):
        """Emits a log record to the function set by <set_function()>."""
        if self.func is not None:
            log_entry = f"{self.format(record)}\n"
            self.func(log_entry)


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-02-13    fJ      1.0     Dev tests: passed ... works as intended
# ++ 24-02-13    fJ      0.1     Created
# ++---------------------------------------------------------------------------------------------------------------------++#
class UserLevelFilter(logging.Filter):
    """Filters log records by level 'USERINFO' (35) and 'USERERROR' (45)."""

    def filter(self, record):
        return record.levelno in [logging.USERINFO, logging.USERERROR]


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-03-04    fJ      1.0     Dev tests: passed ... works as intended
# ++ 24-03-01    fJ      0.1     Created
# ++---------------------------------------------------------------------------------------------------------------------++#
def LogUnhandledExceptionsHook(ExcType: type[BaseException], ExcValue: BaseException, ExcTraceback: TracebackType):
    """Creates a custom global exception hook for logging uncaught exceptions.\n
    - -> | <ExcType> Exception type\n
    - -> | <ExcValue> Exception\n
    - -> | <ExcTraceback> Exception traceback"""

    separator = f"#++{'-'*114}++#"
    traceback = "".join(extract_tb(ExcTraceback).format())

    LogLOGGER.critical(f"\n{separator}\nUnhandled exception!{ExcType}:{ExcValue}\n{traceback}\n{separator}")


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-03-04    fJ      2.0     Dev tests: passed ... works as intended
# ++ 24-02-16    fJ      1.1     Changed raising errors on allready existing logging levels to just skipping
# ++ 24-02-13    fJ      1.0     Dev tests: passed ... works as intended
# ++ 24-02-13    fJ      0.1     Created
# ++---------------------------------------------------------------------------------------------------------------------++#
def AddCustomLoggingLevel(level_name: str, level_num: int, method_name: str | None = None):
    """Adds a new logging level to the logging module and the currently configured logging class.\n
    - -> | <level_name> Logging level name\n
    - -> | <level_num> Logging level numeric\n
    - -> | <method_name> Convenience method for logging the class returned by logging.getLoggerClass()\n
    Source: https://stackoverflow.com/a/35804945"""

    method_name = level_name.lower() if method_name is None else method_name

    # Skip adding if logging level or the convenience methed allready exists
    if hasattr(logging, level_name) or hasattr(logging, method_name) or hasattr(logging.getLoggerClass(), method_name):
        print("[INFO|logging:AddLoggingLevel] Logging level allready exists.")
        return

    # Function to add to logging for the new level
    def logForLevel(self, message, *args, **kwargs):
        if self.isEnabledFor(level_num):
            self._log(level_num, message, args, **kwargs)

    # Function to add to the root logger for the new level
    def logToRoot(message, *args, **kwargs):
        logging.log(level_num, message, *args, **kwargs)

    # Add new logging level and logging functions
    logging.addLevelName(level_num, level_name)
    setattr(logging, level_name, level_num)
    setattr(logging.getLoggerClass(), method_name, logForLevel)
    setattr(logging, method_name, logToRoot)


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-03-04    fJ      2.0     Dev tests: passed ... works as intended
# ++ 24-02-25    fJ      1.2     Replaced os.path with pathlib.Path
# ++ 24-02-16    fJ      1.1     Deleted unspecific error handling
# ++ 24-02-13    fJ      1.0     Dev tests: passed ... works as intended
# ++ 24-02-13    fJ      0.3     Added FunctionHandler
# ++ 24-02-12    fJ      0.2     Reworked
# ++ 24-02-01    fJ      0.1     Created
# ++---------------------------------------------------------------------------------------------------------------------++#
def SetRootLogger() -> logging.Logger:
    """Creates and configures the root logger for the app. Logs are written to the console and to a file.\n
    Includes: StreamHandler, FileHandler, FunctionHandler\n
    - <- | <return> Root logger with the appended handlers"""

    AddCustomLoggingLevel("USERINFO", 25, "userinfo")
    AddCustomLoggingLevel("USERERROR", 45, "usererror")

    # Log levels: NOTSET = 0 | DEBUG = 10 | INFO = 20 | WARNING = 30 | ERROR = 40 | CRITICAL = 50
    log_level = {
        "console": logging.USERINFO,
        "file": logging.INFO,
        "user": logging.USERINFO,
    }

    base_log_format = "[%(levelname)s|%(module)s:%(funcName)s] %(message)s"
    file_log_format = f"%(asctime)s {base_log_format}"
    function_log_format = "%(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    LogLogger = logging.getLogger("CentralLogger")
    # Set minimal logging level of the root logger
    # NOTE: This needs to be equal to the lowest individual log levels of the handlers
    LogLogger.setLevel(min(log_level.values()))

    # Create and setup the StreamHandler for logging to the console
    HdlLogConsole = logging.StreamHandler()
    HdlLogConsole.setFormatter(logging.Formatter(fmt=base_log_format))
    HdlLogConsole.setLevel(log_level["console"])
    LogLogger.addHandler(HdlLogConsole)

    # Create and setup the FileHandler for logging to the logfile
    PthLOGFILE.parent.mkdir(parents=True, exist_ok=True)
    HdlLogFile = logging.FileHandler(filename=PthLOGFILE, mode="a", encoding="utf-8")
    HdlLogFile.setFormatter(logging.Formatter(fmt=file_log_format, datefmt=date_format))
    HdlLogFile.setLevel(log_level["file"])
    LogLogger.addHandler(HdlLogFile)

    # Create and setup the FunctionHandler for using a function to log
    HdlLogFunction = FunctionHandler()
    HdlLogFunction.setFormatter(logging.Formatter(fmt=function_log_format))
    HdlLogFunction.setLevel(log_level["user"])
    HdlLogFunction.addFilter(UserLevelFilter())
    LogLogger.addHandler(HdlLogFunction)

    return LogLogger


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ Global logger
# ++---------------------------------------------------------------------------------------------------------------------++#
LogLOGGER = SetRootLogger()
"""Root logger for console and logfile logging."""

# Uses a custom global exception hook for logging uncaught exceptions.
sys.excepthook = LogUnhandledExceptionsHook


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-03-04    fJ      2.0     Dev tests: passed ... works as intended
# ++ 24-02-16    fJ      1.1     Deleted unspecific error handling
# ++ 24-02-12    fJ      1.0     Dev tests: passed ... works as intended
# ++ 24-02-09    fJ      0.1     Created
# ++---------------------------------------------------------------------------------------------------------------------++#
def GetHandlerLevel(ClsHandler: logging.Handler) -> int:
    """Returns the current log level of a log handler.\n
    - -> | <ClsHandler> logging.StreamHandler or logging.FileHandler\n
    - <- | <return> log level, -1 if no handler of that instance was found"""

    return next((HdlHandler.level for HdlHandler in LogLOGGER.handlers if isinstance(HdlHandler, ClsHandler)), -1)


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-03-04    fJ      2.0     Dev tests: passed ... works as intended
# ++ 24-02-16    fJ      1.1     Deleted unspecific error handling
# ++ 24-02-12    fJ      1.0     Dev tests: passed ... works as intended
# ++ 24-02-09    fJ      0.1     Created
# ++---------------------------------------------------------------------------------------------------------------------++#
def GetLowestHandlerLevel() -> int:
    """Returns the currently lowest log level of the global logger handlers.\n
    - <- | <return> log level, -1 if no handler of that instance was found"""

    return min((HdlHandler.level for HdlHandler in LogLOGGER.handlers), default=-1)


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-03-04    fJ      2.0     Dev tests: passed ... works as intended
# ++ 24-02-16    fJ      1.1     Deleted unspecific error handling
# ++ 24-02-12    fJ      1.0     Dev tests: passed ... works as intended
# ++ 24-02-09    fJ      0.1     Created
# ++---------------------------------------------------------------------------------------------------------------------++#
def SetHandlerLevel(ClsHandler: logging.Handler, log_level: int):
    """Sets the log level of a log handler and, if necessary, the root logger.\n
    - -> | <ClsHandler> logging.StreamHandler or logging.FileHandler\n
    - -> | <log_levels> NOTSET = 0 | DEBUG = 10 | INFO = 20 | WARNING = 30 | ERROR = 40 | CRITICAL = 50"""

    for HdlHandler in LogLOGGER.handlers:
        if isinstance(HdlHandler, ClsHandler):
            HdlHandler.setLevel(log_level)
            SetLowestHandlerLevelInRoot()
            return


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-03-04    fJ      2.0     Dev tests: passed ... works as intended
# ++ 24-02-16    fJ      1.1     Deleted unspecific error handling
# ++ 24-02-12    fJ      1.0     Dev tests: passed ... works as intended
# ++ 24-02-09    fJ      0.1     Created
# ++---------------------------------------------------------------------------------------------------------------------++#
def SetLowestHandlerLevelInRoot():
    """Sets the log level of the root logger to the lowest log level of it's handlers."""
    LogLOGGER.setLevel(GetLowestHandlerLevel())
    return
