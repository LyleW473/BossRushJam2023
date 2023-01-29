import pygame, random
from Global.settings import * 
from Global.functions import draw_text

class Button:
    def __init__(self, rect_info_dict, purpose, text_font, surface):
        
        self.rect_info_dict = rect_info_dict
        
        # Create a rect at the positions passed into the class
        self.rect = pygame.Rect(
                                rect_info_dict["x"] - (rect_info_dict["button_measurements"][0] / 2), 
                                rect_info_dict["y"] - (rect_info_dict["button_measurements"][1] / 2), 
                                rect_info_dict["button_measurements"][0],
                                rect_info_dict["button_measurements"][1]
                                )

        # Purpose of the button (e.g. Play, Controls, Quit, etc.)
        self.purpose = purpose

        # Surfaces the button will be drawn onto
        # The main surface that the text will be drawn onto
        self.surface = surface

        # The minimum and maximum alpha levels of the button's alpha surface
        self.button_alpha_surface_minimum_alpha_level = 125
        self.button_alpha_surface_maximum_alpha_level = 255

        # The button's alpha surface, with the colour-key set as black and the default alpha level set as the minimum alpha level
        self.button_alpha_surface = pygame.Surface((self.rect.width, self.rect.height))
        self.button_alpha_surface.set_colorkey("black")
        self.button_alpha_surface.set_alpha(self.button_alpha_surface_minimum_alpha_level)

        # The amount the button will inflate / deflate by when the player hovers over the button
        self.button_inflation_amount = (30, 30)

        # A dictionary containing the colours for each "item"
        self.colours = {
                        "BorderAnimation": (221, 227, 146),
                        "ButtonRect": (113, 179, 64),
                        "Text": (255, 255, 255),
                        "ButtonRectBorder": (0, 0 ,0)
                       }
        # -------------------------------------
        # Button text

        # Set the text font as an attribute
        self.text_font = text_font
        
        # Find the amount of space needed to render the button text (This is for positioning the text at the center of the button)
        self.text_font_size = text_font.size(self.purpose)

        # -------------------------------------
        # Border animations

        # Tuple that stores the co-ordinates of the four corners of the button
        self.button_points = (self.rect.topleft, self.rect.topright, self.rect.bottomright, self.rect.bottomleft)

        # Speed that the animation travels on the button
        self.border_animation_max_x_speed = rect_info_dict["button_measurements"][0] / 5
        self.border_animation_max_y_speed = rect_info_dict["button_measurements"][1]

        # Radius of the animation
        self.border_animation_radius = 7

        # Randomise the starting point of the animation, it can start from any of the four corners
        self.border_animation_current_point = random.randrange(0, 3)
        self.border_animation_rect = pygame.Rect(self.button_points[self.border_animation_current_point][0], self.button_points[self.border_animation_current_point][1], self.border_animation_radius, self.border_animation_radius)

    def play_border_animations(self):

        # ------------------------------------------------------------------------
        # Updating the border animation rect

        pygame.draw.circle(surface = self.surface, color = self.colours["BorderAnimation"], center = (self.border_animation_rect.x, self.border_animation_rect.y), radius = self.border_animation_radius)

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
    
    def inflate_button(self, boolean_check): 

        # Inflating the button
        if boolean_check == True:
            
            # If the button has not been inflated already
            if self.rect.size != (self.rect_info_dict["button_measurements"][0] + self.button_inflation_amount[0], self.rect_info_dict["button_measurements"][1] + self.button_inflation_amount[1]):
                
                # Inflate the button
                self.rect = self.rect.inflate(self.button_inflation_amount[0], self.button_inflation_amount[1])

                # Set the new button points 
                self.button_points = (self.rect.topleft, self.rect.topright, self.rect.bottomright, self.rect.bottomleft)
                
                # Move the border animation rect based on the side that it is currently on
                # Note: Inflation amount divided by 2 because it is a centered inflation
                match self.border_animation_current_point:
                    # Top side of the button
                    case 0:
                        self.border_animation_rect[1] -= self.button_inflation_amount[1] / 2
                    # Right side of the button
                    case 1:
                        self.border_animation_rect[0] += self.button_inflation_amount[0] / 2
                    # Bottom side of the button
                    case 2:
                        self.border_animation_rect[1] += self.button_inflation_amount[1] / 2
                    # Left side of the button
                    case 3:
                        self.border_animation_rect[0] -= self.button_inflation_amount[0] / 2
                
        # Deflating the button
        elif boolean_check == False:
            
            # If the size of the button is not the same as the original size of the button (i.e. if the button has not been deflated yet)
            if self.rect.size != self.rect_info_dict["button_measurements"]:
                
                # Reset the button rect to its original measurements and position
                self.rect.size = self.rect_info_dict["button_measurements"]
                self.rect.x = self.rect_info_dict["x"] - (self.rect_info_dict["button_measurements"][0] / 2)
                self.rect.y = self.rect_info_dict["y"] - (self.rect_info_dict["button_measurements"][1] / 2)

                # Reset the button points 
                self.button_points = (self.rect.topleft, self.rect.topright, self.rect.bottomright, self.rect.bottomleft)

                # Re-adjust the border animation rect depending on the current side of the button the border animation rect is on
                match self.border_animation_current_point:
                    # Top side of the button
                    case 0:
                        self.border_animation_rect[1] += self.button_inflation_amount[1] / 2
                    # Right side of the button
                    case 1:
                        self.border_animation_rect[0] -= self.button_inflation_amount[0] / 2
                    # Bottom side of the button
                    case 2:
                        self.border_animation_rect[1] -= self.button_inflation_amount[1] / 2
                    # Left side of the button
                    case 3:
                        self.border_animation_rect[0] += self.button_inflation_amount[0] / 2
        
        # Resize the alpha surface for the button
        self.button_alpha_surface = pygame.transform.scale(surface = self.button_alpha_surface, size = (self.rect.width, self.rect.height))

    def draw(self):

        # Fill the alpha surface with black
        self.button_alpha_surface.fill("black")

        # Draw the button onto the alpha surface
        pygame.draw.rect(surface = self.button_alpha_surface, color = self.colours["ButtonRect"], rect = (0, 0, self.rect.width, self.rect.height), width = 0)

        # Draw the alpha surface onto the main surface
        self.surface.blit(self.button_alpha_surface, (self.rect.x, self.rect.y))

        pygame.draw.rect(surface = self.surface, color = self.colours["ButtonRectBorder"], rect = self.rect, width = 3)

        # Draw the button text onto the main surface
        draw_text(
            text = self.purpose, 
            text_colour = self.colours["Text"], 
            font = self.text_font, 
            x = self.rect.centerx - (self.text_font_size[0] / 2),
             y = self.rect.centery - (self.text_font_size[1] / 2), 
             surface = self.surface)