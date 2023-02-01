from Global.generic import Generic

class SikaDeerBoss(Generic):

    # ImagesDict = ?? (This is set when the boss is instantiated)


    def __init__(self, x, y):
        
        starting_image = SikaDeerBoss.ImagesDict["Stomp"][0]

        # Inherit from the Generic class, which has basic attributes and methods.
        Generic.__init__(self, x = x , y = y, image = starting_image)

        # Spawn the boss at the middle of the tile, with the bottom of the boss being at the bottom of the tile
        self.rect.midbottom = (x, y)

        # # Health
        # self.health = 4000