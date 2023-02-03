from pygame.draw import rect as pygame_draw_rect
from pygame import Rect as pygame_Rect
from Global.functions import draw_text


class DisplayCard:
    
    # Default attributes of all display cards
    alpha_surface_alpha_level = 125
    border_thickness = 12
    inner_outline_thickness = 1
    outer_outline_thickness = 2

    def __init__(self, rect, surface, alpha_surface, images, purpose, text_font = None, extra_information_dict = None):
        
        # Main surface that the display card alpha surface is drawn onto
        self.surface = surface
        
        # The surface that the display card is drawn onto
        self.alpha_surface = alpha_surface

        # Set a colorkey and alpha level for the alpha surface
        self.alpha_surface.set_colorkey("black")
        self.alpha_surface.set_alpha(DisplayCard.alpha_surface_alpha_level)

        # Display card's rect
        self.rect = rect
        
        # Save the purpose of this display card in an attribute
        self.purpose = purpose
        
        # If the purpose of this display card is for the players' stats e.g. Number of building tiles, amount of bamboo resource, etc.
        if purpose == "PlayerStats":

            # Images for each "stat"
            self.images = images

            # Dictionary holding extra information
            self.extra_information_dict = extra_information_dict

            # A list of the size of each "stat" image
            self.images_size = [self.images[i].get_size() for i in range(0, len(self.images))]

            # Font used for the stats text
            self.text_font = text_font

        # If the purpose of this display card is for the players' tools
        elif purpose == "PlayerTools":
            self.image = images
    
    # --------------------------------------------
    # Common methods

    def draw_inner_and_outer_body(self):

        # ------------------------------
        # Drawing the outer body
        pygame_draw_rect(
                        surface = self.alpha_surface, 
                        color = "darkgreen", 
                        rect = pygame_Rect(0, 0, self.rect.width, self.rect.height), 
                        width = 0)

        # ------------------------------
        # Inner body rect
        inner_body_rect = pygame_Rect(
                        0 + (DisplayCard.border_thickness / 2), 
                        0 + (DisplayCard.border_thickness  / 2), 
                        self.rect.width - DisplayCard.border_thickness,
                        self.rect.height - DisplayCard.border_thickness
                                )
        
        # Drawing the inner body
        pygame_draw_rect(surface = self.alpha_surface, color = (120, 120, 120), rect = inner_body_rect, width = 0)

        # Return the inner body rect
        return inner_body_rect

    def draw_outlines(self, inner_body_rect):

        # Inner border outline (Other approach would be creating a new rect and inflating it in place with 2 * the inner outline thickness)
        # Note: This uses the inner body rect's starting position on the screen and moves back by the inner outline thickness, increasing the height and width of the entire rect by the (inner outline thickness * 2).
        pygame_draw_rect(
                        surface = self.surface, 
                        color = "white", 
                        rect = pygame_Rect(
                                            (self.rect.x + inner_body_rect.x) - DisplayCard.inner_outline_thickness,
                                            (self.rect.y + inner_body_rect.y) - DisplayCard.inner_outline_thickness, 
                                            inner_body_rect.width + (DisplayCard.inner_outline_thickness * 2), 
                                            inner_body_rect.height + (DisplayCard.inner_outline_thickness * 2)),
                        width = DisplayCard.inner_outline_thickness
                    )

        # Outer body outline
        pygame_draw_rect(
                        surface = self.surface, 
                        color = "black", 
                        rect = (
                                self.rect.x - DisplayCard.outer_outline_thickness,
                                self.rect.y - DisplayCard.outer_outline_thickness,
                                self.rect.width + (DisplayCard.outer_outline_thickness * 2),
                                self.rect.height + (DisplayCard.outer_outline_thickness * 2),
                               ),
                        width = DisplayCard.outer_outline_thickness
                        )
    
    # --------------------------------------------
    # Specific methods for different purposes

    def draw_tool_display_card_contents(self, inner_body_rect):

        # --------------------------------------------
        # Draw the icon image at the center of the display card  

        # Distance between center of the inner rect minus the center of the icon image
        dx = inner_body_rect.centerx - (self.image.get_width() / 2)
        dy = inner_body_rect.centery - (self.image.get_height() / 2)

        # Blit the icon image at the center of the inner body rect
        self.surface.blit(
                        self.image, 
                        ((self.rect.x + dx, self.rect.y + dy))
                        )

    def draw_stats_display_card_contents(self, inner_body_rect, player_tools, player_gameplay_info_dict):

        # -----------------------------------------------------------------
        # Drawing the amount of existing building tiles that the player has

        # Position that the building tile image
        building_tile_image_position = (
                                        self.rect.x + inner_body_rect.x + self.extra_information_dict["starting_position_from_inner_rect"][0], 
                                        self.rect.y + inner_body_rect.y + self.extra_information_dict["starting_position_from_inner_rect"][1]
                                    )

        # Draw the building tile image 
        self.surface.blit(self.images[0], building_tile_image_position)

        # The text that displays how many building tiles exist inside the map currently
        existing_building_tiles_text = f'Number of tiles: {len(player_tools["BuildingTool"]["ExistingBuildingTilesDict"])}'

        # Draw the text displaying the number of building tiles that exist inside the map currently
        draw_text(
                text = existing_building_tiles_text, 
                text_colour = "white",
                font = self.text_font,
                x = building_tile_image_position[0] + self.images_size[0][0] + self.extra_information_dict["spacing_x_between_image_and_text"], # self.images_size[1][0] = image width
                y = building_tile_image_position[1],
                surface = self.surface, 
                scale_multiplier = self.extra_information_dict["scale_multiplier"]
                )

        # -----------------------------------------------------------------
        # Drawing the amount of bamboo resource that the player has (used for ammo and building tiles)

        bamboo_resource_image_position = (
                    building_tile_image_position[0],
                    building_tile_image_position[1] + self.images_size[1][1] + self.extra_information_dict["spacing_y_between_stats"])

        # Building tile image 
        self.surface.blit(self.images[1], bamboo_resource_image_position)

        # The text that displays how much bamboo resource the player has
        amount_of_bamboo_resource_text = f'Bamboo: {player_gameplay_info_dict["AmountOfBambooResource"]} / {player_gameplay_info_dict["MaximumAmountOfBambooResource"]}'

        # Draw the text displaying the amount of bamboo resource
        draw_text(
                text = amount_of_bamboo_resource_text, 
                text_colour = "white",
                font = self.text_font,
                x = bamboo_resource_image_position[0] + self.images_size[1][0] + self.extra_information_dict["spacing_x_between_image_and_text"],
                y = bamboo_resource_image_position[1],
                surface = self.surface, 
                scale_multiplier = self.extra_information_dict["scale_multiplier"]
                )
        
        # -----------------------------------------------------------------
        # Drawing the health bar


        # Difference between the bottom of the inner body rect and the bottom of the last 
        bottom_of_inner_body_rect = self.rect.y + (inner_body_rect.y + inner_body_rect.height)
        bottom_of_final_stat = (bamboo_resource_image_position[1] + self.images_size[1][1])
    
        dy = bottom_of_inner_body_rect - bottom_of_final_stat
        displacement_from_bottom_of_final_stat = (dy - self.extra_information_dict["health_bar_height"]) / 2

        health_bar_measurements = (
                                bamboo_resource_image_position[0], # x
                                bottom_of_final_stat + displacement_from_bottom_of_final_stat, # y
                                inner_body_rect.width - (self.extra_information_dict["starting_position_from_inner_rect"][0] * 2), # width
                                self.extra_information_dict["health_bar_height"] # height
                               )
        # Health bar outer outline
        pygame_draw_rect(
                        surface = self.surface,
                        color = "black", 
                        rect = (
                                health_bar_measurements[0] - self.extra_information_dict["health_bar_outline_thickness"], 
                                health_bar_measurements[1] - self.extra_information_dict["health_bar_outline_thickness"], 
                                health_bar_measurements[2] + (self.extra_information_dict["health_bar_outline_thickness"] * 2),
                                health_bar_measurements[3] + (self.extra_information_dict["health_bar_outline_thickness"] * 2)
                                ),
                        width = 0,
                        border_radius = self.extra_information_dict["health_bar_border_radius"]
                        )

        # Default health bar in red
        pygame_draw_rect(
                        surface = self.surface,
                        color = "red", 
                        rect = (
                                health_bar_measurements[0], 
                                health_bar_measurements[1], 
                                health_bar_measurements[2],
                                health_bar_measurements[3]
                                ),
                        width = 0,
                        border_radius = self.extra_information_dict["health_bar_border_radius"]
                        )

        # The width should be the percentage of the current health compared to the maximum health, multiplied by the default health bar width
        # Limit the width to be 0 if the player's current health is negative
        green_health_bar_width = max((player_gameplay_info_dict["CurrentHealth"] / player_gameplay_info_dict["MaximumHealth"]) * health_bar_measurements[2], 0)

        # Update the text that will be displayed on the screen depending on the player's current health
        players_health_text = f'{max(player_gameplay_info_dict["CurrentHealth"], 0)} / {player_gameplay_info_dict["MaximumHealth"]}'

        # Calculate the font size, used to position the text at the center of the health bar
        players_health_text_font_size = self.text_font.size(players_health_text)

        # Current health bar in green
        pygame_draw_rect(
                        surface = self.surface,
                        color = "green", 
                        rect = (
                                health_bar_measurements[0], 
                                health_bar_measurements[1], 
                                green_health_bar_width,
                                health_bar_measurements[3]
                                ),
                        width = 0,
                        border_radius = self.extra_information_dict["health_bar_border_radius"]
                        )      

        # Draw the text displaying the amount of bamboo resource
        draw_text(
                text = players_health_text, 
                text_colour = "white",
                font = self.text_font,
                x = (health_bar_measurements[0] + (health_bar_measurements[2] / 2)) - ((players_health_text_font_size[0] / self.extra_information_dict["scale_multiplier"]) / 2),
                y = (health_bar_measurements[1] + (health_bar_measurements[3] / 2)) - ((players_health_text_font_size[1] / self.extra_information_dict["scale_multiplier"]) / 2),
                surface = self.surface, 
                scale_multiplier = self.extra_information_dict["scale_multiplier"]
                )

    # --------------------------------------------
    # Main draw method
    
    def draw(self, player_tools = None, player_gameplay_info_dict = None):

        # Fill the alpha surface with black
        self.alpha_surface.fill("black")

        # --------------------------------------------
        # Draw the inner and outer body, save the returned inner body rect for positioning other elements of the display card
        inner_body_rect = self.draw_inner_and_outer_body()

        # --------------------------------------------
        # Draw the alpha surface onto the main surface
        self.surface.blit(self.alpha_surface, (self.rect.x, self.rect.y))

        # If this display card is for the players' tools
        if self.purpose == "PlayerTools":
            # Draw the contents of the tool display card
            self.draw_tool_display_card_contents(inner_body_rect = inner_body_rect)

        # If this display card is for the players' stats
        if self.purpose == "PlayerStats":
            # Draw the contents of the stats display card
            self.draw_stats_display_card_contents(inner_body_rect = inner_body_rect, player_tools = player_tools, player_gameplay_info_dict = player_gameplay_info_dict)

        # --------------------------------------------
        # Outlines
        self.draw_outlines(inner_body_rect = inner_body_rect)
