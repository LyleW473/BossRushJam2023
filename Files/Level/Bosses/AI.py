from math import atan2, pi, cos, dist, sin, copysign
from Global.settings import TILE_SIZE
from pygame import Rect as pygame_Rect


class AI:

    # The default distance travelled
    default_distance_travelled = 4 * TILE_SIZE
    # Time to travel the horizontal/vertical distance at the final veloctiy
    default_horizontal_time_to_travel_distance_at_final_velocity = 0.42
    default_vertical_time_to_travel_distance_at_final_velocity = 0.42
    
    # Time to reach / accelerate to the final horizontal/vertical velocity
    default_horizontal_time_to_reach_final_velocity = 0.3
    default_vertical_time_to_reach_final_velocity = 0.3


    # Reminder: If adding more bosses, you can have these class attributes set as instance attributes


    def __init__(self):
        
        # Dictionary containing information involving the movement of the AI
        self.movement_information_dict = {

                                        # "Angle": None,

                                        # # Delta time
                                        # "DeltaTime": None,

                                        # # Positions
                                        # "CurrentPosition": None,wwa
                                        # "PlayersPosition": None
                                        "NewPositionCenterX": self.rect.centerx,
                                        "NewPositionCenterY": self.rect.centery,
                                        "Dx": 0,
                                        "Dy": 0,
                                        "CollisionTolerance": 12,

                                        # Small floating point numbers storage    
                                        # Note: This is used for values that are less than 1, so the boss will actually continue to move 
                                        "FloatingPointCorrectionX": 0,
                                        "FloatingPointCorrectionY": 0,
                                             
                                        # The distance the AI has to be away from the player to stop chasing them
                                        "DistanceThreshold": 0,

                                        # Starting velocity for accelerated movement, these will be changed over time     
                                        "HorizontalSuvatU" : 0,
                                        "VerticalSuvatU": 0,

                                        # The amount of time the boss has to wait after knocking back a player
                                        "KnockbackCollisionIdleTime": 400,
                                        "KnockbackCollisionIdleTimer": None,
                                        
                                        # World tile collision results (For cancelling the charge state for the Sika Deer.)
                                        "WorldTileCollisionResultsX": False, 
                                        "WorldTileCollisionResultsY": False        
                                        }
        
        # Dictionary used to hold the neighbouring tiles near the AI(i.e. within 1 tile of the AI, movemently and vertically)
        self.neighbouring_tiles_dict = {}

        # Dict used to store collision results when a collision has been detected between a world tile and the AI (For the SikaDeer boss, used for cancelling charge attack)
        self.world_tiles_collision_results_dict = {}

    def move(self):
        
        # If the distance between the AI and the player is greater than the distance threshold and there is no timer set for the cooldown after knockback collision
        if dist(self.movement_information_dict["CurrentPosition"], self.movement_information_dict["PlayersPosition"]) > self.movement_information_dict["DistanceThreshold"] and \
            self.movement_information_dict["KnockbackCollisionIdleTimer"] == None:
            
            # ------------------------------------------------------------------------------------------
            # Moving the AI

            # ----------------------------------------
            # Horizontal

            # -----------------
            # Updating SUVAT

            # If the current horizontal velocity of the AI is less than its final velocity
            if abs(self.movement_information_dict["HorizontalSuvatU"]) < abs(self.movement_information_dict["HorizontalSuvatV"]):
                # Increase the current horizontal velocity
                self.movement_information_dict["HorizontalSuvatU"] += (self.movement_information_dict["HorizontalSuvatA"] * self.movement_information_dict["DeltaTime"])

            # If the current horizontal velocity of the AI is greater than its final velocity
            if abs(self.movement_information_dict["HorizontalSuvatU"]) > abs(self.movement_information_dict["HorizontalSuvatV"]):
                # Set it back to the final velocity
                self.movement_information_dict["HorizontalSuvatU"] = self.movement_information_dict["HorizontalSuvatV"]

            # Set the horizontal distance travelled based on the current velocity of the boss
            self.movement_information_dict["HorizontalSuvatS"] = ((self.movement_information_dict["HorizontalSuvatU"] * self.movement_information_dict["DeltaTime"]) + (0.5 * self.movement_information_dict["HorizontalSuvatA"] * (self.movement_information_dict["DeltaTime"] ** 2)))

            # -----------------
            # Handling collisions and setting the AI's position

            # Handle tile collisions using the horizontal distance to travel (and any additional floating point numbers that were not counted previously)
            self.handle_tile_collisions(
                                        distance_to_travel = self.movement_information_dict["HorizontalSuvatS"] + self.movement_information_dict["FloatingPointCorrectionX"], 
                                        check_x = True, 
                                        check_y = False
                                        )

            # If int(dx) != 0
            if int(self.movement_information_dict["Dx"]) != 0:

                # If the distance to travel is positive
                if self.movement_information_dict["HorizontalSuvatS"] > 0:
                    
                    # If moving right will place the AI out of the tile map / out of the screen
                    if self.rect.right + self.movement_information_dict["HorizontalSuvatS"] >= self.last_tile_position[0]:
                        # Set the AI's right position to be at the last tile position in the tile map
                        self.rect.right = self.last_tile_position[0]

                    # Otherwise
                    elif self.rect.right + self.movement_information_dict["HorizontalSuvatS"] < self.last_tile_position[0]:
                        # Move the player right
                        self.movement_information_dict["NewPositionCenterX"] += self.movement_information_dict["Dx"] 
                        self.rect.centerx = round(self.movement_information_dict["NewPositionCenterX"])

                # If the distance to travel is negative
                elif self.movement_information_dict["HorizontalSuvatS"] < 0:
                    
                    # If moving left will place the AI out of the screen
                    if self.rect.left - self.movement_information_dict["HorizontalSuvatS"] <= 0:
                        # Set the AI's x position to be at 0
                        self.rect.left = 0

                    # Otherwise
                    elif self.rect.left - self.movement_information_dict["HorizontalSuvatS"] > 0:
                        # Move the AI left
                        self.movement_information_dict["NewPositionCenterX"] += self.movement_information_dict["Dx"] 
                        self.rect.centerx = round(self.movement_information_dict["NewPositionCenterX"])
                    
            # ----------------------------------------
            # Vertical
            # -----------------
            # Updating SUVAT

            # If the current vertical velocity of the AI is less than its final velocity
            if abs(self.movement_information_dict["VerticalSuvatU"]) < abs(self.movement_information_dict["VerticalSuvatV"]):
                # Increase the current vertical velocity
                self.movement_information_dict["VerticalSuvatU"] += (self.movement_information_dict["VerticalSuvatA"] * self.movement_information_dict["DeltaTime"])

            # If the current vertical velocity of the AI is greater than its final velocity
            if abs(self.movement_information_dict["VerticalSuvatU"]) > abs(self.movement_information_dict["VerticalSuvatV"]):
                # Set it back to the final velocity
                self.movement_information_dict["VerticalSuvatU"] = self.movement_information_dict["VerticalSuvatV"]

            # Set the vertical distance travelled based on the current velocity of the boss
            self.movement_information_dict["VerticalSuvatS"] = ((self.movement_information_dict["VerticalSuvatU"] * self.movement_information_dict["DeltaTime"]) + (0.5 * self.movement_information_dict["VerticalSuvatA"] * (self.movement_information_dict["DeltaTime"] ** 2)))
            
            # -----------------
            # Handling collisions and setting the AI's position

            # Handle tile collisions using the vertical distance to travel (and any additional floating point numbers that were not counted previously)
            self.handle_tile_collisions(
                                        distance_to_travel = self.movement_information_dict["VerticalSuvatS"] + self.movement_information_dict["FloatingPointCorrectionY"], 
                                        check_x = False, 
                                        check_y = True
                                        )

            # If int(dy) != 0
            if int(self.movement_information_dict["Dy"]) != 0:
                
                # If the distance to travel is positive
                if self.movement_information_dict["VerticalSuvatS"] > 0:

                    # If moving up will place the AI out of the screen
                    if self.rect.top - self.movement_information_dict["VerticalSuvatS"] < 0:
                        # Set the AI's top position to be at the top of the screen 
                        self.rect.top = 0

                    # Otherwise
                    elif self.rect.top - self.movement_information_dict["VerticalSuvatS"] >= 0:
                        # Move the AI up
                        self.movement_information_dict["NewPositionCenterY"] -= self.movement_information_dict["Dy"] 
                        self.rect.centery = round(self.movement_information_dict["NewPositionCenterY"])

                # If the distance to travel is negative
                elif self.movement_information_dict["VerticalSuvatS"] < 0:

                    # If moving down will place the player out of the tile map
                    if self.rect.bottom - self.movement_information_dict["VerticalSuvatS"] > self.last_tile_position[1]:
                        # Set the player's bottom position to the y position of the last tile position
                        self.rect.bottom = self.last_tile_position[1] 

                    # Otherwise
                    elif self.rect.bottom - self.movement_information_dict["VerticalSuvatS"] <= self.last_tile_position[1]:
                        # Move the player down
                        self.movement_information_dict["NewPositionCenterY"] -= self.movement_information_dict["Dy"] 
                        self.rect.centery = round(self.movement_information_dict["NewPositionCenterY"])

    def find_player(self, player_position, current_position, delta_time):

        # Find the angle between the AI and the player (The angle that the center of the player is, relative to the center of AI)
        dx = player_position[0] - current_position[0] 
        dy = player_position[1] - current_position[1]
        self.movement_information_dict["Angle"] = atan2(-dy, dx) % (2 * pi)

        # print(degrees(self.movement_information_dict["Angle"]))
    
        self.update_movement_information_dict(player_position, current_position, delta_time)

    def update_movement_information_dict(self, player_position, current_position, delta_time):

        # Updates the dictionary with the necessary information

        # Positions and delta time
        self.movement_information_dict["PlayersPosition"] = player_position
        self.movement_information_dict["CurrentPosition"] = current_position
        self.movement_information_dict["DeltaTime"] = delta_time

        # ------------------------------------------------------------------------------
        # Movement  

        # ----------------------------------------
        # Horizontal

        # Set the horizontal distance travelled based on the current angle that the player is to the AI
        horizontal_distance_travelled_at_final_velocity = (AI.default_distance_travelled * cos(self.movement_information_dict["Angle"]))

        # Equation = (2s - at^2) / 2t
        self.movement_information_dict["HorizontalSuvatV"] = (2 * horizontal_distance_travelled_at_final_velocity) / (2 * AI.default_horizontal_time_to_travel_distance_at_final_velocity)

        # Set the current acceleration of the AI depending on the current velocity of the player
        self.movement_information_dict["HorizontalSuvatA"] = (self.movement_information_dict["HorizontalSuvatV"] - self.movement_information_dict["HorizontalSuvatU"]) / AI.default_horizontal_time_to_reach_final_velocity

        # ----------------------------------------
        # Vertical

        # Set the vertical distance travelled based on the current angle that the player is to the AI
        vertical_distance_travelled_at_final_velocity = (AI.default_distance_travelled * sin(self.movement_information_dict["Angle"]))

        # Equation = (2s - at^2) / 2t
        self.movement_information_dict["VerticalSuvatV"] = (2 * vertical_distance_travelled_at_final_velocity) / (2 * AI.default_vertical_time_to_travel_distance_at_final_velocity)

        # Set the current acceleration of the AI depending on the current velocity of the player
        self.movement_information_dict["VerticalSuvatA"] = (self.movement_information_dict["VerticalSuvatV"] - self.movement_information_dict["VerticalSuvatU"]) / AI.default_vertical_time_to_reach_final_velocity

    def reset_movement_acceleration(self, vertical_reset = True, horizontal_reset = True):

        # Resets the AI's movement acceleration variables

        # Only resetting the horizontal movement acceleration
        if horizontal_reset == True and vertical_reset == False:
            self.movement_information_dict["Dx"] = 0
            self.movement_information_dict["HorizontalSuvatU"] = 0
            self.movement_information_dict["HorizontalSuvatA"] = (self.movement_information_dict["HorizontalSuvatV"] - self.movement_information_dict["HorizontalSuvatU"]) / AI.default_horizontal_time_to_reach_final_velocity
            self.movement_information_dict["HorizontalSuvatS"] = ((self.movement_information_dict["HorizontalSuvatU"] * self.movement_information_dict["DeltaTime"]) + (0.5 * self.movement_information_dict["HorizontalSuvatA"] * (self.movement_information_dict["DeltaTime"] ** 2)))
        
        # Only resetting the vertical movement acceleration
        elif vertical_reset == True and horizontal_reset == False:
            self.movement_information_dict["Dy"] = 0
            self.movement_information_dict["VerticalSuvatU"] = 0
            self.movement_information_dict["VerticalSuvatA"] = (self.movement_information_dict["VerticalSuvatV"] - self.movement_information_dict["VerticalSuvatU"]) / AI.default_vertical_time_to_reach_final_velocity
            self.movement_information_dict["VerticalSuvatS"] = ((self.movement_information_dict["VerticalSuvatU"] * self.movement_information_dict["DeltaTime"]) + (0.5 * self.movement_information_dict["VerticalSuvatA"] * (self.movement_information_dict["DeltaTime"] ** 2)))

        # Resetting both the horizontal and vertical movement acceleration
        elif horizontal_reset == True and vertical_reset == True:

            # Reset dx and dy
            self.movement_information_dict["Dx"] = 0
            
            # Reset the horizontal and vertical velocity
            self.movement_information_dict["HorizontalSuvatU"] = 0
            self.movement_information_dict["VerticalSuvatU"] = 0

            # Set the current acceleration of the AI depending on the current velocity of the player again
            self.movement_information_dict["HorizontalSuvatA"] = (self.movement_information_dict["HorizontalSuvatV"] - self.movement_information_dict["HorizontalSuvatU"]) / AI.default_horizontal_time_to_reach_final_velocity

            # Set the current acceleration of the AI depending on the current velocity of the player again
            self.movement_information_dict["VerticalSuvatA"] = (self.movement_information_dict["VerticalSuvatV"] - self.movement_information_dict["VerticalSuvatU"]) / AI.default_vertical_time_to_reach_final_velocity

            # Set the horizontal distance travelled based on the current velocity of the boss
            self.movement_information_dict["HorizontalSuvatS"] = ((self.movement_information_dict["HorizontalSuvatU"] * self.movement_information_dict["DeltaTime"]) + (0.5 * self.movement_information_dict["HorizontalSuvatA"] * (self.movement_information_dict["DeltaTime"] ** 2)))
                
            # Set the vertical distance travelled based on the current velocity of the boss
            self.movement_information_dict["VerticalSuvatS"] = ((self.movement_information_dict["VerticalSuvatU"] * self.movement_information_dict["DeltaTime"]) + (0.5 * self.movement_information_dict["VerticalSuvatA"] * (self.movement_information_dict["DeltaTime"] ** 2)))

    def update_knockback_collision_idle_timer(self, delta_time):
        
        # Updates the knockback collision idle timer (The period of time the AI will idle after knocking back the player)
        
        # If there has been a timer set to count down
        if self.movement_information_dict["KnockbackCollisionIdleTimer"] != None:
            
            # If the timer has not finished counting
            if self.movement_information_dict["KnockbackCollisionIdleTimer"] > 0:
                # Decrease the timer
                self.movement_information_dict["KnockbackCollisionIdleTimer"] -= 1000  * delta_time

            # If the timer has finished counting
            if self.movement_information_dict["KnockbackCollisionIdleTimer"] <= 0:
                # Reset the timer back to None
                self.movement_information_dict["KnockbackCollisionIdleTimer"] = None

    def handle_tile_collisions(self, distance_to_travel, check_x, check_y):
        
        # Handles collisions between tiles and the AI
        """ Notes: 
        - abs() calls because the distances to travel depend on the angle that the player is from the boss
        - A collision is only triggered when one rect is overlapping another rect by less than self.movement_information_dict["CollisionTolerance"].

        - check_x so that we only check x collisions with the specified horizontal distance travelled
        - check_y so that we only check y collisions with the specified vertical distance travelled
        (This is also because since the method is called twice to move, it will continuously reset the x / y collision results when called separately (hence why there are two variables to keep track of
        the collision results (i.e. self.movement_information_dict["WorldTileCollisionResultsX"] and self.movement_information_dict["WorldTileCollisionResultsY"])
        """

        # If the distance to travel is greater or equal to 1
        if abs(distance_to_travel) >= 1:
            # ---------------------------------------------------------------------------------
            # Horizontal collisions
            
            if check_x == True:

                # Find the x collisions to the left and right of the AI
                x_collisions_left = pygame_Rect(self.rect.x - abs(distance_to_travel) , self.rect.y, self.rect.width, self.rect.height).collidedict(self.neighbouring_tiles_dict)
                x_collisions_right = pygame_Rect(self.rect.x + abs(distance_to_travel) , self.rect.y, self.rect.width, self.rect.height).collidedict(self.neighbouring_tiles_dict)


                # If there is an x collision to the right of the AI
                if x_collisions_right != None:

                    # Set the world tiles collision results x to True
                    self.movement_information_dict["WorldTileCollisionResultsX"] = True

                    # If the difference between the AI's right and the tile's left is less than the collision tolerance (there is a collision) and the AI is trying to move right
                    if abs(self.rect.right - x_collisions_right[0].rect.left) < self.movement_information_dict["CollisionTolerance"] and self.movement_information_dict["HorizontalSuvatU"] > 0:
                        # Set the AI's right to the tile's left
                        self.rect.right = x_collisions_right[0].rect.left
                        # Don't allow the AI to move
                        self.movement_information_dict["Dx"] = 0
                        # Reset the horizontal acceleration only
                        self.reset_movement_acceleration(vertical_reset = False, horizontal_reset = True)

                    # If the difference between the AI's right and the tile's left is less than the collision tolerance (there is a collision) and the AI is trying to move in any direction but right
                    elif abs(self.rect.right - x_collisions_right[0].rect.left) < self.movement_information_dict["CollisionTolerance"] and self.movement_information_dict["HorizontalSuvatU"] < 0:
                        # Allow the AI to move
                        self.movement_information_dict["Dx"] = distance_to_travel
                        # Reset floating point correction X
                        self.movement_information_dict["FloatingPointCorrectionX"] = 0

                # If there is an x collision to the left of the AI
                if x_collisions_left != None:

                    # Set the world tiles collision results x to True
                    self.movement_information_dict["WorldTileCollisionResultsX"] = True

                    # If the difference between the AI's left and the tile's right is less than the collision tolerance (there is a collision) and the AI is trying to move left
                    if abs(self.rect.left - x_collisions_left[0].rect.right) < self.movement_information_dict["CollisionTolerance"] and self.movement_information_dict["HorizontalSuvatU"] < 0:
                        # Set the AI's left to the tile's right
                        self.rect.left = x_collisions_left[0].rect.right
                        # Don't allow the AI to move
                        self.movement_information_dict["Dx"] = 0
                        # Reset the horizontal acceleration only
                        self.reset_movement_acceleration(vertical_reset = False, horizontal_reset = True)
                        
                    # If the difference between the AI's left and the tile's right is less than the collision tolerance (there is a collision) and the AI is trying to move in any direction but left
                    elif abs(self.rect.left - x_collisions_left[0].rect.right) < self.movement_information_dict["CollisionTolerance"] and self.movement_information_dict["HorizontalSuvatU"] > 0:
                        # Allow the AI to move
                        self.movement_information_dict["Dx"] = distance_to_travel
                        # Reset floating point correction X
                        self.movement_information_dict["FloatingPointCorrectionX"] = 0
                    
                # If there is no x collision to the left of the AI and there is no x collision to the right of the AI
                elif x_collisions_left == None and x_collisions_right == None:
                    # Allow the AI to move
                    self.movement_information_dict["Dx"] = distance_to_travel

                    # Set the world tiles collision results x to False
                    self.movement_information_dict["WorldTileCollisionResultsX"] = False

                    # Reset floating point correction X
                    self.movement_information_dict["FloatingPointCorrectionX"] = 0

            # ---------------------------------------------------------------------------------
            # Vertical collisions      

            elif check_y == True:

                # Find the collisions above and below the AI
                y_collisions_up = pygame_Rect(self.rect.x, self.rect.y - abs(distance_to_travel), self.rect.width, self.rect.height).collidedict(self.neighbouring_tiles_dict)     
                y_collisions_down = pygame_Rect(self.rect.x, self.rect.y + abs(distance_to_travel), self.rect.width, self.rect.height).collidedict(self.neighbouring_tiles_dict)  

                # If there is an y collision above the AI
                if y_collisions_up != None:

                    # Set the world tiles collision results y to True
                    self.movement_information_dict["WorldTileCollisionResultsY"] = True
                
                    # If the difference between the AI's top and the tile's bottom is less than the collision tolerance (there is a collision) and the AI is trying to move up
                    if abs(self.rect.top - y_collisions_up[0].rect.bottom) < self.movement_information_dict["CollisionTolerance"] and self.movement_information_dict["VerticalSuvatU"] > 0:
                        # Set the AI's top to the tile's bottom
                        self.rect.top = y_collisions_up[0].rect.bottom
                        # Don't allow the AI to move
                        self.movement_information_dict["Dy"] = 0
                        # Reset the vertical acceleration only
                        self.reset_movement_acceleration(vertical_reset = True, horizontal_reset = False)

                    # If the difference between the AI's top and the tile's bottom is less than the collision tolerance (there is a collision) and the AI is trying to move in any direction but up
                    elif abs(self.rect.top - y_collisions_up[0].rect.bottom) < self.movement_information_dict["CollisionTolerance"] and self.movement_information_dict["VerticalSuvatU"] < 0:
                        # Allow the AI to move
                        self.movement_information_dict["Dy"] = distance_to_travel
                        # Reset floating point correction Y
                        self.movement_information_dict["FloatingPointCorrectionY"] = 0

                # If there is an y collision below the AI
                if y_collisions_down != None:

                    # Set the world tiles collision results y to True
                    self.movement_information_dict["WorldTileCollisionResultsY"] = True
                    
                    # If the difference between the AI's bottom and the tile's top is less than the collision tolerance (there is a collision) and the AI is trying to move down
                    if abs(self.rect.bottom - y_collisions_down[0].rect.top) < self.movement_information_dict["CollisionTolerance"] and self.movement_information_dict["VerticalSuvatU"] < 0:
                        # Set the AI's bottom to the tile's top
                        self.rect.bottom = y_collisions_down[0].rect.top
                        # Don't allow the AI to move
                        self.movement_information_dict["Dy"] = 0
                        # Reset the vertical acceleration only
                        self.reset_movement_acceleration(vertical_reset = True, horizontal_reset = False)

                    # If the difference between the AI's bottom and the tile's top is less than the collision tolerance (there is a collision) and the AI is trying to move in any direction but down
                    elif abs(self.rect.bottom - y_collisions_down[0].rect.top) < self.movement_information_dict["CollisionTolerance"] and self.movement_information_dict["VerticalSuvatU"] > 0:
                        # Allow the AI to move
                        self.movement_information_dict["Dy"] = distance_to_travel
                        # Reset floating point correction Y
                        self.movement_information_dict["FloatingPointCorrectionY"] = 0

                # If there is no y collision above the AI and there is no y collision below the AI
                elif y_collisions_up == None and y_collisions_down == None:
                    # Allow the AI to move
                    self.movement_information_dict["Dy"] = distance_to_travel

                    # Set the world tiles collision results y to False
                    self.movement_information_dict["WorldTileCollisionResultsY"] = False

                    # Reset floating point correction Y
                    self.movement_information_dict["FloatingPointCorrectionY"] = 0

        # If the distance to travel is less than 1 (i.e a small floating point number, where collisions are inaccurate)
        # Note: (This is because pygame Rect's truncate floating point values so e.g. 250 + 0.25 = 250, so the collision checking would not work)
        elif abs(distance_to_travel) < 1:

            # If this distance to travel is horizontal movement
            if check_x == True:
                # Add the floating point number to the sum of floating points collected so far
                self.movement_information_dict["FloatingPointCorrectionX"] += distance_to_travel

                # Set dx as 0 (i.e. don't move)
                self.movement_information_dict["Dx"] = 0

            # If this distance to travel is vertical
            elif check_y == True:
                # Add the floating point number to the sum of floating points collected so far
                self.movement_information_dict["FloatingPointCorrectionY"] += distance_to_travel

                # Set dy as 0 (i.e. don't move)
                self.movement_information_dict["Dy"] = 0