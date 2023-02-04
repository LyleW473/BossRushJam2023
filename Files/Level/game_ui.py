from pygame import Rect as pygame_Rect
from pygame import Surface as pygame_Surface
from pygame.font import Font as pygame_font_Font
from pygame.draw import rect as pygame_draw_rect
from pygame.draw import line as pygame_draw_line
from pygame.image import load as load_image
from Level.display_card import DisplayCard
from Global.settings import TILE_SIZE, BAR_ALPHA_LEVEL
from Global.functions import draw_text, sin_change_object_colour
from pygame import Surface as pygame_Surface

class GameUI:

    def __init__(self, surface, scale_multiplier, player_tools, player_gameplay_info_dict):

        # Surface the UI will be drawn onto
        self.surface = surface
        
        # The scale multiplier used in the game
        self.scale_multiplier = scale_multiplier
        
        # Delta time attribute
        self.delta_time = None

        # The current boss
        self.current_boss = None

        # The current mouse position
        self.mouse_position = None

        # The tools that the player has
        self.player_tools = player_tools
        
        # A dictionary containing information such as the HP the player has, the current tool equipped, amount of bamboo resource, etc.
        self.player_gameplay_info_dict = player_gameplay_info_dict

        # A dictionary containing information for each element of the game UI
        self.dimensions = {
                            "player_tools": { "x": round(25 / scale_multiplier),
                                                            "y": round(140 / scale_multiplier),
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
                                "scale_multiplier": scale_multiplier,

                                # Health bar
                                "spacing_y_between_stats_and_health_bar": round(20 / scale_multiplier),
                                # The width is calculated inside the display card class, using the inner body rect
                                "health_bar_height": int(52 / scale_multiplier), # Odd values will result in the health bar not being aligned properly
                                "health_bar_border_radius": 0,
                                "health_bar_outline_thickness": 2,
                                "changing_health_bar_edge_thickness" : 3,

                                # Frenzy mode bar
                                "frenzy_mode_bar_x": (self.surface.get_width() - (int(92 / scale_multiplier))) - TILE_SIZE,
                                "frenzy_mode_bar_y": (self.surface.get_height() - round(500 / scale_multiplier)) - TILE_SIZE,
                                "frenzy_mode_bar_width": int(92 / scale_multiplier),
                                "frenzy_mode_bar_height": round( 500 / scale_multiplier),
                                "changing_frenzy_mode_bar_edge_thickness": 3,
                                "frenzy_mode_bar_outline_thickness": 3,
                                "frenzy_mode_value_text_font": pygame_font_Font("graphics/Fonts/frenzy_mode_value_font.ttf", 18),
                                

                                # Frenzy mode glow visual effect (The bar will glow at a slow rate, once activated, the effect is synced with the player's visual effect)
                                "frenzy_mode_visual_effect_colour": self.player_gameplay_info_dict["FrenzyModeVisualEffectColour"].copy(),
                                "frenzy_mode_visual_effect_angle_time_gradient": (360 - 0) / 2, # The rate of change of the angle over time (time in seconds)
                                "frenzy_mode_visual_effect_current_sin_angle": 0,

                                            },
                            "boss_bar": {
                                "x": (self.surface.get_width() - round(800 / scale_multiplier)) / 2,
                                "y": (self.surface.get_height() - round( (52 + 4) / scale_multiplier)) - TILE_SIZE, # Positioned 1 tile from the bottom of the screen (The 4 = the bar outline thickness)
                                "width": round((800) / scale_multiplier),
                                "height": round(52 / scale_multiplier),
                                "bar_outline_thickness": 4,
                                "text_font": pygame_font_Font("graphics/Fonts/player_stats_font.ttf", 32),
                                "changing_health_bar_edge_thickness": 3,
                                }
                          }
                            
        # A dictionary containing the display cards of all the elements of the game UI
        self.display_cards_dict = {
                                    "player_tools": [],
                                    "player_stats": [],
                                  }

        # A dictionary containing the images for the player stats
        self.stats_images_dict = {
                        "BambooResource": load_image("graphics/Misc/BambooResource.png").convert_alpha(),
                        "BuildingTiles": self.player_tools["BuildingTool"]["Images"]["TileImage"]
                                 }

        # Create display cards
        self.create_player_tools_display_cards()
        self.create_player_stats_display_cards()

        # ------------------------------------------------------------
        # Alpha surfaces

        # Frenzy mode bar
        self.dimensions["player_stats"]["frenzy_mode_bar_alpha_surface"] =  pygame_Surface((self.dimensions["player_stats"]["frenzy_mode_bar_width"], self.dimensions["player_stats"]["frenzy_mode_bar_height"]))
        self.dimensions["player_stats"]["frenzy_mode_bar_alpha_surface"].set_colorkey("black")
        self.dimensions["player_stats"]["frenzy_mode_bar_alpha_surface"].set_alpha(BAR_ALPHA_LEVEL)

        # Boss' health bar
        self.dimensions["boss_bar"]["alpha_surface"] =  pygame_Surface((self.dimensions["boss_bar"]["width"], self.dimensions["boss_bar"]["height"]))
        self.dimensions["boss_bar"]["alpha_surface"].set_colorkey("black")
        self.dimensions["boss_bar"]["alpha_surface"].set_alpha(BAR_ALPHA_LEVEL)

        # ------------------------------------------------------------
        # Cursor image
        self.default_cursor_image = load_image("graphics/Cursors/Default.png").convert_alpha()


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
                                            rect = pygame_Rect(
                                                            self.dimensions["player_tools"]["x"], 
                                                            self.dimensions["player_tools"]["y"] + (self.dimensions["player_tools"]["height"] * len(self.display_cards_dict["player_tools"])) + (spacing_y * len(self.display_cards_dict["player_tools"])),
                                                            self.dimensions["player_tools"]["width"],
                                                            self.dimensions["player_tools"]["height"]),
                                            surface = self.surface,
                                            alpha_surface = pygame_Surface((self.dimensions["player_tools"]["width"], self.dimensions["player_tools"]["height"])),
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
        self.display_cards_dict["player_stats"].append(DisplayCard
                                                                    (
                                                                        rect = pygame_Rect(
                                                                                            self.dimensions["player_stats"]["x"],
                                                                                            self.dimensions["player_stats"]["y"], 
                                                                                            self.dimensions["player_stats"]["width"], 
                                                                                            self.dimensions["player_stats"]["height"]
                                                                                            ),
                                                                        surface = self.surface, 
                                                                        alpha_surface = pygame_Surface((self.dimensions["player_stats"]["width"], self.dimensions["player_stats"]["height"])),
                                                                        images = [self.stats_images_dict["BuildingTiles"], self.stats_images_dict["BambooResource"]],
                                                                        text_font = pygame_font_Font("graphics/Fonts/player_stats_font.ttf", 32),
                                                                        extra_information_dict = {key:value for key, value in self.dimensions["player_stats"].items() if key not in ["x", "y", "width", "height"]}, # Adds extra information into a dictionary
                                                                        purpose = "PlayerStats"
                                                                    )
                                                                )

    def draw_boss_health(self):
        
        # If a boss has been spawned
        if self.current_boss != None:

            # Fill the boss bar's alpha surface with black
            self.dimensions["boss_bar"]["alpha_surface"].fill("black")

            # --------------------------------------
            # Default body

            pygame_draw_rect(
                            surface = self.dimensions["boss_bar"]["alpha_surface"],
                            color = "gray21",
                            rect = pygame_Rect(
                                            0,
                                            0,
                                            self.dimensions["boss_bar"]["width"],
                                            self.dimensions["boss_bar"]["height"]
                                            ),
                            width = 0
                            )
            
            # --------------------------------------
            # Bar that changes depending on the health of the current boss

            health_bar_width = max((self.current_boss.extra_information_dict["CurrentHealth"] / self.current_boss.extra_information_dict["MaximumHealth"] ) * self.dimensions["boss_bar"]["width"], 0)
            pygame_draw_rect(
                            surface = self.dimensions["boss_bar"]["alpha_surface"],
                            color = "firebrick3",
                            rect = pygame_Rect(
                                            0,
                                            0,
                                            health_bar_width,
                                            self.dimensions["boss_bar"]["height"] / 2
                                            ),
                            width = 0
                            )

            pygame_draw_rect(
                            surface = self.dimensions["boss_bar"]["alpha_surface"],
                            color = "firebrick4",
                            rect = pygame_Rect(
                                            0,
                                            0 + (self.dimensions["boss_bar"]["height"] / 2),
                                            health_bar_width,
                                            self.dimensions["boss_bar"]["height"] / 2
                                            ),
                            width = 0
                            )

            # Only draw the edge when the width of the health bar is greater than 0
            if health_bar_width > 0:

                # Edge at the end of the changing part of the boss' health
                pygame_draw_line(
                                surface = self.dimensions["boss_bar"]["alpha_surface"], 
                                color = (200, 44, 44),
                                start_pos = ((health_bar_width) - (self.dimensions["boss_bar"]["changing_health_bar_edge_thickness"] / 2), 0),
                                end_pos = ((health_bar_width) - (self.dimensions["boss_bar"]["changing_health_bar_edge_thickness"] / 2), self.dimensions["boss_bar"]["height"]),
                                width = self.dimensions["boss_bar"]["changing_health_bar_edge_thickness"]
                                )

            # --------------------------------------
            # Draw the alpha surface onto the main surface
            self.surface.blit(self.dimensions["boss_bar"]["alpha_surface"], (self.dimensions["boss_bar"]["x"], self.dimensions["boss_bar"]["y"]))

            # --------------------------------------
            # Outline
            pygame_draw_rect(
                            surface = self.surface,
                            color = "black",
                            rect = pygame_Rect(
                                            self.dimensions["boss_bar"]["x"] - (self.dimensions["boss_bar"]["bar_outline_thickness"]),
                                            self.dimensions["boss_bar"]["y"] - (self.dimensions["boss_bar"]["bar_outline_thickness"]),
                                            self.dimensions["boss_bar"]["width"] + (self.dimensions["boss_bar"]["bar_outline_thickness"] * 2),
                                            self.dimensions["boss_bar"]["height"] + (self.dimensions["boss_bar"]["bar_outline_thickness"] * 2)
                                            ),
                            width = self.dimensions["boss_bar"]["bar_outline_thickness"]
                                )

            # --------------------------------------
            # Health bar text:

            # Update the text that will be displayed on the screen depending on the boss' current health
            boss_health_text = f'{max(self.current_boss.extra_information_dict["CurrentHealth"], 0)} / {self.current_boss.extra_information_dict["MaximumHealth"]}'

            # Calculate the font size, used to position the text at the center of the health bar
            boss_health_text_font_size = self.dimensions["boss_bar"]["text_font"].size(boss_health_text)
            
            # Draw the text displaying the amount of bamboo resource
            draw_text(
                    text = boss_health_text, 
                    text_colour = "white",
                    font = self.dimensions["boss_bar"]["text_font"],
                    x = (self.dimensions["boss_bar"]["x"] + (self.dimensions["boss_bar"]["width"] / 2)) - ((boss_health_text_font_size[0] / self.scale_multiplier) / 2),
                    y = (self.dimensions["boss_bar"]["y"] + (self.dimensions["boss_bar"]["height"] / 2)) - ((boss_health_text_font_size[1] / self.scale_multiplier) / 2),
                    surface = self.surface, 
                    scale_multiplier = self.scale_multiplier
                    )

    def draw_player_frenzy_mode_bar(self):

        # Fill the frenzy mode bar's alpha surface with black
        self.dimensions["player_stats"]["frenzy_mode_bar_alpha_surface"].fill("black")

        # --------------------------------------
        # Default body

        pygame_draw_rect(
                        surface = self.dimensions["player_stats"]["frenzy_mode_bar_alpha_surface"],
                        color = "gray21",
                        rect = pygame_Rect(
                                        0,
                                        0,
                                        self.dimensions["player_stats"]["frenzy_mode_bar_width"],
                                        self.dimensions["player_stats"]["frenzy_mode_bar_height"]
                                        ),
                        width = 0
                        ) 
        # --------------------------------------
        # Bar that changes depending on the frenzy mode value

        # Calculate the height of the bar
        frenzy_mode_bar_height = max(self.player_gameplay_info_dict["CurrentFrenzyModeValue"] / self.player_gameplay_info_dict["MaximumFrenzyModeValue"] * self.dimensions["player_stats"]["frenzy_mode_bar_height"], 0)
        # Calculate the y position based on the height of the bar (int(frenzy_mode_bar_height) so that the bar doesn't get misaligned with decimal increments in the frenzy mode value)
        frenzy_mode_bar_y_pos = (self.dimensions["player_stats"]["frenzy_mode_bar_height"]) - int(frenzy_mode_bar_height)

        # If the player has not activated frenzy mode
        if self.player_gameplay_info_dict["FrenzyModeTimer"] == None:

            # If the frenzy mode bar is not completely full
            if self.player_gameplay_info_dict["CurrentFrenzyModeValue"] != self.player_gameplay_info_dict["MaximumFrenzyModeValue"]:
                # Set the colour of the bar to be the default colours
                frenzy_mode_bar_colour = ("darkorchid2", "darkorchid3")

            # If the frenzy mode bar is completely full
            elif self.player_gameplay_info_dict["CurrentFrenzyModeValue"] == self.player_gameplay_info_dict["MaximumFrenzyModeValue"]:
                
                # Note: This is not synced with the player, but a separate visual effect to indicate that the bar is full
                
                # Lambda function to offset the rgb values of the current frenzy mode colour
                darker_colour = lambda x: x - min(self.dimensions["player_stats"]["frenzy_mode_visual_effect_colour"])
                
                # Set the colour of the bar to oscillate slowly with the visual effect settings
                self.dimensions["player_stats"]["frenzy_mode_visual_effect_colour"], self.dimensions["player_stats"]["frenzy_mode_visual_effect_current_sin_angle"] = sin_change_object_colour(
                                                                                                                                        
                                                                                                            # The current sin angle
                                                                                                            current_sin_angle = self.dimensions["player_stats"]["frenzy_mode_visual_effect_current_sin_angle"],

                                                                                                            # The rate of change in the sin angle over time
                                                                                                            angle_time_gradient = self.dimensions["player_stats"]["frenzy_mode_visual_effect_angle_time_gradient"], 

                                                                                                            # Set the colour that will be changed (the return value)
                                                                                                            colour_to_change = self.dimensions["player_stats"]["frenzy_mode_visual_effect_colour"],

                                                                                                            # Set the original colour as either the min or max colour 
                                                                                                            # Note:  The order does not matter because the colour will always start at the midpoint RGB value
                                                                                                            original_colour = self.player_gameplay_info_dict["FrenzyModeVisualEffectMinMaxColours"][0],

                                                                                                            # The minimum and maximum colours
                                                                                                            min_max_colours = self.player_gameplay_info_dict["FrenzyModeVisualEffectMinMaxColours"],

                                                                                                            # A list containing values indicating whether we should subtract or add for each RGB value at a given angle, e.g. (-1, 0, 1)
                                                                                                            plus_or_minus_list = self.player_gameplay_info_dict["FrenzyModeVisualEffectRGBValuesPlusOrMinus"],

                                                                                                            # Delta time to increase the angle over time
                                                                                                            delta_time = self.delta_time
                                                                                                                                                                                    )

                # Set the frenzy mode bar colour (A tuple because the bar is made up of two rectangles)
                frenzy_mode_bar_colour = (
                                        self.dimensions["player_stats"]["frenzy_mode_visual_effect_colour"], 
                                        tuple(darker_colour(self.dimensions["player_stats"]["frenzy_mode_visual_effect_colour"][i]) for i in range(0, len(self.dimensions["player_stats"]["frenzy_mode_visual_effect_colour"])))
                                        )

        # If the player has activated frenzy mode
        if self.player_gameplay_info_dict["FrenzyModeTimer"] != None:

            # Note: This is synced to the visual effect of the player
            
            # Lambda function to offset the rgb values of the current frenzy mode colour
            darker_colour = lambda x: x - 10

            # Set the frenzy mode bar colour (A tuple because the bar is made up of two rectangles)
            frenzy_mode_bar_colour = (
                                    self.player_gameplay_info_dict["FrenzyModeVisualEffectColour"], 
                                    tuple(darker_colour(self.player_gameplay_info_dict["FrenzyModeVisualEffectColour"][i]) for i in range(0, len(self.player_gameplay_info_dict["FrenzyModeVisualEffectColour"])))
                                    
                                    )
        
        # Drawing the frenzy mode bar
        pygame_draw_rect(
                        surface = self.dimensions["player_stats"]["frenzy_mode_bar_alpha_surface"],
                        color = frenzy_mode_bar_colour[0],
                        rect = pygame_Rect(
                                        0,
                                        frenzy_mode_bar_y_pos,
                                        self.dimensions["player_stats"]["frenzy_mode_bar_width"] / 2,
                                        frenzy_mode_bar_height
                                        ),
                        width = 0
                        ) 

        pygame_draw_rect(
                        surface = self.dimensions["player_stats"]["frenzy_mode_bar_alpha_surface"],
                        color = frenzy_mode_bar_colour[1],
                        rect = pygame_Rect(
                                        0 + (self.dimensions["player_stats"]["frenzy_mode_bar_width"] / 2),
                                        frenzy_mode_bar_y_pos,
                                        self.dimensions["player_stats"]["frenzy_mode_bar_width"] / 2,
                                        frenzy_mode_bar_height
                                        ),
                        width = 0
                        ) 

        # Only draw the edge when the height of the frenzy mode bar is greater than 0
        if frenzy_mode_bar_height > 0:
            
            # If the player has not activated frenzy mode
            if self.player_gameplay_info_dict["FrenzyModeTimer"] == None:
                # Set the edge colour as the default colour
                bar_edge_colour = (174, 50, 205)
            
            # If the player has activated frenzy mode
            elif self.player_gameplay_info_dict["FrenzyModeTimer"] != None:
                # Set the bar edge as the current frenzy mode visual effect colour 
                # Note: Call the darker colour lambda function again for a colour that will always be darker than the bar
                bar_edge_colour = tuple(darker_colour(frenzy_mode_bar_colour[1][i]) for i in range(0, len(self.player_gameplay_info_dict["FrenzyModeVisualEffectColour"])))

            # Edge at the end of the changing part of the boss' health
            pygame_draw_line(
                            surface = self.dimensions["player_stats"]["frenzy_mode_bar_alpha_surface"], 
                            color = bar_edge_colour,
                            start_pos = (0, frenzy_mode_bar_y_pos - (self.dimensions["player_stats"]["changing_frenzy_mode_bar_edge_thickness"] / 2)),
                            end_pos = (0 + self.dimensions["player_stats"]["frenzy_mode_bar_width"], frenzy_mode_bar_y_pos - (self.dimensions["player_stats"]["changing_frenzy_mode_bar_edge_thickness"] / 2)),
                            width = self.dimensions["player_stats"]["changing_frenzy_mode_bar_edge_thickness"]
                            )
        
        # --------------------------------------
        # Draw the alpha surface onto the main surface
        self.surface.blit(self.dimensions["player_stats"]["frenzy_mode_bar_alpha_surface"], (self.dimensions["player_stats"]["frenzy_mode_bar_x"], self.dimensions["player_stats"]["frenzy_mode_bar_y"]))
        
        # --------------------------------------
        # Outline
        pygame_draw_rect(
                        surface = self.surface,
                        color = "black",
                        rect = pygame_Rect(
                                        self.dimensions["player_stats"]["frenzy_mode_bar_x"] - (self.dimensions["player_stats"]["frenzy_mode_bar_outline_thickness"]),
                                        self.dimensions["player_stats"]["frenzy_mode_bar_y"] - (self.dimensions["player_stats"]["frenzy_mode_bar_outline_thickness"]),
                                        self.dimensions["player_stats"]["frenzy_mode_bar_width"] + (self.dimensions["player_stats"]["frenzy_mode_bar_outline_thickness"] * 2),
                                        self.dimensions["player_stats"]["frenzy_mode_bar_height"] + (self.dimensions["player_stats"]["frenzy_mode_bar_outline_thickness"] * 2)
                                        ),
                        width = self.dimensions["player_stats"]["frenzy_mode_bar_outline_thickness"]
                            )
        
        # --------------------------------------
        # Frenzy mode bar text:

        # Update the text that will be displayed on the screen depending on the current frenzy mode value
        frenzy_mode_value_text = f'{int((self.player_gameplay_info_dict["CurrentFrenzyModeValue"] / self.player_gameplay_info_dict["MaximumFrenzyModeValue"]) * 100)} %' # A percentage meter

        # Calculate the font size, used to position the text at the center of the health bar
        frenzy_mode_value_text_font_size = self.dimensions["player_stats"]["frenzy_mode_value_text_font"].size(frenzy_mode_value_text)
        
        # Draw the text displaying the amount of bamboo resource
        draw_text(
                text = frenzy_mode_value_text, 
                text_colour = "white",
                font = self.dimensions["player_stats"]["frenzy_mode_value_text_font"],
                x = (self.dimensions["player_stats"]["frenzy_mode_bar_x"] + (self.dimensions["player_stats"]["frenzy_mode_bar_width"] / 2)) - ((frenzy_mode_value_text_font_size[0]) / 2),
                y = (self.dimensions["player_stats"]["frenzy_mode_bar_y"] + (self.dimensions["player_stats"]["frenzy_mode_bar_height"] / 2)) - ((frenzy_mode_value_text_font_size[1]) / 2),
                surface = self.surface, 

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

    def draw_mouse_cursor(self):

        # Draws the new cursor

        # Blit the cursor image at the mouse position, subtracting half of the cursor image's width and height
        self.surface.blit(self.default_cursor_image, (self.mouse_position[0] - (self.default_cursor_image.get_width()/ 2), self.mouse_position[1]- (self.default_cursor_image.get_height() / 2)))

    def draw_guidelines_between_a_and_b(self, a, b, guidelines_surface, main_surface, camera_position, guidelines_segments_thickness):

        # Draws guidelines between the two subjects
        """ Note: This is a method of the Game class because """
    
        # The number of segments desired for the guidelines
        number_of_segments = 6

        # Calculate the distance between the a and b
        dx, dy = a[0] - b[0], a[1] - b[1]

        # Calculate the length of each segment 
        segment_length_x = dx / (number_of_segments * 2)
        segment_length_y = dy / (number_of_segments * 2)

        # Fill the guidelines surface with black. (The colour-key has been set to black)
        guidelines_surface.fill("black")

        # Draw lines
        for i in range(1, (number_of_segments * 2) + 1, 2):     
            pygame_draw_line(
                surface = guidelines_surface, 
                color = "white",
                start_pos = ((b[0] - camera_position[0]) + (segment_length_x * i), (b[1] - camera_position[1]) + (segment_length_y * i)),
                end_pos = ((b[0] - camera_position[0]) + (segment_length_x * (i + 1)), (b[1] - camera_position[1]) + (segment_length_y * (i + 1))),
                width = guidelines_segments_thickness)

        # Draw the guidelines surface onto the main surface
        main_surface.blit(guidelines_surface, (0, 0))

    def run(self):

        # Draw the display cards onto the screen
        self.draw_display_cards()

        # Draw the boss' health if a boss has been spawned
        self.draw_boss_health()

        # Draw the player's frenzy mode bar
        self.draw_player_frenzy_mode_bar()

        # Draw the mouse cursor
        self.draw_mouse_cursor()


