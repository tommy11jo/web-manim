from manim import *


class SquareDemo(Scene):
    def __init__(self):
        super().__init__()
        self.last_frame_path = ""
        self.cur_frame = 0

    def construct(self):
        s = Square(color=RED)
        self.add(s)
        # self.capture()
        self.renderer.show_frame(self)

    def capture(self):
        # self.file_suffix not used atm
        self.renderer.camera.capture_mobjects(self.mobjects)
        pixel_array = self.renderer.camera.pixel_array
        img = self.renderer.camera.get_image(pixel_array).copy()
        self.last_frame_path = f"./media/square/step{self.cur_frame}.png"
        img.save(self.last_frame_path)
        self.renderer.camera.reset()
        self.cur_frame += 1


scene = SquareDemo()
scene.construct()
# scene.render(preview=True, last_frame_path=scene.last_frame_path)
