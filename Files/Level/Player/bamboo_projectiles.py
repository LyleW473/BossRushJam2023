import pygame
from Global.generic import Generic
from math import sin, cos, degrees
from Global.settings import *

class BambooProjectile(Generic, pygame.sprite.Sprite):
    # Projectile image of all bamboo projectiles
    projectile_image = pygame.image.load("graphics/Projectiles/bamboo_projectile.png")

    def __init__(self, x, y, angle):

        # The angle that the projectile will travel in

        # The total distance travelled (including the horizontal and vertical components)
        desired_distance_travelled = 6 * TILE_SIZE

        # The time for the projectile to cover the desired distnace travelled
        time_to_travel_distance_at_final_velocity = 0.25 # t

        # Calculate the horizontal and vertical distance the player must travel based on the desired distance travelled
        horizontal_distance = desired_distance_travelled * cos(angle)
        vertical_distance = desired_distance_travelled * sin(angle)

        # Calculate the horizontal and vertical gradients
        self.horizontal_gradient = horizontal_distance / time_to_travel_distance_at_final_velocity
        self.vertical_gradient = vertical_distance / time_to_travel_distance_at_final_velocity
        """
        self.delta_time = 0
        """
        # Inherit from the Generic class, which has basic attributes and methods.
        Generic.__init__(self, x = x, y = y, image = pygame.transform.rotozoom(surface = BambooProjectile.projectile_image.convert_alpha(), angle = degrees(angle), scale = 1))

        # Inherit from pygame's sprite class
        pygame.sprite.Sprite.__init__(self)

        """ Override the rect position, and instead position the center of the projectile at the x and y co-ordinate:
        - As the image is rotated, the image may be resized, therefore this ensures that the center of the projectile will always be at the center of the player.
        """
        self.rect.centerx = x
        self.rect.centery = y

        # The attributes that will hold the new x and y positions of the projectile (for more accurate shooting as the floating point values are saved)
        self.new_position_x = self.rect.x
        self.new_position_y = self.rect.y

    def move_projectile(self):

        # Moves the projectile

        # Horizontal movement
        self.new_position_x += self.horizontal_gradient * self.delta_time
        self.rect.x = round(self.new_position_x)

        # Vertical movement
        self.new_position_y -= self.vertical_gradient * self.delta_time
        self.rect.y = round(self.new_position_y)