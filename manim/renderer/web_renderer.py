from __future__ import annotations

import typing

import numpy as np


from ..camera.camera import Camera
from ..mobject.mobject import Mobject
from ..utils.iterables import list_update

if typing.TYPE_CHECKING:

    from manim.scene.scene import Scene

__all__ = ["WebRenderer"]


# web-manim
class WebRenderer:
    """A renderer built for use on the web."""

    def __init__(
        self,
        camera_class=None,
        **kwargs,
    ):
        # All of the following are set to EITHER the value passed via kwargs,
        # OR the value stored in the global config dict at the time of
        # _instance construction_.
        camera_cls = camera_class if camera_class is not None else Camera
        self.camera = camera_cls()
        self.static_image = None

    def init_scene(self, scene):
        # web-manim
        pass

    def update_frame(  # TODO Description in Docstring
        self,
        scene,
        mobjects: typing.Iterable[Mobject] | None = None,
        include_submobjects: bool = True,
        ignore_skipping: bool = True,
        **kwargs,
    ):
        """Update the frame.

        Parameters
        ----------
        scene

        mobjects
            list of mobjects

        include_submobjects

        ignore_skipping

        **kwargs

        """
        if not mobjects:
            mobjects = list_update(
                scene.mobjects,
                scene.foreground_mobjects,
            )
        if self.static_image is not None:
            self.camera.set_frame_to_background(self.static_image)
        else:
            self.camera.reset()

        kwargs["include_submobjects"] = include_submobjects
        self.camera.capture_mobjects(mobjects, **kwargs)

    def render(self, scene, time, moving_mobjects):
        self.update_frame(scene, moving_mobjects)
        self.add_frame(self.get_frame())

    def get_frame(self):
        """
        Gets the current frame as NumPy array.

        Returns
        -------
        np.array
            NumPy array of pixel values of each pixel in screen.
            The shape of the array is height x width x 3
        """
        return np.array(self.camera.pixel_array)

    def show_frame(self, scene):
        """
        Opens the current frame in the Default Image Viewer
        of your system.
        """
        self.update_frame(scene, ignore_skipping=True)
        self.camera.get_image().show()

    def save_static_frame_data(
        self,
        scene: Scene,
        static_mobjects: typing.Iterable[Mobject],
    ) -> typing.Iterable[Mobject] | None:
        """Compute and save the static frame, that will be reused at each frame
        to avoid unnecessarily computing static mobjects.

        Parameters
        ----------
        scene
            The scene played.
        static_mobjects
            Static mobjects of the scene. If None, self.static_image is set to None

        Returns
        -------
        typing.Iterable[Mobject]
            The static image computed.
        """
        self.static_image = None
        if not static_mobjects:
            return None
        self.update_frame(scene, mobjects=static_mobjects)
        self.static_image = self.get_frame()
        return self.static_image
