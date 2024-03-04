# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ Imports
# ++---------------------------------------------------------------------------------------------------------------------++#
import unittest
from pathlib import Path
from unittest.mock import patch

import pandas

from src.fctlib.pandas import GetDfFromFilePath, GetDfFromNtList, GetUniqueColsFromDf, WriteDfToXlsx

#
# Didn't invest the time to get this running ...
#
# # ++---------------------------------------------------------------------------------------------------------------------++#
# # ++ Unit test for GetDfFromFilePath (generated by Cody.AI)
# # ++---------------------------------------------------------------------------------------------------------------------++#
# class TestGetDfFromFilePath(unittest.TestCase):
#     def test_xlsx_file(self):
#         test_file = Path("test.xlsx")
#         expected = pandas.DataFrame({"A": [1, 2], "B": [3, 4]})

#         with patch("pandas.read_excel") as mock_read_excel:
#             mock_read_excel.return_value = expected
#             result = GetDfFromFilePath(test_file)

#         self.assertEqual(result.to_dict(), expected.to_dict())

#     def test_xls_file(self):
#         test_file = Path("test.xls")
#         expected = pandas.DataFrame({"A": [1, 2], "B": [3, 4]})

#         with patch("pandas.read_excel") as mock_read_excel:
#             mock_read_excel.return_value = expected
#             result = GetDfFromFilePath(test_file)

#         self.assertEqual(result.to_dict(), expected.to_dict())

#     def test_csv_file(self):
#         test_file = Path("test.csv")
#         expected = pandas.DataFrame({"A": [1, 2], "B": [3, 4]})

#         with patch("pandas.read_csv") as mock_read_csv:
#             mock_read_csv.return_value = expected
#             result = GetDfFromFilePath(test_file)

#         self.assertEqual(result.to_dict(), expected.to_dict())

#     def test_other_file_extension(self):
#         test_file = Path("test.txt")
#         result = GetDfFromFilePath(test_file)
#         self.assertIsNone(result)

#     def test_permission_error(self):
#         test_file = Path("test.xlsx")

#         with patch("pandas.read_excel") as mock_read_excel:
#             mock_read_excel.side_effect = PermissionError
#             result = GetDfFromFilePath(test_file)

#         self.assertIsNone(result)


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ Unit test for GetUniqueColsFromDf (generated by Cody.AI)
# ++---------------------------------------------------------------------------------------------------------------------++#
class TestGetUniqueColsFromDf(unittest.TestCase):
    def test_single_unique_col(self):
        test_df = pandas.DataFrame({"A": [1, 2], "B": [3, 3]})
        expected = pandas.DataFrame({"B": [3, 3]})
        result = GetUniqueColsFromDf(test_df, ["B"])
        self.assertTrue(expected.equals(result))

    def test_multiple_unique_cols(self):
        test_df = pandas.DataFrame({"A": [1, 2], "B": [3, 4]})
        expected = test_df
        result = GetUniqueColsFromDf(test_df, ["A", "B"])
        self.assertTrue(expected.equals(result))

    def test_no_unique_cols_found(self):
        test_df = pandas.DataFrame({"A": [1, 1], "B": [2, 2]})
        expected = pandas.DataFrame([], index=[0, 1])
        result = GetUniqueColsFromDf(test_df, ["C"])
        self.assertTrue(expected.equals(result))

    def test_empty_df(self):
        test_df = pandas.DataFrame()
        expected = pandas.DataFrame([])
        result = GetUniqueColsFromDf(test_df, ["A"])
        self.assertTrue(expected.equals(result))

    # def test_none_df(self):
    #     with self.assertRaises(TypeError):
    #         GetUniqueColsFromDf(None, ["A"])


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ Unit test for GetDfFromNtList (generated by Cody.AI)
# ++---------------------------------------------------------------------------------------------------------------------++#
class TestGetDfFromNtList(unittest.TestCase):
    def test_normal(self):
        from collections import namedtuple

        TestNT = namedtuple("TestNT", ["col1", "col2"])
        test_data = [TestNT(1, 2), TestNT(3, 4)]

        expected = pandas.DataFrame([[1, 2], [3, 4]], columns=["col1", "col2"])
        result = GetDfFromNtList(test_data, TestNT)

        self.assertEqual(expected.equals(result), True)

    def test_empty(self):
        from collections import namedtuple

        TestNT = namedtuple("TestNT", ["col1", "col2"])
        test_data = []

        expected = pandas.DataFrame(columns=["col1", "col2"])
        result = GetDfFromNtList(test_data, TestNT)

        self.assertEqual(expected.equals(result), True)

    # def test_missing_columns(self):
    #     from collections import namedtuple

    #     TestNT = namedtuple("TestNT", ["col1"])
    #     test_data = [TestNT(1), TestNT(2)]

    #     with self.assertRaises(KeyError):
    #         GetDfFromNtList(test_data, TestNT)


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ Unit test for WriteDfToXlsx (generated by Cody.AI)
# ++---------------------------------------------------------------------------------------------------------------------++#
class TestWriteDfToXlsx(unittest.TestCase):
    @patch("pandas.DataFrame.to_excel")
    def test_write_df_to_xlsx_success(self, mock_to_excel):
        test_df = pandas.DataFrame()
        test_pth = Path("test.xlsx")

        result = WriteDfToXlsx(test_df, test_pth)

        self.assertTrue(result)
        mock_to_excel.assert_called_with(excel_writer=test_pth, sheet_name="Query Output", index=True, engine="openpyxl")

    @patch("pandas.DataFrame.to_excel")
    def test_write_df_to_xlsx_permission_error(self, mock_to_excel):
        test_df = pandas.DataFrame()
        test_pth = Path("test.xlsx")

        mock_to_excel.side_effect = PermissionError()

        result = WriteDfToXlsx(test_df, test_pth)

        self.assertFalse(result)
