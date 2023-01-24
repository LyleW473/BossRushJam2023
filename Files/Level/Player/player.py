import pygame, os, math
from Global.generic import Generic
from Global.settings import *

class Player(Generic, pygame.sprite.Sprite):
    def __init__(self, x, y, surface):
        
        # Surface that the player is drawn onto
        self.surface = surface

        # ---------------------------------------------------------------------------------
        # Movement

        self.declare_movement_attributes()

        # ---------------------------------------------------------------------------------
        # Animations

        # Load the animation images
        self.load_animations()

        # Inherit from the Generic class, which has basic attributes and methods.
        Generic.__init__(self, x = x, y = y, image = self.animations_dict[self.current_player_element][self.current_animation_state][self.animation_index])

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
        # Shooting

        # Note: Time and cooldowns are measured in milliseconds
        self.current_weapon = "BambooAssaultRifle"
        self.weapons = {
                        "BambooLauncher": {},
                        "BambooAssaultRifle": {"ShootingCooldown": 200, "PreviouslyShotTime": 0}
                        }
        
    # ---------------------------------------------------------------------------------
    # Animations

    def load_animations(self):

        # Set the current player version (i.e. Normal, ADDING MORE LETTER, e.g. GLOWING MUSHROOM, GOLDEN MUSHROOM ETC.)
        self.current_player_element = "Normal"
        self.current_animation_state = "Idle"

        # A dictionary that will hold all of the animations
        # Note: The images were originally 24 pixels, but then scaled up to 48 pixels
        self.animations_dict = {"Normal": {"Idle": [pygame.image.load(f"graphics/Player/Normal/Idle/{i}.png") for i in range(len(os.listdir("graphics/Player/Normal/Idle")))],
                                        "Run": [pygame.image.load(f"graphics/Player/Normal/Run/{i}.png") for i in range(len(os.listdir("graphics/Player/Normal/Run")))],
                                        }}

        # Create attributes used for the animations
        self.animation_index = 0 # Tracks which animation frame to show
        self.animation_frame_counter = 0 # Used to track how much time has passed since the last frame update
        
        # Dictionary to hold the time between each animation frame for each animation 
        # Values are in ms
        self.animation_frame_cooldowns_dict = {"Idle": 200,
                                            "Run": 200}

    def change_players_animation_state(self):

        # If the player is moving left, right, up or down
        if pygame.key.get_pressed()[pygame.K_a] or pygame.key.get_pressed()[pygame.K_d] or pygame.key.get_pressed()[pygame.K_w] or pygame.key.get_pressed()[pygame.K_s]:

            """ 
            Don't play the run animation and play the idle animation:
                - If the player is at the beginning or end of the tile map
                or 
                - If the player moving will collide with the a neighbouring tile
            """
            if (self.rect.x == 0 or self.rect.right == self.last_tile_position[0]) or \
                (pygame.Rect(self.rect.x - 1, self.rect.y, self.rect.width, self.rect.height).collidedict(self.neighbouring_tiles_dict) != None or pygame.Rect(self.rect.x + 1, self.rect.y, self.rect.width, self.rect.height).collidedict(self.neighbouring_tiles_dict) != None):

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
        elif pygame.key.get_pressed()[pygame.K_a] == False and pygame.key.get_pressed()[pygame.K_d] == False:
            # If the current animation state has not been set to "Idle" yet
            if self.current_animation_state != "Idle":
                
                # If the player has stopped running
                if self.current_animation_state == "Run":
                    # Set the current animation state to "Idle"
                    self.current_animation_state = "Idle"

                    # Reset the animation frame counter and index
                    self.animation_frame_counter = 0
                    self.animation_index = 0

    def play_animations(self):
        
        # Check whether we need to change the player's animation state based on what the player is doing
        self.change_players_animation_state()

        # Increment the animation frame counter based on time
        self.animation_frame_counter += 1000 * self.delta_time

        """ Temporary variables to store the: 
            - Current player animation state's list, e.g. The list containing the images of the "Idle" animation
            - The current animation image
            """
        current_player_state_animation_list = self.animations_dict[self.current_player_element][self.current_animation_state]
        current_animation_image = self.animations_dict[self.current_player_element][self.current_animation_state][self.animation_index]

        # ---------------------------------------------------------------------------------
        # Set the image to be this animation frame and rotate it depending on the where the player's mouse is positioned
        # Note: Rotozoom is for anti-aliasing when rotating the image
        self.image = pygame.transform.rotozoom(surface = current_animation_image, angle = math.degrees(self.look_angle), scale = 1)

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
        self.draw(surface = self.surface, x = (self.rect.centerx - self.camera_position[0]) - int(self.image.get_width() / 2), y = (self.rect.centery - self.camera_position[1]) - int(self.image.get_height() / 2))

    # ---------------------------------------------------------------------------------
    # Movement       

    def declare_movement_attributes(self):

        """
        self.delta_time = delta_time (Used for framerate independence)

        """
        # Dictionary that holds which direction the player is currently facing 
        self.direction_variables_dict = {"Left": False, "Right": False, "Up": False, "Down": False}

        # ---------------------------------------
        # Movement

        # Set the initial movement velocity to be 0
        self.movement_suvat_u = 0
        # The movement distance the player can move
        self.movement_suvat_s = 0

        # Calculate the velocity that the player moves at given a distance that the player travels within a given time span

        # After re-arranging s = vt + 1/2(a)(t^2), v is given by the equation: (2s - a(t)^2) / 2t, where a is 0 because acceleration is constant
        time_to_travel_distance_at_final_movement_velocity = 0.5 # t
        distance_travelled_at_final_movement_velocity = 4.5 * TILE_SIZE # s 
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
    
    def update_direction_variables(self, true_direction):

        # Method to update the direction variables inside the dictionary. The "true direction" refers to the direction that the player is attempting to move towards.

        # Left
        if pygame.key.get_pressed()[pygame.K_a] == False:
            self.direction_variables_dict["Left"] = False

        # Right
        if pygame.key.get_pressed()[pygame.K_d] == False:
            self.direction_variables_dict["Right"] = False

        # Up
        if pygame.key.get_pressed()[pygame.K_w] == False:
            self.direction_variables_dict["Up"] = False

        # Down
        if pygame.key.get_pressed()[pygame.K_s] == False:
            self.direction_variables_dict["Down"] = False

        # Set the "true direction" to True
        self.direction_variables_dict[true_direction] = True

    def movement_acceleration(self):

        # Method that executes the movement acceleration of the player

        # If the current velocity has not reached the final velocity set for the player
        if self.movement_suvat_u < self.movement_suvat_v:
            # Increase the current velocity
            self.movement_suvat_u += (self.movement_suvat_a * self.delta_time)

        # Limit the current velocity to the final velocity set for the player (in case that the current velocity is greater)
        self.movement_suvat_u = min(self.movement_suvat_u, self.movement_suvat_v)

        # Set the distance travelled based on the current velocity
        self.movement_suvat_s = ((self.movement_suvat_u * self.delta_time) + (0.5 * self.movement_suvat_a * (self.delta_time ** 2)))

    def handle_player_movement(self):

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
            self.update_direction_variables(true_direction = "Left")

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
            self.update_direction_variables(true_direction = "Right")

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

        if pygame.key.get_pressed()[pygame.K_w] and pygame.key.get_pressed()[pygame.K_s] == False:

            # If the player is decelerating currently
            if self.decelerating == True:
                # Stop decelerating
                self.decelerating = False
            
            # Update the direction variables
            self.update_direction_variables(true_direction = "Up")

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

        elif pygame.key.get_pressed()[pygame.K_s] and pygame.key.get_pressed()[pygame.K_w] == False:

            # If the player is decelerating currently
            if self.decelerating == True:
                # Stop decelerating
                self.decelerating = False

            # Update the direction variables
            self.update_direction_variables(true_direction = "Down")

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
        self.look_angle = math.atan2(-dy, dx) % (2 * math.pi)

        # Draw the new cursor
        # Blit the cursor image at the mouse position divided by the scale multiplier, subtracting half of the cursor image's width and height
        self.surface.blit(self.default_cursor_image, ((self.mouse_position[0] - self.camera_position[0]) - (self.default_cursor_image.get_width()/ 2), (self.mouse_position[1] - self.camera_position[1]) - (self.default_cursor_image.get_height() / 2)))

        # Draw the guidelines to the mouse cursor
        self.draw_guidelines_to_cursor(dx, dy)

    def draw_guidelines_to_cursor(self, dx, dy):

        # Method to draw the guidelines to the mouse cursor / position

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

    def run(self):

        #pygame.draw.line(self.surface, "white", (self.surface.get_width() / 2, 0), (self.surface.get_width() / 2, self.surface.get_height()))

        # Find the mouse position and angle
        self.find_mouse_position_and_angle()

        # Play animations
        self.play_animations()

        # TEMPORARY
        # for tile in self.neighbouring_tiles_dict.keys():
        #     pygame.draw.rect(self.surface, "green", (tile.rect.x - self.camera_position[0], tile.rect.y - self.camera_position[1], tile.rect.width, tile.rect.height))

        # Handle tile collisions (affects player movement)
        self.handle_tile_collisions()

        # Track player movement
        self.handle_player_movement()

        # # Create / update a mask for pixel - perfect collisions (Uncomment later when adding collisions with objects other than tiles)
        # self.mask = pygame.mask.from_surface(self.image)
