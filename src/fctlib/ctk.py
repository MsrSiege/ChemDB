# # ++---------------------------------------------------------------------------------------------------------------------++#
# # ++ Imports
# # ++---------------------------------------------------------------------------------------------------------------------++#
from ctypes import windll
from pathlib import Path
from typing import Any, Callable, Optional

import customtkinter as ctk
from PIL import Image

from src.settings import STD_FONT_FAMILY, STD_SIZE


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-03-04    fJ      1.0     Dev tests: passed ... works as intended
# ++ 24-02-25    fJ      0.2     Changed image to use pathlib path
# ++ 24-02-20    fJ      0.1     Recreated as helper class
# ++---------------------------------------------------------------------------------------------------------------------++#
class BaseWidget(ctk.CTkBaseClass):
    """Base class to set standard widget settings. Needs to get and process all possible widget parameters."""

    # Stores and preserves all ctkWidget instances
    _WidgetInstances = []

    def __init__(
        self,
        master: ctk.CTk | ctk.CTkFrame,
        base_size: Optional[int] = STD_SIZE,
        height: Optional[int] = -1,
        width: Optional[int] = -1,
        corner_radius: Optional[int] = 10,
        fg_color: Optional[str] = None,
        anchor: Optional[str] = "center",
        justify: Optional[str] = "left",
        text: Optional[str | list[str]] = None,
        text_placeholder: Optional[str | list[str]] = None,
        PthImage: Optional[Path] = None,
        font_color: Optional[str] = None,
        font_family: Optional[str] = STD_FONT_FAMILY,
        font_bold: Optional[bool] = False,
        textvariable: Optional[ctk.StringVar] = None,
        wrap: Optional[str] = "none",
        variable: Optional[ctk.BooleanVar] = None,
        FncCommand: Optional[Callable[..., Any]] = None,
        state_disabled: Optional[bool] = False,
    ):
        self.master = master
        self.corner_radius = corner_radius
        self.fg_color = fg_color
        self.anchor = anchor
        self.justify = justify
        self.textvariable = textvariable
        self.text_color = font_color
        self.wrap = wrap
        self.variable = variable
        self.command = FncCommand

        self.height = height if height != -1 else base_size + 14
        self.width = width if width != -1 else base_size * 10
        self.state = "disabled" if state_disabled else "normal"
        self.text = text if PthImage is None else None
        self.text_placeholder = text_placeholder if PthImage is None else None

        self.image = CtkImage(PthImage=PthImage) if PthImage is not None else None
        self.font = CtkFont(family=font_family, size=base_size, weight="bold" if font_bold else "normal")

        # Store instance in class instance list
        self.__class__._WidgetInstances.append(self)

    @classmethod
    def GetWidgetInstances(cls) -> list["BaseWidget"]:
        """Return all ctkWidget instances."""
        return cls._WidgetInstances


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-03-04    fJ      1.0     Dev tests: passed ... works as intended
# ++ 24-02-20    fJ      0.1     Created as helper class
# ++---------------------------------------------------------------------------------------------------------------------++#
class BaseGrid(ctk.CTkBaseClass):
    """Base class to set standard grid settings. Needs to get and process all possible widget parameters."""

    def __init__(
        self,
        row: int,
        column: int,
        padx: int | tuple[int, int] = 0,
        pady: int | tuple[int, int] = 0,
        sticky: Optional[str] = "ew",
        columnspan: Optional[int] = 1,
        colconfig: Optional[int] = None,
        colweight: Optional[int] = None,
        rowconfig: Optional[int] = None,
        rowweight: Optional[int] = None,
    ):
        self.grid(
            row=row,
            column=column,
            padx=padx,
            pady=pady,
            sticky=sticky,
            columnspan=columnspan,
        )
        if colconfig is not None:
            self.grid_columnconfigure(index=colconfig, weight=colweight if colweight is not None else 1)
        if rowconfig is not None:
            self.grid_rowconfigure(index=rowconfig, weight=rowweight if rowweight is not None else 1)


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-03-04    fJ      1.0     Dev tests: passed ... works as intended
# ++ 24-02-20    fJ      0.3     Refactored to get rid of mediator class CtkWidget
# ++ 24-02-12    fJ      0.2     Pythonized ...
# ++ 24-02-07    fJ      0.1     Created
# ++---------------------------------------------------------------------------------------------------------------------++#
class CtkFont(ctk.CTkFont):
    """Custom CTk font class."""

    def __init__(
        self,
        family: Optional[str] = STD_FONT_FAMILY,
        size: Optional[int] = STD_SIZE,
        weight: Optional[str] = "normal",
    ):
        super().__init__(
            family=family,
            size=size,
            weight=weight,
        )


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-03-04    fJ      1.0     Dev tests: passed ... works as intended
# ++ 24-02-25    fJ      0.4     Changed to use pathlib path
# ++ 24-02-20    fJ      0.3     Refactored to get rid of mediator class CtkWidget
# ++ 24-02-12    fJ      0.2     Pythonized ...
# ++ 24-02-07    fJ      0.1     Created
# ++---------------------------------------------------------------------------------------------------------------------++#
class CtkImage(ctk.CTkImage):
    """Custom CTk image class."""

    def __init__(
        self,
        PthImage: Path,
        size: Optional[int] = STD_SIZE + 8,
    ):
        super().__init__(
            light_image=Image.open(PthImage),
            dark_image=Image.open(PthImage),
            size=(size, size),
        )


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-03-04    fJ      1.0     Dev tests: passed ... works as intended
# ++ 24-02-20    fJ      0.3     Refactored, replaced mediator class CtkWidget with helper classes BaseWidget and BaseGrid
# ++ 24-02-12    fJ      0.2     Pythonized ...
# ++ 24-02-07    fJ      0.1     Created
# ++---------------------------------------------------------------------------------------------------------------------++#
class CtkButton(BaseWidget, BaseGrid, ctk.CTkButton):
    """Custom CTk button class."""

    def __init__(self, Widget: dict[Any], Grid: dict[Any]):
        BaseWidget.__init__(self, **Widget)
        ctk.CTkButton.__init__(
            self,
            master=self.master,
            height=self.height,
            # Make square sized in case of image
            width=self.width if self.image is None else self.height,
            corner_radius=self.corner_radius,
            fg_color=self.fg_color,
            anchor=self.anchor,
            text=self.text,
            image=self.image,
            text_color=self.text_color,
            font=self.font,
            command=self.command,
            state=self.state,
        )
        BaseGrid.__init__(self, **Grid)


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-03-04    fJ      1.0     Dev tests: passed ... works as intended
# ++ 24-02-27    fJ      0.1     Created
# ++---------------------------------------------------------------------------------------------------------------------++#
class CtkCheckbox(BaseWidget, BaseGrid, ctk.CTkCheckBox):
    """Custom CTk checkbox class."""

    def __init__(self, Widget: dict[Any], Grid: dict[Any]):
        BaseWidget.__init__(self, **Widget)
        ctk.CTkCheckBox.__init__(
            self,
            master=self.master,
            height=self.height,
            width=self.width,
            corner_radius=self.corner_radius,
            fg_color=self.fg_color,
            textvariable=self.textvariable,
            text=self.text,
            text_color=self.text_color,
            font=self.font,
            variable=self.variable,
            command=self.command,
            state=self.state,
        )
        BaseGrid.__init__(self, **Grid)


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-03-04    fJ      1.0     Dev tests: passed ... works as intended
# ++ 24-02-20    fJ      0.3     Refactored, replaced mediator class CtkWidget with helper classes BaseWidget and BaseGrid
# ++ 24-02-12    fJ      0.2     Pythonized ...
# ++ 24-02-07    fJ      0.1     Created
# ++---------------------------------------------------------------------------------------------------------------------++#
class CtkEntry(BaseWidget, BaseGrid, ctk.CTkEntry):
    """Custom CTk entry field class."""

    def __init__(self, Widget: dict[Any], Grid: dict[Any]):
        BaseWidget.__init__(self, **Widget)
        ctk.CTkEntry.__init__(
            self,
            master=self.master,
            height=self.height,
            width=self.width,
            corner_radius=self.corner_radius,
            fg_color=self.fg_color,
            justify=self.justify,
            textvariable=self.textvariable,
            placeholder_text=self.text_placeholder,
            text_color=self.text_color,
            font=self.font,
            state=self.state,
        )
        BaseGrid.__init__(self, **Grid)


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-03-04    fJ      1.0     Dev tests: passed ... works as intended
# ++ 24-02-20    fJ      0.3     Refactored, replaced mediator class CtkWidget with helper classes BaseWidget and BaseGrid
# ++ 24-02-12    fJ      0.2     Pythonized ...
# ++ 24-02-08    fJ      0.1     Created
# ++---------------------------------------------------------------------------------------------------------------------++#
class CtkFrame(BaseWidget, BaseGrid, ctk.CTkFrame):
    """Custom CTk frame class."""

    def __init__(self, Widget: dict[Any], Grid: dict[Any]):
        BaseWidget.__init__(self, **Widget)
        ctk.CTkFrame.__init__(
            self,
            master=self.master,
            height=self.height,
            width=self.width,
            corner_radius=self.corner_radius,
            fg_color=self.fg_color,
        )
        BaseGrid.__init__(self, **Grid)


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-03-04    fJ      1.0     Dev tests: passed ... works as intended
# ++ 24-02-20    fJ      0.3     Refactored, replaced mediator class CtkWidget with helper classes BaseWidget and BaseGrid
# ++ 24-02-12    fJ      0.2     Pythonized ...
# ++ 24-02-07    fJ      0.1     Created
# ++---------------------------------------------------------------------------------------------------------------------++#
class CtkLabel(BaseWidget, BaseGrid, ctk.CTkLabel):
    """Custom CTk label class."""

    def __init__(self, Widget: dict[Any], Grid: dict[Any]):
        BaseWidget.__init__(self, **Widget)
        ctk.CTkLabel.__init__(
            self,
            master=self.master,
            height=self.height,
            width=self.width,
            corner_radius=self.corner_radius,
            fg_color=self.fg_color,
            anchor=self.anchor,
            textvariable=self.textvariable,
            text=self.text,
            text_color=self.text_color,
            font=self.font,
        )
        BaseGrid.__init__(self, **Grid)


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-03-04    fJ      1.0     Dev tests: passed ... works as intended
# ++ 24-02-20    fJ      0.3     Refactored, replaced mediator class CtkWidget with helper classes BaseWidget and BaseGrid
# ++ 24-02-12    fJ      0.2     Pythonized ...
# ++ 24-02-11    fJ      0.1     Created
# ++---------------------------------------------------------------------------------------------------------------------++#
class CtkProgressBar(BaseWidget, BaseGrid, ctk.CTkProgressBar):
    """Custom CTk progress bar class."""

    def __init__(self, Widget: dict[Any], Grid: dict[Any]):
        BaseWidget.__init__(self, **Widget)
        ctk.CTkProgressBar.__init__(
            self,
            master=self.master,
            height=self.height,
            width=self.width,
            corner_radius=self.corner_radius,
            fg_color=self.fg_color,
        )
        BaseGrid.__init__(self, **Grid)


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-03-04    fJ      1.0     Dev tests: passed ... works as intended
# ++ 24-02-20    fJ      0.3     Refactored, replaced mediator class CtkWidget with helper classes BaseWidget and BaseGrid
# ++ 24-02-12    fJ      0.2     Pythonized ...
# ++ 24-02-07    fJ      0.1     Created
# ++---------------------------------------------------------------------------------------------------------------------++#
class CtkTabView(BaseWidget, BaseGrid, ctk.CTkTabview):
    """Custom CTk tabview class."""

    def __init__(self, Widget: dict[Any], Grid: dict[Any]):
        BaseWidget.__init__(self, **Widget)
        ctk.CTkTabview.__init__(
            self,
            master=self.master,
            height=self.height,
            width=self.width,
            corner_radius=self.corner_radius,
            fg_color=self.fg_color,
            anchor=self.anchor,
            text_color=self.text_color,
            state=self.state,
        )

        for text in self.text:
            self.add(text)

        BaseGrid.__init__(self, **Grid)


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-03-04    fJ      1.0     Dev tests: passed ... works as intended
# ++ 24-02-20    fJ      0.3     Refactored, replaced mediator class CtkWidget with helper classes BaseWidget and BaseGrid
# ++ 24-02-12    fJ      0.2     Pythonized ...
# ++ 24-02-09    fJ      0.1     Created
# ++---------------------------------------------------------------------------------------------------------------------++#
class CtkTextbox(BaseWidget, BaseGrid, ctk.CTkTextbox):
    """Custom CTk textbox class."""

    def __init__(self, Widget: dict[Any], Grid: dict[Any]):
        BaseWidget.__init__(self, **Widget)
        ctk.CTkTextbox.__init__(
            self,
            master=self.master,
            height=self.height,
            width=self.width,
            corner_radius=self.corner_radius,
            fg_color=self.fg_color,
            text_color=self.text_color,
            font=self.font,
            wrap=self.wrap,
            state=self.state,
        )
        BaseGrid.__init__(self, **Grid)


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-03-04    fJ      1.0     Dev tests: passed ... works as intended
# ++ 24-02-27    fJ      0.3     Changed to be compatible with storing config to a file
# ++ 24-02-27    fJ      0.3     Changed to be compatible with different CtkVars
# ++ 24-02-20    fJ      0.2     Deleted unspecific error handling
# ++ 24-02-12    fJ      0.1     Combined from multiple functions
# ++---------------------------------------------------------------------------------------------------------------------++#
def SetCtkVar(CtkWidget: ctk.Variable, value: Any):
    """Sets the value of a CtkVar.\n
    - -> | <CtkWidget> Target CtkVar\n
    - -> | <value> Value to set"""

    if value is not None:
        CtkWidget.set(value)


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-03-04    fJ      1.0     Dev tests: passed ... works as intended
# ++ 24-02-27    fJ      0.2     Changed to be compatible with different CtkVars
# ++ 24-02-21    fJ      0.1     Created
# ++---------------------------------------------------------------------------------------------------------------------++#
def GetCtkVar(CtkWidget: ctk.Variable) -> Any:
    """Gets the value of a CtkVar.\n
    - -> | <CtkWidget> Target CtkVar\n
    - <- | <return> Value of the CtkVar"""

    return CtkWidget.get()


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-03-04    fJ      1.0     Dev tests: passed ... works as intended
# ++ 24-02-21    fJ      0.1     Created
# ++---------------------------------------------------------------------------------------------------------------------++#
def GetWidgetAttribute(CtkWidget: ctk.CTkBaseClass, wdg_attribute: str) -> Any:
    """Gets the value of a widget attribute.\n
    - -> | <CtkWidget> Target widget\n
    - -> | <wdg_attribute> Widgets attribute to get\n
    - <- | <return> Value of the widgets attribute"""

    return CtkWidget.cget(wdg_attribute)


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-03-04    fJ      1.0     Dev tests: passed ... works as intended
# ++ 24-02-21    fJ      0.1     Created
# ++---------------------------------------------------------------------------------------------------------------------++#
def SetWidgetAttribute(CtkWidget: ctk.CTkBaseClass, wdg_attribute: str, value: Any):
    """Sets the value of a widget attribute.\n
    - -> | <CtkWidget> Target widget\n
    - -> | <wdg_attribute> Widgets attribute to set, supported: text | textvariable\n
    - -> | <value> Value to set"""

    match wdg_attribute:
        case "text":
            CtkWidget.configure(text=value)
        case "textvariable":
            CtkWidget.configure(textvariable=value)


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-03-04    fJ      1.0     Dev tests: passed ... works as intended
# ++ 24-02-22    fJ      0.5     Separated windows resizing to ResizeCtkWindowByWidgetSize()
# ++ 24-02-20    fJ      0.4     Deleted unspecific error handling
# ++ 24-02-12    fJ      0.3     Adopted to window scaling
# ++ 24-02-12    fJ      0.2     Pythonized ...
# ++ 24-02-09    fJ      0.1     Created
# ++---------------------------------------------------------------------------------------------------------------------++#
def ToggleWidgetVisibility(
    CtkWidget: ctk.CTkBaseClass,
    force_hide: Optional[bool] = False,
    resize_width: Optional[bool] = False,
) -> bool:
    """Toggles the visibility of a tkinter widget and rescales the window height (and width if requested) accordingly.\n
    - -> | <CtkWidget> Target widget\n
    - -> | <force_hide> Switch to force hiding the widget\n
    - -> | <resize_width> Switch to also rescale the width\n
    - <- | <return> Resulting widget visibility: True | False"""

    if CtkWidget.winfo_ismapped() or force_hide:
        ResizeCtkWindowByWidgetSize(CtkWidget=CtkWidget, shrink_window=True, resize_width=resize_width)
        CtkWidget.grid_remove()
        return False

    CtkWidget.grid()
    ResizeCtkWindowByWidgetSize(CtkWidget=CtkWidget, shrink_window=False, resize_width=resize_width)
    return True


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-03-04    fJ      1.0     Dev tests: passed ... works as intended
# ++ 24-02-22    fJ      0.1     Separated from ToggleWidgetVisibility()
# ++---------------------------------------------------------------------------------------------------------------------++#
def ResizeCtkWindowByWidgetSize(
    CtkWidget: ctk.CTkBaseClass,
    shrink_window: Optional[bool] = False,
    resize_width: Optional[bool] = False,
):
    """Rescales the window height (and width if requested) based on a widgets size.\n
    - -> | <CtkWidget> Target widget\n
    - -> | <shrink_window> Switch to shrink or stretch the window by the widget size\n
    - -> | <resize_width> Switch to also rescale the width"""

    screen_scaling_factor = float(windll.shcore.GetScaleFactorForDevice(0) * 0.01)

    ctkWindow = CtkWidget.winfo_toplevel()
    window_curr_width = int(ctkWindow.winfo_width() / screen_scaling_factor)
    window_curr_height = int(ctkWindow.winfo_height() / screen_scaling_factor)

    widget_width = int(CtkWidget.winfo_width() / screen_scaling_factor) if resize_width else 0
    widget_height = int(CtkWidget.winfo_height() / screen_scaling_factor)

    if shrink_window:
        ctkWindow.geometry(f"{window_curr_width - widget_width}x{window_curr_height - widget_height}")
        return

    ctkWindow.geometry(f"{window_curr_width + widget_width}x{window_curr_height + widget_height}")
    return


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-03-04    fJ      1.0     Dev tests: passed ... works as intended
# ++ 24-02-20    fJ      0.2     Deleted unspecific error handling
# ++ 24-02-12    fJ      0.1     Combined from multiple functions
# ++---------------------------------------------------------------------------------------------------------------------++#
def ToggleWidgetState(
    CtkWidgets: ctk.CTkBaseClass | list[ctk.CTkBaseClass],
    force_enable: Optional[bool] = False,
    force_disable: Optional[bool] = False,
) -> list[str]:
    """Toggles the state of one ore multiple tkinter widgets. Compatible widgets: Button | EntryField | TabView | TextBox\n
    - -> | <CtkWidgets> Target widget(s)\n
    - -> | <force_enable> Switch to force enabling the widget\n
    - -> | <force_disable> Switch to force disabling the widget\n
    - <- | <return> List of final widget states: normal | disabled"""

    CtkWidgets = CtkWidgets if isinstance(CtkWidgets, list) else [CtkWidgets]

    final_states = []
    for CtkWidget in CtkWidgets:
        CtkWidget.configure(
            state="normal"
            if force_enable
            else "disabled"
            if force_disable
            else "normal"
            if CtkWidget.cget("state") == "disabled"
            else "disabled"
        )
        final_states.append(CtkWidget.cget("state"))
    return final_states
