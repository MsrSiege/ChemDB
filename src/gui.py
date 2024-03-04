# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ Imports
# ++---------------------------------------------------------------------------------------------------------------------++#
from ctypes import windll
from multiprocessing import cpu_count
from pathlib import Path
from platform import system
from threading import Event, Thread
from typing import Optional
from webbrowser import open

from customtkinter import BooleanVar, CTk, StringVar, Variable, set_appearance_mode, set_default_color_theme
from PIL import ImageTk

import src.fctlib.ctk as fctCtk
from src.fctlib.configfile import GetConfigValue, StoreConfig
from src.fctlib.io import GetFilePaths, GetSupportedFilesFromPath
from src.fctlib.logging import FunctionHandler, LogLOGGER
from src.main import AnalyseFiles, ProcessFiles
from src.settings import (
    APP_AUTHOR,
    APP_GITHUB_LINK,
    APP_MAIL,
    APP_NAME,
    APP_VERSION,
    GUI_PADDING,
    SUPPORTED_EXTENSIONS,
    PthASSET_FILEDIALOG,
    PthASSET_ICON,
    PthCONFIG_FILE,
)

# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ Module variables
# ++---------------------------------------------------------------------------------------------------------------------++#
GUI_PADDING_SML = int(GUI_PADDING * 0.5)
""" GUI small padding."""

