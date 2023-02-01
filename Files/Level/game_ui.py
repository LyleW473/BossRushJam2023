import pygame
from Level.display_card import DisplayCard

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

        # A dictionary containing information for each element of the game UI
        self.dimensions = {
                            "player_tools": { "x": round(25 / scale_multiplier),
                                                            "y": round(50 / scale_multiplier),
                                                            "width": round(125 / scale_multiplier),
                                                            "height": round(125 / scale_multiplier),
                                                            "spacing_y": round(20 / scale_multiplier),
                                                            },
                            "player_stats": {
                                "x": round(25 / scale_multiplier),
                                "y": 0,
                                "width": round(310 / scale_multiplier),
                                "height": round(200 / scale_multiplier),
                                "starting_position_from_inner_rect": (round(10 / scale_multiplier), round(10 / scale_multiplier)),
                                "spacing_y_between_stats": round(12 / scale_multiplier),
                                "spacing_x_between_image_and_text" : round(15 / scale_multiplier),
                            }
                            }
                            
        # A dictionary containing the display cards of all the elements of the game UI
        self.display_cards_dict = {
                                    "player_tools": [],
                                    "player_stats": []
                                  }

        # A dictionary containing the images for the player stats
        self.stats_images_dict = {
                        "BambooResource": pygame.image.load("graphics/Misc/BambooResource.png").convert_alpha(),
                        "BuildingTiles": self.player_tools["BuildingTool"]["Images"]["TileImage"]
                                 }

        # Create display cards
        self.create_player_tools_display_cards()
        self.create_player_stats_display_cards()

    def create_player_tools_display_cards(self):

        # Creates the players' tools' display cards

        # If the length of the inventory display cards dict is not the same as the length of the amount of tools 
        if len(self.display_cards_dict["player_tools"]) != len(self.player_tools):
            
            # For each tool in the player's inventory of tools
            for tool in self.player_tools.keys():
                # The spacing on the y-axis between each card
                spacing_y = self.dimensions["player_tools"]["spacing_y"]

                # Create a display card, passing in: The rect, main surface, an alpha surface for the display card and icon image.
                self.display_cards_dict["player_tools"].append(DisplayCard(
                                            rect = pygame.Rect(
                                                            self.dimensions["player_tools"]["x"], 
                                                            self.dimensions["player_tools"]["y"] + (self.dimensions["player_tools"]["height"] * len(self.display_cards_dict["player_tools"])) + (spacing_y * len(self.display_cards_dict["player_tools"])),
                                                            self.dimensions["player_tools"]["width"],
                                                            self.dimensions["player_tools"]["height"]),
                                            surface = self.surface,
                                            alpha_surface = pygame.Surface((self.dimensions["player_tools"]["width"], self.dimensions["player_tools"]["height"])),
                                            images = self.player_tools[tool]["Images"]["IconImage"],
                                            purpose = "PlayerTools",
                                                                )
                                                            )
                
                # If this is the last tool inside the player's inventory of tools
                if len(self.display_cards_dict["player_tools"]) == len(self.player_tools):
                    # Temp variable for the last display card
                    last_display_card = self.display_cards_dict["player_tools"][len(self.display_cards_dict["player_tools"]) - 1]
                    
                    # Set the dimensions of where the player stats to start to be below that
                    self.dimensions["player_stats"]["y"] = last_display_card.rect.y + last_display_card.rect.height + spacing_y
    
    def create_player_stats_display_cards(self):

        # Creates the players' stats' display cards
        
        # Create player stats cards and add it to the list in the player stats of the display cards dictionary
        self.display_cards_dict["player_stats"].append(DisplayCard(
                                                                rect = pygame.Rect(
                                                                                    self.dimensions["player_stats"]["x"],
                                                                                    self.dimensions["player_stats"]["y"], 
                                                                                    self.dimensions["player_stats"]["width"], 
                                                                                    self.dimensions["player_stats"]["height"]
                                                                                    ),
                                                                surface = self.surface, 
                                                                alpha_surface = pygame.Surface((self.dimensions["player_stats"]["width"], self.dimensions["player_stats"]["height"])),
                                                                images = [self.stats_images_dict["BuildingTiles"], self.stats_images_dict["BambooResource"]],
                                                                text_font = pygame.font.Font("graphics/Fonts/player_stats_font.ttf", 32),
                                                                extra_information_dict = {   
                                                                                        "starting_position_from_inner_rect": (round(10 / self.scale_multiplier), round(10 / self.scale_multiplier)),
                                                                                        "spacing_y_between_stats": round(12 / self.scale_multiplier),
                                                                                        "spacing_x_between_image_and_text" : round(15 / self.scale_multiplier),
                                                                                        "scale_multiplier": self.scale_multiplier
                                                                                        },
                                                                purpose = "PlayerStats"
                                                            )
                                                        )

    def draw_display_cards(self):

        # For each tool display card
        for tool_display_card in self.display_cards_dict["player_tools"]:
            # Draw the card
            tool_display_card.draw()

        # For each stats display card
        for stats_display_card in self.display_cards_dict["player_stats"]:
            # Draw the card, passing in the player tools dictionary and the players gameplay info dictionary
            stats_display_card.draw(player_tools = self.player_tools, player_gameplay_info_dict = self.player_gameplay_info_dict)

    def run(self):

        # Draw the display cards onto the screen
        self.draw_display_cards()


