# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ Imports
# ++---------------------------------------------------------------------------------------------------------------------++#
from multiprocessing import cpu_count
from pathlib import Path
from queue import Queue
from time import sleep
from typing import Optional

from selenium import webdriver
from selenium.common.exceptions import JavascriptException, NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as Expect
from selenium.webdriver.support.wait import WebDriverWait

from src.fctlib.logging import LogLOGGER
from src.settings import DRV_NO_TIMEOUT, DRV_RUN_HEADLESS, DRV_SLEEPTIME, DRV_TIMEOUT

# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ Global webdriver elements
# ++---------------------------------------------------------------------------------------------------------------------++#
WEBDRIVERS: dict[int, WebDriver | None] = {}
"""Global selenium webdriver instances dictionary. Contains webdriver instances indexed by their worker ID for queueing."""
QueWEBDRIVERS: Queue = Queue()
"""Global selenium webdriver instances queue. Contains webdriver instance worker IDs for queueing."""

# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ Module variables
# ++---------------------------------------------------------------------------------------------------------------------++#
BY_LOCATORS = {
    "CLASS_NAME": By.CLASS_NAME,
    "CSS_SELECTOR": By.CSS_SELECTOR,
    "ID": By.ID,
    "XPATH": By.XPATH,
}
"""Selenium locators lookup dictionary"""


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-03-04    fJ      2.0     Dev tests: passed ... works as intended
# ++ 24-02-25    fJ      1.2     Replaced os.path with pathlib.Path
# ++ 24-02-16    fJ      1.1     Deleted unspecific error handling
# ++ 24-02-14    fJ      1.0     Dev tests: passed ... works as intended
# ++ 24-02-13    fJ      0.1     Separated from InitWebDriver, reworked to be invoked on initialisation
# ++---------------------------------------------------------------------------------------------------------------------++#
def InitChromeOptions() -> Options:
    """Initialises global chrome webdriver options.\n
    - <- | <return> Chrome options"""

    WopChromeOptions = webdriver.ChromeOptions()

    WopChromeOptions.add_argument("--disable-dev-shm-usage")
    WopChromeOptions.add_argument("--disable-extensions")
    WopChromeOptions.add_argument("--disable-features=Translate")
    WopChromeOptions.add_argument("--disable-search-engine-choice-screen")
    if DRV_RUN_HEADLESS:
        WopChromeOptions.add_argument("--headless=new")
    WopChromeOptions.add_argument("--incognito")
    WopChromeOptions.add_argument("--no-default-browser-check")
    WopChromeOptions.add_argument("--no-first-run")
    WopChromeOptions.add_argument("--start-maximized")
    # WopChromeOptions.add_argument("--enable-chrome-browser-cloud-management")
    WopChromeOptions.add_experimental_option(name="prefs", value={"profile.managed_default_content_settings.images": 2})
    WopChromeOptions.add_experimental_option(name="excludeSwitches", value=["logging", "enable-automation"])

    PthChromeBinary = Path.cwd() / "src" / "chrome-win64" / "chrome.exe"
    if PthChromeBinary.is_file():
        WopChromeOptions.binary_location = str(PthChromeBinary)
    else:
        LogLOGGER.warning("The bundled chrome binary can't be accessed. Trying system default ...")

    return WopChromeOptions


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-03-04    fJ      2.0     Dev tests: passed ... works as intended
# ++ 24-02-25    fJ      1.2     Replaced os.path with pathlib.Path
# ++ 24-02-16    fJ      1.1     Deleted unspecific error handling
# ++ 24-02-14    fJ      1.0     Dev tests: passed ... works as intended
# ++ 24-02-13    fJ      0.1     Separated from InitWebDriver, reworked to be invoked on initialisation
# ++---------------------------------------------------------------------------------------------------------------------++#
def InitChromeService() -> Service:
    """Initialises global chrome webdriver service.\n
    - <- | <return> Chrome service"""

    PthLogFile = Path.cwd() / "logs" / "selenium.log"
    PthLogFile.parent.mkdir(parents=True, exist_ok=True)
    WsvChromeService = Service(
        service_args=[
            # log levels: ALL | DEBUG | INFO | WARNING | SEVERE | OFF
            "--log-level=WARNING",
            "--append-log",
            "--readable-timestamp",
        ],
        log_output=str(PthLogFile),
    )

    return WsvChromeService


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-03-04    fJ      2.0     Dev tests: passed ... works as intended
# ++ 24-02-27    fJ      1.3     Moved Options and Service initialisation into the function for threading compatibility
# ++ 24-02-26    fJ      1.2     Reworked to get rid of global webdriver instance
# ++ 24-02-16    fJ      1.1     Deleted unspecific error handling
# ++ 24-02-14    fJ      1.0     Dev tests: passed ... works as intended
# ++ 24-02-13    fJ      0.3     Reworked and pythonised
# ++ 24-02-06    fJ      0.2     Added docstring
# ++ 24-02-04    fJ      0.1     Created
# ++---------------------------------------------------------------------------------------------------------------------++#
def InitWebDriver(use_existing: Optional[bool] = True) -> WebDriver | None:
    """Initialises and returns a new or returns an existing selenium webdriver.\n
    - <- | <use_existing> Switch to use an existing webdriver if available\n
    - <- | <return> Webdriver or None if it can't be initialised"""

    # Get the last webdriver instance from the global webdriver instances dictionary
    WdrDriver = next((dict_value for dict_value in reversed(list(WEBDRIVERS.values())) if dict_value is not None), None)

    if use_existing and WdrDriver is not None:
        return WdrDriver

    WopChromeOptions = InitChromeOptions()
    WsvChromeService = InitChromeService()
    if WopChromeOptions is None or WsvChromeService is None:
        LogLOGGER.error("Webdriver components not initialised.")
        return None

    # Create a new webdriver instance and append it to the global webdriver instances dictionary and queue
    worker_id = max(list(WEBDRIVERS.keys())) + 1 if len(WEBDRIVERS) > 0 else 0
    QueWEBDRIVERS.put(worker_id)
    WEBDRIVERS[worker_id] = webdriver.Chrome(options=WopChromeOptions, service=WsvChromeService)

    return WEBDRIVERS[worker_id]


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-03-04    fJ      1.0     Dev tests: passed ... works as intended
# ++ 24-02-27    fJ      0.1     Created
# ++---------------------------------------------------------------------------------------------------------------------++#
def InitWebDriversForThreading(max_threads: Optional[int] = 1):
    """Initialises multiple webdrivers for threading.\n
    - -> | <max_threads> Maximum number of webdriver threads\n
    The function ensures that the generated threads count never exceeds the logical CPU count."""

    if max_threads > cpu_count():
        max_threads = cpu_count()

    QuitWebDrivers()

    for _ in list(range(max_threads)):
        InitWebDriver(use_existing=False)
    return


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-03-04    fJ      2.0     Dev tests: passed ... works as intended
# ++ 24-02-16    fJ      1.1     Deleted unspecific error handling
# ++ 24-02-14    fJ      1.0     Dev tests: passed ... works as intended
# ++ 24-02-14    fJ      0.3     Reworked and pythonised
# ++ 24-02-06    fJ      0.2     Added docstring
# ++ 24-02-04    fJ      0.1     Created
# ++---------------------------------------------------------------------------------------------------------------------++#
def NavigateURL(WdrDriver: WebDriver, url: str):
    """Navigates to the given URL.\n
    - -> | <WdrDriver> WebDriver to use\n
    - -> | <url> URL to navigate to"""

    WdrDriver.get(url)
    # Sleep so the browser catches up to the visuals change
    sleep(DRV_SLEEPTIME)


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-03-04    fJ      2.0     Dev tests: passed ... works as intended
# ++ 24-02-16    fJ      1.1     Deleted unspecific error handling
# ++ 24-02-14    fJ      1.0     Dev tests: passed ... works as intended
# ++ 24-02-13    fJ      0.3     Reworked and pythonised
# ++ 24-02-06    fJ      0.2     Added docstring
# ++ 24-02-01    fJ      0.1     Created
# ++---------------------------------------------------------------------------------------------------------------------++#
def ScrollTo(WdrDriver: WebDriver, WelTarget: WebElement):
    """Scrolls the given target into view.\n
    - -> | <WdrDriver> Target element-containing WebDriver\n
    - -> | <WelTarget> Target element\n
    On occasions, we need to force scroll the target into view to get access to its content."""

    try:
        while not WelTarget.is_displayed():
            WdrDriver.execute_script("arguments[0].scrollIntoView(true);", WelTarget)
    # JavascriptException usually means that the element is not defined
    except JavascriptException:
        LogLOGGER.warning(f"Element <{WelTarget.__class__}> not defined!")


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-03-04    fJ      2.0     Dev tests: passed ... works as intended
# ++ 24-02-19    fJ      1.2     Deleted retry decorator
# ++ 24-02-16    fJ      1.1     Deleted unspecific error handling
# ++ 24-02-14    fJ      1.0     Dev tests: passed ... works as intended
# ++ 24-02-14    fJ      0.3     Reworked and pythonised
# ++ 24-02-06    fJ      0.2     Added docstring
# ++ 24-02-01    fJ      0.1     Created
# ++---------------------------------------------------------------------------------------------------------------------++#
def GetSingleWebElement(
    WdrParent: WebDriver | WebElement,
    descriptor: str,
    locator: Optional[str] = "XPATH",
    no_timeout: Optional[bool] = False,
) -> WebElement | None:
    """Gets single specific web element from the parent.\n
    - -> | <WdrParent> Target element-containing WebDriver or WebElement\n
    - -> | <descriptor> Descriptor uniquely identifying the target element\n
    - -> | <locator> Locator to identify the target element by\n
    - -> | <no_timeout> Switch for WebDriverWait to not use a timeout\n
    - <- | <return> Found web element or None in case of an error"""

    timeout = DRV_TIMEOUT if not no_timeout else DRV_NO_TIMEOUT
    poll_freq = DRV_SLEEPTIME if not no_timeout else DRV_NO_TIMEOUT

    try:
        # Get web element using WebDriverWait() to wait for their presence
        # NOTE: "Presence" seems to be enough to get the elements content, "Visibility" is not necessary
        WelElement = WebDriverWait(WdrParent, timeout, poll_freq).until(
            Expect.presence_of_element_located((BY_LOCATORS[locator], descriptor))
        )

    # Handle exceptions that may occur if web element is not present at all
    except (NoSuchElementException, TimeoutException):
        LogLOGGER.debug(f"Element(s) not found: <{WdrParent.__class__}>:<{descriptor}> by <{locator}>.")
        return None

    return WelElement


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-03-04    fJ      1.0     Dev tests: passed ... works as intended
# ++ 24-02-01    fJ      0.1     Created from GetSingleWebElement
# ++---------------------------------------------------------------------------------------------------------------------++#
def GetWebElements(
    WdrParent: WebDriver | WebElement,
    descriptor: str,
    locator: Optional[str] = "XPATH",
    no_timeout: Optional[bool] = False,
) -> list[WebElement] | None:
    """Gets multiple specific web elements from the parent.\n
    - -> | <WdrParent> Target elements-containing WebDriver or WebElement\n
    - -> | <descriptor> Descriptor uniquely identifying the target elements\n
    - -> | <locator> Locator to identify the target elements by\n
    - -> | <no_timeout> Switch for WebDriverWait to not use a timeout\n
    - <- | <return> Found web elements or None in case of an error"""

    timeout = DRV_TIMEOUT if not no_timeout else DRV_NO_TIMEOUT
    poll_freq = DRV_SLEEPTIME if not no_timeout else DRV_NO_TIMEOUT

    try:
        # Get web elements using WebDriverWait() to wait for their presence
        # NOTE: "Presence" seems to be enough to get the elements content, "Visibility" is not necessary
        WelElement = WebDriverWait(WdrParent, timeout, poll_freq).until(
            Expect.presence_of_all_elements_located((BY_LOCATORS[locator], descriptor))
        )

    # Handle exceptions that may occur if web element is not present at all
    except (NoSuchElementException, TimeoutException):
        LogLOGGER.debug(f"Element(s) not found: <{WdrParent.__class__}>:<{descriptor}> by <{locator}>.")
        return None

    return WelElement


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-03-04    fJ      1.0     Dev tests: passed ... works as intended
# ++ 24-02-19    fJ      0.3     Reworked and pythonised
# ++ 24-02-06    fJ      0.2     Added docstring
# ++ 24-02-04    fJ      0.1     Created
# ++---------------------------------------------------------------------------------------------------------------------++#
def XpathConstructor(locator_list: list[str]) -> tuple[str, bool]:
    """Constructs an XPath based on a location descriptor list.\n
    - -> | <locator_list> List of location descriptors (Descriptor name|parent ID|target XPath parts ...)\n
    - <- | <return> Tuple: resulting XPath, switch to get multiple elements"""

    xpath_list = [".//"]
    xpath_closed = False
    get_multiple = False

    for locator in locator_list:
        match locator[0]:
            # XPath: target
            case "@":
                xpath_list.append(f"{locator[1:]}[")
            # XPath: is string
            case "=":
                xpath_list.append(f"text()='{locator[1:]}'")
            # XPath: contains string
            case "+":
                xpath_list.append(f"contains(text(),'{locator[1:]}')")
            # XPath: don't contain string
            case "-":
                xpath_list.append(f"not(contains(text(),'{locator[1:]}'))")
            # XPath: and
            case "&":
                xpath_list.append(" and ")
            # XPath: targets' relative, first following sibling
            case ">":
                xpath_list.append(f"]/following-sibling::{locator[1:]}[1]")
                xpath_closed = True
            # XPath: targets' relative, first child
            case "<":
                xpath_list.append(f"]/{locator[1:]}")
                xpath_closed = True
            # Modifier: get multiple elements
            case "*":
                get_multiple = True

    xpath = "".join(xpath_list)

    # Close XPath
    if xpath[-1] != "]" and not xpath_closed:
        xpath += "]"
    # Get rid of empty brackets
    xpath = xpath.replace("[]", "")

    return xpath, get_multiple


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-03-04    fJ      2.0     Dev tests: passed ... works as intended
# ++ 24-02-27    fJ      1.2     Changed to quitting all webdriver instances instead of one for threading capability
# ++ 24-02-16    fJ      1.1     Deleted unspecific error handling
# ++ 24-02-14    fJ      1.0     Dev tests: passed ... works as intended
# ++ 24-02-14    fJ      0.3     Reworked and pythonised
# ++ 24-02-06    fJ      0.2     Added docstring
# ++ 24-02-05    fJ      0.1     Created
# ++---------------------------------------------------------------------------------------------------------------------++#
def QuitWebDrivers():
    """Quits all running webdriver instances and clears global webdriver instances dictionary."""

    for WdrDriver in WEBDRIVERS.values():
        if WdrDriver is not None:
            WdrDriver.close()
    WEBDRIVERS.clear()
