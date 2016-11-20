import string

from cocos.actions import Delay, CallFunc
from cocos.layer import Layer
from cocos.text import Label


class RegularLabel(Label):
    def __init__(self, txt, **kwargs):
        super().__init__(txt, **kwargs)
        self._text = self.element.text

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, new_text):
        self._text = self.element.text = new_text


class CenteredLabel(RegularLabel):
    def __init__(self, txt, center, **kwargs):
        super().__init__(txt, **kwargs)
        self.center = center
        self.position = center

    @property
    def final_text(self):
        return

    @final_text.setter
    def final_text(self, final_text):
        offset = Label(final_text,
                       font_name=self.element.font_name,
                       font_size=self.element.font_size).element.content_width
        self.position = (self.center[0] - offset / 2, self.center[1])


class TextSequence(Layer):
    speed = {"fast": 0.1, "med": 0.3, "slow": 0.5}

    def __init__(self, centered=False, draw_speed="med", position=(0, 0), lines=None, delay=1):
        super().__init__()
        self.centered = centered
        self.lines = [] if lines is None else lines
        self.draw_speed = self.speed.get(draw_speed, self.speed["med"])
        self.time = 0
        self.chars_shown = 0
        self.line_no = 0
        self.selected_line = "" if lines is None else lines[0]
        self.full_length = 0 if self.selected_line == "" else len(self.selected_line)
        self.delay = delay
        self.ready = False

        self.line = ""
        if self.centered:
            self.message = CenteredLabel("", position, font_name="Arial", font_size=20, anchor_x="left",
                                         anchor_y="center")
            self.message.color = (255, 255, 255, 255)
            self.message.final_text = self.selected_line
        else:
            self.message = RegularLabel("", font_name="Arial", font_size=20, anchor_x="left", anchor_y="center")
            self.message.position = position
        self.add(self.message)

        self.busy = True

    def start(self):
        if not self.ready:
            self.ready = True
            self.schedule(self.update)

    def update(self, dt):
        if self.line is None and self.ready:
            return
        self.time += dt
        if self.time >= self.draw_speed:
            add = self.time / self.draw_speed
            self.chars_shown += int(add)
            self.time = 0
        if 0 < self.chars_shown < self.full_length:
            while True:
                self.line = self.selected_line[:self.chars_shown]
                if self.line[-1] in string.whitespace:
                    self.chars_shown += 1
                    continue
                break
        elif self.chars_shown >= self.full_length:
            self.chars_shown = self.full_length
            self.line = self.selected_line
            self.unschedule(self.update)
            self.do(Delay(self.delay) + CallFunc(self.advance))
        self.message.text = self.line

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
            if self.centered:
                self.message.final_text = self.selected_line
            self.schedule(self.update)
