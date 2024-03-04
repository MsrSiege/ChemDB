# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ Imports
# ++---------------------------------------------------------------------------------------------------------------------++#
import unittest
from pathlib import Path
from unittest.mock import patch

from src.fctlib.io import GetFilePaths, GetFolderPath, GetSupportedFilesFromPath


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ Unit test for GetFolderPath (generated by Cody.AI)
# ++---------------------------------------------------------------------------------------------------------------------++#
class TestGetFolderPath(unittest.TestCase):
    @patch("tkinter.filedialog.askdirectory")
    def test_valid_folder_selected(self, mock_askdirectory):
        mock_askdirectory.return_value = "/test/folder"
        result = GetFolderPath()
        self.assertEqual(result, Path("/test/folder"))

    @patch("tkinter.filedialog.askdirectory")
    def test_no_folder_selected(self, mock_askdirectory):
        mock_askdirectory.return_value = ""
        result = GetFolderPath()
        self.assertIsNone(result)

    @patch("tkinter.filedialog.askdirectory")
    def test_cancel_pressed(self, mock_askdirectory):
        mock_askdirectory.return_value = None
        result = GetFolderPath()
        self.assertIsNone(result)


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ Unit test for GetFilePaths (generated by Cody.AI)
# ++---------------------------------------------------------------------------------------------------------------------++#
class TestGetFilePaths(unittest.TestCase):
    @patch("src.fctlib.io.filedialog")
    def test_no_selection(self, mock_filedialog):
        mock_filedialog.askopenfilenames.return_value = []
        result = GetFilePaths({"Excel": ".xlsx"})
        self.assertEqual(result, [])

    @patch("src.fctlib.io.filedialog")
    def test_valid_selection(self, mock_filedialog):
        mock_filedialog.askopenfilenames.return_value = ["file1.xlsx", "file2.csv"]
        result = GetFilePaths({"Excel": ".xlsx", "CSV": ".csv"})
        self.assertEqual(result, [Path("file1.xlsx"), Path("file2.csv")])

    @patch("src.fctlib.io.filedialog")
    def test_unsupported_extension(self, mock_filedialog):
        mock_filedialog.askopenfilenames.return_value = ["file.exe", "file.txt"]
        result = GetFilePaths({"Excel": ".xlsx"})
        self.assertEqual(result, [])

    @patch("src.fctlib.io.filedialog")
    def test_relative_path(self, mock_filedialog):
        mock_filedialog.askopenfilenames.return_value = ["folder/file.xlsx"]
        result = GetFilePaths({"Excel": ".xlsx"})
        self.assertEqual(result, [Path("folder/file.xlsx")])

    @patch("src.fctlib.io.filedialog")
    def test_absolute_path(self, mock_filedialog):
        mock_filedialog.askopenfilenames.return_value = ["/full/path/to/file.xlsx"]
        result = GetFilePaths({"Excel": ".xlsx"})
        self.assertEqual(result, [Path("/full/path/to/file.xlsx")])


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ Unit test for GetSupportedFilesFromPath (generated by Cody.AI)
# ++---------------------------------------------------------------------------------------------------------------------++#
class TestGetSupportedFilesFromPath(unittest.TestCase):
    def test_empty_file_paths(self):
        file_paths = []
        extensions = {"Excel": ".xlsx"}
        result = GetSupportedFilesFromPath(file_paths, extensions)
        self.assertEqual(result, [])

    def test_no_supported_files(self):
        file_paths = [Path("file1.txt"), Path("file2.jpg")]
        extensions = {"Excel": ".xlsx"}
        result = GetSupportedFilesFromPath(file_paths, extensions)
        self.assertEqual(result, [])

    def test_supported_files_filtered(self):
        file_paths = [Path("file1.xlsx"), Path("file2.jpg")]
        extensions = {"Excel": ".xlsx"}
        expected = [Path("file1.xlsx")]
        result = GetSupportedFilesFromPath(file_paths, extensions)
        self.assertEqual(result, expected)

    def test_hidden_files_excluded(self):
        file_paths = [Path(".hidden"), Path("file.xlsx")]
        extensions = {"Excel": ".xlsx"}
        expected = [Path("file.xlsx")]
        result = GetSupportedFilesFromPath(file_paths, extensions)
        self.assertEqual(result, expected)

    def test_office_owner_files_excluded(self):
        file_paths = [Path("~$owner.xlsx"), Path("file.xlsx")]
        extensions = {"Excel": ".xlsx"}
        expected = [Path("file.xlsx")]
        result = GetSupportedFilesFromPath(file_paths, extensions)
        self.assertEqual(result, expected)

    def test_output_files_excluded(self):
        file_paths = [Path("file_OUT.xlsx"), Path("file.xlsx")]
        extensions = {"Excel": ".xlsx"}
        expected = [Path("file.xlsx")]
        result = GetSupportedFilesFromPath(file_paths, extensions)
        self.assertEqual(result, expected)