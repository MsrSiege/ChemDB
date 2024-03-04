# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ Imports
# ++---------------------------------------------------------------------------------------------------------------------++#
from time import process_time, time
from typing import Optional

from src.fctlib.logging import LogLOGGER


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-02-12    fJ      1.0     Dev tests: passed ... works as intended
# ++ 24-02-06    fJ      0.3     Added docstring
# ++ 24-02-05    fJ      0.2     Added type hinting
# ++ 24-02-01    fJ      0.1     Created
# ++---------------------------------------------------------------------------------------------------------------------++#
def GetRunTime(timer: Optional[tuple[float, float]] | None = None) -> tuple[float, float]:
    """Returns and logs execution and process time.\n
    Initialise with >>timer = fctTime.LogRunTime()<<. Log result with >>fctTime.LogRunTime(timer)<<.\n
    - -> | <timer> None, starts timer or (execution start time, process start time)\n
    - <- | <return> Tuple: execution time, process time"""

    if timer is None:
        return (time(), process_time())
    else:
        wall_time = time() - timer[0]
        cpu_time = process_time() - timer[1]
        LogLOGGER.info(f"Wall time: {wall_time:.4f} s, CPU time: {cpu_time:.4f} s")
        return (wall_time, cpu_time)
