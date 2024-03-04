# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ Imports
# ++---------------------------------------------------------------------------------------------------------------------++#
from collections import namedtuple
from datetime import datetime
from pathlib import Path
from time import sleep
from typing import Any

from requests import get
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

import src.fctlib.selenium as fctSelenium
import src.gui as gui
from src.fctlib.ctk import GetCtkVar
from src.fctlib.decorators import Retry, RetryException, RetryFailedException
from src.fctlib.logging import LogLOGGER
from src.fctlib.regex import CheckCasNo
from src.settings import DRV_SLEEPTIME

# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ Module variables
# ++---------------------------------------------------------------------------------------------------------------------++#
# ChemInfo URL
URL = "https://gestis.dguv.de/search"

# ChemInfo XPaths: Search page
XPATH_SEARCH_CAS = ".//input[@placeholder='Nummern']"
XPATH_SEARCH_NAME = ".//input[@placeholder='Stoffname']"
XPATH_SEARCH_HITS = ".//div[@role='list']"
XPATH_SEARCH_HITLIST = "./div[@role='listitem']"
XPATH_SEARCH_MULTI_HEADER = ".//h2[@class='hit-list-title']"
XPATH_SEARCH_MULTI_CAS = ".//div[@class='v-data-table__wrapper']/table/tbody/tr/td[3]"
XPATH_SEARCH_MULTI_NAME = ".//div[@class='v-data-table__wrapper']/table/tbody/tr/td[4]"

