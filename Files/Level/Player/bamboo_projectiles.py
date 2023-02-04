import pygame
from Global.generic import Generic
from math import sin, cos, degrees
from Global.settings import *

class BambooProjectile(Generic):
    
    # Projectile image of all bamboo projectiles
    projectile_image = pygame.image.load("graphics/Projectiles/BambooProjectile.png")

    # Default time to cover the distance travelled
    default_time_to_travel_distance_at_final_velocity = 0.25

    def __init__(self, x, y, angle, damage_amount, is_frenzy_mode_projectile):

        # --------------------------------------------------------------------------------
        # Movement

        # The total distance travelled (including the horizontal and vertical components)
        desired_distance_travelled = 6 * TILE_SIZE

        # If this projectile was created when the player was not in frenzy mode
        if is_frenzy_mode_projectile == False:
            # Set the time for the projectile to cover the desired distance travelled to be the default time
            time_to_travel_distance_at_final_velocity = BambooProjectile.default_time_to_travel_distance_at_final_velocity # t

        # If this projectile was created when the player was in frenzy mode
        elif is_frenzy_mode_projectile == True:
            # Set the time for the projectile to cover the desired distance travelled to be a smaller value for time
            time_to_travel_distance_at_final_velocity = BambooProjectile.default_time_to_travel_distance_at_final_velocity * 0.8 # t
            print(time_to_travel_distance_at_final_velocity)

        # Calculate the horizontal and vertical distance the projectile must travel based on the desired distance travelled
        horizontal_distance = desired_distance_travelled * cos(angle)
        vertical_distance = desired_distance_travelled * sin(angle)

        # Calculate the horizontal and vertical gradients
        self.horizontal_gradient = horizontal_distance / time_to_travel_distance_at_final_velocity
        self.vertical_gradient = vertical_distance / time_to_travel_distance_at_final_velocity
        """
        self.delta_time = 0
        """
        # The original image of the bamboo projectile
        """ Note: This is so that when the bamboo projectile's colour is changed to be the same as the player's frenzy mode colour, it won't go completely white.
        - This is because the BLEND_RGB_ADD flag is used, so saving bamboo_projectile.image as the changed colour image will keep adding up the RGB values
        """

        self.original_image = pygame.transform.rotozoom(surface = BambooProjectile.projectile_image.convert_alpha(), angle = degrees(angle), scale = 1)
        # Inherit from the Generic class, which has basic attributes and methods.
        Generic.__init__(self, x = x, y = y, image = self.original_image)


        # -------------------------------------------------------------------------------
        # Positioning

        """ Override the rect position, and instead position the center of the projectile at the x and y co-ordinate:
        - As the image is rotated, the image may be resized, therefore this ensures that the center of the projectile will always be at the center of the player.
        """
        self.rect.centerx = x
        self.rect.centery = y

        # The attributes that will hold the new x and y positions of the projectile (for more accurate shooting as the floating point values are saved)
        self.new_position_x = self.rect.x
        self.new_position_y = self.rect.y
        # --------------------------------------------------------------------------------
        # Damage

        # The damage amount (the damage depends on what weapon this was shot from)
        self.damage_amount = damage_amount

        # Attribute to check if this projectile was created when the player was in frenzy mode
        self.is_frenzy_mode_projectile = is_frenzy_mode_projectile

    def move_projectile(self):

        # Moves the projectile

        # Horizontal movement
        self.new_position_x += self.horizontal_gradient * self.delta_time
        self.rect.x = round(self.new_position_x)

        # Vertical movement
        self.new_position_y -= self.vertical_gradient * self.delta_time
        self.rect.y = round(self.new_position_y)