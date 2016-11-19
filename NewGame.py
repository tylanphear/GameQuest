from cocos.actions import Delay, FadeOut, CallFunc
from cocos.director import director
from cocos.layer import Layer, ColorLayer
from cocos.scene import Scene
from cocos.sprite import Sprite
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
        self.text = TextSequence((30, 30),
                                 lines=["But no man starts out a hero.", "Everyone has to start off somewhere",
                                        "Where do you choose to start?"])
        self.add(self.text)

        guy = Sprite("assets/guy.png")
        guy.position = self.window_size[0] / 2, self.window_size[1] / 2
        self.add(guy)

        self.fade_overlay = ColorLayer(255, 255, 255, 255)
        self.add(self.fade_overlay)
        self.fade_overlay.do(Delay(0.5) + FadeOut(10))


class NewGame(Scene):
    class IntroLayer(Layer):
        is_event_handler = True

        def __init__(self):
            super().__init__()
            self.text = TextSequence(lines=["A long time ago...", "There was a man.", "A manly man."])
            self.text.message.element.color = (150, 230, 230, 255)
            self.text.message.position = (self.text.position[0] + self.text.message.element.content_width / 2 + 10,
                                          self.text.position[1] + self.text.message.element.content_height + 30)
            self.add(self.text)

        def on_key_press(self, key, modifiers):
            if key == window.key.ENTER:
                self.text.advance()

        def on_enter(self):
            super().on_enter()

        def on_draw(self):
            if not self.text.busy:
                self.do(Delay(1) + CallFunc(lambda: director.replace(CharacterCreate())))

    def __init__(self):
        super().__init__()
        self.intro = self.IntroLayer()
        self.add(self.intro)

    def on_enter(self):
        super().on_enter()
