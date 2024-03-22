from manim import *


class SquareDemo(Scene):
    def construct(self):
        s = Square(color=RED)
        self.add(s)


scene = SquareDemo()
scene.construct()
scene.render(preview=True)
