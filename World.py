from cocos.layer import ScrollingManager, ScrollableLayer, ColorLayer, director
from cocos.scene import Scene
from cocos.sprite import Sprite


class World(Scene):
    class Map(ScrollingManager):
        class Area(ScrollableLayer):
            def __init__(self, world_width, world_height):
                super().__init__()
                self.bg = ColorLayer(139, 69, 19, 255, world_width, world_height)
                self.w_width = world_width
                self.w_height = world_height
                self.player = self.get_ancestor(Scene).player
                self.player.position = 200, 200
                self.add(self.player, z=2)

        def __init__(self):
            dim = director.get_window_size()
            super().__init__(viewport=(0, 0, *dim))
            self.area = self.Area(1000, 1000)

    def __init__(self):
        super().__init__()
        self.player = Sprite("assets/test.png")
        self.map = self.Map()
