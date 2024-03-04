# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ Imports
# ++---------------------------------------------------------------------------------------------------------------------++#
from collections import namedtuple
from pathlib import Path
from queue import Queue
from threading import Event, Thread
from time import sleep
from typing import NamedTuple

from selenium.webdriver.chrome.webdriver import WebDriver

import src.gui as gui
from src.fctlib.ctk import GetCtkVar
from src.fctlib.logging import LogLOGGER
from src.fctlib.pandas import GetDfFromFilePath, GetDfFromNtList, GetUniqueColsFromDf, WriteDfToXlsx
from src.fctlib.regex import CheckCasNo
from src.fctlib.selenium import WEBDRIVERS, InitWebDriversForThreading, QueWEBDRIVERS, QuitWebDrivers
from src.fctlib.time import GetRunTime
from src.queries.chemikalieninfo import NtpCI_CONSTRUCTOR, QueryChemInfo
from src.queries.gestis import NtpGT_CONSTRUCTOR, QueryGestis
from src.queries.pubchem import NtpPC_CONSTRUCTOR, QueryPubChem
from src.settings import SUPPORTED_REQUEST_COL_NAMES

# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ Module variables
# ++---------------------------------------------------------------------------------------------------------------------++#
REPORT: dict[str, int | str] = {}
"""Process report dictionary."""

