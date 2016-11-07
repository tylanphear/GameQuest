import string
from random import randint, random

import cocos as cs
import pyglet
from cocos.actions import FadeOut, Delay, FadeIn, Move
from cocos.audio.pygame import mixer
from cocos.audio.pygame.mixer import Sound
from cocos.director import director
from cocos.menu import MenuItem
from cocos.scenes import FadeTransition


class Audio(Sound):
    def __init__(self, file):
        super().__init__(file)


class CharacterCreate(cs.scene.Scene):
    """
    This is the character creation scene where the player inputs their name, chooses their class and other variables
    which are to be determined.
    """
    class KBLayer(cs.layer.Layer):
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
            self.holding = False
            self.held_time = 0

        def on_key_press(self, key, modifiers):
            """
            When a key is pressed, just add it to the set of keys. Duplicate keys will not be added twice (since it's a
            set)
            """
            if key == pyglet.window.key.ENTER and self.parent.black is not None:
                self.parent.remove(self.parent.black)
                self.parent.black = None
            self.keys_pressed[pyglet.window.key.symbol_string(key)] = True
            self.modifiers = modifiers
            self.pressing = True
            self.update_text(0)
            self.schedule(self.check_holding)

        def check_holding(self, dt):
            if self.pressing and not self.holding:
                self.held_time += dt
                if self.held_time > 0.5:
                    self.holding = True
                    self.unschedule(self.check_holding)
                    self.schedule_interval(self.update_text, 0.1)

        def update_text(self, dt):
            """
            Takes each key and then checks the modifiers to determine whether it will be capital or lowercase, then
            adds it to the current attribute. If the key is
            :return:
            """
            if not self.pressing or not self.holding:
                return
            for k in filter(lambda x: self.keys_pressed[x] is True, self.keys_pressed):
                if k in string.ascii_letters:
                    if self.modifiers is not None and self.modifiers & pyglet.window.key.LSHIFT:
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
            self.held_time = 0

        def on_key_release(self, key, modifiers):
            self.keys_pressed[pyglet.window.key.symbol_string(key)] = False
            self.modifiers = None
            self.holding = False
            self.held_time = 0

    def __init__(self):
        super().__init__()
        self.window_size = director.get_window_size()
        creation = cs.text.Label("Character Creation", font_name="Arial", font_size=30, anchor_x="center",
                                 anchor_y="center")
        creation.position = self.window_size[0] / 2, self.window_size[1] - 50
        self.add(creation)

        guy = cs.sprite.Sprite("assets/guy.png")
        guy.position = self.window_size[0] / 2, self.window_size[1] / 2
        self.add(guy)

        self.name_in = cs.text.Label("Name: ", font_name="Arial", font_size=25)
        self.name_in.position = self.window_size[0] / 2 - 200, self.window_size[1] - 200
        self.add(self.name_in)

        self.keyboard = self.KBLayer()
        self.add(self.keyboard)

        self.black = cs.layer.ColorLayer(255, 255, 255, 255)
        self.add(self.black)
        self.black.do(Delay(0.5) + FadeOut(10))


class NewGame(cs.scene.Scene):
    class IntroLayer(cs.layer.Layer):
        is_event_handler = True

        def __init__(self, window_size):
            super().__init__()
            self.window_size = window_size
            self.text = cs.text.Label("A long time ago...", font_name="Arial", font_size=20, anchor_x="center",
                                      anchor_y="center")
            self.text.position = window_size[0] / 2, window_size[1] - 100
            self.text.opacity = 0
            self.add(self.text)

            self.do(Delay(1) + FadeIn(1) + Delay(2) + FadeOut(2), target=self.text)

        def on_key_press(self, key, modifiers):
            if key == pyglet.window.key.ENTER:
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