EvtCANCEL_PROCESSING = Event()
"""Event to cancel processing."""


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-03-04    fJ      1.0     Dev tests: passed ... works as intended
# ++ 24-03-03    fJ      0.3     Placeholder prevents updates of StvParentFolder on user input, so we got rid of it
# ++ 24-02-08    fJ      0.2     Changed so placeholder text can be used
# ++ 24-02-08    fJ      0.1     Created
# ++---------------------------------------------------------------------------------------------------------------------++#
def GuiSetFilePaths():
    """Sets the folder path text widget."""

    file_paths = GetFilePaths(SUPPORTED_EXTENSIONS)
    PthParent = next((PthFile.parent for PthFile in file_paths if PthFile.is_file()), None)
    if not file_paths or PthParent is None:
        return

    # Set two CTk variable holders so that we have access to the file path list as well as the parent folder
    fctCtk.SetCtkVar(CtkWidget=VarFilePaths, value=file_paths)
    fctCtk.SetCtkVar(CtkWidget=StvParentFolder, value=PthParent)
    return


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-03-04    fJ      1.0     Dev tests: passed ... works as intended
# ++ 24-03-03    fJ      0.3     Moved file selection here to accomodate for FilePaths (before: FolderPaths)
# ++ 24-02-26    fJ      0.2     Reworked to accomodate for splitted AnalyseFiles()/ProcessFiles()
# ++ 24-02-10    fJ      0.1     Created, combined from ThreadedAnalyseFiles() and ThreadedProcessFiles()
# ++---------------------------------------------------------------------------------------------------------------------++#
def GuiExecute(argument: str = None):
    """Run a function in separate thread to separate it from the GUI logic.\n
    The function is executed as daemon to ensure it terminates itself or gets terminated on main thread termination.\n
    - -> | <argument> Process to start, valid: analysis | processing"""

    folder_path: str = fctCtk.GetCtkVar(StvParentFolder)
    if fctCtk.GetCtkVar(BlvAllFiles):
        file_paths = [PthFile for PthFile in Path(folder_path).iterdir() if PthFile.is_file()] if folder_path else []
    else:
        file_paths = [Path(file_path) for file_path in fctCtk.GetCtkVar(VarFilePaths)]
    PthParent = next((PthFile.parent for PthFile in file_paths if PthFile.is_file()), None)

    if not file_paths or PthParent is None:
        return EvaluateOnError(PthFolder=PthParent, error="Invalid path!")

    # This is necessary because the User can choose files via file dialog and change the folder path afterwards. This would
    # lead to inconsistencies when one of both paths are used later.
    if not fctCtk.GetCtkVar(BlvAllFiles) and Path(folder_path) != PthParent:
        return EvaluateOnError(
            PthFolder=PthParent, error="Deviation in given paths! Use the file dialog to choose single files."
        )

    compatible_files = GetSupportedFilesFromPath(file_paths=file_paths, supported_extensions=SUPPORTED_EXTENSIONS)
    if not compatible_files:
        return EvaluateOnError(PthFolder=PthParent, error="No compatible files found!")

    kwargs = {}
    if argument == "analysis":
        target = AnalyseFiles
        kwargs["file_paths"] = compatible_files
    elif argument == "processing":
        if EvtCANCEL_PROCESSING.is_set():
            EvtCANCEL_PROCESSING.clear()

        target = ProcessFiles
        kwargs["file_paths"] = compatible_files
        kwargs["EvtCancel"] = EvtCANCEL_PROCESSING
        kwargs["run_threaded"] = bool(fctCtk.GetCtkVar(BlvRunThreaded))

    ThrExecuteMain = Thread(target=target, kwargs=kwargs, daemon=True)
    ThrExecuteMain.start()


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-03-04    fJ      1.0     Dev tests: passed ... works as intended
# ++ 24-02-11    fJ      0.1     Created
# ++---------------------------------------------------------------------------------------------------------------------++#
def GuiToggleExecutionLock(force_enable: Optional[bool] = False, force_disable: Optional[bool] = False):
    """Toggles widget states when a function is executed by the GUI or the execution ended by the function.\n
    - -> | <force_enable> Switch to force enabling widget states\n
    - -> | <force_disable> Switch to force disabling widget states"""

    widget_list = [
        EntFilePath,
        ChbAllFiles,
        BtnAnalyseFiles,
        BtnProcessFiles,
        ChbQueryChemInfo,
        ChbQueryPubChem,
        ChbQueryGestis,
        ChbRunThreaded,
        EntMaxThreads,
    ]
    fctCtk.ToggleWidgetState(CtkWidgets=widget_list, force_enable=force_enable, force_disable=force_disable)


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-03-04    fJ      1.0     Dev tests: passed ... works as intended
# ++ 24-02-21    fJ      0.2     Reworked
# ++ 24-02-11    fJ      0.1     Created
# ++---------------------------------------------------------------------------------------------------------------------++#
def EvaluateOnError(PthFolder: Path, error: str, show_in_gui: Optional[bool] = True):
    """Evaluate the processing report on errors and set the GUI accordingly.\n
    - -> | <PthFolder> Current folder path for error logging\n
    - -> | <error> Error message to log\n
    - -> | <show_in_gui> Switch to show "Error!" in GUI or not"""

    LblHideAnalysis.lift()
    LblHideProgress.lift()
    fctCtk.SetCtkVar(CtkWidget=StvCurrentJob, value="Error!" if show_in_gui else str())
    SetWdgPrinterText(print="", clear_printer=True)
    LogLOGGER.warning(f"USERINFO triggered by user-provided folder path <{PthFolder}>:")
    LogLOGGER.userinfo(error)
    GuiToggleExecutionLock(force_enable=True)
    return


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-03-04    fJ      1.0     Dev tests: passed ... works as intended
# ++ 24-02-21    fJ      0.2     Reworked
# ++ 24-02-11    fJ      0.1     Created
# ++---------------------------------------------------------------------------------------------------------------------++#
def EvaluateAnalysis(report: dict[str, int | str]):
    """Evaluate the processing report after the analysis and set the GUI accordingly.\n
    - -> | <report> Report dictionary"""

    LblHideProgress.lift()
    SetWdgPrinterText(print="", clear_printer=True)
    fctCtk.SetCtkVar(CtkWidget=StvCurrentJob, value="File Analysis:")
    fctCtk.SetCtkVar(CtkWidget=StvFilesCnt, value=report["files_count"])
    fctCtk.SetCtkVar(CtkWidget=StvChemsCnt, value=report["chems_count"])
    fctCtk.SetCtkVar(CtkWidget=StvCasCnt, value=report["cas_count"])
    LblHideAnalysis.lower()
    GuiToggleExecutionLock(force_enable=True)
    return


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-03-04    fJ      1.0     Dev tests: passed ... works as intended
# ++ 24-02-21    fJ      0.2     Reworked
# ++ 24-02-11    fJ      0.1     Created
# ++---------------------------------------------------------------------------------------------------------------------++#
def EvaluateProzessing(report: dict[str, int | str | None] | None, final: bool = False):
    """Evaluate the processing report after file prozessing and set the GUI accordingly.\n
    - -> | <report> Report dictionary or None if threading is currently initialised\n
    - -> | <final> Switch to indicate if the report is during or at the end of processing"""

    if report is None and not final:
        fctCtk.SetCtkVar(CtkWidget=StvCurrentJob, value="Preparing ...")
        SetWdgPrinterText(print="", clear_printer=True)
        LogLOGGER.userinfo("Preparing for processing ...")
        return

    if report is None and final:
        fctCtk.SetCtkVar(CtkWidget=StvCurrentJob, value="Cleaning ...")
        LogLOGGER.userinfo("Cleaning after processing ...")
        return

    fctCtk.SetCtkVar(CtkWidget=StvCurrentJob, value="Working on:" if not final else "Finished!")
    fctCtk.SetCtkVar(CtkWidget=StvFilesCnt, value=f"{report['file_no']}|{report['files_count']}")
    fctCtk.SetCtkVar(CtkWidget=StvChemsCnt, value=f"{report['chem_no']}|{report['chems_count']}")
    fctCtk.SetCtkVar(CtkWidget=StvCasCnt, value=f"{report['cas_no']}|{report['cas_count']}")
    fctCtk.SetCtkVar(CtkWidget=PrbProgress, value=int(report["chem_no"]) / int(report["chems_count"]))
    LblHideAnalysis.lower()
    LblHideProgress.lower()

    if not final:
        LogLOGGER.userinfo(
            f"Working on File {report['file_no']}|{report['files_count']} ({report['file_name']}): Chemical {report['chem_no']}|{report['chems_count']} (<{report['chem_id']}>) ..."
        )
        return

    LogLOGGER.userinfo(f"Finished after {report["execution_time"]:.2f} s!")
    LblHideProgress.lift()
    GuiToggleExecutionLock(force_enable=True)
    return


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-03-04    fJ      1.0     Dev tests: passed ... works as intended
# ++ 24-02-11    fJ      0.1     Created
# ++---------------------------------------------------------------------------------------------------------------------++#
def GuiToggleLog():
    """Toggles the visibility of the Printer textbox."""

    printer_visible = fctCtk.ToggleWidgetVisibility(CtkWidget=TxbPrinter)
    BtnToggleLog.configure(text="Hide Log" if printer_visible else "Show Log")


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-03-04    fJ      1.0     Dev tests: passed ... works as intended
# ++ 24-02-26    fJ      0.1     Created
# ++---------------------------------------------------------------------------------------------------------------------++#
def GuiCancel():
    global EvtCANCEL_PROCESSING
    if not EvtCANCEL_PROCESSING.is_set():
        EvtCANCEL_PROCESSING.set()


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-03-04    fJ      1.0     Dev tests: passed ... works as intended
# ++ 24-02-09    fJ      0.1     Created
# ++---------------------------------------------------------------------------------------------------------------------++#
def SetWdgPrinterText(print: str | list[str], clear_printer: bool = False):
    """Sets the text of the Printer textbox.\n
    - -> | <print> Text to print\n
    - -> | <clear_printer> Switch to clear the Printer textbox before printing"""

    if clear_printer:
        TxbPrinter.delete(index1="0.0", index2="end")

    if isinstance(print, str):
        TxbPrinter.insert(index="0.0", text=print)
    else:
        TxbPrinter.insert(index="0.0", text="\n".join(print))


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-02-20    fJ      1.0     Dev tests: passed ... works as intended
# ++ 24-02-20    fJ      0.2     Added mail string concealment
# ++ 24-02-10    fJ      0.1     Created
# ++---------------------------------------------------------------------------------------------------------------------++#
def MailAuthor():
    """Opens the systems default email programm to write the apps' author."""

    app_mail = APP_MAIL.replace("[at]", "@").replace("[dot]", ".")
    open(url=f"mailto:{app_mail}", new=2, autoraise=True)


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-02-20    fJ      1.0     Dev tests: passed ... works as intended
# ++ 24-02-10    fJ      0.1     Created
# ++---------------------------------------------------------------------------------------------------------------------++#
def OpenGitHubRepository():
    """Opens the apps' GitHub repository in the systems default browser."""

    open(url=APP_GITHUB_LINK, new=2, autoraise=True)


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ GUI setup
# ++---------------------------------------------------------------------------------------------------------------------++#
# CustomTKinter is allready DPI aware (s. https://customtkinter.tomschimansky.com/documentation/scaling), but its own
# setting will mess with the apps' rescaling function ctk.ToggleWidgetVisibility(). We set it to a broader scope.
if system() == "Windows":
    windll.user32.SetProcessDPIAware()

