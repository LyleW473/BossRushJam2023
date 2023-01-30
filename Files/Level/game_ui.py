import pygame

class GameUI:

    def __init__(self, surface, scale_multiplier):

        # Surface the UI will be drawn onto
        self.surface = surface
        
        # The scale multiplier used in the game
        self.scale_multiplier = scale_multiplier
        
        # Delta time attribute
        self.delta_time = None

        # The tools that the player has
        self.player_tools = None

        # A dictionary containing the display cards for each tool inside the player's inventory of tools
        self.player_tools_display_cards_dict = {}

        # A dictionary containing information for each element of the game UI
        self.dimensions = {
                            "player_tools_display_cards": { "x": round(25 / scale_multiplier),
                                                            "y": round(300 / scale_multiplier),
                                                            "width": round(150 / scale_multiplier),
                                                            "height": round(150 / scale_multiplier),
                                                            "border_thickness": 12,
                                                            "alpha_level": 225,
                                                            "inner_outline_thickness": 1
                                                            }

                            }
    
    def create_player_tools_display_cards(self):

        # Creates the players' tools' display cards

        # If the length of the inventory display cards dict is not the same as the length of the amount of tools 
        if len(self.player_tools_display_cards_dict) != len(self.player_tools):
            
            
            # For each tool in the player's inventory of tools
            for tool in self.player_tools.keys():
                # The spacing on the y-axis between each card
                spacing_y = (len(self.player_tools_display_cards_dict) * self.dimensions["player_tools_display_cards"]["height"] * 1.1)

                # Create a rect containing the dimensions for the "display card" and an alpha surface for each "display card"
                self.player_tools_display_cards_dict[tool] = {
                                                            "Rect": pygame.Rect(
                                                                                self.dimensions["player_tools_display_cards"]["x"], 
                                                                                self.dimensions["player_tools_display_cards"]["y"] + spacing_y,
                                                                                self.dimensions["player_tools_display_cards"]["width"],
                                                                                self.dimensions["player_tools_display_cards"]["height"]
                                                                                ),
                                                            "AlphaSurface": pygame.Surface((self.dimensions["player_tools_display_cards"]["width"], self.dimensions["player_tools_display_cards"]["height"])),
                                                            "IconImage": self.resize_icon_image(image = self.player_tools[tool]["Images"]["IconImage"])
                                                            }
                
                # Set a colorkey and alpha level for the alpha surface
                self.player_tools_display_cards_dict[tool]["AlphaSurface"].set_colorkey("black")
                self.player_tools_display_cards_dict[tool]["AlphaSurface"].set_alpha(self.dimensions["player_tools_display_cards"]["alpha_level"])

    def resize_icon_image(self, image):

        """ Used to resize the icon message to fit inside the inner boundaries of the player tools display cards.
        - Ensures that the aspect ratio of the image is maintained as both the width and height are scaled by the same amount.
        - Finds the maximum amount we can scale the image to before the width or height is the same size as the width or height of the boundaries.
        """

        # The inner boundaries of the player tools display cards
        inner_boundaries = (
                self.dimensions["player_tools_display_cards"]["width"] - self.dimensions["player_tools_display_cards"]["border_thickness"], 
                self.dimensions["player_tools_display_cards"]["height"] - self.dimensions["player_tools_display_cards"]["border_thickness"]
                )

        # Size of the image as a tuple
        image_size = image.get_size()

        # Find the largest measurement (i.e. The width or height of the image, so that the scaled up image will always have one measurement that is the same as the boundaries size)
        largest_measurement = max(image_size)
        
        # If the largest measurement is the width of the image
        if largest_measurement == image_size[0]:
            # Calculate the decimal percentage of the boundaries (e.g. if the largest measurement was 30 and the boundaries was 40, the value would be 30 / 40 = 0.75)
            decimal_percentage_of_boundaries = largest_measurement / inner_boundaries[0] 

        # If the largest measurement is the height of the image
        elif largest_measurement == image_size[1]:
            # Calculate the decimal percentage of the boundaries
            decimal_percentage_of_boundaries = largest_measurement / inner_boundaries[1] 

        # The new image size is the image size divided by the percentage of boundaries
        new_image_size = (image_size[0] / decimal_percentage_of_boundaries, image_size[1] / decimal_percentage_of_boundaries)

        # Return a scaled up image of the icon image
        return pygame.transform.scale(image, (new_image_size[0], new_image_size[1]))

    def draw_player_tools_display_cards(self):

        # Draws the player's tools' display cards onto the main surface

        # For each tool card rect 
        for tool_display_card_info_dict in self.player_tools_display_cards_dict.values():

            # Fill the alpha surface with black
            tool_display_card_info_dict["AlphaSurface"].fill("black")

            # Draw the following rects:

            # ------------------------------
            # Drawing the outer body
            pygame.draw.rect(
                            surface = tool_display_card_info_dict["AlphaSurface"], 
                            color = "darkgreen", 
                            rect = pygame.Rect(0, 0, tool_display_card_info_dict["Rect"].width, tool_display_card_info_dict["Rect"].height), 
                            width = 0)
            

            # ------------------------------
            # Inner body rect
            inner_body_rect = pygame.Rect(
                            0 + (self.dimensions["player_tools_display_cards"]["border_thickness"] / 2), 
                            0 + (self.dimensions["player_tools_display_cards"]["border_thickness"] / 2), 
                            tool_display_card_info_dict["Rect"].width - self.dimensions["player_tools_display_cards"]["border_thickness"], 
                            tool_display_card_info_dict["Rect"].height - self.dimensions["player_tools_display_cards"]["border_thickness"]
                                    )
            
            # Drawing the inner body
            pygame.draw.rect(surface = tool_display_card_info_dict["AlphaSurface"], color = (120, 120, 120), rect = inner_body_rect, width = 0)

            # --------------------------------------------
            # Draw the icon image at the center of the display card

            # Distance between center of the inner rect minus the center of the icon image
            dx = inner_body_rect.centerx - (tool_display_card_info_dict["IconImage"].get_width() / 2)
            dy = inner_body_rect.centery - (tool_display_card_info_dict["IconImage"].get_height() / 2)

            # Draw the alpha surface onto the main surface
            self.surface.blit(tool_display_card_info_dict["AlphaSurface"], (tool_display_card_info_dict["Rect"].x, tool_display_card_info_dict["Rect"].y))

            # Blit the icon image at the center of the inner body rect
            self.surface.blit(
                                                            tool_display_card_info_dict["IconImage"], 
                                                            ((tool_display_card_info_dict["Rect"].x + dx, tool_display_card_info_dict["Rect"].y + dy)))
    

            # --------------------------------------------
            # Outlines

            # Inner border outline (Other approach would be creating a new rect and inflating it in place with 2 * the inner outline thickness)
            # Note: This uses the inner body rect's starting position on the screen and moves back by the inner outline thickness, increasing the height and width of the entire rect by the (inner outline thickness * 2).
            pygame.draw.rect(
                            surface = self.surface, 
                            color = "white", 
                            rect = pygame.Rect(
                                                (tool_display_card_info_dict["Rect"].x + inner_body_rect.x) - self.dimensions["player_tools_display_cards"]["inner_outline_thickness"],
                                                (tool_display_card_info_dict["Rect"].y + inner_body_rect.y) - (self.dimensions["player_tools_display_cards"]["inner_outline_thickness"]), 
                                                inner_body_rect.width + (self.dimensions["player_tools_display_cards"]["inner_outline_thickness"] * 2), 
                                                inner_body_rect.height + (self.dimensions["player_tools_display_cards"]["inner_outline_thickness"] * 2)),
                            # rect = border_rect, 
                            width = self.dimensions["player_tools_display_cards"]["inner_outline_thickness"]
                        )

            # Outer body outline
            pygame.draw.rect(
                            surface = self.surface, 
                            color = "black", 
                            rect = tool_display_card_info_dict["Rect"], 
                            width = 1
                            )

    def run(self):

        # Create the players' tools' display cards
        self.create_player_tools_display_cards()

        # Draw the players' tools' display cards onto the screen
        self.draw_player_tools_display_cards()

