#
# Didn't invest the time to get this running ...
#
# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ Imports
# ++---------------------------------------------------------------------------------------------------------------------++#
import unittest
from unittest.mock import MagicMock, patch

import customtkinter as ctk

from src.fctlib.ctk import (
    GetCtkVar,
    GetWidgetAttribute,
    ResizeCtkWindowByWidgetSize,
    SetCtkVar,
    SetWidgetAttribute,
    ToggleWidgetState,
    ToggleWidgetVisibility,
)


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ Unit test for SetCtkVar (generated by Cody.AI)
# ++---------------------------------------------------------------------------------------------------------------------++#
class TestSetCtkVar(unittest.TestCase):
    @patch("src.fctlib.ctk.ctk")
    def test_set_ctkvar_valid(self, mock_ctk):
        mock_var = mock_ctk.Variable()
        SetCtkVar(mock_var, "test")
        mock_var.set.assert_called_with("test")

    @patch("src.fctlib.ctk.ctk")
    def test_set_ctkvar_none(self, mock_ctk):
        mock_var = mock_ctk.Variable()
        SetCtkVar(mock_var, None)
        mock_var.set.assert_not_called()


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ Unit test for GetCtkVar (generated by Cody.AI)
# ++---------------------------------------------------------------------------------------------------------------------++#
class TestGetCtkVar(unittest.TestCase):
    @patch("customtkinter.CTkVariable")
    def test_get_ctkvar_string(self, mock_var):
        mock_var.get.return_value = "test"
        result = GetCtkVar(mock_var)
        self.assertEqual(result, "test")

    @patch("customtkinter.CTkVariable")
    def test_get_ctkvar_int(self, mock_var):
        mock_var.get.return_value = 123
        result = GetCtkVar(mock_var)
        self.assertEqual(result, 123)

    @patch("customtkinter.CTkVariable")
    def test_get_ctkvar_none(self, mock_var):
        mock_var.get.return_value = None
        result = GetCtkVar(mock_var)
        self.assertEqual(result, None)


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ Unit test for GetWidgetAttribute (generated by Cody.AI)
# ++---------------------------------------------------------------------------------------------------------------------++#
class TestGetWidgetAttribute(unittest.TestCase):
    def test_get_text(self):
        mock_widget = MagicMock(spec=ctk.CTkBaseClass)
        mock_widget.cget.return_value = "Hello World"

        result = GetWidgetAttribute(mock_widget, "text")

        self.assertEqual(result, "Hello World")

    def test_get_textvariable(self):
        mock_var = MagicMock()
        mock_widget = MagicMock(spec=ctk.CTkBaseClass)
        mock_widget.cget.return_value = mock_var

        result = GetWidgetAttribute(mock_widget, "textvariable")

        self.assertEqual(result, mock_var)

    def test_invalid_attribute(self):
        mock_widget = MagicMock(spec=ctk.CTkBaseClass)

        with self.assertRaises(AttributeError):
            GetWidgetAttribute(mock_widget, "invalid")


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ Unit test for SetWidgetAttribute (generated by Cody.AI)
# ++---------------------------------------------------------------------------------------------------------------------++#
class TestSetWidgetAttribute(unittest.TestCase):
    @patch("customtkinter.CTkBaseClass.configure")
    def test_set_text(self, mock_configure):
        widget = ctk.CTkLabel()
        SetWidgetAttribute(widget, "text", "Hello World")
        mock_configure.assert_called_with(text="Hello World")

    @patch("customtkinter.CTkBaseClass.configure")
    def test_set_textvariable(self, mock_configure):
        widget = ctk.CTkLabel()
        var = ctk.StringVar()
        SetWidgetAttribute(widget, "textvariable", var)
        mock_configure.assert_called_with(textvariable=var)

    def test_invalid_attribute(self):
        widget = ctk.CTkLabel()
        with self.assertRaises(AttributeError):
            SetWidgetAttribute(widget, "invalid", "value")


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ Unit test for ToggleWidgetVisibility (generated by Cody.AI)
# ++---------------------------------------------------------------------------------------------------------------------++#
class TestToggleWidgetVisibility(unittest.TestCase):
    @patch("src.fctlib.ctk.ResizeCtkWindowByWidgetSize")
    def test_visible_to_hidden(self, mock_resize):
        mock_widget = ctk.CTkButton()
        mock_widget.winfo_ismapped.return_value = True

        result = ToggleWidgetVisibility(mock_widget, force_hide=True)

        self.assertFalse(result)
        mock_widget.grid_remove.assert_called_once()
        mock_resize.assert_called_once_with(mock_widget, shrink_window=True, resize_width=False)

    @patch("src.fctlib.ctk.ResizeCtkWindowByWidgetSize")
    def test_hidden_to_visible(self, mock_resize):
        mock_widget = ctk.CTkButton()
        mock_widget.winfo_ismapped.return_value = False

        result = ToggleWidgetVisibility(mock_widget)

        self.assertTrue(result)
        mock_widget.grid.assert_called_once()
        mock_resize.assert_called_once_with(mock_widget, shrink_window=False, resize_width=False)

    def test_resize_width(self):
        mock_widget = ctk.CTkButton()
        mock_widget.winfo_ismapped.return_value = False

        ToggleWidgetVisibility(mock_widget, resize_width=True)

        mock_widget.grid.assert_called_once()

    def test_already_hidden(self):
        mock_widget = ctk.CTkButton()
        mock_widget.winfo_ismapped.return_value = False

        result = ToggleWidgetVisibility(mock_widget, force_hide=True)

        self.assertFalse(result)
        mock_widget.grid_remove.assert_not_called()


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ Unit test for ResizeCtkWindowByWidgetSize (generated by Cody.AI)
# ++---------------------------------------------------------------------------------------------------------------------++#
class TestResizeCtkWindowByWidgetSize(unittest.TestCase):
    @patch("src.fctlib.ctk.windll")
    def test_shrink_window(self, mock_windll):
        mock_windll.shcore.GetScaleFactorForDevice.return_value = 100
        mock_ctk_window = ctk.CTk()
        mock_ctk_window.geometry("400x300")
        mock_ctk_widget = ctk.CTkButton(master=mock_ctk_window, width=100, height=50)

        ResizeCtkWindowByWidgetSize(mock_ctk_widget, shrink_window=True)

        mock_ctk_window.geometry.assert_called_with("300x250")

    @patch("src.fctlib.ctk.windll")
    def test_stretch_window(self, mock_windll):
        mock_windll.shcore.GetScaleFactorForDevice.return_value = 100
        mock_ctk_window = ctk.CTk()
        mock_ctk_window.geometry("400x300")
        mock_ctk_widget = ctk.CTkButton(master=mock_ctk_window, width=100, height=50)

        ResizeCtkWindowByWidgetSize(mock_ctk_widget, shrink_window=False)

        mock_ctk_window.geometry.assert_called_with("500x350")

    @patch("src.fctlib.ctk.windll")
    def test_resize_width(self, mock_windll):
        mock_windll.shcore.GetScaleFactorForDevice.return_value = 100
        mock_ctk_window = ctk.CTk()
        mock_ctk_window.geometry("400x300")
        mock_ctk_widget = ctk.CTkButton(master=mock_ctk_window, width=100, height=50)

        ResizeCtkWindowByWidgetSize(mock_ctk_widget, resize_width=True)

        mock_ctk_window.geometry.assert_called_with("500x300")


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ Unit test for ToggleWidgetState (generated by Cody.AI)
# ++---------------------------------------------------------------------------------------------------------------------++#
class TestToggleWidgetState(unittest.TestCase):
    def test_single_widget_enable(self):
        mock_widget = ctk.CTkButton()
        mock_widget.configure(state="disabled")

        result = ToggleWidgetState(mock_widget)

        self.assertEqual(result, ["normal"])
        mock_widget.configure.assert_called_with(state="normal")

    def test_single_widget_disable(self):
        mock_widget = ctk.CTkButton()

        result = ToggleWidgetState(mock_widget)

        self.assertEqual(result, ["disabled"])
        mock_widget.configure.assert_called_with(state="disabled")

    def test_multiple_widgets(self):
        mock_widget1 = ctk.CTkButton(state="disabled")
        mock_widget2 = ctk.CTkButton(state="normal")

        result = ToggleWidgetState([mock_widget1, mock_widget2])

        self.assertEqual(result, ["normal", "disabled"])

    def test_force_enable(self):
        mock_widget = ctk.CTkButton(state="disabled")

        result = ToggleWidgetState(mock_widget, force_enable=True)

        self.assertEqual(result, ["normal"])
        mock_widget.configure.assert_called_with(state="normal")

    def test_force_disable(self):
        mock_widget = ctk.CTkButton(state="normal")

        result = ToggleWidgetState(mock_widget, force_disable=True)

        self.assertEqual(result, ["disabled"])
        mock_widget.configure.assert_called_with(state="disabled")
