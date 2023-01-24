import pygame
from Global.generic import Generic
from math import sin, cos, degrees
from Global.settings import *

class BambooProjectile(Generic, pygame.sprite.Sprite):
    def __init__(self, x, y, angle, image):

        # The angle that the projectile will travel in
        self.angle = angle
        self.distance = 12

        """
        self.delta_time = 0
        """

        # Inherit from the Generic class, which has basic attributes and methods.
        Generic.__init__(self, x = x, y = y, image = pygame.transform.rotozoom(surface = image, angle = degrees(self.angle), scale = 1))

        # Inherit from pygame's sprite class
        pygame.sprite.Sprite.__init__(self)

    def move_projectile(self):
        
        # Method to move the projectile based on the distance

        new_position_x, new_position_y = self.rect.x, self.rect.y
        new_position_x += self.distance * (cos(self.angle))
        new_position_y -= self.distance * (sin(self.angle))
        self.rect.x, self.rect.y = round(new_position_x), round(new_position_y)

    def draw(self, surface, x, y):
        
        # Draw the tile onto the surface
        surface.blit(self.image, (x, y))
        

