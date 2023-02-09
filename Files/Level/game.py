import pygame
from Global.settings import *
from Level.world_tile import WorldTile
from Level.Player.player import Player
from Level.game_ui import GameUI
from Level.bamboo_pile import BambooPile
from random import choice as random_choice
from random import randrange as random_randrange
from math import sin, cos, dist, copysign
from os import listdir as os_listdir

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
        self.boss_group = pygame.sprite.GroupSingle()

        # --------------------------------------------------------------------------------------
        # Boss and player guidelines

        # Thickness of each segment
        self.guidelines_segments_thickness = 5

        # Surface
        self.guidelines_surface = pygame.Surface((self.scaled_surface.get_width(), self.scaled_surface.get_height()))
        self.guidelines_surface.set_colorkey("black")
        self.guidelines_surface_default_alpha_level = 105
        self.guidelines_surface.set_alpha(self.guidelines_surface_default_alpha_level)

        # ---------------------------------------------------------------------------------
        # Cursor images

        self.default_cursor_image = pygame.image.load("graphics/Cursors/Default.png").convert_alpha()
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
        self.tile_images = {i + 1: pygame.image.load(f"graphics/Tiles/{i + 1}.png").convert() for i in range(0, len(os_listdir("graphics/Tiles")))} 

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
                        if pygame.sprite.collide_mask(bamboo_projectile, self.bosses_dict[self.bosses_dict["CurrentBoss"]]) != None:
                            # If there is a pixel-perfect collision:

                            # Damage the current boss by the amount of damage that was passed into the bamboo projectile
                            # Note: This allows for different damage values for e.g. different weaponssa
                            self.bosses_dict[self.bosses_dict["CurrentBoss"]].extra_information_dict["CurrentHealth"] -= bamboo_projectile.damage_amount

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
                                                                text = "-" + str(bamboo_projectile.damage_amount),
                                                                )

                            # Remove the bamboo projectile
                            self.bamboo_projectiles_group.remove(bamboo_projectile)

        # --------------------------------------------------------------------------------------
        # Bamboo piles

        # Look for collisions between the player and bamboo piles, and only delete the bamboo pile if there is a collision and the player does not currently have the maximum amount of bamboo resource
        player_and_bamboo_piles_collision_list = pygame.sprite.spritecollide(self.player, self.bamboo_piles_group, dokill = False, collided = pygame.sprite.collide_rect)
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
                    if pygame.sprite.collide_mask(stomp_attack_node, collision_result[0]) != None:
                        
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
                    if pygame.sprite.collide_mask(stomp_attack_node, self.player) != None:

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
                    if pygame.sprite.collide_mask(stomp_attack_node, self.bosses_dict[self.bosses_dict["CurrentBoss"]]) != None:
                        
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
                    if pygame.sprite.collide_mask(self.boss_group.sprite, self.player.tools["BuildingTool"]["ExistingBuildingTilesList"][building_collision_result_index]) != None:
                        
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

                            # If the current boss is alive
                            if self.boss_group.sprite.extra_information_dict["CurrentHealth"] > 0:

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
            # --------------------------------------
            # World tiles while charging

            # Only if the boss is the "SikaDeer"
            if self.bosses_dict["CurrentBoss"] == "SikaDeer" and self.boss_group.sprite.current_action == "Charge":
                    # If there is an x or y world tile collision
                    if self.boss_group.sprite.movement_information_dict["WorldTileCollisionResultsX"] == True or self.boss_group.sprite.movement_information_dict["WorldTileCollisionResultsY"] == True:
                        # Set the "Charge" duration timer to 0 (to end the charge attack)
                        self.boss_group.sprite.behaviour_patterns_dict["Charge"]["DurationTimer"] = 0
            
            # --------------------------------------
            # Player

            # If there is a rect collision between the player and the boss is not currently idling after the knockback 
            # Note: Second check is so that the player doesn't keep setting off the idle timer in quick succession
            if self.boss_group.sprite.rect.colliderect(self.player.rect) == True and (self.boss_group.sprite.movement_information_dict["KnockbackCollisionIdleTimer"] == None):

                # If there is pixel-perfect collision 
                if pygame.sprite.collide_mask(self.boss_group.sprite, self.player):

                    # Knockback the player
                    self.player.player_gameplay_info_dict["KnockbackAttackDirection"] = [self.boss_group.sprite.movement_information_dict["HorizontalSuvatS"], self.boss_group.sprite.movement_information_dict["VerticalSuvatS"]]
                    self.player.player_gameplay_info_dict["KnockbackTimer"] = self.player.player_gameplay_info_dict["KnockbackTime"]

                    # Set the horizontal and vertical distance the player should travel based on the angle the boss hit it
                    # Note: Divided by 1000 because the knockback time is in milliseconds
                    self.player.player_gameplay_info_dict["KnockbackHorizontalDistanceTimeGradient"] = (self.player.player_gameplay_info_dict["KnockbackDistanceTravelled"] * cos(self.boss_group.sprite.movement_information_dict["Angle"])) / (self.player.player_gameplay_info_dict["KnockbackTime"] / 1000)
                    self.player.player_gameplay_info_dict["KnockbackVerticalDistanceTimeGradient"] = (self.player.player_gameplay_info_dict["KnockbackDistanceTravelled"] * sin(self.boss_group.sprite.movement_information_dict["Angle"])) / (self.player.player_gameplay_info_dict["KnockbackTime"] / 1000)

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
            if pygame.sprite.collide_mask(item, collision_result[0]) != None:
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
            time_to_spawn = 8000
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
                # Set the valid spawning position attribute to True
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
                                pygame.draw.rect(
                                    surface = self.scaled_surface, 
                                    color = (40, 40, 40), 
                                    rect = (empty_tile[0] - self.camera_position[0], empty_tile[1] - self.camera_position[1], empty_tile[2], empty_tile[3]), 
                                    width = 1,
                                    border_radius = 5
                                    )
                                # Draw a circle which grows with the spawning effect counter (inner circle)
                                pygame.draw.circle(
                                                surface = self.scaled_surface, 
                                                color = (60, 60, 60),
                                                center = ((self.bosses_dict["ValidSpawningPosition"][0] + (TILE_SIZE / 2)) - self.camera_position[0], (self.bosses_dict["ValidSpawningPosition"][1] + (TILE_SIZE / 2)) - self.camera_position[1]), 
                                                radius = ((self.bosses_dict["SpawningEffectCounter"] - 1) * TILE_SIZE),
                                                width = 1
                                                )

                                # Draw a circle which grows with the spawning effect counter (outer circle)
                                pygame.draw.circle(
                                                surface = self.scaled_surface, 
                                                color = (80, 80, 80), 
                                                center = ((self.bosses_dict["ValidSpawningPosition"][0] + (TILE_SIZE / 2)) - self.camera_position[0], (self.bosses_dict["ValidSpawningPosition"][1] + (TILE_SIZE / 2)) - self.camera_position[1]), 
                                                radius = (self.bosses_dict["SpawningEffectCounter"] * TILE_SIZE),
                                                width = 1
                                                )

                    # Draw the spawning tile
                    pygame.draw.rect(
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
                    pygame.draw.rect(
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

                    "Chase": [pygame.image.load(f"graphics/Bosses/SikaDeer/Chase/{i}.png").convert_alpha() for i in range(0, len(os_listdir("graphics/Bosses/SikaDeer/Chase")))],
                    "Stomp": [pygame.image.load(f"graphics/Bosses/SikaDeer/Stomp/{i}.png").convert_alpha() for i in range(0, len(os_listdir("graphics/Bosses/SikaDeer/Stomp")))],

                    "Target": { 
                            "Up": [pygame.image.load(f"graphics/Bosses/SikaDeer/Target/Up/{i}.png").convert_alpha() for i in range(0, len(os_listdir("graphics/Bosses/SikaDeer/Target/Up")))],
                            "Up Left": [pygame.transform.flip(surface = pygame.image.load(f"graphics/Bosses/SikaDeer/Target/UpRight/{i}.png").convert_alpha(), flip_x = True, flip_y = False) for i in range(0, len(os_listdir("graphics/Bosses/SikaDeer/Target/UpRight")))],
                            "Up Right": [pygame.image.load(f"graphics/Bosses/SikaDeer/Target/UpRight/{i}.png").convert_alpha() for i in range(0, len(os_listdir("graphics/Bosses/SikaDeer/Target/UpRight")))],

                            "Left": [pygame.transform.flip(surface = pygame.image.load(f"graphics/Bosses/SikaDeer/Target/Right/{i}.png").convert_alpha(), flip_x = True, flip_y = False) for i in range(0, len(os_listdir("graphics/Bosses/SikaDeer/Target/Right")))],
                            "Right": [pygame.image.load(f"graphics/Bosses/SikaDeer/Target/Right/{i}.png").convert_alpha() for i in range(0, len(os_listdir("graphics/Bosses/SikaDeer/Target/Right")))],

                            "Down": [pygame.image.load(f"graphics/Bosses/SikaDeer/Target/Down/{i}.png").convert_alpha() for i in range(0, len(os_listdir("graphics/Bosses/SikaDeer/Target/Down")))],
                            "Down Left": [pygame.transform.flip(surface = pygame.image.load(f"graphics/Bosses/SikaDeer/Target/DownRight/{i}.png").convert_alpha(), flip_x = True, flip_y = False) for i in range(0, len(os_listdir("graphics/Bosses/SikaDeer/Target/DownRight")))],
                            "Down Right": [pygame.image.load(f"graphics/Bosses/SikaDeer/Target/DownRight/{i}.png").convert_alpha() for i in range(0, len(os_listdir("graphics/Bosses/SikaDeer/Target/DownRight")))],
                            },
                    "Charge": {
                            "Up": [pygame.image.load(f"graphics/Bosses/SikaDeer/Charge/Up/{i}.png").convert_alpha() for i in range(0, len(os_listdir("graphics/Bosses/SikaDeer/Charge/Up")))],
                            "Up Left": [pygame.transform.flip(surface = pygame.image.load(f"graphics/Bosses/SikaDeer/Charge/UpRight/{i}.png").convert_alpha(), flip_x = True, flip_y = False) for i in range(0, len(os_listdir("graphics/Bosses/SikaDeer/Charge/UpRight")))],
                            "Up Right": [pygame.image.load(f"graphics/Bosses/SikaDeer/Charge/UpRight/{i}.png").convert_alpha() for i in range(0, len(os_listdir("graphics/Bosses/SikaDeer/Charge/UpRight")))],

                            "Left": [pygame.transform.flip(surface = pygame.image.load(f"graphics/Bosses/SikaDeer/Charge/Right/{i}.png").convert_alpha(), flip_x = True, flip_y = False) for i in range(0, len(os_listdir("graphics/Bosses/SikaDeer/Charge/Right")))],
                            "Right": [pygame.image.load(f"graphics/Bosses/SikaDeer/Charge/Right/{i}.png").convert_alpha() for i in range(0, len(os_listdir("graphics/Bosses/SikaDeer/Charge/Right")))],

                            "Down": [pygame.image.load(f"graphics/Bosses/SikaDeer/Charge/Down/{i}.png").convert_alpha() for i in range(0, len(os_listdir("graphics/Bosses/SikaDeer/Charge/Down")))],
                            "Down Left": [pygame.transform.flip(surface = pygame.image.load(f"graphics/Bosses/SikaDeer/Charge/DownRight/{i}.png").convert_alpha(), flip_x = True, flip_y = False) for i in range(0, len(os_listdir("graphics/Bosses/SikaDeer/Charge/DownRight")))],
                            "Down Right": [pygame.image.load(f"graphics/Bosses/SikaDeer/Charge/DownRight/{i}.png").convert_alpha() for i in range(0, len(os_listdir("graphics/Bosses/SikaDeer/Charge/DownRight")))],
                                
                                },
                    "Stunned": [pygame.image.load(f"graphics/Bosses/SikaDeer/Stunned/{i}.png").convert_alpha() for i in range(0, len(os_listdir("graphics/Bosses/SikaDeer/Stunned")))],


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
                self.stomp_attack_nodes_group = pygame.sprite.Group()
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

            # Update the current boss with the current position of the player
            self.boss_group.sprite.players_position = self.player.rect.center

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
            
        # Mouse position 
        self.game_ui.mouse_position = (self.player.mouse_position[0] - self.camera_position[0], self.player.mouse_position[1] - self.camera_position[1])

    def run(self, delta_time):

        # Fill the scaled surface with a colour
        self.scaled_surface.fill("cornsilk4")

        # Update the camera position 
        self.update_camera_position()


        # Spawn bamboo piles if enough time has passed since the last bamboo pile was spawned
        self.spawn_bamboo_pile(delta_time = delta_time)

        if pygame.key.get_pressed()[pygame.K_f] or (hasattr(self, "bosses_dict") == True and self.bosses_dict["TimeToSpawnTimer"] != None):
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
        
        # If the current boss is not alive
        elif self.boss_group.sprite != None and self.boss_group.sprite.extra_information_dict["CurrentHealth"] <= 0:
            # Update and run the boss
            self.update_and_run_boss(delta_time = delta_time)

            # Draw all objects inside the tile map / level
            self.draw_tile_map_objects()

            # Run the player methods
            self.player.run(delta_time = delta_time)
        # ---------------------------------------------------------

        # Update the game UI
        self.update_game_ui(delta_time = delta_time)

        # Run the game UI 
        self.game_ui.run(camera_position = self.camera_position)

        # Draw the scaled surface onto the screen
        self.screen.blit(pygame.transform.scale(self.scaled_surface, (screen_width, screen_height)), (0, 0))