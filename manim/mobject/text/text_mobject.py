from typing import Sequence

from manim.constants import *
from manim.mobject.svg.svg_mobject import SVGMobject
from manim.mobject.types.vectorized_mobject import VGroup, VMobject
from manim.utils.color import ManimColor, ParsableManimColor

TEXT_MOB_SCALE_FACTOR = 0.05
DEFAULT_LINE_SPACING_SCALE = 0.3
TEXT2SVG_ADJUSTMENT_FACTOR = 4.8

__all__ = ["Text", "Paragraph", "MarkupText"]


class Paragraph(VGroup):
    r"""Display a paragraph of text.

    For a given :class:`.Paragraph` ``par``, the attribute ``par.chars`` is a
    :class:`.VGroup` containing all the lines. In this context, every line is
    constructed as a :class:`.VGroup` of characters contained in the line.


    Parameters
    ----------
    line_spacing
        Represents the spacing between lines. Defaults to -1, which means auto.
    alignment
        Defines the alignment of paragraph. Defaults to None. Possible values are "left", "right" or "center".

    """

    def __init__(
        self,
        *text: Sequence[str],
        line_spacing: float = -1,
        alignment: str | None = None,
        **kwargs,
    ) -> None:
        # web-manim
        print("Paragraphs not handled yet")


class Text:
    def __init__(
        self,
        text: str,
        fill_opacity: float = 1.0,
        stroke_width: float = 0,
        color: ParsableManimColor | None = None,
        font_size: float = DEFAULT_FONT_SIZE,
        line_spacing: float = -1,
        font: str = "",
        slant: str = NORMAL,
        weight: str = NORMAL,
        gradient: tuple = None,
        tab_width: int = 4,
        **kwargs,
    ) -> None:
        # web-manim
        # DO: Handle when fonts don't exist, or handle loading
        print("Text not handled yet")
        # self.line_spacing = line_spacing
        # self.font = font
        # self._font_size = float(font_size)
        # # needs to be a float or else size is inflated when font_size = 24
        # # (unknown cause)
        # self.slant = slant
        # self.weight = weight
        # self.gradient = gradient
        # self.tab_width = tab_width

        # self.text = text
        # if self.line_spacing == -1:
        #     self.line_spacing = (
        #         self._font_size + self._font_size * DEFAULT_LINE_SPACING_SCALE
        #     )
        # else:
        #     self.line_spacing = self._font_size + self._font_size * self.line_spacing

        # self.color: ManimColor = ManimColor(color) if color else VMobject().color
        # self.fill_opacity = fill_opacity
        # self.stroke_width = stroke_width

    def __repr__(self):
        return f"Text({repr(self.original_text)})"


class MarkupText(SVGMobject):
    """
    Parameters
    ----------

    text
        The text that needs to be created as mobject.
    fill_opacity
        The fill opacity, with 1 meaning opaque and 0 meaning transparent.
    stroke_width
        Stroke width.
    font_size
        Font size.
    line_spacing
        Line spacing.
    font
        Global font setting for the entire text. Local overrides are possible.
    slant
        Global slant setting, e.g. `NORMAL` or `ITALIC`. Local overrides are possible.
    weight
        Global weight setting, e.g. `NORMAL` or `BOLD`. Local overrides are possible.
    gradient
        Global gradient setting. Local overrides are possible.
    warn_missing_font
        If True (default), Manim will issue a warning if the font does not exist in the
        (case-sensitive) list of fonts returned from `manimpango.list_fonts()`.

    Returns
    -------
    :class:`MarkupText`
        The text displayed in form of a :class:`.VGroup`-like mobject.

    """

    def __init__(
        self,
        text: str,
        fill_opacity: float = 1,
        stroke_width: float = 0,
        color: ParsableManimColor | None = None,
        font_size: float = DEFAULT_FONT_SIZE,
        line_spacing: int = -1,
        font: str = "",
        slant: str = NORMAL,
        weight: str = NORMAL,
        justify: bool = False,
        gradient: tuple = None,
        tab_width: int = 4,
        **kwargs,
    ) -> None:
        print("Markup Text not handled yet")
        self.text = text
        self.line_spacing = line_spacing
        # web-manim
        # verify font is supported via katex
        # verify that latex is valid
        self.font = font
        self._font_size = float(font_size)
        self.slant = slant
        self.weight = weight
        self.gradient = gradient
        self.tab_width = tab_width
        self.justify = justify

        self.text = text

        if self.line_spacing == -1:
            self.line_spacing = (
                self._font_size + self._font_size * DEFAULT_LINE_SPACING_SCALE
            )
        else:
            self.line_spacing = self._font_size + self._font_size * self.line_spacing

        self.color = ManimColor(color) if color else VMobject().color

        self.text = text

    def __repr__(self):
        return f"MarkupText({repr(self.text)})"