# GUI color theme. Options: blue (default), dark-blue, green
set_default_color_theme("green")
set_appearance_mode("light")

# Initialise GUI
CtkGui = CTk()
CtkGui.title(APP_NAME)
CtkGui.geometry(f"{800}x{500}")
CtkGui.minsize(600, 350)
CtkGui.wm_iconbitmap()
CtkGui.iconphoto(False, ImageTk.PhotoImage(file=PthASSET_ICON))

CtkGui.grid_columnconfigure((0, 1), weight=1)
CtkGui.grid_rowconfigure(2, weight=1)

# Main: Label Header
LblHeader = fctCtk.CtkLabel(
    Widget={
        "master": CtkGui,
        "base_size": fctCtk.STD_SIZE * 2,
        "fg_color": ["gray75", "gray25"],
        "text": APP_NAME,
        "font_bold": True,
    },
    Grid={
        "row": 0,
        "column": 0,
        "padx": GUI_PADDING,
        "pady": GUI_PADDING,
        "sticky": "new",
        "columnspan": 2,
    },
)
# Main: TabView
TabMain = fctCtk.CtkTabView(
    Widget={
        "master": CtkGui,
        "text": ["Processing", "Settings"],
        "font_bold": True,
    },
    Grid={
        "row": 1,
        "column": 0,
        "padx": GUI_PADDING,
        "pady": (GUI_PADDING_SML, 0),
        "sticky": "nsew",
        "columnspan": 2,
    },
)
# Main: Tab 1
TabProcessing = TabMain.tab("Processing")
TabProcessing.grid_columnconfigure(1, weight=1)
TabProcessing.grid_rowconfigure(4, weight=1)

