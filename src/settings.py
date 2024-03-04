# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ Imports
# ++---------------------------------------------------------------------------------------------------------------------++#
from datetime import datetime
from pathlib import Path

# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ App settings
# ++---------------------------------------------------------------------------------------------------------------------++#
# App details
APP_NAME = "ChemDB: SDB Query Tool"
APP_AUTHOR = "Falko Jähnert"
APP_MAIL = "mrsiege[AT]web[DOT]de"
APP_VERSION = "b1.0"
APP_UPDATE_DATE = "2024-03-03"
APP_GITHUB_LINK = "https://github.com/MsrSiege/ChemDB"
APP_STATUS = "Production"
APP_LICENCE = None

# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ File and folder paths
# ++---------------------------------------------------------------------------------------------------------------------++#
PthASSET_ICON = Path.cwd() / "assets" / "ChemDB.png"
"""Application icon asset path."""
PthASSET_FILEDIALOG = Path.cwd() / "assets" / "FileDialog.png"
"""Folder dialog icon asset path."""
PthCONFIG_FILE = Path.cwd() / "config.ini"
"""Config.ini file path."""
PthLOGFILE = Path.cwd() / "logs" / f"{datetime.now().strftime('%Y-%m')}.log"
"""Log file path."""


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ CustomTkinter Settings
# ++---------------------------------------------------------------------------------------------------------------------++#
STD_FONT_FAMILY = "Aptos"
""" GUI font family."""
STD_SIZE = 14
""" GUI base size for fonts and widgets."""
GUI_PADDING = 8
""" GUI standard padding."""

# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ IO settings
# ++---------------------------------------------------------------------------------------------------------------------++#
SUPPORTED_EXTENSIONS = {
    "Excel Files": (".xlsx", ".xls"),
    "CSV Files": (".csv",),
}
"""File extensions supported by the app."""

SUPPORTED_REQUEST_COL_NAMES = ["CAS", "Name"]
"""Column names supported as sources for web requests.""" ""

# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ Queries settings
# ++---------------------------------------------------------------------------------------------------------------------++#
NOT_LISTED = "Not listed!"
"""String used for denoting not listed entries."""

# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ Selenium settings
# ++---------------------------------------------------------------------------------------------------------------------++#
DRV_RUN_HEADLESS = True
"""Switch to run webdriver in headless mode."""
DRV_SLEEPTIME = 0.25
"""Time to sleep between webdriver actions."""
DRV_TIMEOUT = 3
"""Timeout for webdriver actions."""
DRV_NO_TIMEOUT = 0.01
"""Timeout and poll frequency for webdriver actions if none is needed."""
