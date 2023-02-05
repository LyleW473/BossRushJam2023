from math import atan2, pi, cos, dist, sin
from Global.settings import TILE_SIZE

class AI:

    # The default distance travelled
    default_distance_travelled = 4 * TILE_SIZE
    # Time to travel the horizontal/vertical distance at the final veloctiy
    default_horizontal_time_to_travel_distance_at_final_velocity = 0.4
    default_vertical_time_to_travel_distance_at_final_velocity = 0.4
    
    # Time to reach / accelerate to the final horizontal/vertical velocity
    default_horizontal_time_to_reach_final_velocity = 0.75
    default_vertical_time_to_reach_final_velocity = 0.75


    # Reminder: If adding more bosses, you can have these class attributes set as instance attributes


    def __init__(self):
        
        # Dictionary containing information involving the movement of the AI
        self.movement_information_dict = {

                                        # "Angle": None,

                                        # # Delta time
                                        # "DeltaTime": None,

                                        # # Positions
                                        # "CurrentPosition": None,
                                        # "PlayersPosition": None
                                        "NewPositionCenterX": self.rect.centerx,
                                        "NewPositionCenterY": self.rect.centery,

                                        "DistanceThreshold": 50,

                                        # Starting velocity for accelerated movement, these will be changed over time     
                                        "HorizontalSuvatU" : 0,
                                        "VerticalSuvatU": 0


                                        }
    
    def move(self):
        
        # If the distance between the AI and the player is greater than the distance threshold
        if dist(self.movement_information_dict["CurrentPosition"], self.movement_information_dict["PlayersPosition"]) > self.movement_information_dict["DistanceThreshold"]:
            
            # ------------------------------------------------------------------------------------------
            # Moving the AI

            # ----------------------------------------
            # Horizontal

            # If the current horizontal velocity of the AI is less than its final velocity
            if self.movement_information_dict["HorizontalSuvatU"] < self.movement_information_dict["HorizontalSuvatV"]:
                # Increase the current horizontal velocity
                self.movement_information_dict["HorizontalSuvatU"] += (self.movement_information_dict["HorizontalSuvatA"] * self.movement_information_dict["DeltaTime"])

            # If the current horizontal velocity of the AI is greater than its final velocity
            if self.movement_information_dict["HorizontalSuvatU"] > self.movement_information_dict["HorizontalSuvatV"]:
                # Set it back to the final velocity
                self.movement_information_dict["HorizontalSuvatU"] = self.movement_information_dict["HorizontalSuvatV"]

            # Set the horizontal distance travelled based on the current velocity of the boss
            self.movement_information_dict["HorizontalSuvatS"] = ((self.movement_information_dict["HorizontalSuvatU"] * self.movement_information_dict["DeltaTime"]) + (0.5 * self.movement_information_dict["HorizontalSuvatA"] * (self.movement_information_dict["DeltaTime"] ** 2)))

            # Update the new position center x (for floating point accuracy)
            self.movement_information_dict["NewPositionCenterX"] += self.movement_information_dict["HorizontalSuvatS"]
            # Set the AI's center
            self.rect.centerx = round(self.movement_information_dict["NewPositionCenterX"])


            # ----------------------------------------
            # Vertical

            # If the current vertical velocity of the AI is less than its final velocity
            if self.movement_information_dict["VerticalSuvatU"] < self.movement_information_dict["VerticalSuvatV"]:
                # Increase the current vertical velocity
                self.movement_information_dict["VerticalSuvatU"] += (self.movement_information_dict["VerticalSuvatA"] * self.movement_information_dict["DeltaTime"])

            # If the current vertical velocity of the AI is greater than its final velocity
            if self.movement_information_dict["VerticalSuvatU"] > self.movement_information_dict["VerticalSuvatV"]:
                # Set it back to the final velocity
                self.movement_information_dict["VerticalSuvatU"] = self.movement_information_dict["VerticalSuvatV"]

            # Set the vertical distance travelled based on the current velocity of the boss
            self.movement_information_dict["VerticalSuvatS"] = ((self.movement_information_dict["VerticalSuvatU"] * self.movement_information_dict["DeltaTime"]) + (0.5 * self.movement_information_dict["VerticalSuvatA"] * (self.movement_information_dict["DeltaTime"] ** 2)))
            
            # Update the new position center y (for floating point accuracy)
            self.movement_information_dict["NewPositionCenterY"] -= self.movement_information_dict["VerticalSuvatS"]
            # Set the AI's center
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

    def reset_movement_acceleration(self):

        # Resets the AI's movement acceleration variables
        
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