# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ Imports
# ++---------------------------------------------------------------------------------------------------------------------++#
from collections import namedtuple
from datetime import datetime
from time import sleep
from typing import Any

from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement

import src.fctlib.selenium as fctSelenium
from src.fctlib.decorators import Retry, RetryException, RetryFailedException
from src.fctlib.logging import LogLOGGER
from src.fctlib.regex import CheckCasNo, GetGhsStatements, RepHAZARDS, RepPRECAUTIONARIES
from src.settings import DRV_SLEEPTIME, NOT_LISTED

# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ Module variables
# ++---------------------------------------------------------------------------------------------------------------------++#
# ChemInfo URL
URL = "https://recherche.chemikalieninfo.de/public"

# ChemInfo XPaths: Search page
XPATH_SEARCH_CAS = ".//input[@data-autosuggest-key='CASRN.CASRN']"
XPATH_SEARCH_NAME = ".//input[@data-autosuggest-key='INDEX.NAME']"
XPATH_SEARCH_HITS = ".//div[@id='search-result']"
XPATH_SEARCH_HITLIST = "./div[position() > 1]"
# div[3]: with structure image, div[2]: without structure image
XPATH_SEARCH_HIT = "./div[3]/span/a | ./div[2]/span/a"

# ChemInfo XPaths: Dossier page
XPATH_DOSSIER_HEADING = ".//*[@id='navbar']/h1"
XPATH_DOSSIER = ".//main[@id='dossier-content']"
XPATH_DOSSIER_DEF_LISTS = [
    # Descriptor, parent ID, target XPath
    ["id_cas", "m98", "@dt", "=CAS-RN", ">dd"],
    ["id_gsbl", "m84", "@dt", "=GSBL-RN", ">dd"],
    ["id_eg", "m99", "@dd", "+EG-Nummer", ">dd"],
    ["id_cus", "m99", "@dd", "+CUS", ">dd"],
    ["id_index", "m99", "@dd", "+INDEX", ">dd"],
    ["id_wgk", "m328", "@dt", "=Kenn-Nummer", ">dd"],
    # ["mol_formula", "m96", "@dt" "=Summenformel", ">dd"],
    # ["mol_file", "m84", "@dt", "+MOL-Datei", ">dd"],
    ["ghs_class", "m157", "@dt", "+Piktogramme", ">dd"],
    ["ghs_hazard", "m157", "@dt", "+Kennzeichnung", "&", "+H-Sätze", ">dd"],
    ["ghs_precautionary", "m157", "@dt", "+Sicherheitshinweise - ", ">dd", "*"],
    ["name_registered_ger", "m86", "@tbody", "<tr", "*"],
    ["name_registered_eng", "m86", "@tbody", "<tr", "*"],
    ["nfpa_health", "m477", "@dt", "+Gesundheitsgefahr", ">dd"],
    ["nfpa_fire", "m477", "@dt", "+Brandgefahr", ">dd"],
    ["nfpa_reactivity", "m477", "@dt", "+Reaktionsgefahr", ">dd"],
    ["nfpa_specific", "m477", "@dt", "+Anweisungen", ">dd"],
    ["wgk_class", "m328", "@dt", "=Kenn-Nummer", ">dd"],
    ["wgk_link", "m328", "@dt", "+Rigoletto", ">dd"],
    ["pc_colour", "m73", "@dt", "=Farbe", ">dd"],
    ["pc_consistency", "m25", "@dt", "=Stoffbeschaffenheit", ">dd"],
    ["pc_density", "m42", "@dt", "+Dichte", "&", "-Einheit", ">dd"],
    ["pc_energy_ionisation", "m61", "@dt", "+Ionisierungspotential", "&", "-Einheit", ">dd"],
    ["pc_enthalpy_vaporisation", "m58", "@dt", "+Verdampfungsenthalpie", "&", "-Einheit", ">dd"],
    ["pc_flammability_limit_lower", "m66", "@dt", "+Untere Explosion", "&", "-Einheit", ">dd"],
    ["pc_flammability_limit_upper", "m65", "@dt", "+Obere Explosion", "&", "-Einheit", ">dd"],
    ["pc_odour", "m71", "@dt", "+Geruch", ">dd", "*"],
    ["pc_pressure_critical", "m32", "@dt", "+Kritischer Druck", "&", "-Einheit", ">dd"],
    ["pc_pressure_vapor", "m45", "@dt", "+Dampfdruck", "&", "-Einheit", ">dd"],
    ["pc_refractive_index", "m34", "@dt", "+Brechungsindex", ">dd"],
    ["pc_refractive_index_wavelength", "m34", "@dt", "+Wellenlänge", "&", "-Einheit", ">dd"],
    ["pc_state_of_matter", "m24", "@dt", "+Aggregatzustand", ">dd"],
    ["pc_surface_tension", "m35", "@dt", "+Oberflächenspannung", "&", "-Einheit", ">dd"],
    ["pc_temperature_boiling", "m30", "@dt", "+Siedetemperatur", "&", "-Einheit", ">dd"],
    ["pc_temperature_critical", "m31", "@dt", "+Kritische Temperatur", "&", "-Einheit", ">dd"],
    ["pc_temperature_flash", "m62", "@dt", "+Flammpunkt", "&", "-Einheit", ">dd"],
    ["pc_temperature_melting", "m27", "@dt", "+Schmelztemperatur", "&", "-Einheit", ">dd"],
    ["pc_viscosity", "m36", "@dt", "+Viskosität", "&", "-Einheit", ">dd"],
    # ["pc_xlogp", "m53", "@dt", "+Verteilungskoeffizient", ">dd"],
]


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-03-04    fJ      1.0     Dev tests: passed ... works as intended
# ++ 24-02-28    fJ      0.4     Reworked error handling
# ++ 24-02-19    fJ      0.3     Reworked and pythonised
# ++ 24-02-06    fJ      0.2     Added docstring
# ++ 24-02-02    fJ      0.1     Created
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
        WelSearchField.send_keys(Keys.ENTER)
        # Sleep so the browser catches up to the visual change
        sleep(DRV_SLEEPTIME)

        WelHitField: WebElement = fctSelenium.GetSingleWebElement(WdrParent=WdrDriver, descriptor=XPATH_SEARCH_HITS)
        if "Keine Treffer" in WelHitField.text:
            return []
        return fctSelenium.GetWebElements(WdrParent=WelHitField, descriptor=XPATH_SEARCH_HITLIST)

    # Handle a seldom StaleElement exception by raising a retry exception handled one level up
    except (StaleElementReferenceException, AttributeError) as Error:
        LogLOGGER.warning(Error)
        raise RetryException()


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-03-04    fJ      1.0     Dev tests: passed ... works as intended
# ++ 24-02-28    fJ      0.4     Reworked error handling
# ++ 24-02-19    fJ      0.3     Reworked and pythonised
# ++ 24-02-06    fJ      0.2     Added docstring
# ++ 24-02-02    fJ      0.1     Created
# ++---------------------------------------------------------------------------------------------------------------------++#
def CleanHitList(WdrDriver: WebDriver, hit_list: list[WebElement]) -> list[WebElement]:
    """Tries to return a cleaned hit list from the search hit list in case of multiple hits.\n
    Likely intended hits are defined by the string "Einzelinhaltsstoff" in the hit's text.\n
    - -> | <WdrDriver> Webdriver to use\n
    - -> | <hit_list> List of hit elements\n
    - <- | <return> Cleaned list of hit elements"""

    cleaned_hit_list = []

    try:
        for WelHit in hit_list:
            # NOTE: We need to force scroll the target into view to access its content
            fctSelenium.ScrollTo(WdrDriver=WdrDriver, WelTarget=WelHit)
            if "Einzelinhaltsstoff" in WelHit.text:
                cleaned_hit_list.append(WelHit)

    # Handle a seldom StaleElement exception by raising a retry exception handled one level up
    except (StaleElementReferenceException, AttributeError) as Error:
        LogLOGGER.warning(Error)
        raise RetryException()

    return cleaned_hit_list


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-03-04    fJ      1.0     Dev tests: passed ... works as intended
# ++ 24-02-28    fJ      0.4     Reworked error handling
# ++ 24-02-19    fJ      0.3     Reworked and pythonised
# ++ 24-02-06    fJ      0.2     Added docstring
# ++ 24-02-05    fJ      0.1     Created
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
            hit_list = CleanHitList(WdrDriver=WdrDriver, hit_list=hit_list)
            status = f"Most probable out of {len(hit_list)} query hits selected for <{query_term}>."

        if len(hit_list) == 0:
            status = f"Chemikalieninfo | Skipped <{query_term}>: No query hit found!"
        # Check again if cleaning wasn't successful
        elif len(hit_list) > 1:
            status = f"Chemikalieninfo | Skipped<{query_term}>: More than one query hit found!"
        else:
            status = f"Chemikalieninfo | Success! {status}" if "status" in locals() else "Chemikalieninfo | Success!"

            # NOTE: Accessing the link with Enter leads to "?dv=18" (Ansicht: Standardansicht), which clutters datasheet
            #       representation. Set it to "?dv=0" (Ansicht: [Alle Merkmale]).
            WelHit = fctSelenium.GetSingleWebElement(WdrParent=hit_list[0], descriptor=XPATH_SEARCH_HIT)
            hit_link = WelHit.get_attribute("href").replace("?", "?dv=0&")
            fctSelenium.NavigateURL(WdrDriver=WdrDriver, url=hit_link)

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
# ++ 24-02-28    fJ      0.4     Reworked error handling
# ++ 24-02-19    fJ      0.3     Reworked and pythonised
# ++ 24-02-06    fJ      0.2     Added docstring
# ++ 24-02-04    fJ      0.1     Created
# ++---------------------------------------------------------------------------------------------------------------------++#
def GetElements(WelDossier: WebElement, locators: list[str]) -> WebElement | list[WebElement] | None:
    """Returns definition list entry/entries based on a location descriptor list.\n
    - -> | <WelDossier> Compound data web dossier\n
    - -> | <locators> Location descriptor list\n
    - <- | <return> Web element(s) located by the descriptor list"""

    try:
        welParent = fctSelenium.GetSingleWebElement(
            WdrParent=WelDossier,
            descriptor=f".//h4[@id='{locators[1]}']/parent::div | .//h3[@id='{locators[1]}']/parent::div",
            no_timeout=True,
        )

        if welParent is None:
            return None

        strXpath, get_multiple = fctSelenium.XpathConstructor(locators[2:])
        if not get_multiple:
            return fctSelenium.GetSingleWebElement(WdrParent=welParent, descriptor=strXpath, no_timeout=True)
        else:
            return fctSelenium.GetWebElements(WdrParent=welParent, descriptor=strXpath, no_timeout=True)

    # Handle a seldom StaleElement exception by raising a retry exception handled one level up
    except (StaleElementReferenceException, AttributeError) as Error:
        LogLOGGER.warning(Error)
        raise RetryException()


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-03-04    fJ      1.0     Dev tests: passed ... works as intended
# ++ 24-02-28    fJ      0.4     Reworked error handling
# ++ 24-02-19    fJ      0.3     Reworked and pythonised
# ++ 24-02-06    fJ      0.2     Added docstring
# ++ 24-02-05    fJ      0.1     Created
# ++---------------------------------------------------------------------------------------------------------------------++#
@Retry(RetryException)
def GetCompoundData(WdrDriver: WebDriver | None, query_term: str, query_status: str) -> dict[str, Any]:
    """Returns a dictionary of selected compound data from the Chemikalieninfo website.\n
    - -> | <WdrDriver> Webdriver to use\n
    - -> | <query_term> Term of the PubChem query\n
    - -> | <query_status> Status of PubChem compound query\n
    - <- | <return> Compound data dictionary"""

    cpd_data: dict[str, Any] = {}

    # Get basic compound data that allways should be returned
    cpd_data["query_status_ci"] = query_status
    cpd_data["query_term_ci"] = query_term
    cpd_data["query_database_ci"] = "Chemikalieninfo Public"
    cpd_data["query_time_ci"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if "Success!" in query_status:
        try:
            cpd_data["query_finding_ci"] = fctSelenium.GetSingleWebElement(
                WdrParent=WdrDriver, descriptor=XPATH_DOSSIER_HEADING
            ).text
            cpd_data["query_link_ci"] = WdrDriver.current_url.split("?")[0]

            WelDossier: WebElement = fctSelenium.GetSingleWebElement(WdrParent=WdrDriver, descriptor=XPATH_DOSSIER)

            # Get data from definition lists using xpath_dossier_deflists
            for def_list in XPATH_DOSSIER_DEF_LISTS:
                WelData = GetElements(WelDossier=WelDossier, locators=def_list)

                if WelData is None or not WelData:
                    cpd_data[def_list[0]] = NOT_LISTED
                    continue

                if isinstance(WelData, list):
                    # Handle special cases: registered names (html: table)
                    if "name_registered" in def_list[0]:
                        if def_list[0] in cpd_data:
                            continue

                        name_reg_ger = []
                        name_reg_eng = []
                        for WelDate in WelData:
                            # NOTE: We need to force scroll the target into view to access its content
                            fctSelenium.ScrollTo(WdrDriver=WdrDriver, WelTarget=WelDate)
                            if WelDate.text.split(" ")[-1].lower() == "deutsch":
                                name_reg_ger.append(" ".join(WelDate.text.split(" ")[1:-1]))
                            if WelDate.text.split(" ")[-1].lower() == "englisch":
                                name_reg_eng.append(" ".join(WelDate.text.split(" ")[1:-1]))
                        cpd_data["name_registered_ger"] = "|".join(name_reg_ger)
                        cpd_data["name_registered_eng"] = "|".join(name_reg_eng)
                        continue

                    # Get data from web element lists
                    if isinstance(WelData, list):
                        data_list = []
                        for WelDate in WelData:
                            # NOTE: We need to force scroll the target into view to access its content
                            fctSelenium.ScrollTo(WdrDriver=WdrDriver, WelTarget=WelDate)
                            data_list.append(WelDate.text)
                        data = "|".join(data_list)

                    # Handle special cases: precautionary statements aggregation
                    if def_list[0] == "ghs_precautionary":
                        data = GetGhsStatements(str_input=data, RePattern=RepPRECAUTIONARIES)

                    cpd_data[def_list[0]] = data
                    continue

                fctSelenium.ScrollTo(WdrDriver=WdrDriver, WelTarget=WelData)

                # Handle special cases: GHS class aggregation
                if def_list[0] == "ghs_class":
                    WelGhsImgs: WebElement = fctSelenium.GetWebElements(
                        WdrParent=WelData, descriptor=".//img", no_timeout=True
                    )
                    if WelGhsImgs is not None:
                        cpd_data[def_list[0]] = "|".join([WelGhsImg.get_attribute("alt") for WelGhsImg in WelGhsImgs])
                    continue

                # Handle special cases: hazard statements aggregation
                if def_list[0] == "ghs_hazard":
                    cpd_data[def_list[0]] = GetGhsStatements(str_input=WelData.text, RePattern=RepHAZARDS)
                    continue

                # Get other data
                cpd_data[def_list[0]] = WelData.text

        # Handle a seldom StaleElement exception by retrying
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
# ++ 24-02-19    fJ      0.4     Reworked and pythonised
# ++ 24-02-06    fJ      0.3     Added docstring
# ++ 24-02-05    fJ      0.2     Refactored
# ++ 24-02-02    fJ      0.1     Created
# ++---------------------------------------------------------------------------------------------------------------------++#
def QueryChemInfo(WdrDriver: WebDriver, query_term: str) -> dict[str, Any]:
    """Queries Chemikalieninfo for a query term and returns compound data.\n
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
        status = f"Chemikalieninfo | Skipped <{query_term}>: Error! This is not your fault. Retrying later may help ..."
        cpd_data = GetCompoundData(WdrDriver=None, query_term=query_term, query_status=status)

    return cpd_data


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-03-04    fJ      1.0     Dev tests: passed ... works as intended
# ++ 24-02-19    fJ      0.1     Created
# ++---------------------------------------------------------------------------------------------------------------------++#
def InitChemInfoDataset() -> dict[str, Any]:
    """Initialises the dictionary for the returned dataset namedtuple constructor.\n
    - <- | <return> Dataset constructor"""
    cpd_data: dict[str, Any] = {}
    cpd_data["query_status_ci"] = None
    cpd_data["query_term_ci"] = None
    cpd_data["query_database_ci"] = None
    cpd_data["query_time_ci"] = None
    cpd_data["query_finding_ci"] = None
    cpd_data["query_link_ci"] = None
    for deflist in XPATH_DOSSIER_DEF_LISTS:
        cpd_data[deflist[0]] = None

    return cpd_data


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-02-16    fJ      1.0     Unit test: passed indirectly
# ++ 24-02-16    fJ      0.1     Created
# ++---------------------------------------------------------------------------------------------------------------------++#
DATASET = InitChemInfoDataset().keys()
NtpCI_CONSTRUCTOR = namedtuple(typename="compound_data", field_names=DATASET, defaults=(None,) * len(DATASET))
"""Named tuple constructor for compound data. Gets initialized by InitChemInfoDataset()."""
