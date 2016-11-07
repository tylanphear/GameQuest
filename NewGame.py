from cocos.actions import Delay, FadeOut, FadeIn
from cocos.director import director
from cocos.layer import Layer, ColorLayer
from cocos.scene import Scene
from cocos.sprite import Sprite
from cocos.text import Label
from pyglet import window


class CharacterCreate(Scene):
    """
    This is the character creation scene where the player inputs their name, chooses their class and other variables
    which are to be determined.
    """

    class KBLayer(Layer):
        """
        Just a basic keyboard handling layer. We use this to update the text containing the player's attributes using
        the modifiers and ascii keys.
        """
        is_event_handler = True

        def __init__(self):
            """
            Creates the keyboard layer with a set of pressed keys and modifiers (default empty)
            """
            super().__init__()
            self.keys_pressed = {}
            self.modifiers = set()
            self.count = 0
            self.pressing = True

        def on_key_press(self, key, modifiers):
            """
            When a key is pressed, set the corresponding key value to true
            """
            if key == window.key.ENTER and self.parent.black is not None:
                self.parent.remove(self.parent.black)
                self.parent.black = None
            self.keys_pressed[window.key.symbol_string(key)] = True
            self.modifiers = modifiers
            self.pressing = True
            self.update_text()

        def update_text(self):
            """
            Takes each key and then checks the modifiers to determine whether it will be capital or lowercase, then
            adds it to the current attribute. If the key is
            :return:
            """
            from string import ascii_letters

            if not self.pressing:
                return
            for k in filter(lambda x: self.keys_pressed[x] is True, self.keys_pressed):
                if k in ascii_letters:
                    if self.modifiers is not None and self.modifiers & window.key.LSHIFT:
                        self.parent.name_in.element.text += k
                    else:
                        self.parent.name_in.element.text += k.lower()
                    self.count += 1
                if k == "SPACE":
                    self.parent.name_in.element.text += " "
                    self.count += 1
                if k == "BACKSPACE" and self.count != 0:
                    self.count -= 1
                    self.parent.name_in.element.text = self.parent.name_in.element.text[:-1]

        def on_key_release(self, key, modifiers):
            self.pressing = False
            self.keys_pressed[window.key.symbol_string(key)] = False
            self.modifiers = None

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

        self.name_in = Label("Name: ", font_name="Arial", font_size=25)
        self.name_in.position = self.window_size[0] / 2 - 200, self.window_size[1] - 200
        self.add(self.name_in)

        self.keyboard = self.KBLayer()
        self.add(self.keyboard)

        self.black = ColorLayer(255, 255, 255, 255)
        self.add(self.black)
        self.black.do(Delay(0.5) + FadeOut(10))


class NewGame(Scene):
    class IntroLayer(Layer):
        is_event_handler = True

        def __init__(self, window_size):
            super().__init__()
            self.window_size = window_size
            self.text = Label("A long time ago...", font_name="Arial", font_size=20, anchor_x="center",
                              anchor_y="center")
            self.text.position = window_size[0] / 2, window_size[1] - 100
            self.text.opacity = 0
            self.add(self.text)

            self.do(Delay(1) + FadeIn(1) + Delay(2) + FadeOut(2), target=self.text)

        def on_key_press(self, key, modifiers):
            if key == window.key.ENTER:
                director.replace(CharacterCreate())

        def on_exit(self):
            super().on_exit()

        def on_draw(self):
            if self.are_actions_running() is not True:
                director.replace(CharacterCreate())

    def __init__(self):
        super().__init__()
        self.intro = self.IntroLayer(director.get_window_size())
        self.add(self.intro)
