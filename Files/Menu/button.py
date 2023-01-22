import pygame, random
from Global.settings import * 
from Global.generic import Generic

class Button(Generic):
    def __init__(self, x, y, image, surface):
        
        # Generic
        self.surface = surface

        # Inherit basic attributes from Generic class
        super().__init__(x = x,y = y, image = image)

        # -------------------------------------
        # Border animations

        # Note: Buttons are 400 x 120 pixels wide

        # Tuple that stores the co-ordinates of the four corners of the button
        self.button_points = (
                        (self.rect.x, self.rect.y), 
                        (self.rect.x + self.image.get_width(), self.rect.y), 
                        (self.rect.x + self.image.get_width(), self.rect.y + self.image.get_height()),
                        (self.rect.x, self.rect.y + self.image.get_height())
                        )

        # Speed that the animation travels on the button
        self.border_animation_max_x_speed = self.image.get_width() / 5
        self.border_animation_max_y_speed = self.image.get_height() 

        # Radius of the animation
        self.border_animation_radius = 7

        # Randomise the starting point of the animation, it can start from any of the four corners
        self.border_animation_current_point = random.randrange(0, 4)
        self.border_animation_rect = pygame.Rect(self.button_points[self.border_animation_current_point][0], self.button_points[self.border_animation_current_point][1], self.border_animation_radius, self.border_animation_radius)

    def play_border_animations(self):

        # ------------------------------------------------------------------------
        # Updating the border animation rect

        pygame.draw.circle(surface = self.surface, color = "gray32", center = (self.border_animation_rect.x, self.border_animation_rect.y), radius = self.border_animation_radius)

        # Identify the current point on the button that the animation is on 
        match self.border_animation_current_point:
            # Top left ---> Top right
            case 0:
            
                # Move right
                self.border_animation_rect.x += self.border_animation_max_x_speed * self.delta_time

                # If we have reached the top right corner
                if (self.border_animation_rect.x >= self.button_points[1][0]) and (self.border_animation_rect.y == self.button_points[1][1]):

                    # Set the current point to the top right corner of the button
                    self.border_animation_current_point = 1

                    # The animation may be slightly off the button so correct it 
                    self.border_animation_rect.x = self.button_points[1][0]

            # Top right ---> Bottom right
            case 1:

                # Move down
                self.border_animation_rect.y += self.border_animation_max_y_speed * self.delta_time

                # If we have reached the bottom right corner
                if (self.border_animation_rect.x == self.button_points[2][0]) and (self.border_animation_rect.y >= self.button_points[2][1]):
                    # Set the current point to the bottom right corner of the buttoncorner 
                    self.border_animation_current_point = 2

                    # The animation may be slightly off the button so correct it 
                    self.border_animation_rect.y = self.button_points[2][1]

            # Bottom right ---> Bottom left
            case 2:

                # Move left
                self.border_animation_rect.x -= self.border_animation_max_x_speed * self.delta_time

                # If we have reached the bottom left corner
                if (self.border_animation_rect.x <= self.button_points[3][0]) and (self.border_animation_rect.y == self.button_points[3][1]):
                    # Set the current point to the bottom left corner of the button
                    self.border_animation_current_point = 3

                    # The animation may be slightly off the button so correct it 
                    self.border_animation_rect.x = self.button_points[3][0]

            # Bottom left ---> Top left
            case 3:

                # Move up
                self.border_animation_rect.y -= self.border_animation_max_y_speed * self.delta_time

                # If we have reached the top left corner
                if (self.border_animation_rect.x == self.button_points[0][0]) and (self.border_animation_rect.y <= self.button_points[0][1]):

                    # Set the current point to the top left corner of the buttoncorner 
                    self.border_animation_current_point = 0

                    # The animation may be slightly off the button so correct it 
                    self.border_animation_rect.y = self.button_points[0][1]

    def draw(self):

        # Draw the button onto the surface
        self.surface.blit(self.image, (self.rect))
        