# Main -> Tab 1: Label Folder Path
LblFolderPath = fctCtk.CtkLabel(
    Widget={
        "master": TabProcessing,
        "width": 120,
        "anchor": "w",
        "text": "Folder Path:",
        "font_bold": True,
    },
    Grid={
        "row": 0,
        "column": 0,
        "padx": GUI_PADDING_SML,
        "pady": GUI_PADDING_SML,
    },
)
# Main -> Tab 1: Frame File Paths
FrmFilePaths = fctCtk.CtkFrame(
    Widget={
        "master": TabProcessing,
        "fg_color": ["gray80", "gray20"],
    },
    Grid={
        "row": 0,
        "column": 1,
        "padx": GUI_PADDING_SML,
        "pady": GUI_PADDING_SML,
        "colconfig": 0,
    },
)
# Main -> Tab 1 -> Frame 1: Entry Field File Paths
VarFilePaths = Variable()
"""Stores file paths selected during file dialog."""
StvParentFolder = StringVar()
"""Stores parent folder path selected during file dialog."""
EntFilePath = fctCtk.CtkEntry(
    Widget={
        "master": FrmFilePaths,
        "height": 30,
        "textvariable": StvParentFolder,
        "font_family": "Courier New",
        "font_bold": True,
    },
    Grid={
        "row": 0,
        "column": 0,
        "padx": (GUI_PADDING_SML, 0),
        "pady": GUI_PADDING_SML,
    },
)
# Main -> Tab 1 -> Frame 1: Button File Paths
BtnFileDialog = fctCtk.CtkButton(
    Widget={
        "master": FrmFilePaths,
        "text": "Open ...",
        "PthImage": PthASSET_FILEDIALOG,
        "font_bold": True,
        "FncCommand": GuiSetFilePaths,
    },
    Grid={
        "row": 0,
        "column": 1,
        "padx": (0, GUI_PADDING_SML),
        "pady": GUI_PADDING_SML,
    },
)
# Main -> Tab 1: Checkbox All Files
BlvAllFiles = BooleanVar()
ChbAllFiles = fctCtk.CtkCheckbox(
    Widget={
        "master": TabProcessing,
        "base_size": fctCtk.STD_SIZE - 2,
        "width": 1,
        "text": "All Files",
        "variable": BlvAllFiles,
        "font_bold": True,
    },
    Grid={
        "row": 1,
        "column": 0,
        "padx": int(GUI_PADDING * 1.5),
        "pady": GUI_PADDING_SML,
    },
)

