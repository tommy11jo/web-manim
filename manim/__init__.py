#!/usr/bin/env python
from __future__ import annotations

from importlib.metadata import version

__version__ = version(__name__)


# isort: off

# many scripts depend on this -> has to be loaded first
from ._config import *
from .utils.commands import *

# isort: on

from .camera.camera import *
from .camera.mapping_camera import *
from .camera.moving_camera import *
from .camera.multi_camera import *
from .constants import *
from .mobject.frame import *
from .mobject.geometry.arc import *
from .mobject.geometry.labeled import *
from .mobject.geometry.line import *
from .mobject.geometry.polygram import *
from .mobject.geometry.shape_matchers import *
from .mobject.geometry.tips import *
from .mobject.graph import *
from .mobject.graphing.coordinate_systems import *
from .mobject.graphing.functions import *
from .mobject.graphing.number_line import *
from .mobject.graphing.probability import *
from .mobject.graphing.scale import *
from .mobject.matrix import *
from .mobject.mobject import *
from .mobject.svg.brace import *
from .mobject.svg.svg_mobject import *
from .mobject.table import *
from .mobject.text.code_mobject import *
from .mobject.text.numbers import *
from .mobject.text.tex_mobject import *
from .mobject.text.text_mobject import *
from .mobject.types.image_mobject import *
from .mobject.types.point_cloud_mobject import *
from .mobject.types.vectorized_mobject import *
from .mobject.value_tracker import *
from .mobject.vector_field import *
from .renderer.web_renderer import *
from .scene.moving_camera_scene import *
from .scene.scene import *
from .scene.section import *
from .utils.bezier import *
from .utils.color import *
from .utils.config_ops import *
from .utils.debug import *
from .utils.images import *
from .utils.iterables import *
from .utils.paths import *
from .utils.rate_functions import *
from .utils.simple_functions import *
from .utils.space_ops import *
from .utils.tex import *
from .utils.tex_templates import *
