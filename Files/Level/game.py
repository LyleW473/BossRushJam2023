import pygame, os
from Global.settings import *
from Level.world_tile import WorldTile
from Level.Player.player import Player
from Level.game_ui import GameUI
from math import sin, cos

class Game:
    def __init__(self):

        # Screen
        self.screen = pygame.display.get_surface()  

        # Create a surface for which all objects will be drawn onto. This surface is then scaled and drawn onto the main screen
        self.scale_multiplier = 3
        self.scaled_surface = pygame.Surface((screen_width / self.scale_multiplier, screen_height / self.scale_multiplier))

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
        self.camera_mode = None # Can either be: Static, Follow


        # --------------------------------------------------------------------------------------
        # Groups
        self.all_tile_map_objects_group = pygame.sprite.Group() # Group for all tile map objects, including the player
        self.world_tiles_dict = {} # Dictionary used to hold all the world tiles 
        self.world_tiles_group = pygame.sprite.Group()
        # self.player_group = pygame.sprite.GroupSingle(self.player) This was created inside the create_objects_tile_map method
        self.bamboo_projectiles_group = pygame.sprite.Group() # Group for all bamboo projectiles for the player
        self.empty_tiles_dict = {} # Dictionary used to hold all of the empty tiles in the tile map
        
    # --------------------------------------------------------------------------------------
    # Misc methods

    def update_objects_delta_time(self, delta_time):
        # Used to update the delta time attributes of all objects within the tile map

        # For all objects
        for tile_map_object in self.all_tile_map_objects_group:
            # Update the object's delta time
            tile_map_object.delta_time = delta_time

    # --------------------------------------------------------------------------------------
    # Camera methods

    def set_camera_mode(self):
        # Used to change the camera mode depending on the size of the tile map
        
        # If the width of the tile map is one room
        if self.last_tile_position[0] <= (self.scaled_surface.get_width() / 2):
            # Set the camera mode to "Static"
            self.camera_mode = "Static"
        
        # If the width of the tile map is more than one room
        else:
            # Set the camera mode to "Follow"
            self.camera_mode = "Follow"

    def update_camera_position(self):   
        # Moves the camera's position depending on what mode the camera has been set tow
        
        # If the camera mode is set to "Follow"
        if self.camera_mode == "Follow":
            
            # --------------------------------------------------------------------------------------
            # Adjusting camera x position

            # If the player is in half the width of the scaled screen from the first tile in the tile map
            if 0 <= self.player.rect.centerx <= (self.scaled_surface.get_width() / 2):
                # Don't move the camera
                camera_position_x = 0

            # If the player is in between half of the size of the scaled screen width from the first tile in the tile map and half the width of the scaled screen from the last tile in the tile map
            elif 0 + (self.scaled_surface.get_width() / 2) < self.player.rect.centerx < self.last_tile_position[0] - (self.scaled_surface.get_width() / 2):
                # Set the camera to always follow the player
                camera_position_x = self.player.rect.centerx - (self.scaled_surface.get_width() / 2)

            # If the player is half the scaled screen width away from the last tile in the tile maps
            elif self.player.rect.centerx >= self.last_tile_position[0] - (self.scaled_surface.get_width() / 2):
                # Set the camera to stop moving and be locked at half the size of the scaled screen width from the last tile in the tile map
                camera_position_x = self.last_tile_position[0] - self.scaled_surface.get_width() 

            # --------------------------------------------------------------------------------------
            # Adjusting camera y position

            # If the player is in half the height of the scaled screen from the first tile in the tile map
            if 0 <= self.player.rect.centery <= (self.scaled_surface.get_height() / 2):
                # Don't move the camera
                camera_position_y = 0

            # If the player is in between half of the size of the scaled screen height from the first tile in the tile map and half the width of the scaled screen from the last tile in the tile map
            elif 0 + (self.scaled_surface.get_height() / 2) < self.player.rect.centery < self.last_tile_position[1] - (self.scaled_surface.get_height() / 2):
                # Set the camera to always follow the player
                camera_position_y = self.player.rect.centery - (self.scaled_surface.get_height() / 2)

            # If the player is half the scaled screen width away from the last tile in the tile maps
            elif self.player.rect.centery >= self.last_tile_position[1] - (self.scaled_surface.get_height() / 2):
                # Set the camera to stop moving and be locked at half the size of the scaled screen width from the last tile in the tile map
                camera_position_y = self.last_tile_position[1] - self.scaled_surface.get_height()     

        # If the camera mode is set to "Static"
        elif self.camera_mode == "Static":
            # The camera's x position will always be at 0
            camera_position_x = 0
        
        # Update the camera position
        """
        - The camera's x position:
            - Starts at 0 until the player reaches half the size of the scaled screen width from the player's spawning position
            - Once the player reaches the center of the screen, then the camera will always follow the player
            - Until the player reaches half the size of the scaled screen width from the last tile in the tile map

        - The camera's y position:
            - Starts at 0 until the player reaches half the size of the scaled screen height from the player's spawning position
            - Once the player reaches the center of the screen, then the camera will always follow the player
            - Until the player reaches half the size of the scaled screen height from the last tile in the tile map
            
        """
        self.camera_position = [camera_position_x, camera_position_y]

        # Update the player's camera position attribute so that tile rects are correctly aligned
        self.player.camera_position = self.camera_position
     
    # --------------------------------------------------------------------------------------
    # Tile map methods

    def load_tile_map_images(self):

        # Loads the images of all the world tiles

        # Create a dictionary filled with all of the tiles' images
        # Note: Start at index 1 because the "0" tile represents nothing. 
        self.tile_images = {i + 1: pygame.image.load(f"graphics/Tiles/{i + 1}.png").convert() for i in range(0, len(os.listdir("graphics/Tiles")))} 

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
                        # Add the empty tile to the empty tiles dictionary (For player building and changing tiles)
                        self.empty_tiles_dict[((column_index * TILE_SIZE), (row_index * TILE_SIZE), TILE_SIZE, TILE_SIZE)] = len(self.empty_tiles_dict)

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
                        self.player_group = pygame.sprite.GroupSingle(self.player)

                        # Add the player to the group of all tile map objects
                        self.all_tile_map_objects_group.add(self.player)

                    # World tile 1
                    case 2:
                        # Create a world tile
                        world_tile = WorldTile(x = (column_index * TILE_SIZE), y = (row_index * TILE_SIZE), image = pygame.transform.smoothscale(self.tile_images[1], (TILE_SIZE, TILE_SIZE)))

                        # Add the world tile to the world tiles dictionary
                        # The key is the world tile because we use pygame.rect.collidedict in other areas of the code, the value is the type of world tile (The other type is building tiles)
                        self.world_tiles_dict[world_tile] = "WorldTile"

                        # Add it to the group of all tile map objects
                        self.all_tile_map_objects_group.add(world_tile)

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
        self.game_ui = GameUI(surface = self.scaled_surface, scale_multiplier = self.scale_multiplier, player_tools = self.player.tools, player_gameplay_info_dict = self.player.player_gameplay_info_dict)

    def draw_tile_map_objects(self):

        # Calls the draw methods of all objects in the level

        # ---------------------------------------------
        # World tiles and building tiles

        for tile in self.world_tiles_dict.keys():

            # Check the x co-ordinate of the camera
            match self.camera_position[0]:

                # If the camera is positioned at the start of the tile map and the object is within the boundaries of the screen
                case 0 if tile.rect.right <= self.scaled_surface.get_width():

                    # Draw all tile objects on the screen
                    tile.draw(surface = self.scaled_surface, x = (tile.rect.x - self.camera_position[0]), y = (tile.rect.y - self.camera_position[1]))

                # If the camera is positioned at the end of the tile map and the tile object is within the boundaries of the screen
                case _ if (self.last_tile_position[0] - self.scaled_surface.get_width()) == self.camera_position[0] and tile.rect.right >= self.camera_position[0]:

                    # Draw all tile objects on the screen
                    tile.draw(surface = self.scaled_surface, x = (tile.rect.x - self.camera_position[0]), y = (tile.rect.y - self.camera_position[1]))

                # If the camera is neither at the start or the end of the tile map and the object is within the boundaries of the screen
                case _ if self.player.rect.left - ((self.scaled_surface.get_width() / 2) + TILE_SIZE)  <= tile.rect.right <= self.player.rect.right + (self.scaled_surface.get_width() / 2): 

                    # Draw the tile object
                    tile.draw(surface = self.scaled_surface, x = (tile.rect.x - self.camera_position[0]), y = (tile.rect.y - self.camera_position[1]))

        # ---------------------------------------------
        # Bamboo projectiles

        for bamboo_projectile in self.bamboo_projectiles_group:
            # Draw the bamboo projectile 
            # pygame.draw.rect(self.scaled_surface, "white", (bamboo_projectile.rect.x - self.camera_position[0], bamboo_projectile.rect.y - self.camera_position[1], bamboo_projectile.rect.width, bamboo_projectile.rect.height), 0)
            bamboo_projectile.draw(surface = self.scaled_surface, x = bamboo_projectile.rect.x - self.camera_position[0], y = bamboo_projectile.rect.y - self.camera_position[1])

    # --------------------------------------------------------------------------------------
    # Gameplay methods

    def find_neighbouring_tiles_to_player(self):

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

            # If the tile is within 1 tiles of the player (horizontally and vertically)
            if (self.player.rect.left  - (TILE_SIZE) <= tile.rect.centerx <= self.player.rect.right + (TILE_SIZE)) and (self.player.rect.top - (TILE_SIZE * 2) <= tile.rect.centery <= (self.player.rect.bottom + TILE_SIZE * 1)):
                

                # Add it to the player's neighbouring tiles dictionary
                self.player.neighbouring_tiles_dict[tile] = 0 

                # # If the tile is a building tile
                # elif tile_type == "BuildingTile":
                #     # Add it to the player's neighbouring tiles dictionary
                #     self.player.neighbouring_tiles_dict[tile] = "BuildingTile" 

            # If the tile is not within 1 tiles of the player (horizontally and vertically)
            else:
                # If the tile is inside the neighbouring tiles dict's keys
                if tile in self.player.neighbouring_tiles_dict.keys():
                    # Remove the world/ building tile from the neighbouring tiles dictionary
                    self.player.neighbouring_tiles_dict.pop(tile)
                    

    def handle_collisions(self):

        # Handles collisions between objects (including the player). Collisions between the world tiles and the player are within the Player class.

        # --------------------------------------------------------------------------------------
        # Bamboo projectiles 

        # For each bamboo projectile in the bamboo projectiles group
        for bamboo_projectile in self.bamboo_projectiles_group:
            
            # Look for a slightly less accurate collision check between the tile and the player sprite
            if pygame.sprite.spritecollide(bamboo_projectile, self.world_tiles_group, False):
                # Create a list of all the tiles that the player collided (more accurate collision check)
                if pygame.sprite.spritecollide(bamboo_projectile, self.world_tiles_group, False, pygame.sprite.collide_mask):
                    self.bamboo_projectiles_group.remove(bamboo_projectile)

    # --------------------------------------------------------------------------------------
    # Game UI methods

    def update_game_ui(self, delta_time):

        # Update the delta time
        self.game_ui.delta_time = delta_time

    def run(self, delta_time):

        # Update the delta time of all objects 
        self.update_objects_delta_time(delta_time = delta_time)

        # Update the game UI
        self.update_game_ui(delta_time = delta_time)
        
        # Fill the scaled surface with a colour
        self.scaled_surface.fill("gray23")

        # Update the camera position 
        self.update_camera_position()

        # Draw all objects inside the tile map / level
        self.draw_tile_map_objects()

        # Handle collisions between all objects in the level
        self.handle_collisions()

        # Find the player's neighbouring tiles
        self.find_neighbouring_tiles_to_player()

        # Run the player methods
        self.player.run()
        
        # Run the game UI 
        self.game_ui.run()

        # Draw the scaled surface onto the screen
        self.screen.blit(pygame.transform.scale(self.scaled_surface, (screen_width, screen_height)), (0, 0))