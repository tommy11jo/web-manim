"""Utilities for working with mobjects."""

from __future__ import annotations

__all__ = [
    "get_mobject_class",
    "get_point_mobject_class",
    "get_vectorized_mobject_class",
]

from .._config import config
from ..constants import RendererType
from .mobject import Mobject
from .types.point_cloud_mobject import PMobject
from .types.vectorized_mobject import VMobject


def get_mobject_class() -> type:
    if config.renderer == RendererType.CAIRO:
        return Mobject
    raise NotImplementedError(
        "Base mobjects are not implemented for the active renderer."
    )


def get_vectorized_mobject_class() -> type:
    if config.renderer == RendererType.CAIRO:
        return VMobject
    raise NotImplementedError(
        "Vectorized mobjects are not implemented for the active renderer."
    )


def get_point_mobject_class() -> type:

    if config.renderer == RendererType.CAIRO:
        return PMobject
    raise NotImplementedError(
        "Point cloud mobjects are not implemented for the active renderer."
    )
