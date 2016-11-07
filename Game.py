from random import randint, random

import cocos as cs
from cocos.actions import Move
from cocos.audio.pygame import mixer
from cocos.director import director
from cocos.menu import MenuItem
from cocos.scenes import FadeTransition

from Audio import Audio
from NewGame import NewGame


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


if __name__ == "__main__":
    director.init(caption="Game Quest", width=600, height=480)
    director.show_FPS = True
    mixer.init()
    main_menu = MainMenu()
    director.run(main_menu)
