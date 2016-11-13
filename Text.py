from cocos.layer import Layer
from cocos.text import Label


class TextSequence(Layer):
    def __init__(self, position=(0, 0), lines=None):
        super().__init__()
        self.lines = lines if lines is not None else []
        self.draw_speed = 0.2
        self.time = 0
        self.chars_shown = 0
        self.line_no = 0

        self.line = ""
        self.disp = Label("", font_name="Arial", font_size=20, anchor_x="left", anchor_y="center")
        self.disp.color = (255, 255, 255, 255)
        self.disp.position = position
        self.add(self.disp)

        self.busy = True

        self.schedule(self.update)

    def update(self, dt):
        if self.line is None:
            return
        self.time += dt
        if self.time >= self.draw_speed:
            add = self.time / self.draw_speed
            self.chars_shown += int(add)
            self.time = 0
        if 0 < self.chars_shown <= len(self.lines[self.line_no]):
            self.line = self.lines[self.line_no][:self.chars_shown]
        elif self.chars_shown > len(self.lines[self.line_no]):
            self.line = self.lines[self.line_no]
        self.disp.element.text = self.line

    def next_line(self):
        if self.line_no >= len(self.lines) - 1:
            self.busy = False
            return
        full = len(self.lines[self.line_no])
        if self.chars_shown < full:
            self.chars_shown = full
        else:
            self.line_no += 1
            self.chars_shown = 0
