from random import randint, random

import pyglet
from cocos.actions import Move, CallFunc, Delay
from cocos.audio.pygame import mixer
from cocos.director import director
from cocos.layer import Layer
from cocos.menu import MenuItem, Menu
from cocos.scene import Scene
from cocos.scenes import FadeTransition
from cocos.sprite import Sprite
from cocos.text import Label

from Audio import Audio
from NewGame import NewGame


class MainMenu(Scene):
    class Menu(Menu):
        def __init__(self):
            super().__init__()
            options = [MenuItem("New Game", self.new_game), MenuItem("Quit", self.on_quit)]

            self.font_item['font_size'] = 20
            self.font_item['color'] = (200, 200, 200, 255)

            self.font_item_selected['font_size'] = 25
            self.font_item_selected['color'] = (155, 0, 0, 255)
            self.bg_vertices = []

            self.create_menu(options)

        def new_game(self):
            new_game = NewGame()
            self.do(Delay(1) + CallFunc(lambda: director.replace(FadeTransition(new_game))))


        def on_quit(self):
            self.get_ancestor(Scene).end()

    class CloudLayer(Layer):
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

            cloud = Sprite("assets/cloud.png")
            # If there's no other clouds, just place it
            if len(self.children) == 0:
                cloud.position = random_location(inital_gen)
            # This algorithm tries to place the cloud in its own location
            # without overlapping any clouds, but will give up if this is impossible.
            else:
                placed = False
                fails = 0
                # Try to place it so it doesn't intersect any other clouds
                while not placed:
                    cloud.position = random_location(inital_gen)
                    for index, c in self.children:
                        # If we've failed to place the cloud too many times, just place it
                        if fails > len(self.children):
                            placed = True
                            break
                        # If the cloud is in another cloud, we've failed again and we try another spot
                        elif c.get_rect().contains(*cloud.position):
                            placed = False
                            fails += 1
                            break
                        # Otherwise, so far so good, keep checking other clouds
                        placed = True
            # 10 to 20 in the x direction
            # -2.5 to 2.5 in the y direction
            cloud.velocity = (20 * (random() * 0.5 + 0.5), -2.5 + 5 * random())
            # Move it to the right side of the window to the same y position as it started in
            cloud.do(Move(position=(self.window_size[0], cloud.position[1])))
            self.add(cloud)

        def update(self, dt):
            """"
            Check if any of the clouds have left the screen, if so, remove them and generate a new one to replace it
            """
            for index, cloud in self.children:
                # If the cloud is off the screen, remove it.
                if cloud.position[0] - cloud.width / 2 > self.window_size[0] or \
                                        cloud.position[1] - cloud.width / 2 > self.window_size[1]:
                    self.remove(cloud)
                    self.make_cloud()

    def __init__(self):
        super().__init__()
        self.window_size = director.get_window_size()
        bg = Sprite("assets/menu_bg.png")
        bg.position = self.window_size[0] / 2, self.window_size[1] / 2
        self.add(bg)

        song = Audio("assets/menu.ogg")
        song.play(-1)

        clouds = self.CloudLayer(35)
        self.add(clouds)

        label = Label("Game Quest", font_name="Arial", font_size=30, anchor_x="center", anchor_y="center")
        label.element.color = (230, 50, 50, 255)
        label.position = self.window_size[0] / 2, self.window_size[1] - 100
        self.add(label)

        menu = self.Menu()
        self.add(menu)

    def on_exit(self):
        super().on_exit()
        mixer.stop()


if __name__ == "__main__":
    # Create the window
    pyglet.clock.set_fps_limit(60)
    director.init(caption="Game Quest", width=600, height=480)
    mixer.init()
    main_menu = MainMenu()
    director.run(main_menu)
