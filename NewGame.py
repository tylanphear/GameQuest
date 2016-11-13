from cocos.actions import Delay, FadeOut
from cocos.director import director
from cocos.layer import Layer, ColorLayer
from cocos.scene import Scene
from cocos.sprite import Sprite
from cocos.text import Label
from pyglet import window

from Text import TextSequence


class CharacterCreate(Scene):
    """
    This is the character creation scene where the player inputs their name, chooses their class and other variables
    which are to be determined.
    """

    def __init__(self):
        super().__init__()
        self.window_size = director.get_window_size()
        creation = Label("Character Creation", font_name="Arial", font_size=30, anchor_x="center",
                         anchor_y="center")
        creation.position = self.window_size[0] / 2, self.window_size[1] - 50
        self.add(creation)

        guy = Sprite("assets/guy.png")
        guy.position = self.window_size[0] / 2, self.window_size[1] / 2
        self.add(guy)

        self.fade_overlay = ColorLayer(255, 255, 255, 255)
        self.add(self.fade_overlay)
        self.fade_overlay.do(Delay(0.5) + FadeOut(10))


class NewGame(Scene):
    class IntroLayer(Layer):
        is_event_handler = True

        def __init__(self, window_size):
            super().__init__()
            self.window_size = window_size
            self.text = TextSequence(lines=["A long time ago...", "There was a man.", "A manly man."])
            self.text.disp.element.color = (150, 230, 230, 255)
            self.text.disp.position = (self.text.position[0] + self.text.disp.element.content_width / 2 + 10,
                                       self.text.position[1] + self.text.disp.element.content_height + 30)
            self.add(self.text)

            # self.do(Delay(1) + FadeIn(1) + Delay(2) + FadeOut(2), target=self.text)

        def on_key_press(self, key, modifiers):
            if key == window.key.ENTER:
                self.text.next_line()

        def on_exit(self):
            super().on_exit()

        def on_draw(self):
            if self.text.busy is False:
                director.replace(CharacterCreate())

    def __init__(self):
        super().__init__()
        self.intro = self.IntroLayer(director.get_window_size())
        self.add(self.intro)