# ChemInfo XPaths: Dossier page
XPATH_DOSSIER_HEADING = ".//span[@class='stoffname-title']"
XPATH_BUTTON_PDF_DIALOG = ".//div[@class='data-sheet-actions-wrapper__right']/button"
XPATH_LINK_PDF = ".//div[@class='v-card__actions']/a"


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-03-04    fJ      1.0     Dev tests: passed ... works as intended
# ++ 24-02-28    fJ      0.1     Created
# ++---------------------------------------------------------------------------------------------------------------------++#
def GetHitList(WdrDriver: WebDriver, query_term: str) -> list[WebElement]:
    """Returns the hit list for the given query term.\n
    - -> | <WdrDriver> Webdriver to use\n
    - -> | <query_term> Term to query the database\n
    - <- | <return> List of hit elements"""

    search_field = XPATH_SEARCH_CAS if CheckCasNo(query_term) else XPATH_SEARCH_NAME

    try:
        WelSearchField: WebElement = fctSelenium.GetSingleWebElement(WdrParent=WdrDriver, descriptor=search_field)
        WelSearchField.send_keys(query_term)
        # Sleep so the browser catches up to the visual change
        sleep(DRV_SLEEPTIME)

        WelHitField = fctSelenium.GetSingleWebElement(WdrParent=WdrDriver, descriptor=XPATH_SEARCH_HITS)
        if WelHitField is None:
            return []
        return fctSelenium.GetWebElements(WdrParent=WelHitField, descriptor=XPATH_SEARCH_HITLIST)

    # Handle a seldom StaleElement exception by raising a retry exception handled one level up
    except (StaleElementReferenceException, AttributeError) as Error:
        LogLOGGER.warning(Error)
        raise RetryException()


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-03-04    fJ      1.0     Dev tests: passed ... works as intended
# ++ 24-02-28    fJ      0.1     Created
# ++---------------------------------------------------------------------------------------------------------------------++#
def CleanHitList(WdrDriver: WebDriver, hit_list: list[WebElement], query_term: str) -> list[WebElement]:
    """Tries to return a cleaned hit list from the search hit list in case of multiple hits.\n
    Likely intended hits are defined by the similarity of search and find term.\n
    - -> | <WdrDriver> Webdriver to use\n
    - -> | <hit_list> List of hit elements\n
    - -> | <query_term> Query term for cleaning check\n
    - <- | <return> Cleaned list of hit elements"""

    cleaned_hit_list = []

    try:
        for WelHit in hit_list:
            # NOTE: We need to force scroll the target into view to access its content
            fctSelenium.ScrollTo(WdrDriver=WdrDriver, WelTarget=WelHit)
            if WelHit.text.lower() == query_term.lower():
                cleaned_hit_list.append(WelHit)

    # Handle a seldom StaleElement exception by raising a retry exception handled one level up
    except (StaleElementReferenceException, AttributeError) as Error:
        LogLOGGER.warning(Error)
        raise RetryException()

    return cleaned_hit_list


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-03-04    fJ      1.0     Dev tests: passed ... works as intended
# ++ 24-02-28    fJ      0.1     Created
# ++---------------------------------------------------------------------------------------------------------------------++#
def CleanMultiHit(WdrDriver: WebDriver, query_term: str) -> list[WebElement]:
    """Returns the hit list for the given query term.\n
    - -> | <WdrDriver> Webdriver to use\n
    - -> | <query_term> Term to query the database\n
    - <- | <return> List of hit elements"""

    search_field = XPATH_SEARCH_MULTI_CAS if CheckCasNo(query_term) else XPATH_SEARCH_MULTI_NAME

    multi_hit_list = []
    try:
        hit_list = fctSelenium.GetWebElements(WdrParent=WdrDriver, descriptor=search_field)
        for WelHit in hit_list:
            if WelHit.text.lower() == query_term.lower():
                multi_hit_list.append(WelHit)

    # Handle a seldom StaleElement exception by raising a retry exception handled one level up
    except (StaleElementReferenceException, AttributeError) as Error:
        LogLOGGER.warning(Error)
        raise RetryException()

    return multi_hit_list


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-03-04    fJ      1.0     Dev tests: passed ... works as intended
# ++ 24-02-28    fJ      0.1     Created
# ++---------------------------------------------------------------------------------------------------------------------++#
@Retry(RetryException)
def GetHitStatus(WdrDriver: WebDriver, query_term: str) -> str:
    """Get and analyse the hit list for the query term. In case of a single hit navigate to the hits URL.\n
    - -> | <WdrDriver> Webdriver to use\n
    - -> | <query_term> Term to query the database\n
    - <- | <return> Query status as the analysis result"""

    try:
        hit_list = GetHitList(WdrDriver=WdrDriver, query_term=query_term)
        if len(hit_list) > 1:
            hit_list = CleanHitList(WdrDriver=WdrDriver, hit_list=hit_list, query_term=query_term)
            status = f"Most probable out of {len(hit_list)} query hits selected for <{query_term}>."

        if len(hit_list) == 0:
            status = f"Gestis | Skipped <{query_term}>: No query hit found!"
        # Check again if cleaning wasn't successful
        elif len(hit_list) > 1:
            status = f"Gestis | Skipped <{query_term}>: More than one query hit found!"
        else:
            status = f"Gestis | Success! {status}" if "status" in locals() else "Gestis | Success!"
            hit_list[0].click()

            # Sleep so the browser catches up to the visual change
            sleep(DRV_SLEEPTIME)

        # If we are still on the search page, we encountered a multi result hit (i.e. for CAS 1310-73-2).
        if (
            "Success!" in status
            and fctSelenium.GetSingleWebElement(WdrParent=WdrDriver, descriptor=XPATH_SEARCH_MULTI_HEADER, no_timeout=True)
            is not None
        ):
            multi_hit_list = CleanMultiHit(WdrDriver=WdrDriver, query_term=query_term)
            if len(multi_hit_list) != 1:
                status = f"Gestis | Skipped <{query_term}>: Found unique query hit, but it led to an ambiguous result!"
            else:
                status = f"{status} Most probable hit out of the ambiguous results selected for <{query_term}>."
                multi_hit_list[0].click()

                # Sleep so the browser catches up to the visual change
                sleep(DRV_SLEEPTIME)

    # Handle a seldom StaleElement exception by retrying
    except (StaleElementReferenceException, AttributeError) as Error:
        LogLOGGER.warning(Error)
        raise RetryException()
    # Handle the Retry call from subroutines
    except RetryException:
        raise RetryException()

    return status


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-03-04    fJ      1.0     Dev tests: passed ... works as intended
# ++ 24-02-28    fJ      0.1     Created
# ++---------------------------------------------------------------------------------------------------------------------++#
@Retry(RetryException)
def GetCompoundData(WdrDriver: WebDriver | None, query_term: str, query_status: str) -> dict[str, Any]:
    """Returns a dictionary of selected compound data from the Gestis website.\n
    - -> | <WdrDriver> Webdriver to use\n
    - -> | <query_term> Term of the PubChem query\n
    - -> | <query_status> Status of PubChem compound query\n
    - <- | <return> Compound data dictionary"""

    cpd_data: dict[str, Any] = {}

    # Get basic compound data that allways should be returned
    cpd_data["query_status_gt"] = query_status
    cpd_data["query_term_gt"] = query_term
    cpd_data["query_database_gt"] = "Gestis-Stoffdatenbank"
    cpd_data["query_time_gt"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if "Success!" in query_status:
        try:
            WelHeader = fctSelenium.GetSingleWebElement(WdrParent=WdrDriver, descriptor=XPATH_DOSSIER_HEADING)
            cpd_data["query_finding_gt"] = WelHeader.text
            cpd_data["query_link_gt"] = WdrDriver.current_url
            cpd_data["id_zvg"] = cpd_data["query_link_gt"].split("=")[-1]

            WelPdfDialog = fctSelenium.GetSingleWebElement(WdrParent=WdrDriver, descriptor=XPATH_BUTTON_PDF_DIALOG)
            WelPdfDialog.click()
            WelPdfLink = fctSelenium.GetSingleWebElement(WdrParent=WdrDriver, descriptor=XPATH_LINK_PDF)
            pdf_link = WelPdfLink.get_attribute("href")

            file_name = f"SDB_{cpd_data["id_zvg"]}.pdf"
            PthDownload = Path(GetCtkVar(gui.StvParentFolder)) / "SDB" / file_name
            PthDownload.parent.mkdir(parents=True, exist_ok=True)
            RspPdfStream = get(url=pdf_link, stream=True)
            try:
                with open(PthDownload, "wb") as BwrPdfFile:
                    BwrPdfFile.write(RspPdfStream.content)
                cpd_data["file_sdb"] = file_name
            except PermissionError as Error:
                LogLOGGER.error(f"Error writing to <{file_name}>: <{Error}>.")
                cpd_data["query_status_gt"] = f"Gestis | Error writing SDB to <{file_name}>! Is the file currently open?"

        # Handle a seldom StaleElement exception and an attribute error that results from missing web elements by retrying
        except (StaleElementReferenceException, AttributeError) as Error:
            LogLOGGER.warning(Error)
            raise RetryException()
        # Handle the Retry call from subroutines
        except RetryException:
            raise RetryException()

    return cpd_data


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-03-04    fJ      1.0     Dev tests: passed ... works as intended
# ++ 24-02-28    fJ      0.1     Created
# ++---------------------------------------------------------------------------------------------------------------------++#
def QueryGestis(WdrDriver: WebDriver, query_term: str) -> dict[str, Any]:
    """Queries Gestis for a query term and returns compound data as well as downloads the safety data sheet.\n
    - -> | <WdrDriver> Webdriver to use\n
    - -> | <query_term> Term to query the database\n
    - <- | <return> Compound data"""

    if WdrDriver is None:
        WdrDriver = fctSelenium.InitWebDriver(use_existing=True)
    fctSelenium.NavigateURL(WdrDriver=WdrDriver, url=URL)

    try:
        # Get and analyse query hits to get single compound dataset URL
        status = GetHitStatus(WdrDriver=WdrDriver, query_term=query_term)

        # Get compound data
        cpd_data = GetCompoundData(WdrDriver=WdrDriver, query_term=query_term, query_status=status)

    # Most abundand error is a seldom StaleElement exception that we handle by retrying. If this fails, we skip the compound.
    except RetryFailedException as Error:
        LogLOGGER.error(f"An stale element error occurred while querying compound <{query_term}>: <{Error}>.")
        status = f"Gestis | Skipped <{query_term}>: Error! This is not your fault. Retrying later may help ..."
        cpd_data = GetCompoundData(WdrDriver=None, query_term=query_term, query_status=status)

    return cpd_data


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-03-04    fJ      1.0     Dev tests: passed ... works as intended
# ++ 24-02-29    fJ      0.1     Created
# ++---------------------------------------------------------------------------------------------------------------------++#
def InitGestisDataset() -> dict[str, Any]:
    """Initialises the dictionary for the returned dataset namedtuple constructor.\n
    - <- | <return> Dataset constructor"""
    cpd_data: dict[str, Any] = {}
    cpd_data["query_status_gt"] = None
    cpd_data["query_term_gt"] = None
    cpd_data["query_database_gt"] = None
    cpd_data["query_time_gt"] = None
    cpd_data["query_finding_gt"] = None
    cpd_data["query_link_gt"] = None
    cpd_data["id_zvg"] = None
    cpd_data["file_sdb"] = None

    return cpd_data


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-03-04    fJ      1.0     Dev tests: passed ... works as intended
# ++ 24-02-29    fJ      0.1     Created
# ++---------------------------------------------------------------------------------------------------------------------++#
DATASET = InitGestisDataset().keys()
NtpGT_CONSTRUCTOR = namedtuple(typename="compound_data", field_names=DATASET, defaults=(None,) * len(DATASET))
"""Named tuple constructor for compound data. Gets initialized by InitGestisDataset()."""
