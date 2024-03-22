"""Basic canvas for animations."""

from __future__ import annotations

from manim.utils.file_ops import open_file


__all__ = ["Scene"]

import copy
import inspect
import random
import types
from queue import Queue


from manim.scene.section import DefaultSectionType

from typing import TYPE_CHECKING

import numpy as np
from watchdog.events import FileSystemEventHandler

from manim.mobject.mobject import Mobject

from .. import config
from ..camera.camera import Camera
from ..constants import *
from ..renderer.web_renderer import WebRenderer
from ..utils.exceptions import EndSceneEarlyException, RerunSceneException
from ..utils.family import extract_mobject_family_members
from ..utils.iterables import list_difference_update, list_update

if TYPE_CHECKING:
    pass


class RerunSceneHandler(FileSystemEventHandler):
    """A class to handle rerunning a Scene after the input file is modified."""

    def __init__(self, queue):
        super().__init__()
        self.queue = queue

    def on_modified(self, event):
        self.queue.put(("rerun_file", [], {}))


class Scene:
    """A Scene is the canvas of your animation.

    The primary role of :class:`Scene` is to provide the user with tools to manage
    mobjects and animations.  Generally speaking, a manim script consists of a class
    that derives from :class:`Scene` whose :meth:`Scene.construct` method is overridden
    by the user's code.

    Mobjects are displayed on screen by calling :meth:`Scene.add` and removed from
    screen by calling :meth:`Scene.remove`.  All mobjects currently on screen are kept
    in :attr:`Scene.mobjects`.  Animations are played by calling :meth:`Scene.play`.

    A :class:`Scene` is rendered internally by calling :meth:`Scene.render`.  This in
    turn calls :meth:`Scene.setup`, :meth:`Scene.construct`, and
    :meth:`Scene.tear_down`, in that order.

    It is not recommended to override the ``__init__`` method in user Scenes.  For code
    that should be ran before a Scene is rendered, use :meth:`Scene.setup` instead.

    Examples
    --------
    Override the :meth:`Scene.construct` method with your code.

    .. code-block:: python

        class MyScene(Scene):
            def construct(self):
                self.play(Write(Text("Hello World!")))

    """

    def __init__(
        self,
        renderer=None,
        camera_class=Camera,
        always_update_mobjects=False,
        random_seed=None,
        skip_animations=False,
    ):
        self.camera_class = camera_class
        self.always_update_mobjects = always_update_mobjects
        self.random_seed = random_seed
        self.skip_animations = skip_animations

        self.animations = None
        self.stop_condition = None
        self.moving_mobjects = []
        self.static_mobjects = []
        self.time_progression = None
        self.duration = None
        self.last_t = None
        self.queue = Queue()
        self.skip_animation_preview = False
        self.meshes = []
        self.camera_target = ORIGIN
        self.widgets = []
        self.updaters = []
        self.point_lights = []
        self.ambient_light = None
        self.key_to_function_map = {}
        self.mouse_press_callbacks = []
        self.interactive_mode = False

        if renderer is None:
            self.renderer = WebRenderer(
                camera_class=self.camera_class,
                skip_animations=self.skip_animations,
            )
        else:
            self.renderer = renderer
        self.renderer.init_scene(self)

        self.mobjects = []
        # TODO, remove need for foreground mobjects
        self.foreground_mobjects = []
        if self.random_seed is not None:
            random.seed(self.random_seed)
            np.random.seed(self.random_seed)

    @property
    def camera(self):
        return self.renderer.camera

    def __deepcopy__(self, clone_from_id):
        cls = self.__class__
        result = cls.__new__(cls)
        clone_from_id[id(self)] = result
        for k, v in self.__dict__.items():
            if k in ["renderer", "time_progression"]:
                continue
            if k == "camera_class":
                setattr(result, k, v)
            setattr(result, k, copy.deepcopy(v, clone_from_id))
        result.mobject_updater_lists = []

        # Update updaters
        for mobject in self.mobjects:
            cloned_updaters = []
            for updater in mobject.updaters:
                # Make the cloned updater use the cloned Mobjects as free variables
                # rather than the original ones. Analyzing function bytecode with the
                # dis module will help in understanding this.
                # https://docs.python.org/3/library/dis.html
                # TODO: Do the same for function calls recursively.
                free_variable_map = inspect.getclosurevars(updater).nonlocals
                cloned_co_freevars = []
                cloned_closure = []
                for free_variable_name in updater.__code__.co_freevars:
                    free_variable_value = free_variable_map[free_variable_name]

                    # If the referenced variable has not been cloned, raise.
                    if id(free_variable_value) not in clone_from_id:
                        raise Exception(
                            f"{free_variable_name} is referenced from an updater "
                            "but is not an attribute of the Scene, which isn't "
                            "allowed.",
                        )

                    # Add the cloned object's name to the free variable list.
                    cloned_co_freevars.append(free_variable_name)

                    # Add a cell containing the cloned object's reference to the
                    # closure list.
                    cloned_closure.append(
                        types.CellType(clone_from_id[id(free_variable_value)]),
                    )

                cloned_updater = types.FunctionType(
                    updater.__code__.replace(co_freevars=tuple(cloned_co_freevars)),
                    updater.__globals__,
                    updater.__name__,
                    updater.__defaults__,
                    tuple(cloned_closure),
                )
                cloned_updaters.append(cloned_updater)
            mobject_clone = clone_from_id[id(mobject)]
            mobject_clone.updaters = cloned_updaters
            if len(cloned_updaters) > 0:
                result.mobject_updater_lists.append((mobject_clone, cloned_updaters))
        return result

    def render(self, preview: bool = False, last_frame_path: str = ""):
        """
        Renders this Scene.

        Parameters
        ---------
        preview
            If true, opens scene in a file viewer.
        """
        self.setup()
        try:
            self.construct()
        except EndSceneEarlyException:
            pass
        except RerunSceneException:
            self.remove(*self.mobjects)
            self.renderer.clear_screen()
            self.renderer.num_plays = 0
            return True
        self.tear_down()

        # web-manim
        if preview:
            open_file(last_frame_path)

    def setup(self):
        """
        This is meant to be implemented by any scenes which
        are commonly subclassed, and have some common setup
        involved before the construct method is called.
        """
        pass

    def tear_down(self):
        """
        This is meant to be implemented by any scenes which
        are commonly subclassed, and have some common method
        to be invoked before the scene ends.
        """
        pass

    def construct(self):
        """Add content to the Scene.

        From within :meth:`Scene.construct`, display mobjects on screen by calling
        :meth:`Scene.add` and remove them from screen by calling :meth:`Scene.remove`.
        All mobjects currently on screen are kept in :attr:`Scene.mobjects`.  Play
        animations by calling :meth:`Scene.play`.

        Notes
        -----
        Initialization code should go in :meth:`Scene.setup`.  Termination code should
        go in :meth:`Scene.tear_down`.

        Examples
        --------
        A typical manim script includes a class derived from :class:`Scene` with an
        overridden :meth:`Scene.contruct` method:

        .. code-block:: python

            class MyScene(Scene):
                def construct(self):
                    self.play(Write(Text("Hello World!")))

        See Also
        --------
        :meth:`Scene.setup`
        :meth:`Scene.render`
        :meth:`Scene.tear_down`

        """
        pass  # To be implemented in subclasses

    def next_section(
        self,
        name: str = "unnamed",
        type: str = DefaultSectionType.NORMAL,
        skip_animations: bool = False,
    ) -> None:
        """Create separation here; the last section gets finished and a new one gets created.
        ``skip_animations`` skips the rendering of all animations in this section.
        Refer to :doc:`the documentation</tutorials/output_and_config>` on how to use sections.
        """
        self.renderer.file_writer.next_section(name, type, skip_animations)

    def __str__(self):
        return self.__class__.__name__

    def get_attrs(self, *keys: str):
        """
        Gets attributes of a scene given the attribute's identifier/name.

        Parameters
        ----------
        *keys
            Name(s) of the argument(s) to return the attribute of.

        Returns
        -------
        list
            List of attributes of the passed identifiers.
        """
        return [getattr(self, key) for key in keys]

    def get_top_level_mobjects(self):
        """
        Returns all mobjects which are not submobjects.

        Returns
        -------
        list
            List of top level mobjects.
        """
        # Return only those which are not in the family
        # of another mobject from the scene
        families = [m.get_family() for m in self.mobjects]

        def is_top_level(mobject):
            num_families = sum((mobject in family) for family in families)
            return num_families == 1

        return list(filter(is_top_level, self.mobjects))

    def get_mobject_family_members(self):
        """
        Returns list of family-members of all mobjects in scene.
        If a Circle() and a VGroup(Rectangle(),Triangle()) were added,
        it returns not only the Circle(), Rectangle() and Triangle(), but
        also the VGroup() object.

        Returns
        -------
        list
            List of mobject family members.
        """

        if config.renderer == RendererType.CAIRO:
            return extract_mobject_family_members(
                self.mobjects,
                use_z_index=self.renderer.camera.use_z_index,
            )

    def add(self, *mobjects: Mobject):
        """
        Mobjects will be displayed, from background to
        foreground in the order with which they are added.

        Parameters
        ---------
        *mobjects
            Mobjects to add.

        Returns
        -------
        Scene
            The same scene after adding the Mobjects in.

        """
        if config.renderer == RendererType.CAIRO:
            mobjects = [*mobjects, *self.foreground_mobjects]
            self.restructure_mobjects(to_remove=mobjects)
            self.mobjects += mobjects
            if self.moving_mobjects:
                self.restructure_mobjects(
                    to_remove=mobjects,
                    mobject_list_name="moving_mobjects",
                )
                self.moving_mobjects += mobjects
        return self

    def add_mobjects_from_animations(self, animations):
        curr_mobjects = self.get_mobject_family_members()
        for animation in animations:
            if animation.is_introducer():
                continue
            # Anything animated that's not already in the
            # scene gets added to the scene
            mob = animation.mobject
            if mob is not None and mob not in curr_mobjects:
                self.add(mob)
                curr_mobjects += mob.get_family()

    def remove(self, *mobjects: Mobject):
        """
        Removes mobjects in the passed list of mobjects
        from the scene and the foreground, by removing them
        from "mobjects" and "foreground_mobjects"

        Parameters
        ----------
        *mobjects
            The mobjects to remove.
        """
        if config.renderer == RendererType.CAIRO:
            for list_name in "mobjects", "foreground_mobjects":
                self.restructure_mobjects(mobjects, list_name, False)
            return self

    def replace(self, old_mobject: Mobject, new_mobject: Mobject) -> None:
        """Replace one mobject in the scene with another, preserving draw order.

        If ``old_mobject`` is a submobject of some other Mobject (e.g. a
        :class:`.Group`), the new_mobject will replace it inside the group,
        without otherwise changing the parent mobject.

        Parameters
        ----------
        old_mobject
            The mobject to be replaced. Must be present in the scene.
        new_mobject
            A mobject which must not already be in the scene.

        """
        if old_mobject is None or new_mobject is None:
            raise ValueError("Specified mobjects cannot be None")

        def replace_in_list(
            mobj_list: list[Mobject], old_m: Mobject, new_m: Mobject
        ) -> bool:
            # We use breadth-first search because some Mobjects get very deep and
            # we expect top-level elements to be the most common targets for replace.
            for i in range(0, len(mobj_list)):
                # Is this the old mobject?
                if mobj_list[i] == old_m:
                    # If so, write the new object to the same spot and stop looking.
                    mobj_list[i] = new_m
                    return True
            # Now check all the children of all these mobs.
            for mob in mobj_list:  # noqa: SIM110
                if replace_in_list(mob.submobjects, old_m, new_m):
                    # If we found it in a submobject, stop looking.
                    return True
            # If we did not find the mobject in the mobject list or any submobjects,
            # (or the list was empty), indicate we did not make the replacement.
            return False

        # Make use of short-circuiting conditionals to check mobjects and then
        # foreground_mobjects
        replaced = replace_in_list(
            self.mobjects, old_mobject, new_mobject
        ) or replace_in_list(self.foreground_mobjects, old_mobject, new_mobject)

        if not replaced:
            raise ValueError(f"Could not find {old_mobject} in scene")

    def restructure_mobjects(
        self,
        to_remove: Mobject,
        mobject_list_name: str = "mobjects",
        extract_families: bool = True,
    ):
        """
        tl:wr
            If your scene has a Group(), and you removed a mobject from the Group,
            this dissolves the group and puts the rest of the mobjects directly
            in self.mobjects or self.foreground_mobjects.

        In cases where the scene contains a group, e.g. Group(m1, m2, m3), but one
        of its submobjects is removed, e.g. scene.remove(m1), the list of mobjects
        will be edited to contain other submobjects, but not m1, e.g. it will now
        insert m2 and m3 to where the group once was.

        Parameters
        ----------
        to_remove
            The Mobject to remove.

        mobject_list_name
            The list of mobjects ("mobjects", "foreground_mobjects" etc) to remove from.

        extract_families
            Whether the mobject's families should be recursively extracted.

        Returns
        -------
        Scene
            The Scene mobject with restructured Mobjects.
        """
        if extract_families:
            to_remove = extract_mobject_family_members(
                to_remove,
                use_z_index=self.renderer.camera.use_z_index,
            )
        _list = getattr(self, mobject_list_name)
        new_list = self.get_restructured_mobject_list(_list, to_remove)
        setattr(self, mobject_list_name, new_list)
        return self

    def get_restructured_mobject_list(self, mobjects: list, to_remove: list):
        """
        Given a list of mobjects and a list of mobjects to be removed, this
        filters out the removable mobjects from the list of mobjects.

        Parameters
        ----------

        mobjects
            The Mobjects to check.

        to_remove
            The list of mobjects to remove.

        Returns
        -------
        list
            The list of mobjects with the mobjects to remove removed.
        """

        new_mobjects = []

        def add_safe_mobjects_from_list(list_to_examine, set_to_remove):
            for mob in list_to_examine:
                if mob in set_to_remove:
                    continue
                intersect = set_to_remove.intersection(mob.get_family())
                if intersect:
                    add_safe_mobjects_from_list(mob.submobjects, intersect)
                else:
                    new_mobjects.append(mob)

        add_safe_mobjects_from_list(mobjects, set(to_remove))
        return new_mobjects

    # TODO, remove this, and calls to this
    def add_foreground_mobjects(self, *mobjects: Mobject):
        """
        Adds mobjects to the foreground, and internally to the list
        foreground_mobjects, and mobjects.

        Parameters
        ----------
        *mobjects
            The Mobjects to add to the foreground.

        Returns
        ------
        Scene
            The Scene, with the foreground mobjects added.
        """
        self.foreground_mobjects = list_update(self.foreground_mobjects, mobjects)
        self.add(*mobjects)
        return self

    def add_foreground_mobject(self, mobject: Mobject):
        """
        Adds a single mobject to the foreground, and internally to the list
        foreground_mobjects, and mobjects.

        Parameters
        ----------
        mobject
            The Mobject to add to the foreground.

        Returns
        ------
        Scene
            The Scene, with the foreground mobject added.
        """
        return self.add_foreground_mobjects(mobject)

    def remove_foreground_mobjects(self, *to_remove: Mobject):
        """
        Removes mobjects from the foreground, and internally from the list
        foreground_mobjects.

        Parameters
        ----------
        *to_remove
            The mobject(s) to remove from the foreground.

        Returns
        ------
        Scene
            The Scene, with the foreground mobjects removed.
        """
        self.restructure_mobjects(to_remove, "foreground_mobjects")
        return self

    def remove_foreground_mobject(self, mobject: Mobject):
        """
        Removes a single mobject from the foreground, and internally from the list
        foreground_mobjects.

        Parameters
        ----------
        mobject
            The mobject to remove from the foreground.

        Returns
        ------
        Scene
            The Scene, with the foreground mobject removed.
        """
        return self.remove_foreground_mobjects(mobject)

    def bring_to_front(self, *mobjects: Mobject):
        """
        Adds the passed mobjects to the scene again,
        pushing them to he front of the scene.

        Parameters
        ----------
        *mobjects
            The mobject(s) to bring to the front of the scene.

        Returns
        ------
        Scene
            The Scene, with the mobjects brought to the front
            of the scene.
        """
        self.add(*mobjects)
        return self

    def bring_to_back(self, *mobjects: Mobject):
        """
        Removes the mobject from the scene and
        adds them to the back of the scene.

        Parameters
        ----------
        *mobjects
            The mobject(s) to push to the back of the scene.

        Returns
        ------
        Scene
            The Scene, with the mobjects pushed to the back
            of the scene.
        """
        self.remove(*mobjects)
        self.mobjects = list(mobjects) + self.mobjects
        return self

    def clear(self):
        """
        Removes all mobjects present in self.mobjects
        and self.foreground_mobjects from the scene.

        Returns
        ------
        Scene
            The Scene, with all of its mobjects in
            self.mobjects and self.foreground_mobjects
            removed.
        """
        self.mobjects = []
        self.foreground_mobjects = []
        return self

    def get_moving_mobjects(self, *animations: Animation):
        """
        Gets all moving mobjects in the passed animation(s).

        Parameters
        ----------
        *animations
            The animations to check for moving mobjects.

        Returns
        ------
        list
            The list of mobjects that could be moving in
            the Animation(s)
        """
        # Go through mobjects from start to end, and
        # as soon as there's one that needs updating of
        # some kind per frame, return the list from that
        # point forward.
        animation_mobjects = [anim.mobject for anim in animations]
        mobjects = self.get_mobject_family_members()
        for i, mob in enumerate(mobjects):
            update_possibilities = [
                mob in animation_mobjects,
                len(mob.get_family_updaters()) > 0,
                mob in self.foreground_mobjects,
            ]
            if any(update_possibilities):
                return mobjects[i:]
        return []

    def get_moving_and_static_mobjects(self, animations):
        all_mobjects = list_update(self.mobjects, self.foreground_mobjects)
        all_mobject_families = extract_mobject_family_members(
            all_mobjects,
            use_z_index=self.renderer.camera.use_z_index,
            only_those_with_points=True,
        )
        moving_mobjects = self.get_moving_mobjects(*animations)
        all_moving_mobject_families = extract_mobject_family_members(
            moving_mobjects,
            use_z_index=self.renderer.camera.use_z_index,
        )
        static_mobjects = list_difference_update(
            all_mobject_families,
            all_moving_mobject_families,
        )
        return all_moving_mobject_families, static_mobjects
