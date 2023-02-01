import pygame, os
from Global.settings import *
from Level.world_tile import WorldTile
from Level.Player.player import Player
from Level.game_ui import GameUI
from Level.bamboo_pile import BambooPile
from random import choice as random_choice
from math import dist

class Game:
    def __init__(self):

        # Screen
        self.screen = pygame.display.get_surface()  

        # Create a surface for which all objects will be drawn onto. This surface is then scaled and drawn onto the main screen
        self.scale_multiplier = 2
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
        self.world_tiles_dict = {} # Dictionary used to hold all the world tiles 
        self.world_tiles_group = pygame.sprite.Group()
        # self.player_group = pygame.sprite.GroupSingle(self.player) This was created inside the create_objects_tile_map method
        self.bamboo_projectiles_group = pygame.sprite.Group() # Group for all bamboo projectiles for the player
        self.empty_tiles_dict = {} # Dictionary used to hold all of the empty tiles in the tile map
        self.bamboo_piles_group = pygame.sprite.Group()
        
    # --------------------------------------------------------------------------------------
    # Misc methods

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
                        self.player_group = pygame.sprite.GroupSingle(self.player)


                    # World tile 1
                    case 2:
                        # Create a world tile
                        world_tile = WorldTile(x = (column_index * TILE_SIZE), y = (row_index * TILE_SIZE), image = pygame.transform.smoothscale(self.tile_images[1], (TILE_SIZE, TILE_SIZE)))

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
       
        # ---------------------------------------------
        # Bamboo piles

        for bamboo_pile in self.bamboo_piles_group:
            # Draw the bamboo pile
            bamboo_pile.draw(surface = self.scaled_surface, x = bamboo_pile.rect.x - self.camera_position[0], y = bamboo_pile.rect.y - self.camera_position[1])

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
            if (self.player.rect.left  - (TILE_SIZE * 1.25) <= tile.rect.centerx <= self.player.rect.right + (TILE_SIZE * 1.25)) and (self.player.rect.top - (TILE_SIZE * 1.25) <= tile.rect.centery <= (self.player.rect.bottom + TILE_SIZE * 1.25)):
                # Add it to the player's neighbouring tiles dictionary
                self.player.neighbouring_tiles_dict[tile] = 0 

            # If the tile is not within 1 tiles of the player (horizontally and vertically)
            else:
                # If the tile is inside the neighbouring tiles dict's keys
                if tile in self.player.neighbouring_tiles_dict.keys():
                    # Remove the world/ building tile from the neighbouring tiles dictionary
                    self.player.neighbouring_tiles_dict.pop(tile)
                    
    def handle_collisions(self):

        # Handles collisions between objects (including the player). Collisions between the world tiles and the player are within the Player class.

        # --------------------------------------------------------------------------------------
        # Bamboo projectiles and world tiles
        
        # Look for collisions between bamboo projectiles and world tiles, delete bamboo projectile if there is a collision
        pygame.sprite.groupcollide(self.bamboo_projectiles_group, self.world_tiles_group, dokilla = True, dokillb = False, collided = pygame.sprite.collide_mask)

        # --------------------------------------------------------------------------------------
        # Player and bamboo piles
        
        # Look for collisions between the player and bamboo piles, and only delete the bamboo pile if there is a collision and the player does not currently have the maximum amount of bamboo resource
        player_and_bamboo_piles_collision_list = pygame.sprite.spritecollide(self.player, self.bamboo_piles_group, dokill = False, collided = pygame.sprite.collide_mask)
        if len(player_and_bamboo_piles_collision_list) > 0 and (self.player.player_gameplay_info_dict["AmountOfBambooResource"] != self.player.player_gameplay_info_dict["MaximumAmountOfBambooResource"]):
            
            # Remove the bamboo pile from the bamboo piles group
            self.bamboo_piles_group.remove(player_and_bamboo_piles_collision_list)

            # Add the empty tile back to the empty tiles dictionary so other items can spawn in the tile
            self.empty_tiles_dict[(player_and_bamboo_piles_collision_list[0].rect.x, player_and_bamboo_piles_collision_list[0].rect.y, player_and_bamboo_piles_collision_list[0].rect.width, player_and_bamboo_piles_collision_list[0].rect.height)] = 0

            print((player_and_bamboo_piles_collision_list[0].rect.x, player_and_bamboo_piles_collision_list[0].rect.y, player_and_bamboo_piles_collision_list[0].rect.width, player_and_bamboo_piles_collision_list[0].rect.height))

            # Increase the amount of bamboo resource that the player has, limiting it to the maximum amount the player can hold at one time
            self.player.player_gameplay_info_dict["AmountOfBambooResource"] = min(
                                                                                self.player.player_gameplay_info_dict["MaximumAmountOfBambooResource"], 
                                                                                self.player.player_gameplay_info_dict["AmountOfBambooResource"] + BambooPile.bamboo_pile_info_dict["BambooResourceReplenishAmount"]
                                                                                )

    def spawn_bamboo_pile(self, delta_time):

        # ----------------------------------------------------------------------------
        # Updating the spawning timer
        
        # If there is a timer that has been set to the spawning cooldown and there are less bamboo piles than the maximum amount at one time
        """ Note: The second check is so that once there are the maximum amount of piles at one time, the timer will only start counting when there are less than the maximum amount 
        - This avoids the issue where if the player walks over a bamboo pile after there were the maximum amount of piles, a new pile won't instantly spawn.
        """
        if BambooPile.bamboo_pile_info_dict["SpawningCooldownTimer"] != None and len(self.bamboo_piles_group) < BambooPile.bamboo_pile_info_dict["MaximumNumberOfPilesAtOneTime"]:
            
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

    # --------------------------------------------------------------------------------------
    # Game UI methods

    def update_game_ui(self, delta_time):

        # Update the delta time
        self.game_ui.delta_time = delta_time

    def run(self, delta_time):

        # Update the game UI
        self.update_game_ui(delta_time = delta_time)
        
        # Fill the scaled surface with a colour
        self.scaled_surface.fill("gray23")

        # Update the camera position 
        self.update_camera_position()

        # Draw all objects inside the tile map / level
        self.draw_tile_map_objects()

        # Spawn bamboo piles if enough time has passed since the last bamboo pile was spawned
        self.spawn_bamboo_pile(delta_time = delta_time)

        # Handle collisions between all objects in the level
        self.handle_collisions()

        # Find the player's neighbouring tiles
        self.find_neighbouring_tiles_to_player()

        # Run the player methods
        self.player.run(delta_time = delta_time)
        
        # Run the game UI 
        self.game_ui.run()

        # Draw the scaled surface onto the screen
        self.screen.blit(pygame.transform.scale(self.scaled_surface, (screen_width, screen_height)), (0, 0))