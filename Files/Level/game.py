from Global.settings import *
from Level.world_tile import WorldTile
from Level.Player.player import Player
from Level.game_ui import GameUI
from Level.bamboo_pile import BambooPile
from random import choice as random_choice
from random import randrange as random_randrange
from random import uniform as random_uniform
from math import sin, cos, dist
from os import listdir as os_listdir

from pygame.display import get_surface as pygame_display_get_surface
from pygame import Surface as pygame_Surface
from pygame.sprite import Group as pygame_sprite_Group
from pygame.sprite import GroupSingle as pygame_sprite_GroupSingle
from pygame.sprite import collide_mask as pygame_sprite_collide_mask
from pygame.image import load as pygame_image_load
from pygame.transform import smoothscale as pygame_transform_smoothscale
from pygame.transform import scale as pygame_transform_scale
from pygame.transform import flip as pygame_transform_flip
from pygame.sprite import spritecollide as pygame_sprite_spritecollide
from pygame.sprite import collide_rect as pygame_sprite_collide_rect
from pygame.key import get_pressed as pygame_key_get_pressed
from pygame import K_f as pygame_K_f
from pygame.draw import rect as pygame_draw_rect
from pygame.draw import circle as pygame_draw_circle
from pygame.draw import line as pygame_draw_line