class MainMenu(cs.scene.Scene):
    class Menu(cs.menu.Menu):
        def __init__(self):
            super().__init__()
            options = [MenuItem("New Game", self.new_game), MenuItem("Quit", self.on_quit)]

            self.font_item['font_size'] = 20
            self.font_item['color'] = (200, 200, 200, 255)

            self.font_item_selected['font_size'] = 25
            self.font_item_selected['color'] = (155, 0, 0, 255)

            self.create_menu(options)

        def new_game(self):
            new_game = NewGame()
            director.replace(FadeTransition(new_game))

        def on_quit(self):
            self.get_ancestor(cs.scene.Scene).end()

    class CloudLayer(cs.layer.Layer):
        """"
        The clouds behind the menu text.
        """
        def __init__(self, num_clouds):
            """"
            Places initial clouds.
            """
            from time import clock
            from random import seed
            seed(clock())
            super().__init__()
            self.window_size = director.get_window_size()
            self.clouds = []
            self.num_clouds = num_clouds
            while len(self.children) < self.num_clouds:
                self.make_cloud(inital_gen=True)

            self.schedule(self.update)

        def make_cloud(self, inital_gen=False):
            """"
            Places a cloud in a random location, hopefully not intersecting any other clouds, and sends it rightwards.
            """

            def random_location(scatter):
                """"
                Helper function.
                Generates a random location, putting it random on the screen if scattering, on the left edge if not.
                """
                # The first time generating the clouds, we want them all over the screen
                if scatter:
                    pos = (randint(-cloud.width, self.window_size[0] + cloud.width / 2),
                           randint(cloud.height / 2 + self.window_size[1] / 2 - 100,
                                   self.window_size[1] - cloud.height / 2))
                # The rest of the clouds will be generated starting from the left edge
                else:
                    pos = (-cloud.width,
                           randint(cloud.height / 2 + self.window_size[1] / 2 - 100,
                                   self.window_size[1] - cloud.height / 2))
                return pos

            cloud = cs.sprite.Sprite("assets/cloud.png")
            # If there's no other clouds, just place it
            if len(self.clouds) == 0:
                cloud.position = random_location(inital_gen)
            # This algorithm tries to place the cloud in its own location
            # without overlapping any clouds, but will give up if this is impossible.
            else:
                placed = False
                fails = 0
                # Try to place it so it doesn't intersect any other clouds
                while not placed:
                    cloud.position = random_location(inital_gen)
                    for c in self.clouds:
                        # If we've failed to place the cloud too many times, just place it
                        if fails > len(self.clouds):
                            placed = True
                            break
                        # If the cloud is in another cloud, we've failed again and we try another spot
                        elif c.get_rect().intersects(cloud.get_rect()):
                            placed = False
                            fails += 1
                            break
                        # Otherwise, so far so good, keep checking other clouds
                        placed = True
            # 25 times (1.5 to 0.5) in the x direction
            # -2 to 3 in the y direction
            cloud.velocity = (25 * (random() * 0.5 + 0.5), -2 + 5 * random())
            # Move it to the right side of the window to the same y position as it started in
            cloud.do(Move(position=(self.window_size[0], cloud.position[1])))
            self.add(cloud)

        def update(self, dt):
            """"
            Move the clouds, and generate new ones if any exitted the screen
            """
            while len(self.children) < self.num_clouds:
                self.make_cloud()
            for index, cloud in self.children:
                if cloud.position[0] - cloud.width / 2 > self.window_size[0]:
                    self.remove(cloud)

    def __init__(self):
        super().__init__()
        self.window_size = cs.director.director.get_window_size()
        bg = cs.sprite.Sprite("assets/menu_bg.png")
        bg.position = self.window_size[0] / 2, self.window_size[1] / 2
        self.add(bg)

        song = Audio("assets/menu.ogg")
        song.play(-1)

        clouds = self.CloudLayer(30)
        self.add(clouds)

        label = cs.text.Label("Game Quest", font_name="Arial", font_size=30, anchor_x="center", anchor_y="center")
        label.element.color = (230, 50, 50, 255)
        label.position = self.window_size[0] / 2, self.window_size[1] - 100
        self.add(label)

        menu = self.Menu()
        self.add(menu)

    def on_exit(self):
        super().on_exit()
        mixer.stop()
        for child in self.get_children():
            self.remove(child)


if __name__ == "__main__":
    director.init(caption="Game Quest", width=600, height=480)
    director.show_FPS = True
    mixer.init()
    main_menu = MainMenu()
    director.run(main_menu)
