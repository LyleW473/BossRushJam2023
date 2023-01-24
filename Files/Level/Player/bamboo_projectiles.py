import pygame
from Global.generic import Generic
from math import sin, cos, degrees
from Global.settings import *

class BambooProjectile(Generic, pygame.sprite.Sprite):
    def __init__(self, x, y, angle, image):

        # The angle that the projectile will travel in
        
        self.angle = angle

        # The total distance travelled (including the horizontal and vertical components)
        desired_distance_travelled = 2 * TILE_SIZE
        time_to_travel_distance_at_final_velocity = 0.08 # t
        time_to_reach_final_velocity = 0.2

        # ------------------------------------------------------------------------------------------
        # Horizontal movement
        
        # Set the initial movement velocity to be 0
        self.horizontal_suvat_u = 0

        # The movement distance the player can move
        self.horizontal_suvat_s = 0

        # -----------------------------------------
        # Calculate the velocity that the player moves at given a distance that the player travels within a given time span

        # After re-arranging s = vt + 1/2(a)(t^2), v is given by the equation: (2s - a(t)^2) / 2t, where a is 0 because acceleration is constant

        
        # Horizontal distance travelled is hcos(theta), where h = desired_distance_travelled
        horizontal_distance_travelled_at_final_velocity = desired_distance_travelled * cos(angle) # s 

        # Full version: self.horizontal_suvat_v = ((2 * distance_travelled_at_final_velocity) - (0 * (time_to_travel_distance_at_final_velocity ** 2)) / (2 * time_to_travel_distance_at_final_velocity))
        # Simplified version:
        self.horizontal_suvat_v = ((2 * horizontal_distance_travelled_at_final_velocity) / (2 * time_to_travel_distance_at_final_velocity))

        # -----------------------------------------
        # Calculate the acceleration needed for the player to reach self.horizontal_suvat_v within a given time span
        # After re-arranging v = u + at, a is given by the equation: (v - u) / t, where u is 0

        # Full version: self.horizontal_suvat_a = (self.horizontal_suvat_v - 0) / time_to_reach_final_velocity
        # Simplified version:
        self.horizontal_suvat_a = self.horizontal_suvat_v / time_to_reach_final_velocity

        # ------------------------------------------------------------------------------------------

        # Set the initial movement velocity to be 0
        self.vertical_suvat_u = 0
        # The movement distance the player can move
        self.vertical_suvat_s = 0
        
        # -----------------------------------------
        # Calculate the velocity that the player moves at given a distance that the player travels within a given time span

        # After re-arranging s = ut + 1/2(a)(t^2), v is given by the equation: (2s - a(t)^2) / 2t, where a is 0 because acceleration is constant

        # Horizontal distance travelled is hcos(theta), where h = desired_distance_travelled
        vertical_distance_travelled_at_final_vertical_velocity = desired_distance_travelled * sin(angle) # s 

        # Full version: self.vertical_suvat_v = ((2 * distance_travelled_at_final_vertical_velocity) - (0 * (time_to_travel_distance_at_final_vertical_velocity ** 2)) / (2 * time_to_travel_distance_at_final_vertical_velocity))
        # Simplified version:
        self.vertical_suvat_v = ((2 * vertical_distance_travelled_at_final_vertical_velocity) / (2 * time_to_travel_distance_at_final_velocity))

        # -----------------------------------------
        # Calculate the acceleration needed for the player to reach self.vertical_suvat_v within a given time span

        # After re-arranging v = u + at, a is given by the equation: (v - u) / t, where u is 0
        # Full version: self.vertical_suvat_a = (self.vertical_suvat_v - 0) / time_to_reach_final_velocity = 0.5
        # Simplified version:
        self.vertical_suvat_a = self.vertical_suvat_v / time_to_reach_final_velocity

        """
        self.delta_time = 0
        """

        # Inherit from the Generic class, which has basic attributes and methods.
        Generic.__init__(self, x = x, y = y, image = pygame.transform.rotozoom(surface = image, angle = degrees(self.angle), scale = 1))

        # Inherit from pygame's sprite class
        pygame.sprite.Sprite.__init__(self)

    def move_projectile(self):

        # Method to move the projectile using physics

        # ------------------------------------------------------------------------------------------
        # Horizontal

        # If the current velocity has not reached the final velocity set for the projectile
        if self.horizontal_suvat_u < self.horizontal_suvat_v:
            # Increase the current velocity
            self.horizontal_suvat_u += (self.horizontal_suvat_a * self.delta_time)
        
        # Limit the current velocity to the final velocity set for the projectile (in case that the current velocity is greater)
        self.horizontal_suvat_u = min(self.horizontal_suvat_u, self.horizontal_suvat_v)

        # Set the distance travelled based on the current velocity
        self.horizontal_suvat_s = ((self.horizontal_suvat_u * self.delta_time) + (0.5 * self.horizontal_suvat_a * (self.delta_time ** 2)))

        # Update the projectile's x position
        new_position_x = self.rect.x
        new_position_x += self.horizontal_suvat_s
        self.rect.x = round(new_position_x)

        # ------------------------------------------------------------------------------------------
        # Vertical

        # If the current velocity has not reached the final velocity set for the projectile
        if self.vertical_suvat_u < self.vertical_suvat_v:
            # Increase the current velocity
            self.vertical_suvat_u += (self.vertical_suvat_a * self.delta_time)

        # Limit the current velocity to the final velocity set for the projectile (in case that the current velocity is greater)
        self.vertical_suvat_u = min(self.vertical_suvat_u, self.vertical_suvat_v)

        # Set the distance travelled based on the current velocity
        self.vertical_suvat_s = ((self.vertical_suvat_u * self.delta_time) + (0.5 * self.vertical_suvat_a * (self.delta_time ** 2)))

        # Update the projectile's y position
        new_position_y = self.rect.y
        new_position_y -= self.vertical_suvat_s
        self.rect.y = round(new_position_y)