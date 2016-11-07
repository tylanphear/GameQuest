import string
from copy import copy

import cocos as cs
import math
import pyglet
from cocos.actions import FadeOut, WrappedMove, Delay, FadeIn, MoveTo, Driver, Move
from cocos.menu import MenuItem
from cocos.director import director
from cocos.scenes import FadeTransition

from cocos.audio.pygame.mixer import Sound
from cocos.audio.pygame import mixer


class Audio(Sound):
    def __init__(self, file):
        super().__init__(file)


class CharacterCreate(cs.scene.Scene):
    class KBLayer(cs.layer.Layer):
        is_event_handler = True

        def __init__(self):
            super().__init__()
            self.keys_pressed = set()
            self.modifiers = set()
            self.count = 0
            self.pressing = False

        def on_key_press(self, key, modifiers):
            if key == pyglet.window.key.ENTER and self.parent.black is not None:
                self.parent.remove(self.parent.black)
                self.parent.black = None
            self.pressing = 10
            self.keys_pressed.add(key)
            self.modifiers = modifiers
            self.update_text()

        def on_draw(self):
            self.update_text()

        def update_text(self):
            if self.pressing is not True:
                return
            keys = [k for k in self.keys_pressed if pyglet.window.key.symbol_string(k) in string.ascii_letters]
            for k in keys:
                if self.modifiers is not None and self.modifiers & pyglet.window.key.LSHIFT:
                    self.parent.name_in.element.text += pyglet.window.key.symbol_string(k)
                else:
                    self.parent.name_in.element.text += pyglet.window.key.symbol_string(k).lower()
            self.count += len(keys)
            if pyglet.window.key.SPACE in self.keys_pressed:
                self.parent.name_in.element.text += " "
                self.count += 1
            if pyglet.window.key.BACKSPACE in self.keys_pressed and self.count != 0:
                self.count -= 1
                self.parent.name_in.element.text = self.parent.name_in.element.text[:-1]

        def on_key_release(self, key, modifiers):
            self.pressing = False
            if key in self.keys_pressed:
                self.keys_pressed.remove(key)
            self.modifiers = None

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

        self.schedule_interval(self.fade_in, 0.1)

    def fade_in(self, dt):
        if self.black is None:
            self.unschedule(self)
            return

        if self.black.opacity > 1:
            self.black.opacity -= 10*dt
        else:
            self.remove(self.black)


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
        def __init__(self, num_clouds):
            from time import clock
            from random import seed
            seed(clock())
            super().__init__()
            self.window_size = director.get_window_size()
            self.clouds = []
            self.num_clouds = num_clouds
            while len(self.clouds) < self.num_clouds:
                self.make_cloud(True)

            self.schedule(self.update)

        def make_cloud(self, is_random_placement=False):
            from random import randint, random
            pos = 0
            cloud = cs.sprite.Sprite("assets/cloud.png")
            placed = False
            while not placed:
                if is_random_placement:
                    pos = (randint(cloud.width, self.window_size[0]) - cloud.width,
                           randint(self.window_size[1] / 2, self.window_size[1]) - cloud.height / 2)
                else:
                    pos = (-cloud.width,
                           randint(self.window_size[1] / 2, self.window_size[1]) - cloud.height / 2)
                if len(self.clouds) == 0:
                    placed = True
                else:
                    for c in self.clouds:
                        if c.get_rect().contains(*pos):
                            placed = False
                        else:
                            placed = True
            cloud.position = pos
            # Move the cloud across the screen til we hit the end, then loop it back to the beginning.
            cloud.velocity = (25*(random()*0.5 + 0.5), 0)
            cloud.do(Move(position=(self.window_size[0], cloud.position[1])))
            self.clouds.append(cloud)
            self.add(cloud)

        def update(self, dt):
            while len(self.clouds) < self.num_clouds:
                self.make_cloud()
            clouds_copy = copy(self.clouds)
            for cloud in clouds_copy:
                if cloud.position[0]-cloud.width/2 > self.window_size[0]:
                    self.remove(cloud)
                    self.clouds.remove(cloud)

    def __init__(self):
        super().__init__()
        self.window_size = cs.director.director.get_window_size()
        bg = cs.sprite.Sprite("assets/menu_bg.png")
        bg.position = self.window_size[0] / 2, self.window_size[1] / 2
        self.add(bg)

        song = Audio("assets/menu.ogg")
        song.play(-1)

        clouds = self.CloudLayer(10)
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
    mixer.init()
    main_menu = MainMenu()
    director.run(main_menu)
