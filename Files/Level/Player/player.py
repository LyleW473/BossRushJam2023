import pygame, os
from Global.generic import Generic
from Global.settings import *
from Level.Player.building_tile import BuildingTile
from Level.Player.bamboo_projectiles import BambooProjectile
from math import degrees, sin, cos, atan2, pi, dist

class Player(Generic):
    
    def __init__(self, x, y, surface, sprite_groups):
        
        # Surface that the player is drawn onto
        self.surface = surface

        # The sprite groups that the player interacts with
        self.sprite_groups = sprite_groups

        # ---------------------------------------------------------------------------------
        # Movement

        self.declare_movement_attributes()

        # ---------------------------------------------------------------------------------
        # Animations

        # Load the animation images
        self.load_animations()

        # Inherit from the Generic class, which has basic attributes and methods (The image is set to the thinnest image)
        Generic.__init__(self, x = x, y = y, image = self.animations_dict[self.current_player_element]["Idle"]["Right"][self.animation_index])

        # Inherit from pygame's sprite class
        pygame.sprite.Sprite.__init__(self) 

        # ---------------------------------------------------------------------------------
        # Collisions
        """
        self.camera_position = None # Position of the camera. This is updated inside "Game" class
        self.last_tile_position = None # Position of the last tile that the player can be on. This will be updated by "Game" when the level is created
        """
        self.neighbouring_tiles_dict = {} # Used to hold the neighbouring tiles near the player (i.e. within 1 tile of the player, movemently and vertically)
        self.dx = 0 # The distance the player can move based on if there were any collisions
        self.dy = 0 # The distance the player can move based on if there were any collisions

        # ---------------------------------------------------------------------------------
        # Angles
        """
        self.look_angle = 0
        """
        # ---------------------------------------------------------------------------------
        # Cursor guidelines

        # Thickness of each segment
        self.cursor_guidelines_segments_thickness = 5

        # Surface
        self.cursor_guidelines_surface = pygame.Surface((self.surface.get_width(), self.surface.get_height()))
        self.cursor_guidelines_surface.set_colorkey("black")
        self.cursor_guidelines_surface.set_alpha(90)

        # Cursor images
        self.default_cursor_image = pygame.image.load("graphics/Cursors/Default.png").convert_alpha()

        # ---------------------------------------------------------------------------------
        # Shooting, building etc.

        # Note: Time and cooldowns are measured in milliseconds

        # A dictionary containing information such as the HP the player has, the current tool equipped, amount of bamboo resource, etc.
        self.player_gameplay_info_dict = {
                                        "CurrentToolEquipped": "BambooAssaultRifle",
                                        "AmountOfBambooResource": 75,
                                        "MaximumAmountOfBambooResource": 120
                                         }

        # A dictionary containing the tools and information relating to those tools
        self.tools  =  {
                        "BuildingTool": {
                                        "Images": { 
                                            "IconImage": pygame.image.load("graphics/Weapons/BuildingTool/IconImage.png").convert_alpha(),
                                            "Up": pygame.image.load("graphics/Weapons/BuildingTool/Default.png").convert_alpha(),
                                            "TileImage": pygame.image.load("graphics/Weapons/BuildingTool/BuildingTile.png").convert()
                                                  },
                                        "MaximumBuildingTileHP": 100,
                                        "MaximumPlacingDistance": 5 * TILE_SIZE,
                                        "MinimumPlacingDistance": 2 * TILE_SIZE,
                                        "ExistingBuildingTilesDict": {},
                                        "RemovalCooldown": 200,
                                        "LastTileRemovedTimer": None,
                                        "BambooResourceDepletionAmount": 5
                                        },

                        "BambooAssaultRifle": { 
                            "Images" : {
                                "IconImage": pygame.image.load("graphics/Weapons/BambooAR/UpRight.png").convert_alpha(),
                                "Left": pygame.transform.flip(surface = pygame.image.load(f"graphics/Weapons/BambooAR/Right.png").convert_alpha(), flip_x = True, flip_y = False),
                                "Right": pygame.image.load("graphics/Weapons/BambooAR/Right.png").convert_alpha(),
                                "Up": pygame.image.load("graphics/Weapons/BambooAR/Up.png").convert_alpha(),
                                "Up Left": pygame.transform.flip(surface = pygame.image.load("graphics/Weapons/BambooAR/UpRight.png").convert_alpha(), flip_x = True, flip_y = False),"UpLeft": pygame.transform.flip(surface = pygame.image.load(f"graphics/Weapons/BambooAR/UpRight.png").convert_alpha(), flip_x = True, flip_y = False),
                                "Up Right": pygame.image.load("graphics/Weapons/BambooAR/UpRight.png").convert_alpha(),
                                "Down": pygame.transform.flip(surface = pygame.image.load("graphics/Weapons/BambooAR/Up.png").convert_alpha(), flip_x = False, flip_y = True),
                                "Down Left": pygame.transform.flip(surface = pygame.image.load("graphics/Weapons/BambooAR/DownRight.png").convert_alpha(), flip_x = True, flip_y = False),
                                "Down Right": pygame.image.load("graphics/Weapons/BambooAR/DownRight.png").convert_alpha()
                                        },
                            "ShootingCooldown": 150,
                            "ShootingCooldownTimer": 150, # 150 so that the player starts off being unable to shoot (after pressing the play button)
                            "BambooResourceDepletionAmount": 0.5
                                        
                                             },
                    
                        "BambooLauncher": {
                                            "ShootingCooldown": 0, 
                                            "PreviouslyShotTime": 0,
                                            "Images": {
                                                "IconImage": pygame.image.load("graphics/Weapons/BambooAR/DownRight.png").convert_alpha()
                                                      }
                                          },
                        }

    # ---------------------------------------------------------------------------------
    # Animations

    def load_animations(self):
        
        # Loads the animation images for the player and places them inside their respective dictionaries.

        # Set the default player version, state , player direction and look direction
        self.current_player_element = "Normal"
        self.current_animation_state = "Idle"
        self.player_direction = ["Down"]
        self.current_look_direction = "Down"

        # A dictionary that will hold all of the animations
        self.animations_dict = {"Normal": {
        "Idle": {
            "Left": [pygame.transform.flip(surface = pygame.image.load(f"graphics/Player/Normal/Idle/Right/{i}.png").convert_alpha(), flip_x = True, flip_y = False) for i in range(len(os.listdir("graphics/Player/Normal/Idle/Right")))],
            "Right": [pygame.image.load(f"graphics/Player/Normal/Idle/Right/{i}.png").convert_alpha() for i in range(len(os.listdir("graphics/Player/Normal/Idle/Right")))],
            "Up": [pygame.image.load(f"graphics/Player/Normal/Idle/Up/{i}.png").convert_alpha() for i in range(len(os.listdir("graphics/Player/Normal/Idle/Up")))],
            "Up Left": [pygame.transform.flip(surface = pygame.image.load(f"graphics/Player/Normal/Idle/UpRight/{i}.png").convert_alpha(), flip_x = True, flip_y = False) for i in range(len(os.listdir("graphics/Player/Normal/Idle/UpRight")))],
            "Up Right": [pygame.image.load(f"graphics/Player/Normal/Idle/UpRight/{i}.png").convert_alpha() for i in range(len(os.listdir("graphics/Player/Normal/Idle/UpRight")))],
            "Down": [pygame.image.load(f"graphics/Player/Normal/Idle/Down/{i}.png").convert_alpha() for i in range(len(os.listdir("graphics/Player/Normal/Idle/Down")))],
            "Down Left": [pygame.transform.flip(surface = pygame.image.load(f"graphics/Player/Normal/Idle/DownRight/{i}.png").convert_alpha(), flip_x = True, flip_y = False) for i in range(len(os.listdir("graphics/Player/Normal/Idle/DownRight")))],
            "Down Right": [pygame.image.load(f"graphics/Player/Normal/Idle/DownRight/{i}.png").convert_alpha() for i in range(len(os.listdir("graphics/Player/Normal/Idle/Downright")))],
                },
    
        "Run": {
            "Left": [pygame.transform.flip(surface = pygame.image.load( f"graphics/Player/Normal/Run/Body/Right/{i}.png").convert_alpha(), flip_x = True, flip_y = False) for i in range(len(os.listdir("graphics/Player/Normal/Run/Body/Right")))],
            "Right": [pygame.image.load(f"graphics/Player/Normal/Run/Body/Right/{i}.png").convert_alpha() for i in range(len(os.listdir("graphics/Player/Normal/Run/Body/Right")))],
            "Up": [pygame.image.load(f"graphics/Player/Normal/Run/Body/Up/{i}.png").convert_alpha() for i in range(len(os.listdir("graphics/Player/Normal/Run/Body/Up")))],
            "Down": [pygame.image.load(f"graphics/Player/Normal/Run/Body/Down/{i}.png").convert_alpha() for i in range(len(os.listdir("graphics/Player/Normal/Run/Body/Down")))],
               }
                                         }
                               }

        self.head_dict = {"Normal": {
            "Left": [pygame.transform.flip(surface = pygame.image.load(f"graphics/Player/Normal/Run/Head/Right/{i}.png").convert_alpha(), flip_x = True, flip_y = False) for i in range(len(os.listdir("graphics/Player/Normal/Run/Head/Right")))],
            "Right": [pygame.image.load(f"graphics/Player/Normal/Run/Head/Right/{i}.png").convert_alpha() for i in range(len(os.listdir("graphics/Player/Normal/Run/Head/Right")))],   
            "Up": [pygame.image.load(f"graphics/Player/Normal/Run/Head/Up/{i}.png").convert_alpha() for i in range(len(os.listdir("graphics/Player/Normal/Run/Head/Up")))],
            "Up Left": [pygame.transform.flip(surface = pygame.image.load(f"graphics/Player/Normal/Run/Head/UpRight/{i}.png").convert_alpha(), flip_x = True, flip_y = False) for i in range(len(os.listdir("graphics/Player/Normal/Run/Head/UpRight")))],
            "Up Right": [pygame.image.load(f"graphics/Player/Normal/Run/Head/UpRight/{i}.png").convert_alpha() for i in range(len(os.listdir("graphics/Player/Normal/Run/Head/UpRight")))],
            "Down": [pygame.image.load(f"graphics/Player/Normal/Run/Head/Down/{i}.png").convert_alpha() for i in range(len(os.listdir("graphics/Player/Normal/Run/Head/Down")))],
            "Down Left": [pygame.transform.flip(surface = pygame.image.load(f"graphics/Player/Normal/Run/Head/DownRight/{i}.png").convert_alpha(), flip_x = True, flip_y = False) for i in range(len(os.listdir("graphics/Player/Normal/Run/Head/DownRight")))],
            "Down Right": [pygame.image.load(f"graphics/Player/Normal/Run/Head/DownRight/{i}.png").convert_alpha() for i in range(len(os.listdir("graphics/Player/Normal/Run/Head/DownRight")))],   
                                    }
                        }

        # Create attributes used for the animations
        self.animation_index = 0 # Tracks which animation frame to show
        self.animation_frame_counter = 0 # Used to track how much time has passed since the last frame update
        
        # Dictionary to hold the time between each animation frame for each animation 
        # Values are in ms
        self.animation_frame_cooldowns_dict = {"Idle": 100,
                                            "Run": 100}

    def change_players_animation_state(self):

        # Changes the player's animation state if the conditions are met

        # If the player is moving left, right, up or down
        if pygame.key.get_pressed()[pygame.K_a] or pygame.key.get_pressed()[pygame.K_d] or pygame.key.get_pressed()[pygame.K_w] or pygame.key.get_pressed()[pygame.K_s]:

            """ 
            Play the idle animation:
                - If the player is at the beginning or end of the tile map
                or 
                - If the player is colliding with a neighbouring tile in the direction that the player is going in
                - If there are two directions the player is going and there is a collision on both directions
                - If the player isn't pressing any of the movement input keys (The elif statement)
            """
            # If this dictionary does not already exist
            if hasattr(self, "direction_collisions") == False:
                # Create a dictionary that holds the collisions in the direction that the player is facing
                self.direction_collisions = {
                                            "Left": pygame.Rect(self.rect.x - 5, self.rect.y, self.rect.width, self.rect.height),
                                            "Right": pygame.Rect(self.rect.x + 5, self.rect.y, self.rect.width, self.rect.height),
                                            "Up": pygame.Rect(self.rect.x, self.rect.y - 5, self.rect.width, self.rect.height),
                                            "Down": pygame.Rect(self.rect.x, self.rect.y + 5, self.rect.width, self.rect.height)
                                            }
            # If this dictionary already exists
            else:
                # Update the dictionary's rect values
                self.direction_collisions["Left"]  = pygame.Rect(self.rect.x - 5, self.rect.y, self.rect.width, self.rect.height)
                self.direction_collisions["Right"] = pygame.Rect(self.rect.x + 5, self.rect.y, self.rect.width, self.rect.height)
                self.direction_collisions["Up"] = pygame.Rect(self.rect.x, self.rect.y - 5, self.rect.width, self.rect.height)
                self.direction_collisions["Down"]  = pygame.Rect(self.rect.x, self.rect.y + 5, self.rect.width, self.rect.height)

            # Create a tuple of the directions the player is currently moving in
            current_directions = [key for key in self.direction_variables_dict.keys() if self.direction_variables_dict[key] == True]

            if (self.rect.x == 0 or self.rect.right == self.last_tile_position[0]) or \
                len(current_directions) == 1 and self.direction_collisions[current_directions[0]] != None and self.direction_collisions[current_directions[0]].collidedict(self.neighbouring_tiles_dict) != None or \
                len(current_directions) == 2 and (self.direction_collisions[current_directions[0]] != None and self.direction_collisions[current_directions[1]] != None) and \
                (self.direction_collisions[current_directions[0]].collidedict(self.neighbouring_tiles_dict) != None and self.direction_collisions[current_directions[1]].collidedict(self.neighbouring_tiles_dict) != None):

                # If the current animation state has not been set to "Idle" yet
                if self.current_animation_state != "Idle":
                    # Set the current animation state to "Idle"
                    self.current_animation_state = "Idle"

                    # Reset the animation frame counter and index
                    self.animation_frame_counter = 0
                    self.animation_index = 0

            # If the player isn't colliding with a neighbouring tile or is not at the beginning or end of the tile map
            else:
                # If the current animation state has not been set to "Run" yet
                if self.current_animation_state != "Run":
                    # Set the current animation state to "Run"
                    self.current_animation_state = "Run"

                    # Reset the animation frame counter and index
                    self.animation_frame_counter = 0
                    self.animation_index = 0

        # If the player has stopped running left or right
        elif pygame.key.get_pressed()[pygame.K_a] == False and pygame.key.get_pressed()[pygame.K_d] == False and pygame.key.get_pressed()[pygame.K_w] == False and pygame.key.get_pressed()[pygame.K_s] == False:

            # If the current animation state has not been set to "Idle" yet
            if self.current_animation_state != "Idle":
                
                # # If the player has stopped running
                # if self.current_animation_state == "Run":
                # Set the current animation state to "Idle"
                self.current_animation_state = "Idle"

                # Reset the animation frame counter and index
                self.animation_frame_counter = 0
                self.animation_index = 0

    def play_animations(self):

        # Plays the animations of the player

        # Check whether we need to change the player's animation state based on what the player is doing
        self.change_players_animation_state()

        # Increment the animation frame counter based on time
        self.animation_frame_counter += 1000 * self.delta_time

        # --------------------------------------
        # Identifying the direction that the player is looking toward.
        """ 
        Note: This is used to:
            - Assign which idle animation should be playing if the player is shooting depending on where the player is shooting
            - Assign the correct head onto the torso depending on where the player is looking
        
        Note 2: 360 / 8 (8 directions), = 45, offset everything by half of that so that each direction has a cone like radius 
        """
        segment_offset = 45 / 2

        match self.look_angle:
            # Right
            case _ if (0 <= degrees(self.look_angle) < segment_offset) or ((360 - segment_offset) <= degrees(self.look_angle) < 360):
                self.current_look_direction = "Right"
            # UpRight
            case _ if (segment_offset <= degrees(self.look_angle) < segment_offset + 45):
                self.current_look_direction = "Up Right"
            # Up
            case _ if (90 - segment_offset) <= degrees(self.look_angle) < (90 + segment_offset):
                self.current_look_direction = "Up"
            # UpLeft
            case _ if (90 + segment_offset) <= degrees(self.look_angle) < (90 + segment_offset + 45):
                self.current_look_direction = "Up Left"
            # Left
            case _ if (180 - segment_offset) <= degrees(self.look_angle) < (180 + segment_offset):
                self.current_look_direction = "Left"
            # DownLeft
            case _ if (180 + segment_offset) <= degrees(self.look_angle) < (180 + segment_offset + 45):
                self.current_look_direction = "Down Left"
            # Down
            case _ if (270 - segment_offset) <= degrees(self.look_angle) < (270 + segment_offset):
                self.current_look_direction = "Down" 
            # DownRight
            case _ if (270 + segment_offset) <= degrees(self.look_angle) < (270 + segment_offset + 45):
                self.current_look_direction = "Down Right"

        # --------------------------------------
        # Assigning animation list and image

        """ Temporary variables to store the: 
            - Current player animation state's list, e.g. The list containing the images of the "Idle" animation
            - The current animation image
            """
        # Idle animation state
        if self.current_animation_state == "Idle":
            # If there is only one direction the player is going in (i.e. Left, Right, Up or Down)
            if len(self.player_direction) == 1:
                current_player_state_animation_list = self.animations_dict[self.current_player_element][self.current_animation_state][self.player_direction[0]]
                current_animation_image = self.animations_dict[self.current_player_element][self.current_animation_state][self.player_direction[0]][self.animation_index]
            
            # If there are two directions the player is going in (i.e Up Left, Up Right, Down Left, Down Right)
            elif len(self.player_direction) > 1:
                # Concatenate the strings (e.g. Up Right
                two_direction = self.player_direction[0] + " " + self.player_direction[1]
                current_player_state_animation_list = self.animations_dict[self.current_player_element][self.current_animation_state][two_direction]
                current_animation_image = self.animations_dict[self.current_player_element][self.current_animation_state][two_direction][self.animation_index]

        # Run animation state
        if self.current_animation_state == "Run":
            """ 
            Note: Only the first player direction is checked, therefore if the playing was moving Up and Right, the player direction would be ["Right", "Up"], as the x direction is checked before the y direction.
            - If the player is running Right, the body will face Right as long as the player looks between Up, Up Right, Right and Down Right, Down. Otherwise, the body will face in the direction the player is pointing towards.
              (The same applies for all directions i.e. Up, Down, Left and Right)
            """
            # Moving up or down
            if self.player_direction[0] == "Up" or self.player_direction[0] == "Down":

                # If the player is looking towards any direction in front of where they are moving
                # E.g. Moving down and looking Left, DownLeft, Down, DownRight, Right
                if (self.player_direction[0] == "Down" and 180 <= degrees(self.look_angle) < 360) or (self.player_direction[0] == "Up" and 0 <= degrees(self.look_angle) < 180):
                    # Set the body (torso) to point towards where the player is moving
                    current_player_state_animation_list = self.animations_dict[self.current_player_element][self.current_animation_state][self.player_direction[0]]
                    current_animation_image = self.animations_dict[self.current_player_element][self.current_animation_state][self.player_direction[0]][self.animation_index]

                # If the player is looking towards the opposite direction of where the player is moving towards
                else:
                    if 0 <= degrees(self.look_angle) < 180 :
                        body_direction = "Up"
                    elif 180 <= degrees(self.look_angle) < 360:
                        body_direction = "Down"
                    
                    # Set the body (torso) to point towards where the player is looking towards (with the mouse)
                    current_player_state_animation_list = self.animations_dict[self.current_player_element][self.current_animation_state][body_direction]
                    current_animation_image = self.animations_dict[self.current_player_element][self.current_animation_state][body_direction][self.animation_index]

            # Moving left or right
            if self.player_direction[0] == "Left" or self.player_direction[0] == "Right":
                # If the player is looking towards any direction in front of where they are moving
                # E.g. Moving Left and looking Up, UpLeft, Left, DownLeft, Down
                if self.player_direction[0] == "Right" and (0 <= degrees(self.look_angle) < 90 or 270 <= degrees(self.look_angle) < 360) or \
                    self.player_direction[0] == "Left" and (90 <= degrees(self.look_angle) < 270):

                    # Set the body (torso) to point towards where the player is moving
                    current_player_state_animation_list = self.animations_dict[self.current_player_element][self.current_animation_state][self.player_direction[0]]
                    current_animation_image = self.animations_dict[self.current_player_element][self.current_animation_state][self.player_direction[0]][self.animation_index]
                
                # If the player is looking towards the opposite direction of where the player is moving towards
                else:
                    # If the player is looking left
                    if self.player_direction[0] == "Left":
                        if degrees(self.look_angle) <= 90 :
                            body_direction = "Up"
                        elif degrees(self.look_angle) >= 270:
                            body_direction = "Down"
                    
                    # If the player is looking right
                    elif self.player_direction[0] == "Right":
                        if 180 <= degrees(self.look_angle) <= 270:
                            body_direction = "Down"
                        elif 90 <= degrees(self.look_angle) < 180:
                            body_direction = "Up"

                    # Set the body (torso) to point towards where the player is looking towards (with the mouse)
                    current_player_state_animation_list = self.animations_dict[self.current_player_element][self.current_animation_state][body_direction]
                    current_animation_image = self.animations_dict[self.current_player_element][self.current_animation_state][body_direction][self.animation_index]

        # ---------------------------------------------------------------------------------
        # Set the image to be this animation frame
        self.image = current_animation_image

        # ---------------------------------------------------------------------------------
        # Changing the animation frame

        # Update the animation frames based on the current animation state
        match self.current_animation_state:

            case "Idle":
                # If enough time has passed since the last frame was played or since the animation was reset
                if self.animation_frame_counter >= self.animation_frame_cooldowns_dict["Idle"]:

                    # If the animation index isn't at the end of the list 
                    if self.animation_index < (len(current_player_state_animation_list) - 1):
                        # Increment the animation index
                        self.animation_index += 1

                    # If the animation index is at the end of the list
                    else:
                        # Reset the animation index
                        self.animation_index = 0
                
                    # Reset the animation frame counter
                    self.animation_frame_counter = 0

            case "Run":
                # If enough time has passed since the last frame was played or since the animation was reset
                if self.animation_frame_counter >= self.animation_frame_cooldowns_dict["Run"]:

                    # If the animation index isn't at the end of the list 
                    if self.animation_index < (len(current_player_state_animation_list) - 1):
                        # Increment the animation index
                        self.animation_index += 1

                    # If the animation index is at the end of the list
                    else:
                        # Reset the animation index
                        self.animation_index = 0
                
                    # Reset the animation frame counter
                    self.animation_frame_counter = 0

        # ---------------------------------------------------------------------------------
        # Draw the player onto the main screen

        """
        - The camera position must be subtracted so that the image is drawn within the limits of the screen.
        - Half of the image width and height is subtracted so that the rotation of the player image is centered within the player rect.
        """
        pygame.draw.rect(self.surface, "purple", (self.rect.x - self.camera_position[0], self.rect.y - self.camera_position[1], self.rect.width, self.rect.height), 0)
        
        # If the current animation state is "Run"
        if self.current_animation_state == "Run":

            # ---------------------------------------------------------------------------------
            # Assigning the head image
            head_image = self.head_dict[self.current_player_element][self.current_look_direction][self.animation_index]
        
            # ---------------------------------------------------------------------------------
            # Drawing the torso and the head

            # Temporary variable for the position that the torso should be drawn at
            torso_position = ((self.rect.centerx - self.camera_position[0]) - int(self.image.get_width() / 2), (self.rect.midbottom[1] - self.image.get_height() - self.camera_position[1]))

            # Draw the torso at the bottom of the player rect
            self.draw(surface = self.surface, x = torso_position[0], y = torso_position[1])

            # Adjusting the head image depending on the direction the player is looking towards
            # Note: This is because for some directions, the head may be placed too high or too low
            match self.current_look_direction:
                # Up
                case _ if self.current_look_direction == "Up Left" or self.current_look_direction == "Up" or self.current_look_direction == "Up Right":
                    head_adjustment_y = 2
                # Down
                case _ if self.current_look_direction == "Down Left" or self.current_look_direction == "Down" or self.current_look_direction == "Down Right":
                    head_adjustment_y = 3
                # Left or right
                case _ if self.current_look_direction == "Left" or self.current_look_direction == "Right":
                    head_adjustment_y = 0

            # Draw the head on top the torso
            self.surface.blit(head_image, ((self.rect.centerx - self.camera_position[0]) - int(head_image.get_width()/ 2), head_adjustment_y + torso_position[1] - head_image.get_height()))

        # If the current animation state is "Idle" and the player is pressing the left mouse button
        elif self.current_animation_state == "Idle":

            # If the player is pressing the left mouse button
            if pygame.mouse.get_pressed()[0] == True:
                """ There is an error where the animation index is not reset when switching to this "shooting idle" animation. 
                Therefore, if the animation index + 1 is greater than the number of frames in the current animation list, the animation index should be reset.
                """
                if (self.animation_index + 1) > len(self.animations_dict[self.current_player_element]["Idle"][self.current_look_direction]):
                    # Reset the animation index
                    self.animation_index = 0

                # ------------------------------------------------------------------------------------------------------------
                # Updating the player direction so that the player will point to that direction once the player stops shooting

                # Count the number of capital letters inside the string
                capital_letter_count = sum(map(str.isupper, self.current_look_direction))

                # If there is only 1 capital letter, then current direction is one direction e.g. Right
                if capital_letter_count == 1:
                    self.player_direction = [self.current_look_direction]

                # If there are 2 capital letters, then the current direction is two directions e.g Up Left
                elif capital_letter_count == 2:
                    # Set the player direction into a list consisting of the two directions the player is facing. E.g. ["Up", "Left"]
                    self.player_direction = self.current_look_direction.split()

                # Set the image to be the images that correspond with the direction that the player is facing
                self.image = self.animations_dict[self.current_player_element]["Idle"][self.current_look_direction][self.animation_index]

            # Draw the idle animation
            self.draw(surface = self.surface, x = (self.rect.centerx - self.camera_position[0]) - int(self.image.get_width() / 2), y = (self.rect.centery - self.camera_position[1]) - int(self.image.get_height() / 2))
    
    # ---------------------------------------------------------------------------------
    # Movement       

    def declare_movement_attributes(self):

        # Declares all the movement attributes (used to avoid "crowding" in the init method)

        """
        self.delta_time = delta_time (Used for framerate independence)

        """
        # Dictionary that holds which direction the player is currently facing 
        self.direction_variables_dict = {"Up": False, "Down": False ,"Left": False, "Right": False}

        # ---------------------------------------
        # Movement

        # Set the initial movement velocity to be 0
        self.movement_suvat_u = 0
        # The movement distance the player can move
        self.movement_suvat_s = 0

        # Calculate the velocity that the player moves at given a distance that the player travels within a given time span

        # After re-arranging s = vt + 1/2(a)(t^2), v is given by the equation: (2s - a(t)^2) / 2t, where a is 0 because acceleration is constant
        time_to_travel_distance_at_final_movement_velocity = 0.5 # t
        distance_travelled_at_final_movement_velocity = 4 * TILE_SIZE # s 
        # Full version: self.movement_suvat_v = ((2 * distance_travelled_at_final_movement_velocity) - (0 * (time_to_travel_distance_at_final_movement_velocity ** 2)) / (2 * time_to_travel_distance_at_final_movement_velocity))
        # Simplified version:
        self.movement_suvat_v = ((2 * distance_travelled_at_final_movement_velocity) / (2 * time_to_travel_distance_at_final_movement_velocity))

        # Calculate the acceleration needed for the player to reach self.movement_suvat_v within a given time span

        # After re-arranging v = u + at, a is given by the equation: (v - u) / t, where u is 0
        time_to_reach_final_movement_velocity = 0.15
        # Full version: self.movement_suvat_a = (self.movement_suvat_v - 0) / time_to_reach_final_movement_velocity
        # Simplified version:
        self.movement_suvat_a = self.movement_suvat_v / time_to_reach_final_movement_velocity

        # Deceleration
        self.decelerating = False
        
        # Calculate the deceleration required for the player to decelerate from the final movement velocity to 0 (Store as absolute value)

        # After re-arranging v = u + at, a is given by the equation: (v - u) / t, where v is 0
        self.time_taken_to_decelerate_from_final_movement_velocity = 0.10
        # Full version: self.deceleration_from_final_movement_velocity = abs((0 - self.movement_suvat_v) / time_taken_to_decelerate_from_final_movement_velocity)
        # Simplified version:
        self.deceleration_from_final_movement_velocity = self.movement_suvat_v / self.time_taken_to_decelerate_from_final_movement_velocity
    
    def update_direction_variables(self):

        # Updates the direction variables inside the dictionary direction variables dictionary. Creates a list of the direction the player is moving towards.

        # Left
        if pygame.key.get_pressed()[pygame.K_a] == False:
            self.direction_variables_dict["Left"] = False
        elif pygame.key.get_pressed()[pygame.K_a] == True:
            self.direction_variables_dict["Left"] = True
        
        # Right
        if pygame.key.get_pressed()[pygame.K_d] == False:
            self.direction_variables_dict["Right"] = False
        elif pygame.key.get_pressed()[pygame.K_d] == True:
            self.direction_variables_dict["Right"] = True
        # Up
        if pygame.key.get_pressed()[pygame.K_w] == False:
            self.direction_variables_dict["Up"] = False
        elif pygame.key.get_pressed()[pygame.K_w] == True:
            self.direction_variables_dict["Up"] = True
        # Down
        if pygame.key.get_pressed()[pygame.K_s] == False:
            self.direction_variables_dict["Down"] = False
        elif pygame.key.get_pressed()[pygame.K_s] == True:
            self.direction_variables_dict["Down"] = True

        # Create a list that stores the direction(s) that the player is moving towards
        self.player_direction = [key for key in self.direction_variables_dict.keys() if self.direction_variables_dict[key] == True]

    def movement_acceleration(self):

        # Executes the movement acceleration of the player

        # If the current velocity has not reached the final velocity set for the player
        if self.movement_suvat_u < self.movement_suvat_v:
            # Increase the current velocity
            self.movement_suvat_u += (self.movement_suvat_a * self.delta_time)

        # Limit the current velocity to the final velocity set for the player (in case that the current velocity is greater)
        self.movement_suvat_u = min(self.movement_suvat_u, self.movement_suvat_v)

        # Set the distance travelled based on the current velocity
        self.movement_suvat_s = ((self.movement_suvat_u * self.delta_time) + (0.5 * self.movement_suvat_a * (self.delta_time ** 2)))

    def handle_player_movement(self):

        # Handles the movement of the player

        # (For floating point accuracy)
        next_position_x = self.rect.x
        next_position_y = self.rect.y

        # If the "a" key is pressed
        if pygame.key.get_pressed()[pygame.K_a] and pygame.key.get_pressed()[pygame.K_d] == False:

            # If the player is decelerating currently
            if self.decelerating == True:
                # Stop decelerating
                self.decelerating = False

            # Update the direction variables
            self.update_direction_variables()

            # If the player isn't decelerating currently
            if self.decelerating == False:

                # ---------------------------------------------------------------------------------
                # Acceleration

                # Execute the movement acceleration method
                self.movement_acceleration()

                # ---------------------------------------------------------------------------------
                # Moving the player

                # If moving left will place the player out of the screen
                if self.rect.left - self.movement_suvat_s <= 0:
                    # Set the player's x position to be at 0
                    self.rect.left = 0

                # Otherwise
                elif self.rect.left - self.movement_suvat_s > 0:
                    # Move the player left
                    next_position_x -= self.dx
                    self.rect.x = round(next_position_x)

        # If the "d" key is pressed
        elif pygame.key.get_pressed()[pygame.K_d] and pygame.key.get_pressed()[pygame.K_a] == False:

            # If the player is decelerating currently
            if self.decelerating == True:
                # Stop decelerating
                self.decelerating = False
            
            # Update the direction variables
            self.update_direction_variables()

            # If the player isn't decelerating currently
            if self.decelerating == False:
                
                # ---------------------------------------------------------------------------------
                # Acceleration

                # Execute the movement acceleration method
                self.movement_acceleration()

                # ---------------------------------------------------------------------------------
                # Moving the player

                # If moving right will place the player out of the tile map / out of the screen
                if self.rect.right + self.movement_suvat_s >= self.last_tile_position[0]:
                    # Set the player's right position to be at the last tile position in the tile map
                    self.rect.right = self.last_tile_position[0]

                # Otherwise
                elif self.rect.right + self.movement_suvat_s < self.last_tile_position[0]:
                    # Move the player right
                    next_position_x += self.dx
                    self.rect.x = round(next_position_x)

        # If the "w" key is pressed
        if pygame.key.get_pressed()[pygame.K_w] and pygame.key.get_pressed()[pygame.K_s] == False:

            # If the player is decelerating currently
            if self.decelerating == True:
                # Stop decelerating
                self.decelerating = False
            
            # Update the direction variables
            self.update_direction_variables()

            # If the player isn't decelerating currently
            if self.decelerating == False:
                
                # ---------------------------------------------------------------------------------
                # Acceleration

                # Execute the movement acceleration method
                self.movement_acceleration()

                # ---------------------------------------------------------------------------------
                # Moving the player

                # If moving up will place the player out of the screen
                if self.rect.top - self.movement_suvat_s < 0:
                    # Set the player's top position to be at the top of the screen 
                    self.rect.top = 0

                # Otherwise
                elif self.rect.top - self.movement_suvat_s >= 0:
                    # Move the player up
                    next_position_y -= self.dy
                    self.rect.y = round(next_position_y)

        # If the "s" key is pressed
        elif pygame.key.get_pressed()[pygame.K_s] and pygame.key.get_pressed()[pygame.K_w] == False:

            # If the player is decelerating currently
            if self.decelerating == True:
                # Stop decelerating
                self.decelerating = False

            # Update the direction variables
            self.update_direction_variables()

            # If the player isn't decelerating currently
            if self.decelerating == False:
                
                # ---------------------------------------------------------------------------------
                # Acceleration

                # Execute the movement acceleration method
                self.movement_acceleration()

                # ---------------------------------------------------------------------------------
                # Moving the player

                # If moving down will place the player out of the tile map
                if self.rect.bottom + self.movement_suvat_s > self.last_tile_position[1]:
                    # Set the player's bottom position to the y position of the last tile position
                    self.rect.bottom = self.last_tile_position[1] 

                # Otherwise
                elif self.rect.bottom + self.movement_suvat_s <= self.last_tile_position[1]:
                    # Move the player down
                    next_position_y += self.dy
                    self.rect.y = round(next_position_y)

        # ---------------------------------------------------------------------------------
        # Deceleration

        # If the player has let go of all movement input keys or if the deceleration has already started
        if (pygame.key.get_pressed()[pygame.K_a] == False and pygame.key.get_pressed()[pygame.K_d] == False and pygame.key.get_pressed()[pygame.K_w] == False and pygame.key.get_pressed()[pygame.K_s] == False and self.movement_suvat_u > 0) or self.decelerating == True:

            # (For floating point accuracy)
            # Note: This is declared here because self.rect.x or self.rect.y may have changed 
            next_position_x_2 = self.rect.x
            next_position_y_2 = self.rect.y
                
            if self.decelerating == False:
                # Set the decelerating player attribute to True
                self.decelerating = True

            # If the player has stopped decelerating
            if self.movement_suvat_u <= 0:
                # Set the decelerating player attribute back to False
                self.decelerating = False
                # If the current velocity of the player is less than 0
                if self.movement_suvat_u < 0:
                    # Set the current velocity to 0
                    self.movement_suvat_u = 0

            # If the player's current velocity is greater than 0
            if self.movement_suvat_u > 0:
                # Decelerate the player / decrease the velocity
                self.movement_suvat_u -= (self.deceleration_from_final_movement_velocity * self.delta_time)

            # Limit the current velocity to 0
            self.movement_suvat_u = max(self.movement_suvat_u, 0)

            # Set the distance travelled based on the current velocity
            self.movement_suvat_s = ((self.movement_suvat_u * self.delta_time) + (0.5 * self.movement_suvat_a * (self.delta_time ** 2)))

            # Handle tile collisions again
            # Note: When decelerating, dx will have to keep changing
            self.handle_tile_collisions()

            # ---------------------------------------------------------------------------------
            # Decelerating in the last direction the player was moving towards

            # If the player was moving right
            if self.direction_variables_dict["Right"] == True:

                # If moving right will place the player out of the tile map / out of the screen
                if self.rect.right + self.movement_suvat_s >= self.last_tile_position[0]:
                    # Set the player's right position to be at the last tile position in the tile map
                    self.rect.right = self.last_tile_position[0]

                # Otherwise
                elif self.rect.right + self.movement_suvat_s < self.last_tile_position[0]:
                    # Move the player right
                    next_position_x_2 += self.dx
                    self.rect.x = round(next_position_x_2)

            # If the player was moving left
            elif self.direction_variables_dict["Left"] == True:
    
                # If moving left will place the player out of the screen
                if self.rect.left - self.movement_suvat_s <= 0:
                    # Set the player's x position to be at 0
                    self.rect.left = 0

                # Otherwise
                elif self.rect.left - self.movement_suvat_s > 0:
                    # Move the player left
                    next_position_x_2 -= self.dx
                    self.rect.x = round(next_position_x_2)

            # If the player was moving up
            elif self.direction_variables_dict["Up"] == True:

                # If moving up will place the player out of the screen
                if self.rect.top - self.movement_suvat_s < 0:
                    # Set the player's top position to be at the top of the screen 
                    self.rect.top = 0

                # Otherwise
                elif self.rect.top - self.movement_suvat_s >= 0:
                    # Move the player up
                    next_position_y_2 -= self.dy
                    self.rect.y = round(next_position_y_2)
            
            # If the player was moving down
            elif self.direction_variables_dict["Down"] == True:
                
                # If moving down will place the player out of the tile map
                if self.rect.bottom + self.movement_suvat_s > self.last_tile_position[1]:
                    # Set the player's bottom position to the y position of the last tile position
                    self.rect.bottom = self.last_tile_position[1] 

                # Otherwise
                elif self.rect.bottom + self.movement_suvat_s <= self.last_tile_position[1]:
                    # Move the player down
                    next_position_y_2 += self.dy
                    self.rect.y = round(next_position_y_2)

    # ---------------------------------------------------------------------------------
    # Collisions      
                          
    def handle_tile_collisions(self):
        
        # Handles tile collisions

        # ---------------------------------------------------------------------------------
        # Horizontal collisions

        # If the player is attempting to move left
        if self.direction_variables_dict["Left"] == True:
            # Check for collisions to the left of the player
            x_collisions = pygame.Rect(round(self.rect.x - self.movement_suvat_s), self.rect.y, self.rect.width, self.rect.height).collidedict(self.neighbouring_tiles_dict)

        # If the player is attempting to move right
        elif self.direction_variables_dict["Right"] == True:
            # Check for collisions to the right of the player
            x_collisions = pygame.Rect(round(self.rect.x + self.movement_suvat_s), self.rect.y, self.rect.width, self.rect.height).collidedict(self.neighbouring_tiles_dict)

        # If the player is not attempting to move left or right
        elif self.direction_variables_dict["Left"] == False and self.direction_variables_dict["Right"] == False:
            # Set x collisions to None
            x_collisions = None 

        # If the player is attempting to move left or right
        """ Note: This is because x_collisions could be none either when:
            - There is no horizontal collision but the player is trying to move left or right
            - The player is trying to move up or down 
        """
        if (self.direction_variables_dict["Left"] == True or self.direction_variables_dict["Right"] == True):

            # If there is a horizontal collision
            if x_collisions != None:
                pygame.draw.rect(self.surface, "green", (x_collisions[0].rect.x - self.camera_position[0], x_collisions[0].rect.y - self.camera_position[1], x_collisions[0].rect.width, x_collisions[0].rect.height))

                # If the player is facing right (i.e. moving right)
                if self.direction_variables_dict["Right"] == True:
                    # The player's right should be the tile's left
                    self.rect.right = x_collisions[0].rect.left

                # If the player is facing left (i.e. moving left)
                elif self.direction_variables_dict["Left"] == True:
                    # The player's left should be the tile's right
                    self.rect.left = x_collisions[0].rect.right
                
                # Set dx to be 0, so that the player does not move
                self.dx = 0

            # If there is no horizontal collision (and the player intended to move left or right)
            elif x_collisions == None:
                # Move the player by the movement distance
                self.dx = self.movement_suvat_s

        # ---------------------------------------------------------------------------------
        # Vertical collisions      

        # If the player is attempting to move up
        if self.direction_variables_dict["Up"] == True:
            # Check for collisions above the player
            y_collisions = pygame.Rect(self.rect.x, round(self.rect.y - self.movement_suvat_s), self.rect.width, self.rect.height).collidedict(self.neighbouring_tiles_dict)      

        # If the player is attempting to move down
        elif self.direction_variables_dict["Down"] == True:
            # Check for collisions below the player
            y_collisions = pygame.Rect(self.rect.x, round(self.rect.y + self.movement_suvat_s), self.rect.width, self.rect.height).collidedict(self.neighbouring_tiles_dict)      

        # If the player is not attempting to move up or down
        elif self.direction_variables_dict["Up"] == False and self.direction_variables_dict["Down"] == False:
            # Set y collisions to None
            y_collisions = None

        # If the player is attempting to move up or down
        """ Note: This is because y_collisions could be none either when:
            - There is no vertical collision but the player is trying to move up or down
            - The player is trying to move left or right
        """
        if (self.direction_variables_dict["Up"] == True or self.direction_variables_dict["Down"] == True):

            # If there is a vertical collision    
            if y_collisions != None:
                pygame.draw.rect(self.surface, "green", (y_collisions[0].rect.x - self.camera_position[0], y_collisions[0].rect.y - self.camera_position[1], y_collisions[0].rect.width, y_collisions[0].rect.height))

                # If the player is attempting to move up
                if self.direction_variables_dict["Up"] == True:
                    # The player's top should be the tile's bottom
                    self.rect.top = y_collisions[0].rect.bottom

                # If the player is attempting to move down
                elif self.direction_variables_dict["Down"] == True:
                    # The player's bottom should be the tile's top
                    self.rect.bottom = y_collisions[0].rect.top
                
                # Set dy to be 0, so that the player does not move
                self.dy = 0

            # If there is no vertical collision
            elif y_collisions == None and (self.direction_variables_dict["Up"] == True or self.direction_variables_dict["Down"] == True):
                # Move the player by the movement distance
                self.dy = self.movement_suvat_s

    # ---------------------------------------------------------------------------------
    # Mouse

    def find_mouse_position_and_angle(self):

        # Finds the mouse position according to the position inside the tile map. Finds the angle between the center of the player and the mouse.

        # Retrieve the mouse position
        """
        - The scale multiplier refers to how much the surface that everything will be drawn onto has been scaled by 
        """
        mouse_position = pygame.mouse.get_pos()  
        scale_multiplier = (screen_width / self.surface.get_width(), screen_height / self.surface.get_height())
        self.mouse_position = ((mouse_position[0] / scale_multiplier[0]) + self.camera_position[0] , (mouse_position[1] / scale_multiplier[1]) + self.camera_position[1])

        # Find the distance between the mouse and the center of the player in their horizontal and vertical components
        dx, dy = self.mouse_position[0] - self.rect.centerx, self.mouse_position[1] - self.rect.centery
        
        # Find the angle between the mouse and the center of the player
        """
        - Modulo is so that the value of angle will always be in between 0 and 2pi.
        - If the angle is negative, it will be added to 2pi.
        - "-dy" because the y axis is flipped in PYgame
        """
        self.look_angle = atan2(-dy, dx) % (2 * pi)

        # Draw the new cursor
        # Blit the cursor image at the mouse position divided by the scale multiplier, subtracting half of the cursor image's width and height
        self.surface.blit(self.default_cursor_image, ((self.mouse_position[0] - self.camera_position[0]) - (self.default_cursor_image.get_width()/ 2), (self.mouse_position[1] - self.camera_position[1]) - (self.default_cursor_image.get_height() / 2)))

        # Draw the guidelines to the mouse cursor
        self.draw_guidelines_to_cursor(dx, dy)

    def draw_guidelines_to_cursor(self, dx, dy):

        # Draws the guidelines to the mouse cursor / position

        # The number of segments desired for the guidelines
        number_of_segments = 6
        
        # Calculate the length of each segment 
        segment_length_x = dx / (number_of_segments * 2)
        segment_length_y = dy / (number_of_segments * 2)

        # Fill the cursor guidelines surface with black. (The colour-key has been set to black)
        self.cursor_guidelines_surface.fill("black")

        # Draw
        for i in range(1, (number_of_segments * 2) + 1, 2):     
            pygame.draw.line(
                surface = self.cursor_guidelines_surface, 
                color = "white",
                start_pos = ((self.rect.centerx - self.camera_position[0]) + (segment_length_x * i), (self.rect.centery - self.camera_position[1]) + (segment_length_y * i)),
                end_pos = ((self.rect.centerx - self.camera_position[0]) + (segment_length_x * (i + 1)), (self.rect.centery - self.camera_position[1]) + (segment_length_y * (i + 1))),
                width = self.cursor_guidelines_segments_thickness)

        # Draw the cursor guidelines surface onto the main surface
        self.surface.blit(self.cursor_guidelines_surface, (0, 0))

    # ---------------------------------------------------------------------------------
    # Gameplay

    def switch_tool(self, tool):

        # Switches between tools
        
        # If the current tool is not the tool the player wants to switch to
        if self.player_gameplay_info_dict["CurrentToolEquipped"] != tool:
            # Switch to the tool
            self.player_gameplay_info_dict["CurrentToolEquipped"] = tool
    
    def draw_player_tool(self):

        # Draws the weapon onto main surface
        
        # If the player is pressing the left mouse button
        if pygame.mouse.get_pressed()[0]:

            if self.player_gameplay_info_dict["CurrentToolEquipped"] == "BuildingTool":
                tool_image = self.tools[self.player_gameplay_info_dict["CurrentToolEquipped"]]["Images"]["Up"]

            if self.player_gameplay_info_dict["CurrentToolEquipped"] != "BuildingTool":
                # Assign the weapon image
                tool_image = self.tools[self.player_gameplay_info_dict["CurrentToolEquipped"]]["Images"][self.current_look_direction]
            
            # The following distance will ensure that the weapon is always "hypot_distance" away from the center of the player
            hypot_distance = 10
            distance_x = hypot_distance * cos(self.look_angle)
            distance_y = hypot_distance * sin(self.look_angle)
            
            # Depending on the current look direction, 
            match self.current_look_direction:
                
                # (For up and down, the weapon is centered more with a "-5")
                case _ if self.current_look_direction == "Up" or self.current_look_direction == "Down":
                    self.weapon_position = (
                        ((self.rect.centerx - 5)) + distance_x, 
                        ((self.rect.centery - (tool_image.get_height() / 2))) - distance_y
                    )
                # All other directions
                case _:
                    self.weapon_position = (
                        ((self.rect.centerx - (tool_image.get_width() / 2))) + distance_x, 
                        ((self.rect.centery - (tool_image.get_height() / 2))) - distance_y
                    )
                    
            # Draw the weapon at the position
            # pygame.draw.circle(self.scaled_surface, "white", (self.rect.centerx - self.camera_position[0], self.rect.centery - self.camera_position[1]), hypot_distance, 1)
            self.surface.blit(tool_image, (self.weapon_position[0] - self.camera_position[0], self.weapon_position[1] - self.camera_position[1]))

    # ---------------------------------------
    # Building 

    def handle_building(self):
        
        # If the player currently has the building tool equipped
        if self.player_gameplay_info_dict["CurrentToolEquipped"] == "BuildingTool":
            
            # --------------------------------------
            # Updating building tool removal timer

            # If there is a timer that has been set to start counting and the timer is less than the removal cooldown
            if self.tools["BuildingTool"]["LastTileRemovedTimer"] != None and self.tools["BuildingTool"]["LastTileRemovedTimer"] < self.tools["BuildingTool"]["RemovalCooldown"]:
                # Increase the timer
                self.tools["BuildingTool"]["LastTileRemovedTimer"] += 1000 * self.delta_time
            
            # If there is a timer that has been set to start counting and the timer is greater than or equal to the removal cooldown of building tiles
            elif self.tools["BuildingTool"]["LastTileRemovedTimer"] != None and self.tools["BuildingTool"]["LastTileRemovedTimer"] >= self.tools["BuildingTool"]["RemovalCooldown"]:
                # Set the last tile removed timer back to None
                self.tools["BuildingTool"]["LastTileRemovedTimer"] = None
            
            # --------------------------------------
            # Checking for input to remove building tiles

            # If the player pressed the right mouse button and there is an existing building tile
            if pygame.mouse.get_pressed()[2] and len(self.tools["BuildingTool"]["ExistingBuildingTilesDict"]) > 0:
                
                # If enough time has passed since the player last removed a building tile
                if self.tools["BuildingTool"]["LastTileRemovedTimer"] == None:

                    # The building tile to remove should be the last building tile placed down
                    building_tile_to_remove = self.tools["BuildingTool"]["ExistingBuildingTilesDict"][len(self.tools["BuildingTool"]["ExistingBuildingTilesDict"]) - 1]

                    # Remove the building tile from the world tiles group
                    self.sprite_groups["WorldTiles"].remove(building_tile_to_remove)

                    # Remove the building tile from the world tiles dictionary
                    self.world_tiles_dict.pop(building_tile_to_remove)

                    # "Create" an empty tile where the building tile was
                    self.empty_tiles_dict[(building_tile_to_remove.rect.x, building_tile_to_remove.rect.y, building_tile_to_remove.rect.width, building_tile_to_remove.rect.height)] = len(self.empty_tiles_dict)

                    # Remove the building tile from the existing building tiles dictionary
                    self.tools["BuildingTool"]["ExistingBuildingTilesDict"].pop(len(self.tools["BuildingTool"]["ExistingBuildingTilesDict"]) - 1)

                    # Start the last tile removed timer, so that the player has to wait "self.tools["BuildingTool"]["RemovalCooldown"]" before removing another tile
                    self.tools["BuildingTool"]["LastTileRemovedTimer"] = 0

                    # If the building tile to remove is in the neighbouring tiles dictionary (keys)
                    if building_tile_to_remove in self.neighbouring_tiles_dict.keys():
                        # Remove the building tile
                        self.neighbouring_tiles_dict.pop(building_tile_to_remove)

                    # Refund half of the bamboo resource depletion amount set
                    self.player_gameplay_info_dict["AmountOfBambooResource"] += (self.tools["BuildingTool"]["BambooResourceDepletionAmount"] * 0.5)
            
            # --------------------------------------
            # Checking for placement of building tiles

            # Draw a guide circles to show the minimum and maximum distances the player can place building tiles (MAY REMOVE)
            pygame.draw.circle(self.surface, "red", (self.rect.centerx - self.camera_position[0], self.rect.centery - self.camera_position[1]), self.tools["BuildingTool"]["MinimumPlacingDistance"], 1)
            pygame.draw.circle(self.surface, "red", (self.rect.centerx - self.camera_position[0], self.rect.centery - self.camera_position[1]), self.tools["BuildingTool"]["MaximumPlacingDistance"], 1)

            # Find collisions between the mouse rect and empty tiles inside the tile map
            empty_tile_collision = pygame.Rect(self.mouse_position[0] , self.mouse_position[1] , 1, 1).collidedict(self.empty_tiles_dict)

            # If there is a collision between the mouse rect and an empty tile 
            if empty_tile_collision != None:

                # The tile rect will be the key of the returned value from the collide dict
                empty_tile_rect_info = empty_tile_collision[0]
                
                # The center of the empty tile
                empty_tile_center = (
                                    empty_tile_collision[0][0] + (empty_tile_collision[0][2] / 2),
                                    empty_tile_collision[0][1] + (empty_tile_collision[0][3] / 2)
                                    )   

                # If the distance between the center of the player and the center of the empty tile at the mouse position less than the maximum distance
                if self.tools["BuildingTool"]["MinimumPlacingDistance"] < dist(self.rect.center, empty_tile_center) < self.tools["BuildingTool"]["MaximumPlacingDistance"]:
                    # Highlight the empty tile as green
                    pygame.draw.rect(
                                    surface = self.surface,
                                    color = "green", 
                                    rect = pygame.Rect(
                                                        empty_tile_rect_info[0] - self.camera_position[0], 
                                                        empty_tile_rect_info[1] - self.camera_position[1],
                                                        empty_tile_rect_info[2],
                                                        empty_tile_rect_info[3]),
                                    width = 1                
                                    )   

                    # If the left mouse button is pressed and there are less than 3 existing building tiles
                    if pygame.mouse.get_pressed()[0] == True and len(self.tools["BuildingTool"]["ExistingBuildingTilesDict"]) < 3:
                        
                        # If the player has enough bamboo resource to place down another building tile
                        if self.player_gameplay_info_dict["AmountOfBambooResource"] - self.tools["BuildingTool"]["BambooResourceDepletionAmount"] > 0:

                            # Create a building tile
                            building_tile = BuildingTile(x = empty_tile_rect_info[0], y = empty_tile_rect_info[1], image = self.tools["BuildingTool"]["Images"]["TileImage"])

                            # Add the building tile to the building tiles sprite group
                            self.sprite_groups["WorldTiles"].add(building_tile)

                            # Add the building tile to the world tiles dictionary with the key as the building tile and the value as the type of world tile
                            self.world_tiles_dict[building_tile] = "BuildingTile"

                            # Remove the empty tile from the empty tiles dictionary
                            self.empty_tiles_dict.pop(empty_tile_rect_info)
                            
                            # Add the building tile to the existing building tiles dictionary
                            self.tools["BuildingTool"]["ExistingBuildingTilesDict"][len(self.tools["BuildingTool"]["ExistingBuildingTilesDict"])] = building_tile

                            # Remove bamboo resource by the depletion amount set
                            self.player_gameplay_info_dict["AmountOfBambooResource"] -= self.tools["BuildingTool"]["BambooResourceDepletionAmount"]

                # If the distance between the center of the player and the center of the empty tile at the mouse position:
                # - Less than or equal to the minimum distance
                # - Greater than or equal to the maximum distance
                elif dist(self.rect.center, empty_tile_center) <= self.tools["BuildingTool"]["MinimumPlacingDistance"] or \
                     dist(self.rect.center, empty_tile_center) >= self.tools["BuildingTool"]["MaximumPlacingDistance"]:

                    # Highlight the empty tile as red
                    pygame.draw.rect(
                                    surface = self.surface,
                                    color = "red", 
                                    rect = pygame.Rect(
                                                        empty_tile_rect_info[0] - self.camera_position[0], 
                                                        empty_tile_rect_info[1] - self.camera_position[1],
                                                        empty_tile_rect_info[2],
                                                        empty_tile_rect_info[3]),
                                    width = 1                
                                    )   
    
    # ---------------------------------------
    # Shooting

    def handle_shooting(self):

        # Handles the functionality behind shooting for the player

        # --------------------------------------------------------------------------------------
        # Handling shooting input

        # pygame.draw.circle(self.scaled_surface, "white", (self.rect.centerx - self.camera_position[0], self.rect.centery - self.camera_position[1]), 50, 1)

        # If the current tool equipped by the player is not the building tool
        if self.player_gameplay_info_dict["CurrentToolEquipped"] != "BuildingTool":
            
            # --------------------------------------
            # Updating shooting cooldown timers
            
            # The current weapon selected (as a temp variable)
            current_weapon = self.tools[self.player_gameplay_info_dict["CurrentToolEquipped"]]

            # If there is a timer that has been set to start counting and the timer is greater than 0 (counts down from the shooting cooldown)
            if current_weapon["ShootingCooldownTimer"] != None and current_weapon["ShootingCooldownTimer"] > 0:
                # Increase the timer
                current_weapon["ShootingCooldownTimer"] -= 1000 * self.delta_time

            # If there is a timer that has been set to start counting and the timer is less than or equal to 0 (counts down from the shooting cooldown)
            elif current_weapon["ShootingCooldownTimer"] != None and current_weapon["ShootingCooldownTimer"] <= 0:
                # Set the shooting cooldown timer back to None
                current_weapon["ShootingCooldownTimer"] = None

            # If the left mouse button has been pressed and the player has enough resources to shoot
            if pygame.mouse.get_pressed()[0] == True and self.player_gameplay_info_dict["AmountOfBambooResource"] - current_weapon["BambooResourceDepletionAmount"]:

                # If the player's current weapon is the "BambooAssaultRifle"
                if self.player_gameplay_info_dict["CurrentToolEquipped"] == "BambooAssaultRifle":

                    # If enough time has passed since the last time the player shot
                    if self.tools["BambooAssaultRifle"]["ShootingCooldownTimer"] == None:
                        
                        # Distance to place the projectile at the tip of the gun 
                        hypot_distance = 45
                        distance_x = hypot_distance * cos(self.look_angle)
                        distance_y = -(hypot_distance * sin(self.look_angle))

                        # -----------------------------------------------------
                        # Checking that there are no tiles in between the center of the player and where the bamboo projectile will be spawned
                        # Note: The following checks is so that the player cannot shoot projectiles through walls

                        # Assume that there is no tile in between the center of the player and where the bamboo projectile will be spawned
                        no_tile_in_between = True
                        
                        # For every neighbouring tile
                        for neighbouring_tile in self.neighbouring_tiles_dict.keys():
                            # Check if the tile is in between the center of the player and the spawning positions of the bamboo projectile
                            if len(neighbouring_tile.rect.clipline(self.rect.center, (self.rect.centerx + distance_x, self.rect.centery + distance_y))) != 0:
                                # If there is a collision then set "no_tile_in_between" to False and exit the loop
                                no_tile_in_between = False
                                break
                        
                        # If there is nothing in between the center of the player and where the bamboo projectile will be spawned
                        if no_tile_in_between == True:
                            
                            # Create a bamboo projectile, spawning it at the tip of the gun (Starts at the center of the player but has an added distance which displaces it to right in front of the gun)
                            # Note: The center of the bamboo projectile is placed at the co-ordinates
                            bamboo_projectile = BambooProjectile(
                                                                x = self.rect.centerx + distance_x,
                                                                y = self.rect.centery + distance_y,
                                                                angle = self.look_angle
                                                                )
                
                        
                            # Add the bamboo projectile to the bamboo projectiles group
                            self.sprite_groups["BambooProjectiles"].add(bamboo_projectile)

                            # Set the shooting cooldown timer to the shooting cooldown set
                            self.tools["BambooAssaultRifle"]["ShootingCooldownTimer"] = self.tools["BambooAssaultRifle"]["ShootingCooldown"]

                            # Remove the amount of bamboo resource set for the bamboo assault rifle
                            self.player_gameplay_info_dict["AmountOfBambooResource"] -= self.tools["BambooAssaultRifle"]["BambooResourceDepletionAmount"]

        # ---------------------------------------------------------------------------------
        # Updating bamboo projectiles 

        # For all bamboo projectiles
        for bamboo_projectile in self.sprite_groups["BambooProjectiles"]:

            # Update the bamboo projectile's delta time
            bamboo_projectile.delta_time = self.delta_time

            # Move the projectile
            bamboo_projectile.move_projectile()
    
    def run(self, delta_time):

        #pygame.draw.line(self.surface, "white", (self.surface.get_width() / 2, 0), (self.surface.get_width() / 2, self.surface.get_height()))
        
        # Update the delta time
        self.delta_time = delta_time

        # Find the mouse position and angle
        self.find_mouse_position_and_angle()

        # Play animations
        self.play_animations()

        # # TEMPORARY
        # for tile in self.neighbouring_tiles_dict.keys():
        #     pygame.draw.rect(self.surface, "green", (tile.rect.x - self.camera_position[0], tile.rect.y - self.camera_position[1], tile.rect.width, tile.rect.height))

        # Handle tile collisions (affects player movement)
        self.handle_tile_collisions()

        # Track player movement
        self.handle_player_movement()

        # Draw the player tool
        self.draw_player_tool()

        # Handle player building
        self.handle_building() 

        # Handle player shooting
        self.handle_shooting()

        # # Create / update a mask for pixel - perfect collisions (Uncomment later when adding collisions with objects other than tiles)
        # self.mask = pygame.mask.from_surface(self.image)
