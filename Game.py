import cocos as cs
import pyglet
from cocos.actions import FadeOut, WrappedMove
from cocos.menu import MenuItem
from cocos.director import director


class NewGame(cs.scene.Scene):
    class IntroLayer(cs.layer.Layer):
        def __init__(self, window_size):
            super().__init__()
            self.window_size = window_size
            text = cs.text.Label("A long time ago...", font_name="Arial", font_size=20, anchor_x="center",
                                 anchor_y="center")
            text.position = window_size[0] / 2, window_size[1] - 100
            text.do(FadeOut(1))
            self.add(text)

    def __init__(self):
        super().__init__()
        intro = self.IntroLayer(director.get_window_size())
        self.add(intro)


class MainMenu(cs.scene.Scene):
    class Menu(cs.menu.Menu):
        def __init__(self):
            super().__init__()
            options = []
            options.append(MenuItem("New Game", self.new_game))
            options.append(MenuItem("Quit", self.on_quit))
            self.create_menu(options)

        def new_game(self):
            new_game = NewGame()
            cs.director.director.replace(new_game)

        def on_quit(self):
            self.get_ancestor(cs.scene.Scene).end()

    class CloudLayer(cs.layer.Layer):
        def __init__(self, window_size):
            super().__init__()
            from random import randint, random
            for i in range(0, 5):
                pos = (randint(0, window_size[0]),
                       window_size[1] / 2 + randint(0, window_size[1] - 100))
                cloud = cs.sprite.Sprite("assets/cloud.png")
                cloud.position = pos
                # Move the cloud across the screen til we hit the end, then loop it back to the beginning.
                cloud.velocity = (100 * (random()*0.5 + 0.25), 0)
                cloud.do(WrappedMove(*window_size))
                self.add(cloud)

    def __init__(self):
        super().__init__()
        self.window_size = cs.director.director.get_window_size()
        bg = cs.sprite.Sprite("assets/menu_bg.png")
        bg.position = self.window_size[0] / 2, self.window_size[1] / 2
        self.add(bg)

        clouds = self.CloudLayer(self.window_size)
        self.add(clouds)

        label = cs.text.Label("Game Quest", font_name="Arial", font_size=30, anchor_x="center", anchor_y="center")
        label.element.color = (230, 50, 50, 255)
        label.position = self.window_size[0] / 2, self.window_size[1] - 100
        self.add(label)

        menu = self.Menu()
        self.add(menu)


if __name__ == "__main__":
    pyglet.resource.path.append('.')
    pyglet.resource.reindex()
    director.init(width=600, height=480)
    main_menu = MainMenu()
    director.run(main_menu)