class Game:
    def __init__(self):

        # Screen
        self.screen = pygame_display_get_surface()  

        # Create a surface for which all objects will be drawn onto. This surface is then scaled and drawn onto the main screen
        self.scale_multiplier = 2
        self.scaled_surface = pygame_Surface((screen_width / self.scale_multiplier, screen_height / self.scale_multiplier))

        # Attribute which is monitored by the game states controller
        self.running = False

        # Delta time attribute is created
        # self.delta_time = None

        # --------------------------------------------------------------------------------------
        # Tile map
        
        # Load the tile map images
        self.load_tile_map_images()

        # --------------------------------------------------------------------------------------
        # Camera
        self.last_tile_position = [0, 0] # Stores the position of the last tile in the tile (This is changed inside the create_objects_tile_map method)

        # Camera modes
        self.camera_mode = None # Can either be: Static, Follow, Pan
        
        # A dictionary containing information about camera panning
        """ The panning is as follows:
        - Pans from the player to the boss
        - Locks on the boss for a short period of time
        - Pans from the boss back to the player
        - Locks on the player for a short period of time
        - Resets the camera mode back to "Follow", allowing the player to play
        
        """
        self.camera_pan_information_dict = {
                                            # The rate of change in the distance of the camera over time
                                            "PanHorizontalDistanceTimeGradient": None,
                                            "PanVerticalDistanceTimeGradient": None,                              

                                            # Time it takes to pan the camera from the current camera position to the new position
                                            "PanTime": 3000, # This must be less than the spawning timer of the boss
                                            "PanTimer": None,
                                            
                                            # The time the camera locks onto the boss for after panning from the player to the boss
                                            "BossPanLockTime": 4000,
                                            "BossPanLockTimer": None,
                                            
                                            # The time the camera locks onto the player for after panning from the boss back to the player
                                            "PlayerPanLockTime": 1000, 
                                            "PlayerPanLockTimer": None,

                                            # Boolean variable used to track whether the camera has finished panning to the boss, locking in for a short period of time and started panning back to the player
                                            "BossPanComplete": False, 

                                            # Used to store the changing camera position for floating point accuracy
                                            "NewCameraPositionX": None,
                                            "NewCameraPositionY": None,
                                            }

        # A dictionary containing information to do with the camera / screen shake
        self.camera_shake_info_dict = {
                                        "EventsList": [],

                                        # Timers
                                        "BossTileCollideTimer": None,
                                        "BossTileCollideTime": 800,

                                        "StompTimer": None,
                                        "StompTime": 100,

                                    }

        # --------------------------------------------------------------------------------------
        # Groups
        self.world_tiles_dict = {} # Dictionary used to hold all the world tiles 
        self.world_tiles_group = pygame_sprite_Group()
        # self.player_group = pygame_sprite_GroupSingle(self.player) This was created inside the create_objects_tile_map method
        self.bamboo_projectiles_group = pygame_sprite_Group() # Group for all bamboo projectiles for the player
        self.empty_tiles_dict = {} # Dictionary used to hold all of the empty tiles in the tile map
        self.bamboo_piles_group = pygame_sprite_Group()
        self.boss_group = pygame_sprite_GroupSingle()

        # --------------------------------------------------------------------------------------
        # Boss and player guidelines

        # Thickness of each segment
        self.guidelines_segments_thickness = 5

        # Surface
        self.guidelines_surface = pygame_Surface((self.scaled_surface.get_width(), self.scaled_surface.get_height()))
        self.guidelines_surface.set_colorkey("black")
        self.guidelines_surface_default_alpha_level = 105
        self.guidelines_surface.set_alpha(self.guidelines_surface_default_alpha_level)

        # ---------------------------------------------------------------------------------
        # Cursor images

        self.default_cursor_image = pygame_image_load("graphics/Cursors/Default.png").convert_alpha()
    # --------------------------------------------------------------------------------------
    # Camera methods

    def set_camera_mode(self, manual_camera_mode_setting = None):

        # Used to change the camera mode depending on the size of the tile map or changing the camera mode if a manual camera mode setting was passed in
        
        # If a manual camera mode setting has not been passed to this method
        if manual_camera_mode_setting == None:
            # If the width of the tile map is one room
            if self.last_tile_position[0] <= (self.scaled_surface.get_width() / 2):
                # Set the camera mode to "Static"
                self.camera_mode = "Static"
            
            # If the width of the tile map is more than one room
            else:
                # Set the camera mode to "Follow"
                self.camera_mode = "Follow"

        # If a manual camera mode setting has been passed to this method
        elif manual_camera_mode_setting != None:
            # Set the camera mode as the manual camera mode setting passed
            self.camera_mode = manual_camera_mode_setting
    
    def update_focus_subject(self):
        
        # If a boss has not been created or if a boss has been created and has been spawned
        if hasattr(self, "bosses_dict") == False or (hasattr(self, "bosses_dict") == True and self.bosses_dict["TimeToSpawnTimer"] == None):
            
            # If the player is currently alive
            if self.player.player_gameplay_info_dict["CurrentHealth"] > 0:
                # Return the center of the player (so that the camera follows the player)
                return (self.player.rect.centerx,  self.player.rect.centery)

        # If a boss has been created and is currently being spawned
        elif (hasattr(self, "bosses_dict") == True and self.bosses_dict["TimeToSpawnTimer"] != None) and self.camera_mode != "Pan":

            # Set the camera mode as "Pan"
            self.set_camera_mode(manual_camera_mode_setting = "Pan")
            
            # The position of the center of the screen, that the camera is following (i.e. the center of the camera)
            middle_camera_position = (self.camera_position[0] + (self.scaled_surface.get_width() / 2), self.camera_position[1] + (self.scaled_surface.get_height() / 2))
            
            # Calculate the horizontal and vertical distance time gradients for the panning movement
            # Note: TILE_SIZE / 2 so that the center of the camera is aligned with the center of the spawning tile
            self.camera_pan_information_dict["PanHorizontalDistanceTimeGradient"] = ((self.bosses_dict["ValidSpawningPosition"][0] + (TILE_SIZE / 2)) - middle_camera_position[0]) / (self.camera_pan_information_dict["PanTime"] / 1000)
            self.camera_pan_information_dict["PanVerticalDistanceTimeGradient"] = ((self.bosses_dict["ValidSpawningPosition"][1] + (TILE_SIZE / 2)) - middle_camera_position[1]) / (self.camera_pan_information_dict["PanTime"] / 1000)

            # Set the new camera position X and Y to be the current camera position
            self.camera_pan_information_dict["NewCameraPositionX"] = self.camera_position[0]
            self.camera_pan_information_dict["NewCameraPositionY"] = self.camera_position[1]

            # Set the pan timer to start counting down
            self.camera_pan_information_dict["PanTimer"] = self.camera_pan_information_dict["PanTime"]

            # Don't allow the player to perform actions
            self.player.player_gameplay_info_dict["CanStartOperating"] = False

            # Return None (as nothing is required)
            return None

    def update_camera_position(self, delta_time, focus_subject_center_pos):   
        
        # Moves the camera's position depending on what mode the camera has been set as and according to who the focus subject is (i.e. the boss, the player, etc.)
        
        # If the camera mode is set to "Follow"
        if self.camera_mode == "Follow":
            
            # --------------------------------------------------------------------------------------
            # Adjusting camera x position

            # If the player is in half the width of the scaled screen from the first tile in the tile map
            if 0 <= focus_subject_center_pos[0] <= (self.scaled_surface.get_width() / 2):
                # Don't move the camera
                camera_position_x = 0

            # If the player is in between half of the size of the scaled screen width from the first tile in the tile map and half the width of the scaled screen from the last tile in the tile map
            elif 0 + (self.scaled_surface.get_width() / 2) < focus_subject_center_pos[0] < self.last_tile_position[0] - (self.scaled_surface.get_width() / 2):
                # Set the camera to always follow the player
                camera_position_x = focus_subject_center_pos[0] - (self.scaled_surface.get_width() / 2)

            # If the player is half the scaled screen width away from the last tile in the tile maps
            elif focus_subject_center_pos[0] >= self.last_tile_position[0] - (self.scaled_surface.get_width() / 2):
                # Set the camera to stop moving and be locked at half the size of the scaled screen width from the last tile in the tile map
                camera_position_x = self.last_tile_position[0] - self.scaled_surface.get_width() 

            # --------------------------------------------------------------------------------------
            # Adjusting camera y position

            # If the player is in half the height of the scaled screen from the first tile in the tile map
            if 0 <= focus_subject_center_pos[1] <= (self.scaled_surface.get_height() / 2):
                # Don't move the camera
                camera_position_y = 0

            # If the player is in between half of the size of the scaled screen height from the first tile in the tile map and half the width of the scaled screen from the last tile in the tile map
            elif 0 + (self.scaled_surface.get_height() / 2) <= focus_subject_center_pos[1] <= self.last_tile_position[1] - (self.scaled_surface.get_height() / 2):
                # Set the camera to always follow the player
                camera_position_y = focus_subject_center_pos[1] - (self.scaled_surface.get_height() / 2)

            # If the player is half the scaled screen width away from the last tile in the tile maps
            elif focus_subject_center_pos[1] >= self.last_tile_position[1] - (self.scaled_surface.get_height() / 2):
                # Set the camera to stop moving and be locked at half the size of the scaled screen width from the last tile in the tile map
                camera_position_y = self.last_tile_position[1] - self.scaled_surface.get_height()     

        # If the camera mode is set to "Static"
        elif self.camera_mode == "Static":
            # The camera's x position will always be at 0
            camera_position_x = 0

        # If the camera mode is set to "Pan" (will pan towards a specific location)
        elif self.camera_mode == "Pan":

            # If there has been a timer set for pan timer
            if self.camera_pan_information_dict["PanTimer"] != None:

                # ------------------------------------------------------------------------------
                # Moving the camera
                
                # Increase the new camera position x and y (Floating point accuracy)
                self.camera_pan_information_dict["NewCameraPositionX"] += self.camera_pan_information_dict["PanHorizontalDistanceTimeGradient"] * delta_time
                self.camera_pan_information_dict["NewCameraPositionY"] += self.camera_pan_information_dict["PanVerticalDistanceTimeGradient"] * delta_time

                # Set the camera position as the rounded values
                camera_position_x = round(self.camera_pan_information_dict["NewCameraPositionX"])
                camera_position_y = round(self.camera_pan_information_dict["NewCameraPositionY"])

                # ------------------------------------------------------------------------------
                # Updating the pan timer

                # If the timer has not finished counting
                if self.camera_pan_information_dict["PanTimer"] > 0:
                    # Decrease the timer
                    self.camera_pan_information_dict["PanTimer"] -= 1000 * delta_time
                
                # If the timer has finished counting
                if self.camera_pan_information_dict["PanTimer"] <= 0:
                    # Set the pan timer back to None
                    self.camera_pan_information_dict["PanTimer"] = None

                    # If the camera has finished going from the boss to the player but the camera has not locked onto the player for a short period of time yet
                    if self.camera_pan_information_dict["BossPanComplete"] == True and self.camera_pan_information_dict["PlayerPanLockTimer"] == None:
                        # Set the camera to lock onto the player for a short period of time
                        self.camera_pan_information_dict["PlayerPanLockTimer"] = self.camera_pan_information_dict["PlayerPanLockTime"] 

            # If there has not been a timer set for pan timer
            elif self.camera_pan_information_dict["PanTimer"] == None:

                # Keep the camera the same
                camera_position_x = round(self.camera_pan_information_dict["NewCameraPositionX"])
                camera_position_y = round(self.camera_pan_information_dict["NewCameraPositionY"])

                # -------------------------------------
                # If the boss has finished spawning and and the camera has finished panning to the boss but still needs to lock in for a short period of time

                if self.bosses_dict["TimeToSpawnTimer"] == None and self.camera_pan_information_dict["BossPanLockTimer"] == None:
                    # Set the boss pan lock timer to start
                    self.camera_pan_information_dict["BossPanLockTimer"] = self.camera_pan_information_dict["BossPanLockTime"]

                # ------------------------------------------------------------------------------
                # Updating the boss pan lock timer

                # If a boss pan lock timer has been set (Locks on the boss for short period of time)
                if self.camera_pan_information_dict["BossPanLockTimer"] != None:

                    # If the timer has not finished counting
                    if self.camera_pan_information_dict["BossPanLockTimer"] > 0:
                        # Decrease the timer
                        self.camera_pan_information_dict["BossPanLockTimer"]-= 1000 * delta_time
                    
                    # If the timer has finished counting
                    if self.camera_pan_information_dict["BossPanLockTimer"] <= 0:
                        # Set the timer back to None
                        self.camera_pan_information_dict["BossPanLockTimer"] = None

                        # -----------------------------------------
                        # Set the camera to pan back to the player

                        # Invert the horizontal and vertical distance time gradients so that it pans back to the player
                        self.camera_pan_information_dict["PanHorizontalDistanceTimeGradient"] *= -1
                        self.camera_pan_information_dict["PanVerticalDistanceTimeGradient"] *= -1

                        # Set the camera to pan back to the player (start the pan timer to count down)
                        self.camera_pan_information_dict["PanTimer"] = self.camera_pan_information_dict["PanTime"] 

                        # Set the boss pan to be complete so that once the pan timer has finished panning back to the player.
                        self.camera_pan_information_dict["BossPanComplete"] = True
                
                # -------------------------------------
                # Updating the player pan lock timer

                # If the camera has finished panning back to the player but still needs to lock in for a short period of time (THE FINAL STEP)

                # If a timer has been set to lock on the player for a short period of time
                if self.camera_pan_information_dict["PlayerPanLockTimer"] != None:

                    # If the timer has not finished counting
                    if self.camera_pan_information_dict["PlayerPanLockTimer"] > 0:
                        # Decrease the timer
                        self.camera_pan_information_dict["PlayerPanLockTimer"] -= 1000 * delta_time
                    
                    # If the timer has finished counting
                    if self.camera_pan_information_dict["PlayerPanLockTimer"] <= 0:

                        # Set the timer back to None
                        self.camera_pan_information_dict["PlayerPanLockTimer"] = None

                        # Set the camera mode back to Follow
                        self.set_camera_mode("Follow")

                        # Allow the boss to start operating (i.e, moving and performing actions)
                        self.boss_group.sprite.extra_information_dict["CanStartOperating"] = True

                        # Allow the player to start operating (i.e, moving and performing actions)
                        self.player.player_gameplay_info_dict["CanStartOperating"] = True

        # --------------------------------------------------------------------------------------------------------------
        # Update the camera position
        """
        - The camera's x position:
            - Starts at 0 until the focus subject reaches half the size of the scaled screen width
            - Once the focus subject reaches the center of the screen, then the camera will always follow the focus subject
            - Until the focus subject reaches half the size of the scaled screen width from the last tile in the tile map

        - The camera's y position:
            - Starts at 0 until the focus subject reaches half the size of the scaled screen height
            - Once the focus subject reaches the center of the screen, then the camera will always follow the focus subject
            - Until the focus subject reaches half the size of the scaled screen height from the last tile in the tile map
        """

        # Assign the camera position
        self.camera_position = [camera_position_x, camera_position_y]

        # Perform screen / camera shake if the conditions are met
        self.camera_position = self.shake_camera(camera_position_to_change = self.camera_position, delta_time = delta_time)

        # Update the player's camera position attribute so that tile rects are correctly aligned
        self.player.camera_position = self.camera_position
    
    def shake_camera(self, camera_position_to_change, delta_time):
        
        # Sets the timers for each camera shake event and performs the camera shake
        
        # If there are no camera shake events
        if len(self.camera_shake_info_dict["EventsList"]) == 0:
            # Return the original camera position
            return camera_position_to_change
    
        # If there are any camera shake events
        elif len(self.camera_shake_info_dict["EventsList"]) > 0:

            # ---------------------------------------------------------------------------------------
            # Setting the timers if there are any camera shake events and no timers have been activated
            
            # If all the camera shake events' timers are None (i.e. there is no camera shake to be performed currently)
            if self.camera_shake_info_dict["BossTileCollideTimer"] == None and self.camera_shake_info_dict["StompTimer"] == None:

                # Identify what this camera shake is for and start the timer for the screenshake
                match self.camera_shake_info_dict["EventsList"][0]:

                    # ------------------------------------------------------
                    # Sika Deer boss
                    
                    # The boss collided with a world tile or a building tile
                    case "BossTileCollide":
                        # Set the timer for the boss tile collide screen shake to start
                        self.camera_shake_info_dict["BossTileCollideTimer"] = self.camera_shake_info_dict["BossTileCollideTime"]

                    case "Stomp":
                        # Set the timer for the stomp screen shake to start
                        self.camera_shake_info_dict["StompTimer"] = self.camera_shake_info_dict["StompTime"]

            # ---------------------------------------------------------------------------------------
            # Performing the screen shake and removing events if their timer has finished counting down
        
            # Boss and tile timer:
            if self.camera_shake_info_dict["BossTileCollideTimer"] != None:
                
                # If the timer has not finished counting down
                if self.camera_shake_info_dict["BossTileCollideTimer"] > 0:

                    # Calculate a dampening factor which is dependent on how much time is left before we stop shaking the camera
                    dampening_factor = self.camera_shake_info_dict["BossTileCollideTimer"] / self.camera_shake_info_dict["BossTileCollideTime"]

                    # How impactful the screen shake should be
                    shake_magnitude = 3.5

                    # Set the camera shake for the x and y axis depending on the movement of the boss during the charge
                    # random_uniform is for a random float number between a given range
                    camera_shake_x = random_uniform(-abs(self.boss_group.sprite.movement_information_dict["HorizontalSuvatS"] * shake_magnitude), abs(self.boss_group.sprite.movement_information_dict["HorizontalSuvatS"] * shake_magnitude)) * dampening_factor
                    camera_shake_y = random_uniform(-abs(self.boss_group.sprite.movement_information_dict["VerticalSuvatS"] * shake_magnitude), abs(self.boss_group.sprite.movement_information_dict["VerticalSuvatS"] * shake_magnitude)) * dampening_factor

                    # Adjust the camera position by the camera shake amounts
                    camera_position_to_change[0] += camera_shake_x
                    camera_position_to_change[1] += camera_shake_y

                    # Decrease the timer
                    self.camera_shake_info_dict["BossTileCollideTimer"] -= 1000 * delta_time

                # If the timer has finished counting down 
                if self.camera_shake_info_dict["BossTileCollideTimer"] <= 0:
                    # Remove the event from the camera shake events list
                    self.camera_shake_info_dict["EventsList"].pop()

                    # Set the timer back to None
                    self.camera_shake_info_dict["BossTileCollideTimer"] = None

            # Deer boss stomp timer
            if self.camera_shake_info_dict["StompTimer"] != None:
                
                # If the timer has not finished counting down
                if self.camera_shake_info_dict["StompTimer"] > 0:
                    # Adjust the camera position by the camera shake amounts
                    camera_position_to_change[0] += random_uniform(-1.75, 1.75)
                    camera_position_to_change[1] += random_uniform(-1.75, 1.75)

                    # Decrease the timer
                    self.camera_shake_info_dict["StompTimer"] -= 1000 * delta_time

                # If the timer has finished counting down 
                if self.camera_shake_info_dict["StompTimer"] <= 0:
                    # Remove the event from the camera shake events list
                    # random_uniform is for a random float number between a given range
                    self.camera_shake_info_dict["EventsList"].pop()

                    # Set the timer back to None
                    self.camera_shake_info_dict["StompTimer"] = None

            # Return the new camera position after shaking
            return camera_position_to_change

    # --------------------------------------------------------------------------------------
    # Tile map methods

    def load_tile_map_images(self):

        # Loads the images of all the world tiles

        # Create a dictionary filled with all of the tiles' images
        # Note: Start at index 1 because the "0" tile represents nothing. 
        self.tile_images = {i + 1: pygame_image_load(f"graphics/Tiles/{i + 1}.png").convert() for i in range(0, len(os_listdir("graphics/Tiles")))} 

    def create_objects_tile_map(self, non_transformed_tile_map):

        # Creates the objects tile map
        # Note: The objects tile map is created by the gamestates controller within the load_level method

        # For all rows of objects in the tile map
        for row_index, row in enumerate(non_transformed_tile_map):
            # For each item in each row
            for column_index, tile_map_object in enumerate(row):

                # Identify the tile map object
                match tile_map_object:
                    
                    # Empty tiles
                    case 0:
                        # Add the empty tile to the empty tiles dictionary (For player building and changing tiles, etc.)
                        self.empty_tiles_dict[((column_index * TILE_SIZE), (row_index * TILE_SIZE), TILE_SIZE, TILE_SIZE)] = 0

                    # Player
                    case 1:
                        # Create the player
                        self.player = Player(
                                            x = (column_index * TILE_SIZE), 
                                            y = (row_index * TILE_SIZE), 
                                            surface = self.scaled_surface, 
                                            sprite_groups = {"WorldTiles": self.world_tiles_group, "BambooProjectiles": self.bamboo_projectiles_group}
                                            )

                        # Add the player to its group
                        self.player_group = pygame_sprite_GroupSingle(self.player)


                    # World tile 1
                    case 2:
                        # Create a world tile
                        world_tile = WorldTile(x = (column_index * TILE_SIZE), y = (row_index * TILE_SIZE), image = pygame_transform_smoothscale(self.tile_images[1], (TILE_SIZE, TILE_SIZE)))

                        # Add the world tile to the world tiles dictionary
                        # The key is the world tile because we use pygame.rect.collidedict in other areas of the code, the value is the type of world tile (The other type is building tiles)
                        self.world_tiles_dict[world_tile] = "WorldTile"

                        # Add it to the group of world tiles (For collisions with other objects, excluding the player)
                        self.world_tiles_group.add(world_tile)


        # Save the last tile position so that we can update the camera and limit the player's movement
        self.last_tile_position = [len(non_transformed_tile_map[0]) * TILE_SIZE, len(non_transformed_tile_map) * TILE_SIZE]
        self.player.last_tile_position = self.last_tile_position

        # Save a copy of the world tiles dict for the player, this is for updating the world tiles dict when building tiles are created.
        self.player.world_tiles_dict = self.world_tiles_dict

        # Save a copy of the empty tiles dict for the player, allowing the player to see which tiles can be replaced with building tiles
        self.player.empty_tiles_dict = self.empty_tiles_dict

        # Set the camera mode 
        self.set_camera_mode()

        # Create the game UI
        self.game_ui = GameUI(
                            surface = self.scaled_surface, 
                            scale_multiplier = self.scale_multiplier, 
                            player_tools = self.player.tools, 
                            player_gameplay_info_dict = self.player.player_gameplay_info_dict,
                            camera_pan_information_dict = self.camera_pan_information_dict
                            )

    def draw_tile_map_objects(self):

        # Calls the draw methods of all objects in the level

        # ---------------------------------------------
        # World tiles and building tiles

        for tile in self.world_tiles_dict.keys():

            # If the tile object is within view of the camera (i.e. on the screen)
            if self.camera_position[0] - TILE_SIZE <= tile.rect.x <= (self.camera_position[0] + (self.scaled_surface.get_width())) + TILE_SIZE and \
                self.camera_position[1] - TILE_SIZE <= tile.rect.y <= (self.camera_position[1] + (self.scaled_surface.get_height())) + TILE_SIZE:
                
                # Draw the world / building tile onto the screen
                tile.draw(surface = self.scaled_surface, x = (tile.rect.x - self.camera_position[0]), y = (tile.rect.y - self.camera_position[1]))         

        # ---------------------------------------------
        # Bamboo projectiles

        for bamboo_projectile in self.bamboo_projectiles_group:
            # Draw the bamboo projectile 
            # pygame_draw_rect(self.scaled_surface, "white", (bamboo_projectile.rect.x - self.camera_position[0], bamboo_projectile.rect.y - self.camera_position[1], bamboo_projectile.rect.width, bamboo_projectile.rect.height), 0)
            bamboo_projectile.draw(surface = self.scaled_surface, x = bamboo_projectile.rect.x - self.camera_position[0], y = bamboo_projectile.rect.y - self.camera_position[1])
       
        # ---------------------------------------------
        # Bamboo piles

        for bamboo_pile in self.bamboo_piles_group:
            # Draw the bamboo pile
            bamboo_pile.draw(surface = self.scaled_surface, x = bamboo_pile.rect.x - self.camera_position[0], y = bamboo_pile.rect.y - self.camera_position[1])

    # --------------------------------------------------------------------------------------
    # Gameplay methods

    def find_neighbouring_tiles(self):

        # Used to find the closest tiles to the player to check for collisions (Used for greater performance, as we are only checking for collisions with tiles near the player)

        # Grid lines to show neighbouring tiles
        # pygame.draw.line(self.scaled_surface, "white", (0 - self.camera_position[0], self.player.rect.top - self.camera_position[1]), (screen_width, self.player.rect.top - self.camera_position[1]))
        # pygame.draw.line(self.scaled_surface, "white", (0 - self.camera_position[0], self.player.rect.bottom - self.camera_position[1]), (screen_width, self.player.rect.bottom - self.camera_position[1]))

        # pygame.draw.line(self.scaled_surface, "red", (0 - self.camera_position[0], (self.player.rect.top - TILE_SIZE * 1) - self.camera_position[1]), (screen_width, (self.player.rect.top - TILE_SIZE * 1) - self.camera_position[1]))
        # pygame.draw.line(self.scaled_surface, "red", (0 - self.camera_position[0], (self.player.rect.bottom + TILE_SIZE * 1) - self.camera_position[1]), (screen_width, (self.player.rect.bottom + TILE_SIZE * 1) - self.camera_position[1]))

        # pygame.draw.line(self.scaled_surface, "pink", ((self.player.rect.left - TILE_SIZE) * 1 - self.camera_position[0], 0 - self.camera_position[1]), ((self.player.rect.left - TILE_SIZE) * 1 - self.camera_position[0], screen_height))
        # pygame.draw.line(self.scaled_surface, "pink", ((self.player.rect.right + TILE_SIZE) * 1 - self.camera_position[0], 0 - self.camera_position[1]), ((self.player.rect.right + TILE_SIZE) * 1 - self.camera_position[0], screen_height))

        # For each tile in the world tiles dictionary (Can be a building tile or a world tile)
        for tile in self.world_tiles_dict.keys():


            # ------------------------------------------------------------------------
            # Player

            # If the tile is within 2 tiles of the player (horizontally and vertically)
            if (self.player.rect.left  - (TILE_SIZE * 2) <= tile.rect.centerx <= self.player.rect.right + (TILE_SIZE * 2)) and (self.player.rect.top - (TILE_SIZE * 2) <= tile.rect.centery <= (self.player.rect.bottom + TILE_SIZE * 2)):
                # Add it to the player's neighbouring tiles dictionary
                self.player.neighbouring_tiles_dict[tile] = 0 

            # If the tile is not within 2 tiles of the player (horizontally and vertically)
            else:
                # If the tile is inside the player's neighbouring tiles dict's keys
                if tile in self.player.neighbouring_tiles_dict.keys():
                    # Remove the world/ building tile from the player's neighbouring tiles dictionary
                    self.player.neighbouring_tiles_dict.pop(tile)
                    
            # ------------------------------------------------------------------------
            # Bosses

            # If there is a current boss that has been spawned
            if self.boss_group.sprite != None:

                # If the tile is within 2 tiles of the current boss (horizontally and vertically)
                if (self.boss_group.sprite.rect.left  - (TILE_SIZE * 3) <= tile.rect.centerx <= self.boss_group.sprite.rect.right + (TILE_SIZE * 3)) and (self.boss_group.sprite.rect.top - (TILE_SIZE * 3) <= tile.rect.centery <= (self.boss_group.sprite.rect.bottom + TILE_SIZE * 3)):
                    
                    if self.world_tiles_dict[tile] != "BuildingTile":
                        # Add it to the current boss' neighbouring tiles dictionary
                        self.boss_group.sprite.neighbouring_tiles_dict[tile] = 0 
                # If the tile is not within 2 tiles of the current boss (horizontally and vertically)
                else:
                    # If the tile is inside the current boss' neighbouring tiles dict's keys
                    if tile in self.boss_group.sprite.neighbouring_tiles_dict.keys():
                        # Remove the world/ building tile from the current boss' neighbouring tiles dictionary
                        self.boss_group.sprite.neighbouring_tiles_dict.pop(tile)
                        
    def handle_collisions(self):

        # Handles collisions between objects (including the player). Collisions between the world tiles and the player are within the Player class.

        # --------------------------------------------------------------------------------------
        # Bamboo projectiles 

        
        # Look for collisions between bamboo projectiles and world tiles, delete the bamboo projectile if there is a collision
        if len(self.bamboo_projectiles_group) > 0:

            # For each bamboo projectile 
            for bamboo_projectile in self.bamboo_projectiles_group:

                # --------------------------------
                # World / building tiles

                # Look for tile collisions between the bamboo projectile and world/ building tiles
                self.look_for_world_tile_collisions(item = bamboo_projectile, other_group = self.bamboo_projectiles_group)

                # --------------------------------
                # Bosses

                # If a boss has been spawned
                if self.boss_group.sprite != None: # hasattr(self, "bosses_dict") and self.bosses_dict[self.bosses_dict["CurrentBoss"]] != None:

                    # If the bamboo projectile's rect has collided with the current boss' rect
                    if bamboo_projectile.rect.colliderect(self.bosses_dict[self.bosses_dict["CurrentBoss"]].rect) == True:
                        
                        # Check for a pixel-perfect collision between the bamboo projectile and the current boss
                        if pygame_sprite_collide_mask(bamboo_projectile, self.bosses_dict[self.bosses_dict["CurrentBoss"]]) != None:
                            # If there is a pixel-perfect collision:

                            # Damage the current boss by the amount of damage that was passed into the bamboo projectile and a random additive damage amount (e.g. 25 - 3)
                            # Note: This allows for different damage values for e.g. different weapons
                            
                            randomised_damage_amount = bamboo_projectile.damage_amount + random_randrange(-3, 3)
                            self.bosses_dict[self.bosses_dict["CurrentBoss"]].extra_information_dict["CurrentHealth"] -= randomised_damage_amount

                            # Play the boss' damaged flash effect
                            self.bosses_dict[self.bosses_dict["CurrentBoss"]].extra_information_dict["DamagedFlashEffectTimer"] = self.bosses_dict[self.bosses_dict["CurrentBoss"]].extra_information_dict["DamagedFlashEffectTime"]

                            # If the player's frenzy mode is not activated
                            if self.player.player_gameplay_info_dict["FrenzyModeTimer"] == None:
                                # Increase the player's frenzy mode meter by the deal damage increment amount, limiting it to the maximum frenzy mode value
                                self.player.player_gameplay_info_dict["CurrentFrenzyModeValue"] = min(
                                                                                                    self.player.player_gameplay_info_dict["CurrentFrenzyModeValue"] + self.player.player_gameplay_info_dict["DealDamageFrenzyModeIncrement"],
                                                                                                    self.player.player_gameplay_info_dict["MaximumFrenzyModeValue"]
                                                                                                    )
                            # If the current boss is alive
                            if self.boss_group.sprite.extra_information_dict["CurrentHealth"] > 0:

                                # Create damage effect text
                                self.game_ui.create_effect_text(
                                                                type_of_effect_text = "Damage",
                                                                target = "Boss",
                                                                text = "-" + str(randomised_damage_amount),
                                                                )

                            # Create a few shattered bamboo pieces
                            self.game_ui.create_angled_polygons_effects(
                                                                        purpose = "ShatteredBambooPieces",
                                                                        position = (self.boss_group.sprite.rect.centerx, self.boss_group.sprite.rect.centery),
                                                                        angle = bamboo_projectile.angle,
                                                                        specified_number_of_pieces = random_randrange(2, 6)
                                                                        )

                            # Remove the bamboo projectile
                            self.bamboo_projectiles_group.remove(bamboo_projectile)

        # --------------------------------------------------------------------------------------
        # Bamboo piles

        # Look for collisions between the player and bamboo piles, and only delete the bamboo pile if there is a collision and the player does not currently have the maximum amount of bamboo resource
        player_and_bamboo_piles_collision_list = pygame_sprite_spritecollide(self.player, self.bamboo_piles_group, dokill = False, collided = pygame_sprite_collide_rect)
        if len(player_and_bamboo_piles_collision_list) > 0 and \
            ((self.player.player_gameplay_info_dict["AmountOfBambooResource"] != self.player.player_gameplay_info_dict["MaximumAmountOfBambooResource"]) or (self.player.player_gameplay_info_dict["CurrentHealth"] != self.player.player_gameplay_info_dict["MaximumHealth"])):
            
            # Remove the bamboo pile from the bamboo piles group
            self.bamboo_piles_group.remove(player_and_bamboo_piles_collision_list)

            # Add the empty tile back to the empty tiles dictionary so other items can spawn in the tile
            self.empty_tiles_dict[(player_and_bamboo_piles_collision_list[0].rect.x, player_and_bamboo_piles_collision_list[0].rect.y, player_and_bamboo_piles_collision_list[0].rect.width, player_and_bamboo_piles_collision_list[0].rect.height)] = 0

            # If adding the bamboo pile's replenishment amount exceeds the player's maximum amount of bamboo resource
            if self.player.player_gameplay_info_dict["AmountOfBambooResource"] + BambooPile.bamboo_pile_info_dict["BambooResourceReplenishAmount"] > self.player.player_gameplay_info_dict["MaximumAmountOfBambooResource"]:
                # Find the amount that we can replenish the player's amount of bamboo resource to the maximum amount
                bamboo_resource_replenishment_amount = BambooPile.bamboo_pile_info_dict["BambooResourceReplenishAmount"] - (
                    (self.player.player_gameplay_info_dict["AmountOfBambooResource"] + BambooPile.bamboo_pile_info_dict["BambooResourceReplenishAmount"]) % self.player.player_gameplay_info_dict["MaximumAmountOfBambooResource"])
            
            # If adding the bamboo pile's replenishment amount is less than or equal to the player's maximum amount of bamboo resource
            elif self.player.player_gameplay_info_dict["AmountOfBambooResource"] + BambooPile.bamboo_pile_info_dict["BambooResourceReplenishAmount"] <= self.player.player_gameplay_info_dict["MaximumAmountOfBambooResource"]:
                # Set the health replenishment amount as the bamboo pile's full resource replenishment amount
                bamboo_resource_replenishment_amount = BambooPile.bamboo_pile_info_dict["BambooResourceReplenishAmount"]
            
            # Create bamboo resource replenishment effect text
            self.game_ui.create_effect_text(
                                            type_of_effect_text = "BambooResourceReplenishment",
                                            target = "Player",
                                            text = "+" + str(bamboo_resource_replenishment_amount),
                                        )

            # Increase the amount of bamboo resource that the player has, limiting it to the maximum amount the player can hold at one time
            self.player.player_gameplay_info_dict["AmountOfBambooResource"] += bamboo_resource_replenishment_amount

            # 75% chance of increasing the player's current health
            if random_randrange(0, 100) <= 75:

                # If adding the bamboo pile's health replenishment amount exceeds the player's health
                if self.player.player_gameplay_info_dict["CurrentHealth"] + BambooPile.bamboo_pile_info_dict["HealthReplenishmentAmount"] > self.player.player_gameplay_info_dict["MaximumHealth"]:
                    # Find the amount that we can heal the player up to their maximum health
                    health_replenishment_amount = BambooPile.bamboo_pile_info_dict["HealthReplenishmentAmount"] - (
                        (self.player.player_gameplay_info_dict["CurrentHealth"] + BambooPile.bamboo_pile_info_dict["HealthReplenishmentAmount"]) % self.player.player_gameplay_info_dict["MaximumHealth"])
                
                # If adding the bamboo pile's health replenishment amount is less than or equal to the player's health 
                elif self.player.player_gameplay_info_dict["CurrentHealth"] + BambooPile.bamboo_pile_info_dict["HealthReplenishmentAmount"] <= self.player.player_gameplay_info_dict["MaximumHealth"]:
                    # Set the health replenishment amount as the bamboo pile's full health replenishment amount
                    health_replenishment_amount = BambooPile.bamboo_pile_info_dict["HealthReplenishmentAmount"]

                # If the player is alive / has more than 0 health
                if self.player.player_gameplay_info_dict["CurrentHealth"] > 0:
                    # Create heal effect text
                    self.game_ui.create_effect_text(
                                                    type_of_effect_text = "Heal",
                                                    target = "Player",
                                                    text = "+" + str(health_replenishment_amount),
                                                )


                # Increase the player's current health, limiting it to the maximum health the player can have
                self.player.player_gameplay_info_dict["CurrentHealth"] += health_replenishment_amount

        # --------------------------------------------------------------------------------------
        # Stomp attack nodes

        # Additional check because this group does note exist until the Sika Deer boss has spawned and started stomping
        if hasattr(self, "stomp_attack_nodes_group") and len(self.stomp_attack_nodes_group) > 0:

            # For each stomp attack node
            for stomp_attack_node in self.stomp_attack_nodes_group:

                # --------------------------------
                # World / building tiles

                # Look for tile rect collisions between the stomp attack nodes and world / building tiles
                collision_result = stomp_attack_node.rect.collidedict(self.world_tiles_dict)

                # Look for tile rect collisions between the stomp attack nodes and world / building tiles
                if collision_result != None:
                    
                    # --------------------------------
                    # Building tiles

                    # If the stomp attack node image is not the same as the diameter of the attack node 
                    """ Note: This is here instead of inside the stomp attack node's increase_size method to avoid resizing the image everytime the attack node's size is changed
                    - The rect has already been adjusted according to the changed radius
                    """
                    if stomp_attack_node.image.get_width() != (stomp_attack_node.radius * 2):
                        # Rescale the image for pixel-perfect collision
                        stomp_attack_node.rescale_image()
                    
                    # Check for a pixel-perfect collision between the stomp attack node and the building tile
                    if pygame_sprite_collide_mask(stomp_attack_node, collision_result[0]) != None:
                        
                        # If the stomp attack node was blocked by a building tile
                        if collision_result[1] == "BuildingTile":
                            
                            # If the stomp attack node has not been reflected already
                            # Note: This is so that it does not bounce backwards and forwards when inside a tile
                            if stomp_attack_node.reflected != True:
                                # Reflect the stomp attack node, increasing its speed by 1.75
                                stomp_attack_node.horizontal_gradient *= -1.75 
                                stomp_attack_node.vertical_gradient *= -1.75
                                stomp_attack_node.reflected = True

                            # Take one life away from the building tile
                            collision_result[0].lives -= 1

                            # If the building tile has run out of lives
                            if collision_result[0].lives <= 0:

                                # Remove the building tile from the world tiles group
                                self.world_tiles_group.remove(collision_result[0])

                                # Remove the building tile from the world tiles dictionary
                                self.world_tiles_dict.pop(collision_result[0])

                                # "Create" an empty tile where the building tile was
                                self.empty_tiles_dict[(collision_result[0].rect.x, collision_result[0].rect.y, collision_result[0].rect.width, collision_result[0].rect.height)] = len(self.empty_tiles_dict)

                                # Remove the building tile from the existing building tiles list
                                self.player.tools["BuildingTool"]["ExistingBuildingTilesList"].remove(collision_result[0])

                                # If the building tile to remove is in the neighbouring tiles dictionary (keys)
                                if collision_result[0] in self.player.neighbouring_tiles_dict.keys():
                                    # Remove the building tile
                                    self.player.neighbouring_tiles_dict.pop(collision_result[0])

                                # Create many shattered bamboo pieces
                                self.game_ui.create_angled_polygons_effects(
                                                                            purpose = "ShatteredBambooPieces",
                                                                            position = (collision_result[0].rect.centerx, collision_result[0].rect.centery),
                                                                            specified_number_of_pieces = random_randrange(10, 20)
                                                                            )
                                                                            
                            # If the player's frenzy mode is not activated
                            if self.player.player_gameplay_info_dict["FrenzyModeTimer"] == None:
                                # Increase the player's frenzy mode meter by the block damage increment amount, limiting it to the maximum frenzy mode value
                                self.player.player_gameplay_info_dict["CurrentFrenzyModeValue"] = min(
                                                                                                    self.player.player_gameplay_info_dict["CurrentFrenzyModeValue"] + self.player.player_gameplay_info_dict["BlockDamageFrenzyModeIncrement"],
                                                                                                    self.player.player_gameplay_info_dict["MaximumFrenzyModeValue"]
                                                                                                )
                    # --------------------------------
                    # World tiles

                        # If the collided tile was a world tile
                        elif collision_result[1]  == "WorldTile":
                            # Remove the stomp attack node from the group if there is a collision
                            self.stomp_attack_nodes_group.remove(stomp_attack_node)
                    
                # --------------------------------
                # Player

                # Look for tile rect collisions between the stomp attack nodes and the player
                if stomp_attack_node.rect.colliderect(self.player.rect):
                    
                    # If the stomp attack node image is not the same as the diameter of the attack node 
                    """ Note: This is here instead of inside the stomp attack node's increase_size method to avoid resizing the image everytime the attack node's size is changed
                    - The rect has already been adjusted according to the changed radius
                    """
                    if stomp_attack_node.image.get_width() != (stomp_attack_node.radius * 2):
                        # Rescale the image for pixel-perfect collision
                        stomp_attack_node.rescale_image()

                    # Check for a pixel-perfect collision between the stomp attack node and the player
                    if pygame_sprite_collide_mask(stomp_attack_node, self.player) != None:

                        # Remove the stomp attack node from the group if there is a collision
                        self.stomp_attack_nodes_group.remove(stomp_attack_node)
                        
                        # Damage the player by the stomp attack node damage
                        self.player.player_gameplay_info_dict["CurrentHealth"] -= stomp_attack_node.damage_amount

                        # If the player is alive / has more than 0 health
                        if self.player.player_gameplay_info_dict["CurrentHealth"] > 0:
                            # Create damage effect text
                            self.game_ui.create_effect_text(
                                                            type_of_effect_text = "Damage",
                                                            target = "Player",
                                                            text = "-" + str(stomp_attack_node.damage_amount),
                                                        )
                                                        
                        # Set the damaged flash effect timer to the damage flash effect time set (damaged flashing effect)
                        self.player.player_gameplay_info_dict["DamagedFlashEffectTimer"] = self.player.player_gameplay_info_dict["DamagedFlashEffectTime"]

                        # If the player's frenzy mode is not activated
                        if self.player.player_gameplay_info_dict["FrenzyModeTimer"] == None:
                            # Increase the player's frenzy mode meter by the take damage increment amount, limiting it to the maximum frenzy mode value
                            self.player.player_gameplay_info_dict["CurrentFrenzyModeValue"] = min(
                                                                                                self.player.player_gameplay_info_dict["CurrentFrenzyModeValue"] + self.player.player_gameplay_info_dict["TakeDamageFrenzyModeIncrement"],
                                                                                                self.player.player_gameplay_info_dict["MaximumFrenzyModeValue"]
                                                                                                )
                
                # --------------------------------
                # Boss

                # Look for tile rect collisions between the stomp attack nodes and the current boss
                # Only enter if there is a rect collision and the stomp attack node was reflected
                if stomp_attack_node.rect.colliderect(self.bosses_dict[self.bosses_dict["CurrentBoss"]].rect) and stomp_attack_node.reflected == True:
                    
                    # If the stomp attack node image is not the same as the diameter of the attack node 
                    """ Note: This is here instead of inside the stomp attack node's increase_size method to avoid resizing the image everytime the attack node's size is changed
                    - The rect has already been adjusted according to the changed radius
                    """
                    if stomp_attack_node.image.get_width() != (stomp_attack_node.radius * 2):
                        # Rescale the image for pixel-perfect collision
                        stomp_attack_node.rescale_image()

                    # Check for a pixel-perfect collision between the bamboo projectile and the current boss
                    if pygame_sprite_collide_mask(stomp_attack_node, self.bosses_dict[self.bosses_dict["CurrentBoss"]]) != None:
                        
                        # Remove the stomp attack node from the group if there is a collision
                        self.stomp_attack_nodes_group.remove(stomp_attack_node)
                        
                        # Damage the boss by 5 times the stomp attack node damage
                        self.bosses_dict[self.bosses_dict["CurrentBoss"]].extra_information_dict["CurrentHealth"] -= (stomp_attack_node.damage_amount * self.player.tools["BuildingTool"]["ReflectionDamageMultiplier"])

                        # If the boss is alive / has more than 0 health
                        if self.boss_group.sprite.extra_information_dict["CurrentHealth"] > 0:
                            # Create damage effect text
                            self.game_ui.create_effect_text(
                                                            type_of_effect_text = "Damage",
                                                            target = "Boss",
                                                            text = "-" + str(stomp_attack_node.damage_amount * self.player.tools["BuildingTool"]["ReflectionDamageMultiplier"]),
                                                        )

                        # Set the damaged flash effect timer to the damage flash effect time set (damaged flashing effect)
                        self.bosses_dict[self.bosses_dict["CurrentBoss"]].extra_information_dict["DamagedFlashEffectTimer"] = self.bosses_dict[self.bosses_dict["CurrentBoss"]].extra_information_dict["DamagedFlashEffectTime"]

                        # If the player's frenzy mode is not activated
                        if self.player.player_gameplay_info_dict["FrenzyModeTimer"] == None:
                            # Increase the player's frenzy mode meter by the reflect damage increment amount, limiting it to the maximum frenzy mode value
                            self.player.player_gameplay_info_dict["CurrentFrenzyModeValue"] = min(
                                                                                                self.player.player_gameplay_info_dict["CurrentFrenzyModeValue"] + self.player.player_gameplay_info_dict["ReflectDamageFrenzyModeIncrement"],
                                                                                                self.player.player_gameplay_info_dict["MaximumFrenzyModeValue"]
                                                                                                )

        # -------------------------------------------------------------------------------------- 
        # Bosses

        # If there is a current boss and they are alive
        if self.boss_group.sprite != None and self.boss_group.sprite.extra_information_dict["CurrentHealth"] > 0:

            # --------------------------------------
            # Building tiles

            # If there is at least one existing building tile
            if (len(self.player.tools["BuildingTool"]["ExistingBuildingTilesList"]) > 0):
            
                # Find the index of the building tile in the existing building tiles list if there is a rect collision between the tile and the boss
                building_collision_result_index = self.boss_group.sprite.rect.collidelist(self.player.tools["BuildingTool"]["ExistingBuildingTilesList"])
                
                # If there is a collision
                if building_collision_result_index != -1:
                    
                    # Check for pixel-perfect collision between the boss and the building tile
                    if pygame_sprite_collide_mask(self.boss_group.sprite, self.player.tools["BuildingTool"]["ExistingBuildingTilesList"][building_collision_result_index]) != None:
                        
                        # Temporary variable for the building tile to remove
                        building_tile_to_remove = self.player.tools["BuildingTool"]["ExistingBuildingTilesList"][building_collision_result_index]

                        # Remove the building tile from the world tiles group
                        self.world_tiles_group.remove(building_tile_to_remove)

                        # Remove the building tile from the world tiles dictionary
                        self.world_tiles_dict.pop(building_tile_to_remove)

                        # "Create" an empty tile where the building tile was
                        self.empty_tiles_dict[(building_tile_to_remove.rect.x, building_tile_to_remove.rect.y, building_tile_to_remove.rect.width, building_tile_to_remove.rect.height)] = len(self.empty_tiles_dict)

                        # Remove the building tile from the existing building tiles list
                        self.player.tools["BuildingTool"]["ExistingBuildingTilesList"].pop(building_collision_result_index)

                        # If the building tile to remove is in the neighbouring tiles dictionary (keys)
                        if building_tile_to_remove in self.player.neighbouring_tiles_dict.keys():
                            # Remove the building tile
                            self.player.neighbouring_tiles_dict.pop(building_tile_to_remove)

                        # ------------------------------------------------------------------
                        # Additional effects
                        
                        # Create many shattered bamboo pieces
                        self.game_ui.create_angled_polygons_effects(
                                                                    purpose = "ShatteredBambooPieces",
                                                                    position = (building_tile_to_remove.rect.centerx, building_tile_to_remove.rect.centery),
                                                                    specified_number_of_pieces = random_randrange(10, 20)
                                                                    )

                        # If the boss is currently chasing the player
                        if self.boss_group.sprite.current_action == "Chase":
                            # Reset the boss' movement acceleration, so that they slow down
                            self.boss_group.sprite.reset_movement_acceleration(horizontal_reset = True, vertical_reset = True)

                        # If the boss is the "SikaDeer" and collided with the player whilst charge attacking
                        elif self.bosses_dict["CurrentBoss"] == "SikaDeer" and self.boss_group.sprite.current_action == "Charge":

                            # Reset the boss' movement acceleration, so that they slow down
                            self.boss_group.sprite.reset_movement_acceleration(horizontal_reset = True, vertical_reset = True)

                            # Set the player to change into the "Stunned" state (this will be done inside the SikaDeer class)
                            self.boss_group.sprite.behaviour_patterns_dict["Charge"]["EnterStunnedStateBoolean"] = True

                            # Set the "Charge" duration timer to 0, to end the charge attack
                            self.boss_group.sprite.behaviour_patterns_dict["Charge"]["DurationTimer"] = 0

                            # Set the "Stunned" duration timer to start counting down
                            self.boss_group.sprite.behaviour_patterns_dict["Stunned"]["DurationTimer"] = self.boss_group.sprite.behaviour_patterns_dict["Stunned"]["Duration"]

                            # Damage the current boss by the amount of damage dealt from being stunned
                            self.boss_group.sprite.extra_information_dict["CurrentHealth"] -= self.boss_group.sprite.behaviour_patterns_dict["Stunned"]["StunnedDamageAmount"]

                            # Create damage effect text
                            self.game_ui.create_effect_text(
                                                            type_of_effect_text = "Damage",
                                                            target = "Boss",
                                                            text = "-" + str(self.boss_group.sprite.behaviour_patterns_dict["Stunned"]["StunnedDamageAmount"]),
                                                            )
                                
                            # If the player's frenzy mode is not activated
                            if self.player.player_gameplay_info_dict["FrenzyModeTimer"] == None:
                                # Increase the player's frenzy mode meter by the stun enemy increment amount, limiting it to the maximum frenzy mode value
                                self.player.player_gameplay_info_dict["CurrentFrenzyModeValue"] = min(
                                                                                                    self.player.player_gameplay_info_dict["CurrentFrenzyModeValue"] + self.player.player_gameplay_info_dict["StunEnemyFrenzyModeIncrement"],
                                                                                                    self.player.player_gameplay_info_dict["MaximumFrenzyModeValue"]
                                                                                                    )

                            # Create a camera shake effect for when the boss collides with a tile
                            self.camera_shake_info_dict["EventsList"].append("BossTileCollide")

            # --------------------------------------
            # World tiles while charging

            # Only if the boss is the "SikaDeer"
            if self.bosses_dict["CurrentBoss"] == "SikaDeer" and self.boss_group.sprite.current_action == "Charge":
                    # If there is an x or y world tile collision
                    if self.boss_group.sprite.movement_information_dict["WorldTileCollisionResultsX"] == True or self.boss_group.sprite.movement_information_dict["WorldTileCollisionResultsY"] == True:
                        # Set the "Charge" duration timer to 0 (to end the charge attack)
                        self.boss_group.sprite.behaviour_patterns_dict["Charge"]["DurationTimer"] = 0

                        # Create a camera shake effect for when the boss collides with a tile
                        self.camera_shake_info_dict["EventsList"].append("BossTileCollide")

            # --------------------------------------
            # Player

            # If there is a rect collision between the player and the boss is not currently idling after the knockback and the boss is not currently stunned

            """ Checks:
            - If the boss collides with the player
            - If the boss is not idling after knocking back the player (so that the player doesn't keep setting off the idle timer in quick succession)
            - If the boss is not currently stunned 
            - If the player is not invincible (after getting knocked back recently)
            """
            if self.boss_group.sprite.rect.colliderect(self.player.rect) == True and \
                (self.boss_group.sprite.movement_information_dict["KnockbackCollisionIdleTimer"] == None) and \
                    self.boss_group.sprite.current_action != "Stunned" and \
                        self.player.player_gameplay_info_dict["InvincibilityTimer"] == None:

                # If there is pixel-perfect collision 
                if pygame_sprite_collide_mask(self.boss_group.sprite, self.player):

                    # Knockback the player
                    self.player.player_gameplay_info_dict["KnockbackAttackDirection"] = [self.boss_group.sprite.movement_information_dict["HorizontalSuvatS"], self.boss_group.sprite.movement_information_dict["VerticalSuvatS"]]
                    self.player.player_gameplay_info_dict["KnockbackTimer"] = self.player.player_gameplay_info_dict["KnockbackTime"]

                    # Set the horizontal and vertical distance the player should travel based on the angle the boss hit it
                    # Note: Divided by 1000 because the knockback time is in milliseconds
                    self.player.player_gameplay_info_dict["KnockbackHorizontalDistanceTimeGradient"] = (self.player.player_gameplay_info_dict["KnockbackDistanceTravelled"] * cos(self.boss_group.sprite.movement_information_dict["Angle"])) / (self.player.player_gameplay_info_dict["KnockbackTime"] / 1000)
                    self.player.player_gameplay_info_dict["KnockbackVerticalDistanceTimeGradient"] = (self.player.player_gameplay_info_dict["KnockbackDistanceTravelled"] * sin(self.boss_group.sprite.movement_information_dict["Angle"])) / (self.player.player_gameplay_info_dict["KnockbackTime"] / 1000)

                    # Set the player's invincibility timer to start counting down 
                    self.player.player_gameplay_info_dict["InvincibilityTimer"] = self.player.player_gameplay_info_dict["InvincibilityTime"]

                    # If the player is alive / has more than 0 health
                    if self.player.player_gameplay_info_dict["CurrentHealth"] > 0:
                        # Create damage effect text
                        self.game_ui.create_effect_text(
                                                        type_of_effect_text = "Damage",
                                                        target = "Player",
                                                        text = "-" + str(self.boss_group.sprite.extra_information_dict["KnockbackDamage"]),
                                                    )
                    
                    # If the boss is the "SikaDeer" and collided with the player whilst charge attacking
                    if self.bosses_dict["CurrentBoss"] == "SikaDeer" and self.boss_group.sprite.current_action == "Charge":
                        # Set the "Charge" duration timer to 0 (to end the charge attack)
                        self.boss_group.sprite.behaviour_patterns_dict["Charge"]["DurationTimer"] = 0

                    # Set the boss to stop moving momentarily
                    self.boss_group.sprite.movement_information_dict["KnockbackCollisionIdleTimer"] = self.boss_group.sprite.movement_information_dict["KnockbackCollisionIdleTime"]

                    # Reset the boss' movement acceleration
                    self.boss_group.sprite.reset_movement_acceleration(horizontal_reset = True, vertical_reset = True)

                    # Damage the player by the amount of knockback damage the current boss deals
                    self.player.player_gameplay_info_dict["CurrentHealth"] = max(self.player.player_gameplay_info_dict["CurrentHealth"] - self.boss_group.sprite.extra_information_dict["KnockbackDamage"], 0)
                
    def look_for_world_tile_collisions(self, item, other_group):
        
        # Helper method to find collisions between items in another specified group and world tiles
            
        # Check for a rect collision between the item and world / building tiles inside the world tiles dictionary
        collision_result = item.rect.collidedict(self.world_tiles_dict)

        # If the item collided with a tile
        if collision_result != None:

            # Check for a pixel-perfect collision between the item and the world tile that the item's rect collided with
            if pygame_sprite_collide_mask(item, collision_result[0]) != None:
                # If there is a pixel-perfect collision, remove the item from the specified group
                other_group.remove(item)
    
    def spawn_bamboo_pile(self, delta_time):

        # ----------------------------------------------------------------------------
        # Updating the spawning timer
        
        # If there is a timer that has been set to the spawning cooldown and there are less bamboo piles than the maximum amount at one time and the current boss has been spawned
        """ Note: The second check is so that once there are the maximum amount of piles at one time, the timer will only start counting when there are less than the maximum amount 
        - This avoids the issue where if the player walks over a bamboo pile after there were the maximum amount of piles, a new pile won't instantly spawn.
        """
        if BambooPile.bamboo_pile_info_dict["SpawningCooldownTimer"] != None and len(self.bamboo_piles_group) < BambooPile.bamboo_pile_info_dict["MaximumNumberOfPilesAtOneTime"] and \
            len(self.boss_group) > 0:
            
            # If the timer has finished counting down
            if BambooPile.bamboo_pile_info_dict["SpawningCooldownTimer"] <= 0:
                # Set the spawning cooldown timer back to None, allowing for a new bamboo pile to be spawned
                BambooPile.bamboo_pile_info_dict["SpawningCooldownTimer"] = None

            # If the timer has not finished counting down
            elif BambooPile.bamboo_pile_info_dict["SpawningCooldownTimer"] > 0:
                # Decrease the timer / count down from the timer
                BambooPile.bamboo_pile_info_dict["SpawningCooldownTimer"] -= 1000 * delta_time

        # ----------------------------------------------------------------------------
        # Spawning the bamboo pile

        # If there is no timer, spawn a bamboo pile
        elif BambooPile.bamboo_pile_info_dict["SpawningCooldownTimer"] == None:
            
            # Choose a random empty tile
            random_empty_tile = random_choice(list(self.empty_tiles_dict.keys()))
            
            # Center of the random empty tile
            random_empty_tile_center = (random_empty_tile[0] + (random_empty_tile[2] / 2), random_empty_tile[1] + (random_empty_tile[3] / 2))

            # If the empty tile's center is within the minimum and maximum spawning distance from the player and and there are less bamboo piles than the maximum number of bamboo piles that should be in the map at one time
            if BambooPile.bamboo_pile_info_dict["MinimumSpawningDistanceFromPlayer"] <= dist(self.player.rect.center, random_empty_tile_center) <= BambooPile.bamboo_pile_info_dict["MaximumSpawningDistanceFromPlayer"] and \
                len(self.bamboo_piles_group) < BambooPile.bamboo_pile_info_dict["MaximumNumberOfPilesAtOneTime"]:

                    # Remove the empty tile from the empty tiles dictionary (so that another item does not spawn in the same tile)
                    self.empty_tiles_dict.pop(random_empty_tile)

                    # Create a new bamboo pile and add it to the bamboo piles group
                    self.bamboo_piles_group.add(BambooPile(x = random_empty_tile[0], y = random_empty_tile[1]))

                    # Set the timer to start counting from the spawning cooldown timer set
                    BambooPile.bamboo_pile_info_dict["SpawningCooldownTimer"] = BambooPile.bamboo_pile_info_dict["SpawningCooldown"] 

    # -------------------------------------------
    # Bosses

    def find_valid_boss_spawning_position(self, delta_time):
        
        # Method used to spawn the boss (Spawn the boss once the player presses the button at the top of the screen (add a button at the top of the screen that goes to the next boss))

        # If there isn't a dictionary holding information regarding bosses yet
        if hasattr(self, "bosses_dict") == False:
            
            # Temporary variables for the spawning effect
            number_of_tiles_for_checking = 4
            spawning_effect_counter = 0
            number_of_cycles = 8 # If the NumOfTilesForChecking was 3 and SpawningEffectCounter started at 0, then each cycle would consist of 4 changes
            time_to_spawn = 6000 #8000
            time_between_each_change = (time_to_spawn / number_of_cycles) / ((number_of_tiles_for_checking + 1) - spawning_effect_counter) # The time between each change
            
            # Create a dictionary to hold information regarding bosses
            self.bosses_dict = { 
                        "CurrentBoss": "SikaDeer",
                        "NumOfTilesForChecking": number_of_tiles_for_checking, # The number of tiles to the left / right / up, down of the randomly chosen empty tile for the spawning position to be valid
                        "RandomSpawningPosition" : random_choice(list(self.empty_tiles_dict.keys())), # Choose a random spawning position
                        "ValidSpawningPosition": None, 
                        "SpawningPositionTilesList": [],
                        "TimeToSpawn": time_to_spawn, # The time for the boss to spawn
                        "TimeToSpawnTimer": None,

                        # Spawning effect keys and values
                        "SpawningEffectTimeBetweenEachChange": time_between_each_change,
                        "SpawningEffectOriginalTimeBetweenEachChange": time_between_each_change,
                        "SpawningEffectTimer": None,
                        "OriginalSpawningEffectCounter": spawning_effect_counter,
                        "SpawningEffectCounter": spawning_effect_counter, # If the NumOfTilesForChecking was 3, then each cycle would consist of 4 changes

                        # The bosses (The values will be replaced with a boss instance)
                        "SikaDeer": None,
                        "GoldenMonkey": None,
                        "AsiaticBlackBear": None,
                        
                                }

        # If a valid spawning position has not been found
        if self.bosses_dict["ValidSpawningPosition"] == None:

            # Choose a random empty tile
            self.bosses_dict["RandomSpawningPosition"] = self.bosses_dict["RandomSpawningPosition"]

            # For each empty tile inside the empty tiles dictionary
            for empty_tile in self.empty_tiles_dict.keys():
                
                # If the length of the tiles list is already has enough empty tiles to prove that it is a valid spawning location
                if len(self.bosses_dict["SpawningPositionTilesList"]) == (((self.bosses_dict["NumOfTilesForChecking"] * 2) + 1) ** 2) - 1:
                    # Exit the loop
                    break
                
                # Otherwise
                else:
                    # If the empty tile is not the same as the random empty tile and the tile is a certain distance from the selected random empty tile
                    if empty_tile != self.bosses_dict["RandomSpawningPosition"] and \
                        self.bosses_dict["RandomSpawningPosition"][0]  - (self.bosses_dict["NumOfTilesForChecking"] * TILE_SIZE) <= empty_tile[0] <= self.bosses_dict["RandomSpawningPosition"][0] + (self.bosses_dict["NumOfTilesForChecking"] * TILE_SIZE) and \
                                self.bosses_dict["RandomSpawningPosition"][1] - (self.bosses_dict["NumOfTilesForChecking"] * TILE_SIZE) <= empty_tile[1] <= self.bosses_dict["RandomSpawningPosition"][1] + (self.bosses_dict["NumOfTilesForChecking"] * TILE_SIZE):

                                # Add the empty tile to the spawning position tiles list
                                self.bosses_dict["SpawningPositionTilesList"].append(empty_tile)
            
            # If there is "enough space" for the boss to spawn 
            if len(self.bosses_dict["SpawningPositionTilesList"]) == (((self.bosses_dict["NumOfTilesForChecking"] * 2) + 1) ** 2) - 1:
                # Set the valid spawning position to be the random spawning position
                self.bosses_dict["ValidSpawningPosition"] = self.bosses_dict["RandomSpawningPosition"]
                # Set the boss spawn timer to start
                self.bosses_dict["TimeToSpawnTimer"] = self.bosses_dict["TimeToSpawn"]
                # Set the boss spawn effect timer to start
                self.bosses_dict["SpawningEffectTimer"] = self.bosses_dict["SpawningEffectTimeBetweenEachChange"]

            # If there is not "enough space" for the boss to spawn 
            elif len(self.bosses_dict["SpawningPositionTilesList"]) < (((self.bosses_dict["NumOfTilesForChecking"] * 2) + 1) ** 2) - 1:
                # Generate another random spawning position
                self.bosses_dict["RandomSpawningPosition"] =  random_choice(list(self.empty_tiles_dict.keys()))
                # Empty the spawning position tiles list
                self.bosses_dict["SpawningPositionTilesList"] = []

        # If a valid spawning position has been found and a boss has not been spawned yet
        elif self.bosses_dict["ValidSpawningPosition"] != None and len(self.boss_group) == 0:

                # If a timer has been set to spawn the boss
                if self.bosses_dict["TimeToSpawnTimer"] != None:

                    # For each empty tile in the spawning position tiles list
                    for empty_tile in self.bosses_dict["SpawningPositionTilesList"]:

                            # If the empty tile is the required distance away from the selected spawning tile
                            if self.bosses_dict["ValidSpawningPosition"][0] - (self.bosses_dict["SpawningEffectCounter"] * TILE_SIZE) <= empty_tile[0] <= self.bosses_dict["ValidSpawningPosition"][0] + (self.bosses_dict["SpawningEffectCounter"] * TILE_SIZE) and \
                                self.bosses_dict["ValidSpawningPosition"][1] - (self.bosses_dict["SpawningEffectCounter"] * TILE_SIZE) <= empty_tile[1] <= self.bosses_dict["ValidSpawningPosition"][1] + (self.bosses_dict["SpawningEffectCounter"] * TILE_SIZE):
                                
                                # Highlight the empty tile
                                pygame_draw_rect(
                                    surface = self.scaled_surface, 
                                    color = (40, 40, 40), 
                                    rect = (empty_tile[0] - self.camera_position[0], empty_tile[1] - self.camera_position[1], empty_tile[2], empty_tile[3]), 
                                    width = 1,
                                    border_radius = 5
                                    )
                                # Draw a circle which grows with the spawning effect counter (inner circle)
                                pygame_draw_circle(
                                                surface = self.scaled_surface, 
                                                color = (60, 60, 60),
                                                center = ((self.bosses_dict["ValidSpawningPosition"][0] + (TILE_SIZE / 2)) - self.camera_position[0], (self.bosses_dict["ValidSpawningPosition"][1] + (TILE_SIZE / 2)) - self.camera_position[1]), 
                                                radius = ((self.bosses_dict["SpawningEffectCounter"] - 1) * TILE_SIZE),
                                                width = 1
                                                )

                                # Draw a circle which grows with the spawning effect counter (outer circle)
                                pygame_draw_circle(
                                                surface = self.scaled_surface, 
                                                color = (80, 80, 80), 
                                                center = ((self.bosses_dict["ValidSpawningPosition"][0] + (TILE_SIZE / 2)) - self.camera_position[0], (self.bosses_dict["ValidSpawningPosition"][1] + (TILE_SIZE / 2)) - self.camera_position[1]), 
                                                radius = (self.bosses_dict["SpawningEffectCounter"] * TILE_SIZE),
                                                width = 1
                                                )

                    # Draw the spawning tile
                    pygame_draw_rect(
                                    surface = self.scaled_surface, 
                                    color = "firebrick1", 
                                    rect = (
                                        
                                            self.bosses_dict["ValidSpawningPosition"][0] - self.camera_position[0],
                                            self.bosses_dict["ValidSpawningPosition"][1] - self.camera_position[1], 
                                            self.bosses_dict["ValidSpawningPosition"][2], self.bosses_dict["ValidSpawningPosition"][3]
                                           ),
                                    width = 0, 
                                    border_radius = 5
                                    )
        
                    # Draw the spawning tile outline    
                    pygame_draw_rect(
                                    surface = self.scaled_surface, 
                                    color = "black", 
                                    rect = (
                                        
                                            self.bosses_dict["ValidSpawningPosition"][0] - self.camera_position[0],
                                            self.bosses_dict["ValidSpawningPosition"][1] - self.camera_position[1], 
                                            self.bosses_dict["ValidSpawningPosition"][2], self.bosses_dict["ValidSpawningPosition"][3]
                                           ),
                                    width = 2, 
                                    border_radius = 5
                                    )
                    # --------------------------------------------
                    # Spawning effect timer 

                    # If the timer has not finished counting down
                    if self.bosses_dict["SpawningEffectTimer"] > 0:
                        # Decrease the timer
                        self.bosses_dict["SpawningEffectTimer"] -= 1000 * delta_time

                    # If the timer has finished counting down
                    if self.bosses_dict["SpawningEffectTimer"] <= 0:

                        # If incrementing the spawning effect counter is less than the number of tiles for checking
                        if self.bosses_dict["SpawningEffectCounter"] + 1 <= self.bosses_dict["NumOfTilesForChecking"]:
                            # Increment the spawning effect counter
                            self.bosses_dict["SpawningEffectCounter"] += 1

                        # If incrementing the spawning effect counter is greater than the number of tiles for checking
                        elif self.bosses_dict["SpawningEffectCounter"] + 1 > self.bosses_dict["NumOfTilesForChecking"]:
                            # Reset the spawning effect counter
                            self.bosses_dict["SpawningEffectCounter"] = self.bosses_dict["OriginalSpawningEffectCounter"]

                        # Reset the timer (Adding it will help improve accuracy)
                        self.bosses_dict["SpawningEffectTimer"] += self.bosses_dict["SpawningEffectTimeBetweenEachChange"]

                    # Change the time between each change depending on how close the boss is to spawning
                    self.bosses_dict["SpawningEffectTimeBetweenEachChange"] = self.bosses_dict["SpawningEffectOriginalTimeBetweenEachChange"] * self.bosses_dict["TimeToSpawnTimer"] / self.bosses_dict["TimeToSpawn"]
                                                                                
                    # --------------------------------------------
                    # Spawning timer 

                    # If the timer has not finished counting down
                    if self.bosses_dict["TimeToSpawnTimer"] > 0:
                        # Decrease the timer
                        self.bosses_dict["TimeToSpawnTimer"] -= 1000 * delta_time

                    # If the timer has finished counting down
                    if self.bosses_dict["TimeToSpawnTimer"] <= 0:
                        # Set the boss spawn timer back to None, which will allow for the boss to be spawned
                        self.bosses_dict["TimeToSpawnTimer"] = None

                # If the timer has finished counting down
                if self.bosses_dict["TimeToSpawnTimer"] == None:

                    # If there is no current boss
                    if self.bosses_dict[self.bosses_dict["CurrentBoss"]] == None:
                        # Spawn the boss
                        self.spawn_boss(boss_to_spawn = self.bosses_dict["CurrentBoss"])

    def spawn_boss(self, boss_to_spawn):

        # Spawns the boss

        # Set the bamboo piles to start spawning
        BambooPile.bamboo_pile_info_dict["SpawningCooldownTimer"] = BambooPile.bamboo_pile_info_dict["SpawningCooldown"]
        
        # Check which boss should be spawned
        match boss_to_spawn:
            
            case "SikaDeer":
                # Import the SikaDeer boss
                from Level.Bosses.SikaDeerBoss import SikaDeerBoss

                # Create a class attribute for the SikaDeerBoss, which is an image dictionary holding all the images for each action that the boss has
                SikaDeerBoss.ImagesDict = {

                    "Chase": tuple(pygame_image_load(f"graphics/Bosses/SikaDeer/Chase/{i}.png").convert_alpha() for i in range(0, len(os_listdir("graphics/Bosses/SikaDeer/Chase")))),
                    "Stomp": tuple(pygame_image_load(f"graphics/Bosses/SikaDeer/Stomp/{i}.png").convert_alpha() for i in range(0, len(os_listdir("graphics/Bosses/SikaDeer/Stomp")))),

                    "Target": { 
                            "Up": tuple(pygame_image_load(f"graphics/Bosses/SikaDeer/Target/Up/{i}.png").convert_alpha() for i in range(0, len(os_listdir("graphics/Bosses/SikaDeer/Target/Up")))),
                            "Up Left": tuple(pygame_transform_flip(surface = pygame_image_load(f"graphics/Bosses/SikaDeer/Target/UpRight/{i}.png").convert_alpha(), flip_x = True, flip_y = False) for i in range(0, len(os_listdir("graphics/Bosses/SikaDeer/Target/UpRight")))),
                            "Up Right": tuple(pygame_image_load(f"graphics/Bosses/SikaDeer/Target/UpRight/{i}.png").convert_alpha() for i in range(0, len(os_listdir("graphics/Bosses/SikaDeer/Target/UpRight")))),

                            "Left": tuple(pygame_transform_flip(surface = pygame_image_load(f"graphics/Bosses/SikaDeer/Target/Right/{i}.png").convert_alpha(), flip_x = True, flip_y = False) for i in range(0, len(os_listdir("graphics/Bosses/SikaDeer/Target/Right")))),
                            "Right": tuple(pygame_image_load(f"graphics/Bosses/SikaDeer/Target/Right/{i}.png").convert_alpha() for i in range(0, len(os_listdir("graphics/Bosses/SikaDeer/Target/Right")))),

                            "Down": tuple(pygame_image_load(f"graphics/Bosses/SikaDeer/Target/Down/{i}.png").convert_alpha() for i in range(0, len(os_listdir("graphics/Bosses/SikaDeer/Target/Down")))),
                            "Down Left": tuple(pygame_transform_flip(surface = pygame_image_load(f"graphics/Bosses/SikaDeer/Target/DownRight/{i}.png").convert_alpha(), flip_x = True, flip_y = False) for i in range(0, len(os_listdir("graphics/Bosses/SikaDeer/Target/DownRight")))),
                            "Down Right": tuple(pygame_image_load(f"graphics/Bosses/SikaDeer/Target/DownRight/{i}.png").convert_alpha() for i in range(0, len(os_listdir("graphics/Bosses/SikaDeer/Target/DownRight")))),
                            },
                    "Charge": {
                            "Up": tuple(pygame_image_load(f"graphics/Bosses/SikaDeer/Charge/Up/{i}.png").convert_alpha() for i in range(0, len(os_listdir("graphics/Bosses/SikaDeer/Charge/Up")))),
                            "Up Left": tuple(pygame_transform_flip(surface = pygame_image_load(f"graphics/Bosses/SikaDeer/Charge/UpRight/{i}.png").convert_alpha(), flip_x = True, flip_y = False) for i in range(0, len(os_listdir("graphics/Bosses/SikaDeer/Charge/UpRight")))),
                            "Up Right": tuple(pygame_image_load(f"graphics/Bosses/SikaDeer/Charge/UpRight/{i}.png").convert_alpha() for i in range(0, len(os_listdir("graphics/Bosses/SikaDeer/Charge/UpRight")))),

                            "Left": tuple(pygame_transform_flip(surface = pygame_image_load(f"graphics/Bosses/SikaDeer/Charge/Right/{i}.png").convert_alpha(), flip_x = True, flip_y = False) for i in range(0, len(os_listdir("graphics/Bosses/SikaDeer/Charge/Right")))),
                            "Right": tuple(pygame_image_load(f"graphics/Bosses/SikaDeer/Charge/Right/{i}.png").convert_alpha() for i in range(0, len(os_listdir("graphics/Bosses/SikaDeer/Charge/Right")))),

                            "Down": tuple(pygame_image_load(f"graphics/Bosses/SikaDeer/Charge/Down/{i}.png").convert_alpha() for i in range(0, len(os_listdir("graphics/Bosses/SikaDeer/Charge/Down")))),
                            "Down Left": tuple(pygame_transform_flip(surface = pygame_image_load(f"graphics/Bosses/SikaDeer/Charge/DownRight/{i}.png").convert_alpha(), flip_x = True, flip_y = False) for i in range(0, len(os_listdir("graphics/Bosses/SikaDeer/Charge/DownRight")))),
                            "Down Right": tuple(pygame_image_load(f"graphics/Bosses/SikaDeer/Charge/DownRight/{i}.png").convert_alpha() for i in range(0, len(os_listdir("graphics/Bosses/SikaDeer/Charge/DownRight")))),
                                
                                },
                    "Stunned": tuple(pygame_image_load(f"graphics/Bosses/SikaDeer/Stunned/{i}.png").convert_alpha() for i in range(0, len(os_listdir("graphics/Bosses/SikaDeer/Stunned")))),


                                        }
                
                # Spawn the boss at the middle of the tile, with the bottom of the boss being at the bottom of the tile
                self.bosses_dict["SikaDeer"] = SikaDeerBoss(
                                                            x = self.bosses_dict["ValidSpawningPosition"][0] + (TILE_SIZE / 2), 
                                                            y = self.bosses_dict["ValidSpawningPosition"][1] + TILE_SIZE,
                                                            surface = self.scaled_surface,
                                                            scale_multiplier = self.scale_multiplier
                                                            )
                # ----------------------------------------
                # Preparing groups 

                # Create a sprite group for the stomp attacks nodes created by the Sika Deer boss
                from Level.Bosses.BossAttacks.stomp import StompController
                self.stomp_attack_nodes_group = pygame_sprite_Group()
                StompController.nodes_group = self.stomp_attack_nodes_group

                # Add the boss into the boss group
                self.boss_group.add(self.bosses_dict["SikaDeer"])

                # Update the game UI with this information
                self.game_ui.current_boss = self.boss_group.sprite

                # Set the current boss' last tile position to be the last tile position found (for collisions)
                self.boss_group.sprite.last_tile_position = self.last_tile_position

            case "GoldenMonkey":
                pass

            case "AsiaticBlackBear":
                pass

    def update_and_run_boss(self, delta_time):

        # Updates and runs the boss

        # If there is a current boss
        if self.boss_group.sprite != None:

            # Update the current boss' delta time
            self.boss_group.sprite.delta_time = delta_time

            # Update the current boss' camera position 
            self.boss_group.sprite.camera_position = self.camera_position
            
            # Update the current boss' camera shake events list (Used for camera shake events e.g. SikaDeer stomp attack)
            self.boss_group.sprite.camera_shake_events_list = self.camera_shake_info_dict["EventsList"]

            # Update the current boss with the current position of the player (Used for finding the angle between the boss and the player)
            self.boss_group.sprite.players_position = self.player.rect.center

            # Update the player with the rect information of the current boss (Used for limiting building placement if the player is building on top of the boss)
            self.player.boss_rect = self.boss_group.sprite.rect

            # Run the boss
            self.boss_group.sprite.run()
    
    def draw_boss_guidelines(self, delta_time):

        # If the current boss is the "SikaDeer"
        if self.bosses_dict["CurrentBoss"] == "SikaDeer":

            # If the current action is neither "Target" or "Charge"
            if self.boss_group.sprite.current_action != "Target" and self.boss_group.sprite.current_action != "Charge":
                # Draw guidelines between the player and the boss
                self.game_ui.draw_guidelines_between_a_and_b(
                                                            a = self.boss_group.sprite.rect.center, 
                                                            b = self.player.rect.center, 
                                                            colour = "white",
                                                            camera_position = self.camera_position, 
                                                            guidelines_segments_thickness = self.guidelines_segments_thickness,
                                                            guidelines_surface = self.guidelines_surface,
                                                            main_surface = self.scaled_surface
                                                            )
            # If the current action is "Target"
            elif self.boss_group.sprite.current_action == "Target":

                # Draw red dashed guidelines between the player and the boss
                self.game_ui.draw_guidelines_between_a_and_b(
                                                            a = self.boss_group.sprite.rect.center, 
                                                            b = self.player.rect.center, 
                                                            colour = "red",
                                                            camera_position = self.camera_position, 
                                                            guidelines_segments_thickness = self.guidelines_segments_thickness,
                                                            guidelines_surface = self.guidelines_surface,
                                                            main_surface = self.scaled_surface
                                                            )

                # The new angle time gradient in relation to the current time left
                self.boss_group.sprite.behaviour_patterns_dict["Target"]["BlinkingVisualEffectAngleTimeGradient"] = (self.boss_group.sprite.behaviour_patterns_dict["Target"]["BlinkingVisualEffectAngleChange"] - 0) / (self.boss_group.sprite.behaviour_patterns_dict["Target"]["DurationTimer"] / 1000)

                # Increase the current sin angle
                self.boss_group.sprite.behaviour_patterns_dict["Target"]["BlinkingVisualEffectCurrentSinAngle"] += self.boss_group.sprite.behaviour_patterns_dict["Target"]["BlinkingVisualEffectAngleTimeGradient"] * delta_time

                # Set the new alpha level based on the current sin angle
                # Note: Limit the alpha level to 185 so that it doesn't stand out too much
                self.guidelines_surface.set_alpha (min(125 + (125 * sin(self.boss_group.sprite.behaviour_patterns_dict["Target"]["BlinkingVisualEffectCurrentSinAngle"])), 185))

                # Adjust the current animation duration of the targeting animation according to how much time is left before the current action is set to "Charge"
                # Note: Limit the time between frames to always be at least 20 (because very small times will result in buggy animations)
                self.boss_group.sprite.behaviour_patterns_dict["Target"]["FullAnimationDuration"] = self.boss_group.sprite.behaviour_patterns_dict["Target"]["OriginalAnimationDuration"] * (self.boss_group.sprite.behaviour_patterns_dict["Target"]["DurationTimer"] / self.boss_group.sprite.behaviour_patterns_dict["Target"]["Duration"])
                self.boss_group.sprite.behaviour_patterns_dict["Target"]["TimeBetweenAnimFrames"] = max(
                                            self.boss_group.sprite.behaviour_patterns_dict["Target"]["FullAnimationDuration"] / self.boss_group.sprite.behaviour_patterns_dict["Target"]["AnimationListLength"],
                                            20
                                                                                                        )

            # If the current action is "Charge"
            elif self.boss_group.sprite.current_action == "Charge":
                
                # If the current alpha level of the guidelines surface is not the default alpha level
                if self.guidelines_surface.get_alpha() != self.guidelines_surface_default_alpha_level:
                    # Reset it back to the default alpha level
                    self.guidelines_surface.set_alpha(self.guidelines_surface_default_alpha_level)

                # If the current sin angle for the blinking visual effect is not 0
                if self.boss_group.sprite.behaviour_patterns_dict["Target"]["BlinkingVisualEffectCurrentSinAngle"] != 0:
                    # Reset the current sin angle for the blinking visual effect back to 0
                    self.boss_group.sprite.behaviour_patterns_dict["Target"]["BlinkingVisualEffectCurrentSinAngle"]

                # Calculate a new length and point depending on where the angle at which the boss is charging at 
                # Note: (Extends the line from the current position of the boss and last locked in position of the player)
                new_length = dist(self.boss_group.sprite.behaviour_patterns_dict["Charge"]["PlayerPosAtChargeTime"], self.boss_group.sprite.rect.center) + screen_width / 2
                new_point = (
                    self.boss_group.sprite.rect.centerx + (new_length * cos(self.boss_group.sprite.behaviour_patterns_dict["Charge"]["ChargeAngle"])), 
                    self.boss_group.sprite.rect.centery - (new_length * sin(self.boss_group.sprite.behaviour_patterns_dict["Charge"]["ChargeAngle"]))
                    )

                # Draw red dashed guidelines between the player and the boss
                self.game_ui.draw_guidelines_between_a_and_b(
                                                            a = self.boss_group.sprite.rect.center, 
                                                            b = new_point, 
                                                            colour = "red",
                                                            camera_position = self.camera_position, 
                                                            guidelines_segments_thickness = self.guidelines_segments_thickness,
                                                            guidelines_surface = self.guidelines_surface,
                                                            main_surface = self.scaled_surface
                                                            )

    # --------------------------------------------------------------------------------------
    # Game UI methods

    def update_game_ui(self, delta_time):

        # Updates the game UI
    
        # Delta time
        self.game_ui.delta_time = delta_time

        # Current boss
        self.game_ui.current_boss = self.boss_group.sprite

        # If the game UI does not have the current boss' name yet and a boss is currently being spawned
        if self.game_ui.current_boss_name == None and hasattr(self, "bosses_dict") == True:
            # Update the game UI
            self.game_ui.current_boss_name = self.bosses_dict["CurrentBoss"]
            
        # Mouse position 
        self.game_ui.mouse_position = (self.player.mouse_position[0] - self.camera_position[0], self.player.mouse_position[1] - self.camera_position[1])

        # The camera pan information dict
        self.game_ui.camera_pan_information_dict = self.camera_pan_information_dict

    def run(self, delta_time):

        # Fill the scaled surface with a colour
        self.scaled_surface.fill("cornsilk4")

        # Update the camera position depending on who the focus subject is
        self.update_camera_position(delta_time = delta_time, focus_subject_center_pos = self.update_focus_subject())

        # Spawn bamboo piles if enough time has passed since the last bamboo pile was spawned
        self.spawn_bamboo_pile(delta_time = delta_time)

        if pygame_key_get_pressed()[pygame_K_f] or (hasattr(self, "bosses_dict") == True and self.bosses_dict["TimeToSpawnTimer"] != None):
            self.find_valid_boss_spawning_position(delta_time = delta_time)

        # Handle collisions between all objects in the level
        self.handle_collisions()

        # Find the neighbouring tiles for the player and the current boss
        self.find_neighbouring_tiles()

        # ---------------------------------------------------------
        # Hierarchy of drawing 

        # If there is no boss
        if self.boss_group.sprite == None:

            # Draw all objects inside the tile map / level
            self.draw_tile_map_objects()
            
            # Draw the angled polygon visual effects
            self.game_ui.draw_angled_polygons_effects(camera_position = self.camera_position, delta_time = delta_time)

            # Run the player methods
            self.player.run(delta_time = delta_time)

            # If the current boss is spawning
            if self.boss_group.sprite == None and hasattr(self, "bosses_dict") == True and self.bosses_dict["ValidSpawningPosition"] != None:
                # Draw guidelines between the player and the boss' spawning location
                self.game_ui.draw_guidelines_between_a_and_b(
                                                            a = (self.bosses_dict["ValidSpawningPosition"][0] + (TILE_SIZE / 2), self.bosses_dict["ValidSpawningPosition"][1] + (TILE_SIZE / 2)), 
                                                            b = self.player.rect.center,
                                                            colour = "white",
                                                            camera_position = self.camera_position,
                                                            guidelines_segments_thickness = self.guidelines_segments_thickness,
                                                            guidelines_surface = self.guidelines_surface,
                                                            main_surface = self.scaled_surface
                                                            )
        # If the current boss is alive
        if self.boss_group.sprite != None and self.boss_group.sprite.extra_information_dict["CurrentHealth"] > 0:

            # Draw all objects inside the tile map / level
            self.draw_tile_map_objects()

            # Draw the boss guidelines underneath the player and the boss
            self.draw_boss_guidelines(delta_time = delta_time)

            # Run the player methods
            self.player.run(delta_time = delta_time)

            # Update and run the boss
            self.update_and_run_boss(delta_time = delta_time)
            
            # Draw the angled polygon visual effects
            self.game_ui.draw_angled_polygons_effects(camera_position = self.camera_position, delta_time = delta_time)

        # If the current boss is not alive
        elif self.boss_group.sprite != None and self.boss_group.sprite.extra_information_dict["CurrentHealth"] <= 0:

            # Update and run the boss
            self.update_and_run_boss(delta_time = delta_time)

            # Draw all objects inside the tile map / level
            self.draw_tile_map_objects()

            # Draw the angled polygon visual
            self.game_ui.draw_angled_polygons_effects(camera_position = self.camera_position, delta_time = delta_time)

            # Run the player methods
            self.player.run(delta_time = delta_time)
        
        # ---------------------------------------------------------

        # Update the game UI
        self.update_game_ui(delta_time = delta_time)

        # Run the game UI 
        self.game_ui.run(camera_position = self.camera_position)

        # Draw the scaled surface onto the screen
        self.screen.blit(pygame_transform_scale(self.scaled_surface, (screen_width, screen_height)), (0, 0))