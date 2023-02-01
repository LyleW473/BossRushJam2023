from Global.generic import Generic
from Global.settings import TILE_SIZE
from pygame.image import load as load_image

class BambooPile(Generic):

    # Bamboo pile image
    pile_image = load_image("graphics/Misc/BambooPile.png")
    
    # Dictionary containing information relating to bamboo piles
    bamboo_pile_info_dict = {
                            "BambooResourceReplenishAmount": 25,
                            "SpawningCooldown": 5000, 
                            "SpawningCooldownTimer": 5000, # Set the timer to start as soon as the game starts
                            "MinimumSpawningDistanceFromPlayer": 10 * TILE_SIZE,
                            "MaximumSpawningDistanceFromPlayer": 18 * TILE_SIZE,
                            "MaximumNumberOfPilesAtOneTime": 5
                            }

    def __init__(self, x, y):

        # Inherit from the Generic class, which has basic attributes and methods. (Inherits from Generic and pygame.sprite.Sprite)
        Generic.__init__(self, x = x, y = y, image = BambooPile.pile_image)