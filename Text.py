from cocos.actions import Delay, CallFunc
from cocos.layer import Layer
from cocos.text import Label


class TextSequence(Layer):
    def __init__(self, position=(0, 0), lines=None):
        super().__init__()
        self.lines = [] if lines is None else lines
        self.draw_speed = 0.3
        self.time = 0
        self.chars_shown = 0
        self.line_no = 0
        self.selected_line = "" if lines is None else lines[0]
        self.full_length = 0 if self.selected_line == "" else len(self.selected_line)

        self.line = ""
        self.message = Label("", font_name="Arial", font_size=20, anchor_x="left", anchor_y="center")
        self.message.color = (255, 255, 255, 255)
        self.message.position = position
        self.add(self.message)

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
        if 0 < self.chars_shown < self.full_length:
            self.line = self.selected_line[:self.chars_shown]
        elif self.chars_shown >= self.full_length:
            self.chars_shown = self.full_length
            self.line = self.selected_line
            self.unschedule(self.update)
            self.do(Delay(1) + CallFunc(self.advance))
        self.message.element.text = self.line

    def advance(self):
        if self.chars_shown < self.full_length:
            self.chars_shown = self.full_length
        elif self.line_no >= len(self.lines) - 1:
            self.busy = False
            self.unschedule(self.update)
            return
        else:
            self.line_no += 1
            self.selected_line = self.lines[self.line_no]
            self.full_length = len(self.selected_line)
            self.chars_shown = 0
            self.schedule(self.update)
