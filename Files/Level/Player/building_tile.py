from Level.world_tile import WorldTile

class BuildingTile(WorldTile):


    def __init__(self, x, y, image):

        # Inherit from the world tile class, which has basic attributes and methods. (Inherits from Generic and pygame.sprite.Sprite)
        WorldTile.__init__(self, x = x, y = y, image = image)

        # self.hp = 100 (Continue later when bosses / enemies are implemented