# Main -> Tab 1: Frame Files
FrmFiles = fctCtk.CtkFrame(
    Widget={
        "master": TabProcessing,
    },
    Grid={
        "row": 1,
        "column": 1,
        "padx": GUI_PADDING_SML,
        "pady": GUI_PADDING_SML,
        "colconfig": (0, 1),
    },
)
# Main -> Tab 1 -> Frame 2: Button Analyse Files
BtnAnalyseFiles = fctCtk.CtkButton(
    Widget={
        "master": FrmFiles,
        "text": "Analyse Files",
        "font_bold": True,
        "FncCommand": lambda: GuiExecute("analysis"),
    },
    Grid={
        "row": 0,
        "column": 0,
        "padx": (0, GUI_PADDING_SML),
        "pady": 0,
    },
)
# Main -> Tab 1 -> Frame 2: Button Process Files
BtnProcessFiles = fctCtk.CtkButton(
    Widget={
        "master": FrmFiles,
        "text": "Process Files",
        "font_bold": True,
        "FncCommand": lambda: GuiExecute("processing"),
    },
    Grid={
        "row": 0,
        "column": 1,
        "padx": (GUI_PADDING_SML, 0),
        "pady": 0,
    },
)
# Main -> Tab 1: Label File Analysis
StvCurrentJob = StringVar()
LblCurrentJob = fctCtk.CtkLabel(
    Widget={
        "master": TabProcessing,
        "width": 1,
        "anchor": "w",
        "text": "File Analysis:",
        "font_bold": True,
        "textvariable": StvCurrentJob,
    },
    Grid={
        "row": 2,
        "column": 0,
        "padx": GUI_PADDING_SML,
        "pady": GUI_PADDING_SML,
    },
)
# Main -> Tab 1: Frame Analysis
FrmAnalysis = fctCtk.CtkFrame(
    Widget={
        "master": TabProcessing,
    },
    Grid={
        "row": 2,
        "column": 1,
        "padx": GUI_PADDING_SML,
        "pady": GUI_PADDING_SML,
        "colconfig": (0, 1, 2),
    },
)
# Main -> Tab 1 -> Frame 3: Frame Analyse Files
FrmAnalyseFiles = fctCtk.CtkFrame(
    Widget={
        "master": FrmAnalysis,
    },
    Grid={
        "row": 2,
        "column": 0,
        "padx": (0, GUI_PADDING_SML),
        "pady": 0,
        "colconfig": 0,
    },
)
# # Main -> Tab 1 -> Frame 3.1: Label Files Count
LblFiles = fctCtk.CtkLabel(
    Widget={
        "master": FrmAnalyseFiles,
        "base_size": fctCtk.STD_SIZE - 2,
        "width": 1,
        "text": "Valid Files",
        "fg_color": ["gray80", "gray20"],
        "font_bold": True,
    },
    Grid={
        "row": 0,
        "column": 0,
        "padx": (GUI_PADDING_SML, 0),
        "pady": GUI_PADDING_SML,
    },
)
StvFilesCnt = StringVar()
LblFilesCnt = fctCtk.CtkLabel(
    Widget={
        "master": FrmAnalyseFiles,
        "base_size": fctCtk.STD_SIZE - 2,
        "width": 80,
        "fg_color": ["gray75", "gray25"],
        "font_bold": True,
        "textvariable": StvFilesCnt,
    },
    Grid={
        "row": 0,
        "column": 1,
        "padx": (0, GUI_PADDING_SML),
        "pady": GUI_PADDING_SML,
    },
)
# Main -> Tab 1 -> Frame 3: Frame Analyse Chems
FrmAnalyseChems = fctCtk.CtkFrame(
    Widget={
        "master": FrmAnalysis,
    },
    Grid={
        "row": 2,
        "column": 1,
        "padx": GUI_PADDING_SML,
        "pady": 0,
        "colconfig": 0,
    },
)
# Main -> Tab 1 -> Frame 3.2: Label Chemicals Count
LblChems = fctCtk.CtkLabel(
    Widget={
        "master": FrmAnalyseChems,
        "base_size": fctCtk.STD_SIZE - 2,
        "width": 1,
        "text": "Chemicals",
        "fg_color": ["gray80", "gray20"],
        "font_bold": True,
    },
    Grid={
        "row": 0,
        "column": 0,
        "padx": (GUI_PADDING_SML, 0),
        "pady": GUI_PADDING_SML,
    },
)
StvChemsCnt = StringVar()
LblChemsCnt = fctCtk.CtkLabel(
    Widget={
        "master": FrmAnalyseChems,
        "base_size": fctCtk.STD_SIZE - 2,
        "width": 80,
        "fg_color": ["gray75", "gray25"],
        "font_bold": True,
        "textvariable": StvChemsCnt,
    },
    Grid={
        "row": 0,
        "column": 1,
        "padx": (0, GUI_PADDING_SML),
        "pady": GUI_PADDING_SML,
    },
)
# Main -> Tab 1 -> Frame 3: Frame Analyse Cas
FrmAnalyseCas = fctCtk.CtkFrame(
    Widget={
        "master": FrmAnalysis,
    },
    Grid={
        "row": 2,
        "column": 2,
        "padx": (GUI_PADDING_SML, 0),
        "pady": 0,
        "colconfig": 0,
    },
)
# Main -> Tab 1 -> Frame 3.3: Label Cas Count
LblCas = fctCtk.CtkLabel(
    Widget={
        "master": FrmAnalyseCas,
        "base_size": fctCtk.STD_SIZE - 2,
        "width": 1,
        "text": "CAS Entries",
        "fg_color": ["gray80", "gray20"],
        "font_bold": True,
    },
    Grid={
        "row": 0,
        "column": 0,
        "padx": (GUI_PADDING_SML, 0),
        "pady": GUI_PADDING_SML,
    },
)
StvCasCnt = StringVar()
LblCasCount = fctCtk.CtkLabel(
    Widget={
        "master": FrmAnalyseCas,
        "base_size": fctCtk.STD_SIZE - 2,
        "width": 80,
        "fg_color": ["gray75", "gray25"],
        "font_bold": True,
        "textvariable": StvCasCnt,
    },
    Grid={
        "row": 0,
        "column": 1,
        "padx": (0, GUI_PADDING_SML),
        "pady": GUI_PADDING_SML,
    },
)
# Main -> Tab 1: Label Hide Analysis
LblHideAnalysis = fctCtk.CtkLabel(
    Widget={
        "master": TabProcessing,
    },
    Grid={
        "row": 2,
        "column": 1,
        "padx": 0,
        "pady": 0,
        "sticky": "nsew",
    },
)
# Main -> Tab 1: Button Show Log
BtnToggleLog = fctCtk.CtkButton(
    Widget={
        "master": TabProcessing,
        "base_size": fctCtk.STD_SIZE - 2,
        "width": 1,
        "text": "Show Log",
        "font_bold": True,
        "FncCommand": GuiToggleLog,
    },
    Grid={
        "row": 3,
        "column": 0,
        "padx": 0,
        "pady": 0,
    },
)
# Main -> Tab 1: Frame Progress
FrmProgress = fctCtk.CtkFrame(
    Widget={
        "master": TabProcessing,
    },
    Grid={
        "row": 3,
        "column": 1,
        "padx": GUI_PADDING_SML,
        "pady": GUI_PADDING_SML,
        "colconfig": 0,
    },
)

