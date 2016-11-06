import cocos as cs
import pyglet
from cocos.actions import FadeOut, WrappedMove, Delay, FadeIn
from cocos.menu import MenuItem
from cocos.director import director
from cocos.scenes import FadeTransition

from cocos.audio.pygame.mixer import Sound
from cocos.audio.pygame import mixer


class Audio(Sound):
    def __init__(self, file):
        super().__init__(file)


class CharacterCreate(cs.scene.Scene):
    class NewCharacterLayer(cs.layer.Layer):
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

    def __init__(self):
        super().__init__()
        self.add(self.NewCharacterLayer())


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
        def __init__(self, window_size):
            super().__init__()
            from random import randint, random
            for i in range(0, 5):
                pos = (randint(100, window_size[0]),
                       window_size[1] / 2 + randint(0, window_size[1] - 100))
                cloud = cs.sprite.Sprite("assets/cloud.png")
                cloud.position = pos
                # Move the cloud across the screen til we hit the end, then loop it back to the beginning.
                cloud.velocity = (100 * (random() * 0.5 + 0.25), 0)
                cloud.do(WrappedMove(*window_size))
                self.add(cloud)

    def __init__(self):
        super().__init__()
        self.window_size = cs.director.director.get_window_size()
        bg = cs.sprite.Sprite("assets/menu_bg.png")
        bg.position = self.window_size[0] / 2, self.window_size[1] / 2
        self.add(bg)

        song = Audio("assets/menu.ogg")
        song.play(-1)

        clouds = self.CloudLayer(self.window_size)
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
