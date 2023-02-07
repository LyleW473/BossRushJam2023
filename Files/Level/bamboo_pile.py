from Global.generic import Generic
from Global.settings import TILE_SIZE
from pygame.image import load as load_image

class BambooPile(Generic):

    # Bamboo pile image
    pile_image = load_image("graphics/Misc/BambooPile.png")
    
    # Dictionary containing information relating to bamboo piles
    bamboo_pile_info_dict = {
                            "BambooResourceReplenishAmount": 25,
                            "HealthReplenishmentAmount": 30,
                            "SpawningCooldown": 4000, 
                            "SpawningCooldownTimer": 4000, # Starts counting down when the current boss is spawned
                            "MinimumSpawningDistanceFromPlayer": 10 * TILE_SIZE,
                            "MaximumSpawningDistanceFromPlayer": 25 * TILE_SIZE,
                            "MaximumNumberOfPilesAtOneTime": 8
                            }

    def __init__(self, x, y):

        # Inherit from the Generic class, which has basic attributes and methods. (Inherits from Generic and pygame.sprite.Sprite)
        Generic.__init__(self, x = x, y = y, image = BambooPile.pile_image)