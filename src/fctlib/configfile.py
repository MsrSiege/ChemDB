# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ Imports
# ++---------------------------------------------------------------------------------------------------------------------++#
from configparser import ConfigParser
from typing import Any

from src.fctlib.logging import LogLOGGER
from src.settings import PthCONFIG_FILE


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-03-04    fJ      1.0     Unit test: passed
# ++ 24-02-27    fJ      0.1     Created
# ++---------------------------------------------------------------------------------------------------------------------++#
def StoreConfig(config: dict[str, dict[str, Any]]):
    """Stores current config of the app to a config file.\n
    - -> | <config> Config dictionary containing section string(s) and parameters dictionaries"""

    CfgList = ConfigParser()
    for section, params in config.items():
        CfgList[section] = params

    with open(PthCONFIG_FILE, "w") as CfgFile:
        CfgList.write(CfgFile)


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-03-04    fJ      1.0     Unit test: passed
# ++ 24-02-27    fJ      0.1     Created
# ++---------------------------------------------------------------------------------------------------------------------++#
def GetConfig() -> dict[str, dict[str, Any]]:
    """Gets the config from a config file in printable form.\n
    - <- | <return> Config as dictionary, section:params()"""

    try:
        CfgList = ConfigParser()
        CfgList.read(PthCONFIG_FILE)
    except FileNotFoundError as Error:
        LogLOGGER.error(f"Error while reading config file: {Error}.")
        return {}

    cfg_list = {section: {key: value} for section in CfgList.sections() for key, value in CfgList.items(section)}
    return cfg_list


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-03-04    fJ      1.0     Unit test: passed
# ++ 24-02-27    fJ      0.1     Created
# ++---------------------------------------------------------------------------------------------------------------------++#
def GetConfigValue(section: str, config_key: str) -> Any:
    """Gets a config value from a config file.\n
    - -> | <section> Section of the config dictionary\n
    - -> | <config_key> Key corresponding to the config value\n
    - <- | <return> Config value as expected var type or None if either no config value was found or the value was not a valid var type"""

    try:
        CfgList = ConfigParser()
        CfgList.read(PthCONFIG_FILE)
    except FileNotFoundError as Error:
        LogLOGGER.error(f"Error while reading config file: {Error}.")
        return None

    try:
        value = CfgList[section][config_key]
        if value.lower() == "true":
            return True
        elif value.lower() == "false":
            return False
        elif value.isdigit() or (value[0] == "-" and value[1:].isdigit()):
            return int(value)
        else:
            raise KeyError
    except KeyError:
        LogLOGGER.error(f"Could not get config value for {config_key} in {section} section of the config file.")
        return None