# Main -> Tab 1: Progress Bar
PrbProgress = fctCtk.CtkProgressBar(
    Widget={
        "master": FrmProgress,
        "height": fctCtk.STD_SIZE + 4,
        "fg_color": ["gray75", "gray25"],
    },
    Grid={
        "row": 0,
        "column": 0,
        "padx": GUI_PADDING_SML,
        "pady": 0,
    },
)
# Main -> Tab 1: Button Cancel
BtnCancel = fctCtk.CtkButton(
    Widget={
        "master": FrmProgress,
        "base_size": fctCtk.STD_SIZE - 2,
        "text": "Cancel",
        "font_bold": True,
        "FncCommand": GuiCancel,
    },
    Grid={
        "row": 0,
        "column": 1,
        "padx": 0,
        "pady": 0,
    },
)
# Main -> Tab 1: Label Hide Progress
LblHideProgress = fctCtk.CtkLabel(
    Widget={
        "master": TabProcessing,
    },
    Grid={
        "row": 3,
        "column": 1,
        "padx": 0,
        "pady": 0,
        "sticky": "nsew",
    },
)
# Main: Tab 2
TabSettings = TabMain.tab("Settings")
TabSettings.grid_rowconfigure(0, weight=1)
# TODO: This seems stupid ... but it works for now
TabSettings.grid_columnconfigure(0, weight=4)
TabSettings.grid_columnconfigure(1, weight=1)

