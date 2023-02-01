import pygame
from Global.functions import draw_text

class GameUI:

    def __init__(self, surface, scale_multiplier, player_tools, player_gameplay_info_dict):

        # Surface the UI will be drawn onto
        self.surface = surface
        
        # The scale multiplier used in the game
        self.scale_multiplier = scale_multiplier
        
        # Delta time attribute
        self.delta_time = None

        # The tools that the player has
        self.player_tools = player_tools
            
        # A dictionary containing information such as the HP the player has, the current tool equipped, amount of bamboo resource, etc.
        self.player_gameplay_info_dict = player_gameplay_info_dict

        # A dictionary containing the display cards for each tool inside the player's inventory of tools
        self.player_tools_display_cards_dict = {}

        # The font used to display text for the players' stats
        self.player_stats_font = pygame.font.Font("graphics/Fonts/player_stats_font.ttf", 32)

        # A dictionary containing information for each element of the game UI
        self.dimensions = {
                            "player_tools_display_cards": { "x": round(25 / scale_multiplier),
                                                            "y": round(50 / scale_multiplier),
                                                            "width": round(125 / scale_multiplier),
                                                            "height": round(125 / scale_multiplier),
                                                            "spacing_y": round(20 / scale_multiplier),
                                                            "border_thickness": 12,
                                                            "inner_outline_thickness": 1,
                                                            "alpha_level": 225
                                                            },
                            "player_stats": {
                                "x": round(25 / scale_multiplier),
                                "y": 0,
                                "width": round(310 / scale_multiplier),
                                "height": round(200 / scale_multiplier),
                                "border_thickness" : 12,
                                "inner_outline_thickness": 1,
                                "starting_position_from_inner_rect": (round(10 / scale_multiplier), round(10 / scale_multiplier)),
                                "spacing_y_between_stats": round(12 / scale_multiplier),
                                "spacing_x_between_image_and_text" : round(15 / scale_multiplier)
                            }
                            }

        # A dictionary containing the images for the player stats
        self.stats_images_dict = {
                        "BambooResource": {
                                            "Image": pygame.image.load("graphics/Misc/BambooResource.png").convert_alpha(), 
                                            "ImageWidth": pygame.image.load("graphics/Misc/BambooResource.png").convert().get_width(), 
                                            "ImageHeight": pygame.image.load("graphics/Misc/BambooResource.png").convert().get_height()
                                          },
                        "BuildingTiles": {
                                            "Image": self.player_tools["BuildingTool"]["Images"]["TileImage"],
                                            "ImageWidth" : self.player_tools["BuildingTool"]["Images"]["TileImage"].get_width(),
                                            "ImageHeight": self.player_tools["BuildingTool"]["Images"]["TileImage"].get_height(),
                                         }      
                                 }             

    def create_player_tools_display_cards(self):

        # Creates the players' tools' display cards

        # If the length of the inventory display cards dict is not the same as the length of the amount of tools 
        if len(self.player_tools_display_cards_dict) != len(self.player_tools):
            
            
            # For each tool in the player's inventory of tools
            for tool in self.player_tools.keys():
                # The spacing on the y-axis between each card
                spacing_y = self.dimensions["player_tools_display_cards"]["spacing_y"]

                # Create a rect containing the dimensions for the "display card" and an alpha surface for each "display card"
                self.player_tools_display_cards_dict[tool] = {
                            "Rect": pygame.Rect(
                                self.dimensions["player_tools_display_cards"]["x"], 
                                self.dimensions["player_tools_display_cards"]["y"] + (self.dimensions["player_tools_display_cards"]["height"] * len(self.player_tools_display_cards_dict)) + (spacing_y * len(self.player_tools_display_cards_dict)),
                                self.dimensions["player_tools_display_cards"]["width"],
                                self.dimensions["player_tools_display_cards"]["height"]
                                                    ),
                            "AlphaSurface": pygame.Surface((self.dimensions["player_tools_display_cards"]["width"], self.dimensions["player_tools_display_cards"]["height"])),
                            "IconImage": self.player_tools[tool]["Images"]["IconImage"]
                            }
                
                # If this is the last tool inside the player's inventory of tools
                if len(self.player_tools_display_cards_dict) == len(self.player_tools):
                    # Set the dimensions of where the player stats to start to be below that
                    self.dimensions["player_stats"]["y"] = self.player_tools_display_cards_dict[tool]["Rect"].y + self.player_tools_display_cards_dict[tool]["Rect"].height + spacing_y
                
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

    def draw_player_stats(self):

        # Draws the box(es) and text which contains the players' gameplay information e.g. amount of bamboo resource, number of building tiles placed, etc.
        
        # Outer rect of the stats "card"
        outer_rect = pygame.Rect(
                                self.dimensions["player_stats"]["x"], 
                                self.dimensions["player_stats"]["y"], 
                                self.dimensions["player_stats"]["width"], 
                                self.dimensions["player_stats"]["height"]
                                )
        # Inner rect of the stats "card"
        inner_rect = pygame.Rect(
                                self.dimensions["player_stats"]["x"] + (self.dimensions["player_stats"]["border_thickness"] / 2), 
                                self.dimensions["player_stats"]["y"] + (self.dimensions["player_stats"]["border_thickness"] / 2), 
                                self.dimensions["player_stats"]["width"] - self.dimensions["player_stats"]["border_thickness"], 
                                self.dimensions["player_stats"]["height"] - self.dimensions["player_stats"]["border_thickness"]
                                )

        # Outer body
        pygame.draw.rect(
                        surface = self.surface, 
                        color = "darkgreen", 
                        rect = outer_rect, 
                        width = 0)

        # Outer body outline
        pygame.draw.rect(
                        surface = self.surface, 
                        color = "black", 
                        rect = outer_rect, 
                        width = 1
                        )

        # Inner body
        pygame.draw.rect(
                        surface = self.surface, 
                        color = (120, 120, 120), 
                        rect = inner_rect, 
                        width = 0
                        )

        # Inner body outline
        pygame.draw.rect(
                        surface = self.surface, 
                        color = "white", 
                        rect = pygame.Rect(
                                            inner_rect.x - self.dimensions["player_stats"]["inner_outline_thickness"],
                                            inner_rect.y - (self.dimensions["player_stats"]["inner_outline_thickness"]), 
                                            inner_rect.width + (self.dimensions["player_stats"]["inner_outline_thickness"] * 2), 
                                            inner_rect.height + (self.dimensions["player_stats"]["inner_outline_thickness"] * 2)),
                        # rect = border_rect, 
                        width = self.dimensions["player_stats"]["inner_outline_thickness"]
                        )

        # -----------------------------------------------------------------
        # Drawing the amount of existing building tiles that the player has

        # Position that the building tile image
        building_tile_image_position = (
                                        inner_rect.x + self.dimensions["player_stats"]["starting_position_from_inner_rect"][0], 
                                        inner_rect.y + self.dimensions["player_stats"]["starting_position_from_inner_rect"][1]
                                       )

        # Draw the building tile image 
        self.surface.blit(self.stats_images_dict["BuildingTiles"]["Image"], building_tile_image_position)

        # The text that displays how many building tiles exist inside the map currently
        existing_building_tiles_text = f'Number of tiles: {len(self.player_tools["BuildingTool"]["ExistingBuildingTilesDict"])}'

        # Draw the text displaying the number of building tiles that exist inside the map currently
        draw_text(
                text = existing_building_tiles_text, 
                text_colour = "white",
                font = self.player_stats_font,
                x = building_tile_image_position[0] + self.stats_images_dict["BuildingTiles"]["ImageWidth"] + self.dimensions["player_stats"]["spacing_x_between_image_and_text"],
                y = building_tile_image_position[1],
                surface = self.surface, 
                scale_multiplier = self.scale_multiplier 
                )
        
        # -----------------------------------------------------------------
        # Drawing the amount of bamboo resource that the player has (used for ammo and building tiles)

        bamboo_resource_image_position = (
                    building_tile_image_position[0],
                    building_tile_image_position[1] + self.stats_images_dict["BuildingTiles"]["ImageHeight"] + self.dimensions["player_stats"]["spacing_y_between_stats"])

        # Building tile image 
        self.surface.blit(self.stats_images_dict["BambooResource"]["Image"], bamboo_resource_image_position)

        # The text that displays how much bamboo resource the player has
        amount_of_bamboo_resource_text = f'Bamboo: {self.player_gameplay_info_dict["AmountOfBambooResource"]} / {self.player_gameplay_info_dict["MaximumAmountOfBambooResource"]}'

        # Draw the text displaying the amount of bamboo resource
        draw_text(
                text = amount_of_bamboo_resource_text, 
                text_colour = "white",
                font = self.player_stats_font,
                x = bamboo_resource_image_position[0] + self.stats_images_dict["BambooResource"]["ImageWidth"] + self.dimensions["player_stats"]["spacing_x_between_image_and_text"],
                y = bamboo_resource_image_position[1],
                surface = self.surface, 
                scale_multiplier = self.scale_multiplier 
                )

    def run(self):

        # Create the players' tools' display cards
        self.create_player_tools_display_cards()

        # Draw the players' tools' display cards onto the screen
        self.draw_player_tools_display_cards()

        # Draw the players' stats
        self.draw_player_stats()

