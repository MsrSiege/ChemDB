# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ Imports
# ++---------------------------------------------------------------------------------------------------------------------++#
import unittest
from unittest.mock import patch

from src.fctlib import configfile
from src.settings import PthCONFIG_FILE


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ Unit test for StoreConfig (generated by Cody.AI)
# ++---------------------------------------------------------------------------------------------------------------------++#
class TestStoreConfig(unittest.TestCase):
    @patch("src.fctlib.configfile.open", create=True)
    def test_store_config(self, mock_open):
        test_config = {"section1": {"param1": "value1"}}
        configfile.StoreConfig(test_config)

        with open(PthCONFIG_FILE, "r") as f:
            content = f.read()
            self.assertIn("[section1]\nparam1 = value1\n", content)

    def test_store_config_multiple_sections(self):
        test_config = {"section1": {"param1": "value1"}, "section2": {"param2": "value2"}}
        configfile.StoreConfig(test_config)

        with open(PthCONFIG_FILE, "r") as f:
            content = f.read()
            self.assertIn("[section1]\nparam1 = value1\n", content)
            self.assertIn("[section2]\nparam2 = value2\n", content)

    def test_store_config_invalid_input(self):
        invalid_configs = [None, "", 123, ["list"]]
        for invalid_config in invalid_configs:
            with self.assertRaises(Exception):
                configfile.StoreConfig(invalid_config)


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ Unit test for GetConfig (generated by Cody.AI)
# ++---------------------------------------------------------------------------------------------------------------------++#
class TestGetConfig(unittest.TestCase):
    @patch("src.fctlib.configfile.ConfigParser")
    def test_get_config_success(self, mock_parser):
        mock_parser.return_value.sections.return_value = ["section1"]
        mock_parser.return_value.items.return_value = [("key1", "value1")]

        expected = {"section1": {"key1": "value1"}}
        result = configfile.GetConfig()

        self.assertEqual(result, expected)

    @patch("src.fctlib.configfile.ConfigParser")
    def test_get_config_empty(self, mock_parser):
        mock_parser.return_value.sections.return_value = []

        expected = {}
        result = configfile.GetConfig()

        self.assertEqual(result, expected)

    @patch("src.fctlib.configfile.ConfigParser")
    def test_get_config_missing_file(self, mock_parser):
        mock_parser.return_value.read.side_effect = FileNotFoundError

        expected = {}
        result = configfile.GetConfig()

        self.assertEqual(result, expected)

    @patch("src.fctlib.configfile.ConfigParser")
    def test_get_config_ioerror(self, mock_parser):
        mock_parser.return_value.read.side_effect = IOError

        with self.assertRaises(IOError):
            configfile.GetConfig()


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ Unit test for GetConfigValue (generated by Cody.AI)
# ++---------------------------------------------------------------------------------------------------------------------++#
class TestGetConfigValue(unittest.TestCase):
    @patch("src.fctlib.configfile.ConfigParser")
    def test_get_config_value_success(self, mock_parser):
        mock_parser.return_value.__getitem__.return_value.__getitem__.return_value = "123"

        result = configfile.GetConfigValue("section1", "key1")
        self.assertEqual(result, 123)

    @patch("src.fctlib.configfile.ConfigParser")
    def test_get_config_value_not_found(self, mock_parser):
        mock_parser.return_value.__getitem__.side_effect = KeyError

        result = configfile.GetConfigValue("section1", "key1")
        self.assertIsNone(result)

    @patch("src.fctlib.configfile.ConfigParser")
    def test_get_config_value_boolean_true(self, mock_parser):
        mock_parser.return_value.__getitem__.return_value.__getitem__.return_value = "True"

        result = configfile.GetConfigValue("section1", "key1")
        self.assertTrue(result)

    @patch("src.fctlib.configfile.ConfigParser")
    def test_get_config_value_boolean_false(self, mock_parser):
        mock_parser.return_value.__getitem__.return_value.__getitem__.return_value = "False"

        result = configfile.GetConfigValue("section1", "key1")
        self.assertFalse(result)
