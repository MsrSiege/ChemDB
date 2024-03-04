# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ Imports
# ++---------------------------------------------------------------------------------------------------------------------++#
from functools import wraps
from logging import DEBUG, StreamHandler
from time import sleep
from typing import Any, Callable

from src.fctlib.logging import GetHandlerLevel, LogLOGGER, SetHandlerLevel
from src.fctlib.threads import ReturnThread
from src.fctlib.time import GetRunTime


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-02-19    fJ      0.2     Added RetryFailedException
# ++ 24-02-15    fJ      0.1     Created
# ++---------------------------------------------------------------------------------------------------------------------++#
class RetryException(Exception):
    """Custom exception that can be used to trigger a retry."""

    def __init__(self, msg="Retry function call ..."):
        self.msg = msg

    def __str__(self):
        return repr(self.msg)


class RetryFailedException(Exception):
    """Custom exception that can be used to react to a final retry failure."""

    def __init__(self, msg="Final function call retry failed!"):
        self.msg = msg

    def __str__(self):
        return repr(self.msg)


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-03-04    fJ      2.0     Unit test: passed
# ++ 24-03-04    fJ      1.1     Added prolonged delay
# ++ 24-02-13    fJ      1.0     Unit test: passed
# ++ 24-02-12    fJ      0.1     Created
# ++---------------------------------------------------------------------------------------------------------------------++#
def Retry(
    ExcException: Exception = Exception,
    attempts: int = 3,
    delay: int = 1,
) -> Callable[..., Any]:
    """Decorator for retrying function calls in case of specific exceptions.\n
    - -> | <ExcException> Exception name or tuple of names as reason for retry\n
    - -> | <attempts> Total number of tries (not retries)\n
    - -> | <delay> Base delay [s] between tries, gets multiplied by current attempt count to prolong delay\n
    Source: http://www.saltycrane.com/blog/2009/11/trying-out-retry-decorator-python/"""

    def DecoRetry(FunctionInput: Callable[..., Any]) -> Callable[..., Any]:
        # Preserve introspection
        @wraps(wrapped=FunctionInput)
        def WrapRetry(*args: Any, **kwargs: Any) -> Any:
            attempt = 1
            while attempt < attempts:
                # First (n-1) tries
                try:
                    return FunctionInput(*args, **kwargs)
                except ExcException as Error:
                    LogLOGGER.info(
                        f"Attempt {attempt}/{attempts} for <{FunctionInput.__name__}> failed: <{Error}>! Will retry ..."
                    )
                    sleep(delay * attempt)
                    attempt += 1
            # Final try
            try:
                return FunctionInput(*args, **kwargs)
            except ExcException as Error:
                LogLOGGER.error(f"Final attempt for <{FunctionInput.__name__}> failed: <{Error}>!")
                raise RetryFailedException()

        return WrapRetry

    return DecoRetry


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-02-13    fJ      1.0     Dev tests: passed ... works as intended
# ++ 24-02-12    fJ      0.1     Created
# ++---------------------------------------------------------------------------------------------------------------------++#
def DebugLogging(FunctionInput: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator for logging function signature and return value and setting the log level to DEBUG."""

    # Preserve introspection
    @wraps(wrapped=FunctionInput)
    def WrapDebugLogging(*args: Any, **kwargs: Any) -> Any:
        # Store current log level and temporarily change it to DEBUG
        curr_log_level = GetHandlerLevel(StreamHandler)
        SetHandlerLevel(ClsHandler=StreamHandler, log_level=DEBUG)

        # Log function signature and return result
        args_repr = [repr(arg) for arg in args]
        kwargs_repr = [f"{key}={repr(value)}" for key, value in kwargs.items()]
        signature = ", ".join(args_repr + kwargs_repr)
        LogLOGGER.debug(msg=f"Calling <{FunctionInput.__name__}({signature})>")
        result = FunctionInput(*args, **kwargs)
        LogLOGGER.debug(msg=f"<{FunctionInput.__name__}()> returned <{repr(result)}>")

        # Restore original log level
        SetHandlerLevel(ClsHandler=StreamHandler, log_level=curr_log_level)

        return result

    return WrapDebugLogging


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-02-13    fJ      1.0     Dev tests: passed ... works as intended
# ++ 24-02-12    fJ      0.1     Created
# ++---------------------------------------------------------------------------------------------------------------------++#
def Timer(FunctionInput: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator for logging execution and process time of a function."""

    # Preserve introspection
    @wraps(wrapped=FunctionInput)
    def WrapTimer(*args: Any, **kwargs: Any) -> Any:
        # Measure functions execution and process time and return result
        timer = GetRunTime()
        result = FunctionInput(*args, **kwargs)
        GetRunTime(timer)
        return result

    return WrapTimer


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-02-21    fJ      0.1     Created
# ++---------------------------------------------------------------------------------------------------------------------++#
def RunThreaded(FunctionInput: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to run a function in a separate thread.\n
    Source: https://github.com/cocuni80/thread_decorator/"""

    # Preserve introspection
    @wraps(wrapped=FunctionInput)
    def WrapRunThreaded(*args: Any, **kwargs: Any) -> Any:
        RthThread = ReturnThread(target=FunctionInput, args=args, kwargs=kwargs)
        RthThread.start()
        return RthThread

    return WrapRunThreaded