# Main -> Tab 2: Frame Queries
FrmQueries = fctCtk.CtkFrame(
    Widget={
        "master": TabSettings,
    },
    Grid={
        "row": 0,
        "column": 0,
        "padx": GUI_PADDING_SML,
        "pady": GUI_PADDING_SML,
        "sticky": "new",
        "colconfig": 0,
    },
)
# Main -> Tab 2 -> Frame 1: Label Queries
LblQueries = fctCtk.CtkLabel(
    Widget={
        "master": FrmQueries,
        "fg_color": ["gray75", "gray25"],
        "text": "Query Targets",
        "font_bold": True,
    },
    Grid={
        "row": 0,
        "column": 0,
        "padx": GUI_PADDING_SML,
        "pady": GUI_PADDING_SML,
    },
)
# Main -> Tab 2 -> Frame 1: Checkbox Query Chemikalieninfo
BlvQueryChemInfo = BooleanVar()
ChbQueryChemInfo = fctCtk.CtkCheckbox(
    Widget={
        "master": FrmQueries,
        "base_size": fctCtk.STD_SIZE - 2,
        "text": "Chemikalieninfo",
        "variable": BlvQueryChemInfo,
        "font_bold": True,
    },
    Grid={
        "row": 1,
        "column": 0,
        "padx": GUI_PADDING,
        "pady": (GUI_PADDING_SML, 0),
    },
)
# Main -> Tab 2 -> Frame 1: Checkbox Query PubChem
BlvQueryPubChem = BooleanVar()
ChbQueryPubChem = fctCtk.CtkCheckbox(
    Widget={
        "master": FrmQueries,
        "base_size": fctCtk.STD_SIZE - 2,
        "text": "PubChem",
        "variable": BlvQueryPubChem,
        "font_bold": True,
    },
    Grid={
        "row": 2,
        "column": 0,
        "padx": GUI_PADDING,
        "pady": (GUI_PADDING_SML, 0),
    },
)
# Main -> Tab 2 -> Frame 1: Checkbox Query Gestis
BlvQueryGestis = BooleanVar()
ChbQueryGestis = fctCtk.CtkCheckbox(
    Widget={
        "master": FrmQueries,
        "base_size": fctCtk.STD_SIZE - 2,
        "text": "Gestis",
        "variable": BlvQueryGestis,
        "font_bold": True,
    },
    Grid={
        "row": 3,
        "column": 0,
        "padx": GUI_PADDING,
        "pady": GUI_PADDING_SML,
    },
)

# Main -> Tab 2: Frame Threading
FrmThreading = fctCtk.CtkFrame(
    Widget={
        "master": TabSettings,
    },
    Grid={
        "row": 0,
        "column": 1,
        "padx": GUI_PADDING_SML,
        "pady": GUI_PADDING_SML,
        "sticky": "new",
        "colconfig": 0,
    },
)
# Main -> Tab 2 -> Frame 2: Label Threading
LblThreading = fctCtk.CtkLabel(
    Widget={
        "master": FrmThreading,
        "fg_color": ["gray75", "gray25"],
        "text": "Threading Settings",
        "font_bold": True,
    },
    Grid={
        "row": 0,
        "column": 0,
        "padx": GUI_PADDING_SML,
        "pady": GUI_PADDING_SML,
        "columnspan": 2,
    },
)
# Main -> Tab 2 -> Frame 2: Checkbox Run Threaded
BlvRunThreaded = BooleanVar()
ChbRunThreaded = fctCtk.CtkCheckbox(
    Widget={
        "master": FrmThreading,
        "base_size": fctCtk.STD_SIZE - 2,
        "text": "Multi-threaded Processing, max. Threads:",
        "variable": BlvRunThreaded,
        "font_bold": True,
    },
    Grid={
        "row": 1,
        "column": 0,
        "padx": (GUI_PADDING, 0),
        "pady": GUI_PADDING_SML,
    },
)
# Main -> Tab 2 -> Frame 2: Entry Field Max Threads
StvMaxThreads = StringVar()
EntMaxThreads = fctCtk.CtkEntry(
    Widget={
        "master": FrmThreading,
        "base_size": fctCtk.STD_SIZE - 2,
        "width": 45,
        "justify": "center",
        "font_bold": True,
        "textvariable": StvMaxThreads,
    },
    Grid={
        "row": 1,
        "column": 1,
        "padx": (0, GUI_PADDING),
        "pady": GUI_PADDING_SML,
    },
)


