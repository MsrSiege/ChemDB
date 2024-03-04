# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ Imports
# ++---------------------------------------------------------------------------------------------------------------------++#
from pathlib import Path
from typing import NamedTuple

from pandas import DataFrame, read_csv, read_excel


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-03-04    fJ      1.0     Dev tests: passed ... works as intended
# ++ 24-02-21    fJ      0.3     Reworked
# ++ 24-02-06    fJ      0.2     Added docstring
# ++ 24-02-01    fJ      0.1     Created
# ++---------------------------------------------------------------------------------------------------------------------++#
def GetDfFromFilePath(PthFile: Path) -> DataFrame | None:
    """Returns a pandas dataframe from a spreadsheet-like file.\n
    - -> | <PthFile> Path to the spreadsheet-like file\n
    - <- | <return> Dataframe or None if PermissionError"""

    if PthFile.suffix.lower() in [".xlsx", ".xls"]:
        try:
            return read_excel(PthFile)
        # Catch error if the file is currently open
        except PermissionError:
            return None
    if PthFile.suffix.lower() in [".csv"]:
        return read_csv(PthFile)


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-03-04    fJ      1.0     Unit test: passed
# ++ 24-02-21    fJ      0.3     Reworked
# ++ 24-02-06    fJ      0.2     Added docstring
# ++ 24-02-01    fJ      0.1     Created
# ++---------------------------------------------------------------------------------------------------------------------++#
def GetUniqueColsFromDf(DfDataframe: DataFrame, cols_to_search: list[str]) -> DataFrame:
    """Returns one or more unique column(s) from a pandas dataframe.\n
    - -> | <DfDataframe> Dataframe to search unique column(s) in\n
    - -> | <cols_to_search> Unique column(s) header or header part\n
    - <- | <return> Dataframe of only unique column(s)"""

    unique_cols = []
    for col_header in cols_to_search:
        col_match = [col for col in DfDataframe.columns if "Unnamed" not in col and col_header.lower() in col.lower()]
        if len(col_match) == 1:
            unique_cols.append(col_match[0])

    return DfDataframe[unique_cols]


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-03-04    fJ      1.0     Unit test: passed
# ++ 24-02-25    fJ      0.1     Created
# ++---------------------------------------------------------------------------------------------------------------------++#
def GetDfFromNtList(nt_list: list[NamedTuple], nt_constructor: NamedTuple) -> DataFrame:
    """Returns a pandas dataframe from a list of named tuples.\n
    - -> | <nt_list> List of named tuples\n
    - -> | <nt_constructor> Constructor used to generate named tuples\n
    - <- | <return> Dataframe"""

    return DataFrame.from_records(data=nt_list, columns=nt_constructor._fields)


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-03-04    fJ      1.0     Unit test: passed
# ++ 24-02-25    fJ      0.1     Created
# ++---------------------------------------------------------------------------------------------------------------------++#
def WriteDfToXlsx(DfDataframe: DataFrame, PthXlsFile: Path) -> bool:
    """Writes out a dataframe to an excel .xlsx file.\n
    - -> | <DfDataframe> Dataframe\n
    - -> | <PthXlsFile> Path to store the excel .xlsx file\n
    - <- | <return> Write success"""

    try:
        DfDataframe.to_excel(excel_writer=PthXlsFile, sheet_name="Query Output", index=True, engine="openpyxl")
        return True
    # Catch error if the file is currently open
    except PermissionError:
        return False


# # ++---------------------------------------------------------------------------------------------------------------------++#
# # ++ DATE        DEV     VER     ACTIONS
# # ++ 24-02-06    fJ      0.2     Added docstring
# # ++ 24-02-01    fJ      0.1     Created
# # ++---------------------------------------------------------------------------------------------------------------------++#
# def GetFromPndDfByLoc(pdfInput: DataFrame, RowLocator: str | Series, ColLocator: str | Series) -> str:
#     """Returns a string from a pandas dataframe by row and column locator."""

#     # Try to get the result of row and col locators in input dataframe
#     try:
#         LocatorOutput: str | Series | DataFrame = pdfInput.loc[RowLocator, ColLocator]
#     except KeyError:
#         LogLOGGER.warning(f"No data entry found! <{RowLocator}>:<{ColLocator}>")
#         return None

#     # If Output is string return string
#     if isinstance(LocatorOutput, str):
#         return LocatorOutput

#     # If output is a 2D pandas dataframe stringify it
#     if isinstance(LocatorOutput, DataFrame):
#         LocatorOutput = LocatorOutput.stack().dropna()

#     # If output is a pandas series (1D) stringify it
#     if isinstance(LocatorOutput, Series):
#         # Return list-derived string
#         if len(LocatorOutput.tolist()) == 1:
#             return LocatorOutput.tolist()[0]
#         # Return list-derived joined string ignoring empty entries
#         return "|".join(map(str, [item for item in LocatorOutput.tolist() if not isna(item)]))

#     LogLOGGER.warning(f"Unhandled output type! <{RowLocator}>:<{ColLocator}>")
#     return None
