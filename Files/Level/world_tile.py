import pygame
from Global.generic import Generic

class WorldTile(Generic, pygame.sprite.Sprite):
    def __init__(self, x, y, image):

        # Inherit from the Generic class, which has basic attributes and methods.
        Generic.__init__(self, x = x, y = y, image = image)
        
        # Inherit from pygame's sprite class
        pygame.sprite.Sprite.__init__(self) 