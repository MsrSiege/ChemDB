# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ Imports
# ++---------------------------------------------------------------------------------------------------------------------++#
from pathlib import Path
from tkinter import filedialog
from typing import Any

from src.fctlib.converter import DictToSet, DictToTuple
from src.fctlib.logging import LogLOGGER


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-03-04    fJ      2.0     Unit test: passed
# ++ 24-02-25    fJ      1.2     Replaced os.path with pathlib.Path
# ++ 24-02-16    fJ      1.1     Deleted unspecific error handling
# ++ 24-02-14    fJ      1.0     Unit test: passed
# ++ 24-02-14    fJ      0.2     Reworked
# ++ 24-02-08    fJ      0.1     Created
# ++---------------------------------------------------------------------------------------------------------------------++#
def GetFolderPath() -> Path:
    """Returns a folder path from a system file dialog.\n
    - <- | <return> Folder path or None if no folder was selected"""

    folder_path = filedialog.askdirectory()

    if not folder_path:
        LogLOGGER.debug("User didn't select a folder.")

    return Path(folder_path) if folder_path else None


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-03-04    fJ      2.0     Unit test: passed
# ++ 24-03-03    fJ      1.1     Replaced os.path with pathlib.Path
# ++ 24-02-14    fJ      1.0     Unit test: passed
# ++ 24-02-14    fJ      0.2     Reworked
# ++ 24-02-08    fJ      0.1     Created
# ++---------------------------------------------------------------------------------------------------------------------++#
def GetFilePaths(supported_extensions: dict[str, Any]) -> list[Path]:
    """Returns file paths to supported files from a system file dialog.\n
    - -> | <supported_extensions> Supported extensions to show in the file dialog\n
    - <- | <return> List of file paths, empty list if no supported file was selected"""

    file_paths = filedialog.askopenfilenames(filetypes=DictToTuple(supported_extensions))

    if not file_paths:
        LogLOGGER.debug("User didn't select a file.")
        return []

    supported_file_paths = [
        Path(file_path) for file_path in file_paths if Path(file_path).suffix in DictToSet(supported_extensions)
    ]
    if not supported_file_paths:
        LogLOGGER.debug("User didn't select a supported file.")

    return supported_file_paths


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-03-04    fJ      2.0     Unit test: passed
# ++ 24-02-26    fJ      1.2     Excluded hidden (".") and Office owner files ("~$")
# ++ 24-02-25    fJ      1.1     Replaced os.path with pathlib.Path
# ++ 24-02-14    fJ      1.0     Unit test: passed (but cheated ...)
# ++ 24-02-14    fJ      0.3     Reworked
# ++ 24-02-06    fJ      0.2     Added docstring
# ++ 24-02-01    fJ      0.1     Created
# ++---------------------------------------------------------------------------------------------------------------------++#
def GetSupportedFilesFromPath(file_paths: list[Path], supported_extensions: dict[str, Any]) -> list[Path]:
    """Returns a list of supported files from a path.\n
    - -> | <file_paths> List of file paths\n
    - -> | <supported_extensions> Dictionary values\n
    - <- | <return> File paths, empty list if no supported file was selected"""

    supported_extensions = DictToSet(supported_extensions)

    supported_file_paths = [
        PthFile
        for PthFile in file_paths
        if PthFile.suffix.lower() in supported_extensions
        and not PthFile.name.startswith(".")
        and not PthFile.name.startswith("~$")
        and "_OUT" not in PthFile.name
    ]

    if len(supported_file_paths) == 0:
        LogLOGGER.debug(f"No supported files under <{file_paths}> found.")
        return []

    return supported_file_paths