# Main: Printer
TxbPrinter = fctCtk.CtkTextbox(
    Widget={
        "master": CtkGui,
        "base_size": fctCtk.STD_SIZE - 2,
        "fg_color": ["gray80", "gray20"],
        "font_bold": True,
    },
    Grid={
        "row": 2,
        "column": 0,
        "padx": GUI_PADDING,
        "pady": 0,
        "sticky": "nsew",
        "columnspan": 2,
    },
)
# Main: Label Author
BtnAuthor = fctCtk.CtkButton(
    Widget={
        "master": CtkGui,
        "fg_color": ["gray85", "gray15"],
        "font_color": ["gray10", "#DCE4EE"],
        "text": f"made by {APP_AUTHOR}",
        "font_bold": True,
        "FncCommand": MailAuthor,
    },
    Grid={
        "row": 3,
        "column": 0,
        "padx": (GUI_PADDING, 0),
        "pady": GUI_PADDING,
        "sticky": "sew",
    },
)
# Main: Label Version
BtnVersion = fctCtk.CtkButton(
    Widget={
        "master": CtkGui,
        "fg_color": ["gray85", "gray15"],
        "font_color": ["gray10", "#DCE4EE"],
        "text": f"V. {APP_VERSION}",
        "font_bold": True,
        "FncCommand": OpenGitHubRepository,
    },
    Grid={
        "row": 3,
        "column": 1,
        "padx": (0, GUI_PADDING),
        "pady": GUI_PADDING,
        "sticky": "sew",
    },
)


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-03-04    fJ      1.0     Dev tests: passed ... works as intended
# ++ 24-03-02    fJ      0.1     Created
# ++---------------------------------------------------------------------------------------------------------------------++#
def GuiInitConfig():
    """Sets the default configuration if no config file is present."""

    if PthCONFIG_FILE.exists():
        return

    config = {
        "FILES": {
            "all_files": True,
        },
        "QUERY": {
            "cheminfo": True,
            "pubchem": True,
            "gestis": True,
        },
        "THREADING": {
            "run_threaded": False,
            "max_threads": cpu_count(),
        },
        "DEBUG": {
            "debug_mode": False,
        },
    }

    StoreConfig(config)


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-03-04    fJ      1.0     Dev tests: passed ... works as intended
# ++ 24-02-27    fJ      0.1     Created
# ++---------------------------------------------------------------------------------------------------------------------++#
def OnGuiExit():
    """Writes settings from the GUI to the config file and terminates the GUI."""

    config = {
        "FILES": {
            "all_files": fctCtk.GetCtkVar(BlvAllFiles),
        },
        "QUERY": {
            "cheminfo": fctCtk.GetCtkVar(BlvQueryChemInfo),
            "pubchem": fctCtk.GetCtkVar(BlvQueryPubChem),
            "gestis": fctCtk.GetCtkVar(BlvQueryGestis),
        },
        "THREADING": {
            "run_threaded": fctCtk.GetCtkVar(BlvRunThreaded),
            "max_threads": fctCtk.GetCtkVar(StvMaxThreads),
        },
        "DEBUG": {
            "debug_mode": GetConfigValue("DEBUG", "debug_mode"),
        },
    }
    StoreConfig(config)

    CtkGui.destroy()


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-03-04    fJ      1.0     Dev tests: passed ... works as intended
# ++ 24-02-27    fJ      0.4     Added OnGuiExit to store config to a file
# ++ 24-02-20    fJ      0.3     Refactored
# ++ 24-02-06    fJ      0.2     Added docstring
# ++ 24-02-06    fJ      0.1     Created
# ++---------------------------------------------------------------------------------------------------------------------++#
def StartGui():
    """Sets up and starts the GUI."""

    # Setup loggings FunctionHandler for the Printer function
    for LhdHandler in LogLOGGER.handlers:
        if isinstance(LhdHandler, FunctionHandler):
            LhdHandler.set_function(SetWdgPrinterText)

    # Initialise stuff to prepare everything and prevent frame or grid resizing
    fctCtk.SetCtkVar(CtkWidget=StvCurrentJob, value="File Analysis:")
    fctCtk.SetCtkVar(CtkWidget=PrbProgress, value=0)
    fctCtk.SetCtkVar(CtkWidget=BlvAllFiles, value=GetConfigValue("FILES", "all_files"))
    fctCtk.SetCtkVar(CtkWidget=BlvQueryChemInfo, value=GetConfigValue("QUERY", "cheminfo"))
    fctCtk.SetCtkVar(CtkWidget=BlvQueryPubChem, value=GetConfigValue("QUERY", "pubchem"))
    fctCtk.SetCtkVar(CtkWidget=BlvQueryGestis, value=GetConfigValue("QUERY", "gestis"))
    fctCtk.SetCtkVar(CtkWidget=BlvRunThreaded, value=GetConfigValue("THREADING", "run_threaded"))
    fctCtk.SetCtkVar(CtkWidget=StvMaxThreads, value=GetConfigValue("THREADING", "max_threads"))

    # TODO: This seems stupid ... but it works for now
    CtkGui.after(30, fctCtk.SetCtkVar, StvCurrentJob, "")
    CtkGui.after(30, fctCtk.ToggleWidgetVisibility, TxbPrinter, True)

    # Bind post-close protocol to the GUI
    CtkGui.protocol("WM_DELETE_WINDOW", OnGuiExit)

    # Start GUI
    CtkGui.mainloop()
