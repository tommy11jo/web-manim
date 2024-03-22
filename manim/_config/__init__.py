from manim.constants import RendererType
from ..utils.color.manim_colors import BLACK
from .logger_utils import make_logger

__all__ = [
    "logger",
    "console",
    "error_console",
    "config",
]

logger, console, error_console = make_logger(
    # no logger for now
)
# config = {"frame_width": 1600, "frame_height": 900, "pixel_width": 1, "pixel_height": 1}
# web-manim
# DO: allow this config to be updated by scene perhaps?
FRAME_WIDTH = 800
FRAME_HEIGHT = 800
# config = {
#     "frame_width": FRAME_WIDTH,
#     "frame_height": FRAME_HEIGHT,
#     "pixel_width": 1,
#     "pixel_height": 1,
# }


class ManimConfig:
    def __init__(self):
        self.frame_height = FRAME_HEIGHT
        self.frame_width = FRAME_WIDTH
        self.pixel_width = 1
        self.pixel_height = 1
        self.frame_x_radius = self.frame_width / 2
        self.frame_y_radius = self.frame_height / 2
        self.background_color = BLACK
        self.background_opacity = 1.0

        self.renderer = RendererType.CAIRO

        # appease
        self.dry_run = False
        self.input_file = None
        self.output_file = None
        self.media_dir = None
        self.save_sections = False

    # also make dict-like access and setting work
    def __getitem__(self, key):
        try:
            return getattr(self, key)
        except AttributeError as e:
            raise KeyError(f"'ManimConfig' object has no key '{key}'") from e

    def __setitem__(self, key, value):
        setattr(self, key, value)


config = ManimConfig()