QueQUERY = Queue()
"""Queue for query data."""
QueOUTPUT = Queue()
"""Queue for output data."""


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-03-04    fJ      1.0     Dev tests: passed ... works as intended
# ++ 24-02-25    fJ      0.3     Replaced os.path with pathlib.Path
# ++ 24-02-21    fJ      0.2     Reworked
# ++ 24-02-10    fJ      0.1     Created
# ++---------------------------------------------------------------------------------------------------------------------++#
def PreprocessFiles(file_paths: list[Path]) -> dict[str, dict[int, list[str] | None]] | None:
    """Constructs a queries dictionary for query analysis or processing from given folder path.\n
    - -> | <file_paths> List of file paths\n
    - <- | <return> Queries dictionary, structure: {File Name, {Entry Number, [Entry ID, first is valid CAS or None] | None if empty line}}"""

    queries: dict[str, dict[int, list[str] | None]] = {}
    PthParent = next((PthFile.parent for PthFile in file_paths if PthFile.is_file()), None)

    for PthFile in file_paths:
        file_name = PthFile.name
        DfFile = GetDfFromFilePath(PthFile)
        if DfFile is None:
            return gui.EvaluateOnError(PthFolder=PthParent, error=f"Can't access <{file_name}>! Is it currently open?")

        DfIdentifierCols = GetUniqueColsFromDf(DfDataframe=DfFile, cols_to_search=SUPPORTED_REQUEST_COL_NAMES)

        if not DfIdentifierCols.shape[1]:
            continue

        queries[file_name] = {}
        # Skip files without supported identifier columns
        if DfIdentifierCols.shape[1] == 0:
            continue

        for row_num, PdsRows in DfIdentifierCols.iterrows():
            # Skip completely empty rows
            if PdsRows.isna().all():
                queries[file_name][row_num] = None
                continue

            for Cell in PdsRows:
                if queries[file_name].get(row_num) is None:
                    queries[file_name][row_num] = [str(Cell)] if CheckCasNo(str(Cell)) else [None]
                else:
                    queries[file_name][row_num].append(str(Cell))

    if not queries:
        return gui.EvaluateOnError(PthFolder=PthParent, error="No file with specified identifier columns found!")

    return queries


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-03-04    fJ      1.0     Dev tests: passed ... works as intended
# ++ 24-02-22    fJ      0.2     Reworked
# ++ 24-02-04    fJ      0.1     Created
# ++---------------------------------------------------------------------------------------------------------------------++#
def GetQueryDataset(query_terms: list[str], WdrDriver: WebDriver = None, EvtCancel: Event | None = None) -> NamedTuple:
    """Collects queried data from web services.\n
    - -> | <query_terms> List of terms for a chemical to query for\n
    - -> | <WdrDriver> Webdriver to use\n
    - -> | <EvtCancel> Cancel event to listen to\n
    - <- | <return> Compound dataset from different webservices"""

    data_cheminfo = {}
    data_pubchem = {}
    data_gestis = {}

    # Query Chemikalieninfo
    if GetCtkVar(CtkWidget=gui.BlvQueryChemInfo):
        for query_term in query_terms:
            if EvtCancel is not None and EvtCancel.is_set():
                return NtpEMPTY

            # Skip first query term (allways a valid CAS number) if no CAS number was provided
            if query_term is None or "Success!" in data_cheminfo.get("query_status_ci", str()):
                continue

            data_cheminfo = QueryChemInfo(WdrDriver=WdrDriver, query_term=query_term)
            if "Success!" not in data_cheminfo.get("query_status_ci", str()):
                LogLOGGER.userinfo(f">>> {data_cheminfo['query_status_ci']}")

    # Try to more securely get CAS number from input or Chemikalieninfo output to query PubChem
    # We do this because PubChem won't easily provide a single CAS number for a chemical
    if query_terms[0] is None and CheckCasNo(data_cheminfo.get("id_cas", str())):
        query_terms[0] = data_cheminfo["id_cas"]

    # Query PubChem
    if GetCtkVar(CtkWidget=gui.BlvQueryPubChem):
        for query_term in query_terms:
            if EvtCancel is not None and EvtCancel.is_set():
                return NtpEMPTY

            # Skip first query term (allways a valid CAS number) if no CAS number was provided
            if query_term is None or "Success!" in data_pubchem.get("query_status_pc", str()):
                continue

            data_pubchem = QueryPubChem(query_term)
            if "Success!" not in data_pubchem.get("query_status_pc", str()):
                LogLOGGER.userinfo(f">>> {data_pubchem['query_status_pc']}")

    # Query Gestis
    if GetCtkVar(CtkWidget=gui.BlvQueryGestis):
        for query_term in query_terms:
            if EvtCancel is not None and EvtCancel.is_set():
                return NtpEMPTY

            # Skip first query term (allways a valid CAS number) if no CAS number was provided
            if query_term is None or "Success!" in data_gestis.get("query_status_gt", str()):
                continue

            data_gestis = QueryGestis(WdrDriver=WdrDriver, query_term=query_term)
            if "Success!" not in data_gestis.get("query_status_gt", str()):
                LogLOGGER.userinfo(f">>> {data_gestis['query_status_gt']}")

    return NtpCONSTRUCTOR(**data_cheminfo, **data_pubchem, **data_gestis)


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-03-04    fJ      1.0     Dev tests: passed ... works as intended
# ++ 24-02-27    fJ      0.1     Created
# ++---------------------------------------------------------------------------------------------------------------------++#
def WebDriverListener(QueData: Queue, QueOutput: Queue):
    """Listener for data processing in threaded runs.\n
    - -> | <QueData> Data queue to pull data from\n
    - -> | <QueOutput> Output queue to push output into\n
    Source: https://gist.github.com/wooddar/df4c89f381fa20ce819e94782dc5bc04"""

    while True:
        # Get any currently available data from the data queue, blocking until data is available
        qry_number, current_data = QueData.get()

        # Stop the listener in case of a stop signal and put the stop signal back on the queue to poison other listeners
        if qry_number == -1 and current_data == ["STOP"]:
            QueData.put((qry_number, current_data))
            break

        # Get any currently available worker ID from the webdriver queue, blocking until one is available
        worker_id = QueWEBDRIVERS.get()
        WdrDriver = WEBDRIVERS[worker_id]

        dataset = GetQueryDataset(WdrDriver=WdrDriver, query_terms=current_data)
        QueOutput.put((qry_number, dataset))

        # Put the now freed webdriver back onto the webdriver queue
        QueWEBDRIVERS.put(worker_id)

        # Pause to let everything settle down
        sleep(0.1)


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-03-04    fJ      1.0     Dev tests: passed ... works as intended
# ++ 24-02-27    fJ      0.1     Created from ProcessFiles()
# ++---------------------------------------------------------------------------------------------------------------------++#
def InitMultiThreadProcessing():
    """Initialises webdrivers for multithreading."""

    max_threads = min(int(REPORT["chems_count"]), int(GetCtkVar(CtkWidget=gui.StvMaxThreads)))

    InitWebDriversForThreading(max_threads=max_threads)
    web_driver_listener = [
        Thread(target=WebDriverListener, kwargs={"QueData": QueQUERY, "QueOutput": QueOUTPUT}, daemon=True)
        for _ in list(range(max_threads))
    ]

    for ThrWebDriverListener in web_driver_listener:
        ThrWebDriverListener.start()
        sleep(0.1)


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-03-04    fJ      1.0     Dev tests: passed ... works as intended
# ++ 24-02-27    fJ      0.1     Created from ProcessFiles()
# ++---------------------------------------------------------------------------------------------------------------------++#
def SingleThreadProcessing(qry_dict: dict[str, list[str] | None], EvtCancel: Event) -> list[NamedTuple]:
    """Processes files in the given folder and outputs web datasets .xlsx file. Runs queries in a single thread.\n
    - -> | <qry_dict> Dictionary containing query number and query terms\n
    - -> | <EvtCancel> Cancel event to listen to\n
    - <- | <return> List of compound datasets from different webservices"""

    query_datasets: list[NamedTuple] = []

    for _, qry_terms in qry_dict.items():
        if EvtCancel.is_set():
            return []

        if qry_terms is None:
            query_datasets.append(NtpEMPTY)
            continue

        REPORT["chem_no"] = REPORT["chem_no"] + 1
        REPORT["chem_id"] = next((chem_id for chem_id in qry_terms if chem_id is not None))
        REPORT["cas_no"] = REPORT["cas_no"] + 1 if qry_terms[0] is not None else REPORT["cas_no"]
        gui.EvaluateProzessing(report=REPORT, final=False)

        query_datasets.append(GetQueryDataset(query_terms=qry_terms, EvtCancel=EvtCancel))

    return query_datasets


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-03-04    fJ      1.0     Dev tests: passed ... works as intended
# ++ 24-02-26    fJ      0.1     Created
# ++---------------------------------------------------------------------------------------------------------------------++#
def MultiThreadProcessing(qry_dict: dict[str, list[str]]) -> list[NamedTuple]:
    """Processes files in the given folder and outputs web datasets .xlsx file. Runs queries as separate threads.\n
    - -> | <qry_dict> Dictionary containing query number and query terms\n
    - <- | <return> List of compound datasets from different webservices\n
    Source: https://gist.github.com/wooddar/df4c89f381fa20ce819e94782dc5bc04"""

    query_datasets: list[NamedTuple] = [None] * len(qry_dict)

    for qry_number, qry_terms in qry_dict.items():
        if qry_terms is None:
            query_datasets[qry_number] = NtpEMPTY
            continue

        QueQUERY.put((qry_number, qry_terms))

    while query_datasets.count(None) > 0:
        qry_number, dataset = QueOUTPUT.get()
        query_datasets[qry_number] = dataset

        REPORT["chem_no"] = REPORT["chem_no"] + 1
        REPORT["chem_id"] = next((chem_id for chem_id in list(qry_dict.values())[qry_number] if chem_id is not None))
        REPORT["cas_no"] = REPORT["cas_no"] + 1 if list(qry_dict.values())[qry_number][0] is not None else REPORT["cas_no"]
        gui.EvaluateProzessing(report=REPORT, final=False)

        # Pause to let everything settle down
        sleep(0.1)

    return query_datasets


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-03-04    fJ      1.0     Dev tests: passed ... works as intended
# ++ 24-02-26    fJ      0.3     Splitted AnalyseFiles() and ProcessFiles()
# ++ 24-02-25    fJ      0.2     Replaced os.path with pathlib.Path
# ++ 24-02-21    fJ      0.1     Created
# ++---------------------------------------------------------------------------------------------------------------------++#
def AnalyseFiles(file_paths: list[Path]):
    """Analyses given files for processing.\n
    - -> | <file_paths> List of file paths compatible for processing"""

    gui.GuiToggleExecutionLock(force_disable=True)

    query = PreprocessFiles(file_paths)
    if not query:
        return

    report: dict[str, int | str] = {
        "files_count": len(query),
        "chems_count": sum(1 for qry in query.values() for nty in qry.values() if nty is not None),
        "cas_count": sum(1 for qry in query.values() for nty in qry.values() if nty is not None and nty[0] is not None),
    }
    return gui.EvaluateAnalysis(report)


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-03-04    fJ      TIMER   MultiThr8 | Wall time: 124.8130 s, CPU time: 56.1094 s -> 2.080 s | 0,935 s per item
# ++ 24-03-04    fJ      TIMER   MultiThr6 | Wall time: 118.2340 s, CPU time: 50.2500 s -> 1.971 s | 0,838 s per item
# ++ 24-03-04    fJ      TIMER   SingleThr | Wall time: 395.4463 s, CPU time: 38.6875 s -> 6.591 s | 0,645 s per item
# ++ 24-03-04    fJ      1.0     Dev tests: passed ... works as intended
# ++ 24-02-27    fJ      TIMER   MultiThr6 | Wall time:  97.9698 s, CPU time: 25.4531 s -> 1.633 s | 0,424 s per item
# ++ 24-02-26    fJ      TIMER   SingleThr | Wall time: 235.8989 s, CPU time: 24.0312 s -> 3.932 s | 0,401 s per item
# ++ 24-02-26    fJ      0.3     Splitted AnalyseFiles() and ProcessFiles()
# ++ 24-02-25    fJ      0.2     Replaced os.path with pathlib.Path
# ++ 24-02-21    fJ      0.1     Created
# ++---------------------------------------------------------------------------------------------------------------------++#
def ProcessFiles(file_paths: list[Path], EvtCancel: Event, run_threaded: bool = False):
    """Processes files in the given folder and outputs web datasets .xlsx file. Runs all queries in a single thread.\n
    - -> | <file_paths> List of file paths compatible for processing\n
    - -> | <EvtCancel> Threading event to cancel function execution\n
    - -> | <run_threaded> Switch to run processing in multiple threads instead of a single one"""

    gui.GuiToggleExecutionLock(force_disable=True)

    timer = GetRunTime()

    query = PreprocessFiles(file_paths)
    if not query:
        return

    REPORT["files_count"] = len(query)
    REPORT["chems_count"] = sum(1 for qry in query.values() for nty in qry.values() if nty is not None)
    REPORT["cas_count"] = sum(1 for qry in query.values() for nty in qry.values() if nty is not None and nty[0] is not None)
    REPORT["file_no"] = 0
    REPORT["chem_no"] = 0
    REPORT["cas_no"] = 0
    REPORT["execution_time"] = 0

    gui.EvaluateProzessing(report=None, final=False)

    if run_threaded:
        # Unpoison the query queue (s. below)
        while QueQUERY.qsize() > 0:
            QueQUERY.get()
        # Reset the output queue
        while QueOUTPUT.qsize() > 0:
            QueOUTPUT.get()
        InitMultiThreadProcessing()

    global NtpCONSTRUCTOR
    global NtpEMPTY
    NtpCONSTRUCTOR = GenerateNtpConstructor()
    NtpEMPTY = NtpCONSTRUCTOR()

    PthParent = next((PthFile.parent for PthFile in file_paths if PthFile.is_file()), None)
    for file_name, qry_dict in query.items():
        REPORT["file_no"] = REPORT["file_no"] + 1
        REPORT["file_name"] = file_name

        query_datasets = (
            SingleThreadProcessing(qry_dict=qry_dict, EvtCancel=EvtCancel)
            if not run_threaded
            else MultiThreadProcessing(qry_dict=qry_dict)
        )

        if not run_threaded and EvtCancel.is_set():
            QuitWebDrivers()
            return gui.EvaluateOnError(PthFolder=PthParent, error="You have cancelled file processing!", show_in_gui=False)

        DfDataset = GetDfFromNtList(nt_list=query_datasets, nt_constructor=NtpCONSTRUCTOR)
        outfile_name = f"{Path(file_name).stem}_OUT.xlsx"
        if not WriteDfToXlsx(DfDataframe=DfDataset, PthXlsFile=PthParent / outfile_name):
            return gui.EvaluateOnError(PthFolder=PthParent, error=f"Can't access <{outfile_name}>! Is it currently open?")

    gui.EvaluateProzessing(report=None, final=True)
    # Poison the query queue to stop running threads
    QueQUERY.put((-1, ["STOP"]))
    QuitWebDrivers()

    REPORT["execution_time"], _ = GetRunTime(timer)
    return gui.EvaluateProzessing(report=REPORT, final=True)


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-03-04    fJ      1.0     Dev tests: passed ... works as intended
# ++ 24-03-02    fJ      0.1     Created
# ++---------------------------------------------------------------------------------------------------------------------++#
def GenerateNtpConstructor() -> type[NamedTuple]:
    """Initialises the dataset constructor for the namedtuple to return.\n
    - <- | <return> Dataset constructor"""

    switches = [
        GetCtkVar(CtkWidget=gui.BlvQueryChemInfo),
        GetCtkVar(CtkWidget=gui.BlvQueryPubChem),
        GetCtkVar(CtkWidget=gui.BlvQueryGestis),
    ]
    constructors = [
        NtpCI_CONSTRUCTOR._fields,
        NtpPC_CONSTRUCTOR._fields,
        NtpGT_CONSTRUCTOR._fields,
    ]
    selected = sum([constructor for switch, constructor in zip(switches, constructors) if switch], ())

    return namedtuple(typename="compound_dataset", field_names=selected, defaults=(None,) * len(selected))


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-03-04    fJ      1.0     Dev tests: passed ... works as intended
# ++ 24-03-02    fJ      0.2     Reworked to accomodate for GUI settings
# ++ 24-02-19    fJ      0.1     Created
# ++---------------------------------------------------------------------------------------------------------------------++#
NtpCONSTRUCTOR = namedtuple(
    typename="compound_dataset",
    field_names=NtpCI_CONSTRUCTOR._fields + NtpPC_CONSTRUCTOR._fields + NtpGT_CONSTRUCTOR._fields,
    defaults=(None,) * (len(NtpCI_CONSTRUCTOR._fields) + len(NtpPC_CONSTRUCTOR._fields) + len(NtpGT_CONSTRUCTOR._fields)),
)
NtpCONSTRUCTOR: NamedTuple = None
"""Named tuple constructor for compound data."""

NtpEMPTY: NamedTuple = None
"""Empty compound data named tuple."""
