from math import atan2, pi, cos, dist, sin
from Global.settings import TILE_SIZE

class AI:

    default_distance_travelled = 6 * TILE_SIZE
    default_time_to_travel_distance = 1
    def __init__(self):
        
        # Dictionary containing information involving the movement of the AI
        self.movement_information_dict = {
                                        # # Movement
                                        # "HorizontalDistanceTimeGradient": None,
                                        # "VerticalDistanceTimeGradient": None,
                                        # "Angle": None,

                                        # # Delta time
                                        # "DeltaTime": None,

                                        # # Positions
                                        # "CurrentPosition": None,
                                        # "PlayersPosition": None
                                        "NewPositionCenterX": self.rect.centerx,
                                        "NewPositionCenterY": self.rect.centery,

                                        "DistanceThreshold": 50


                                        }

    def move(self):
        
        # If the distance between the AI and the player is greater than the distance threshold
        if dist(self.movement_information_dict["CurrentPosition"], self.movement_information_dict["PlayersPosition"]) > self.movement_information_dict["DistanceThreshold"]:
            
            # ------------------------------------------------------------------------------------------
            # Updating distance time gradients

            # Update the horizontal distance time gradient depending on the angle
            self.movement_information_dict["HorizontalDistanceTimeGradient"] = (AI.default_distance_travelled * cos(self.movement_information_dict["Angle"])) / AI.default_time_to_travel_distance
                
            # Update the vertical distance time gradient depending on the angle
            self.movement_information_dict["VerticalDistanceTimeGradient"] = (AI.default_distance_travelled * sin(self.movement_information_dict["Angle"])) / AI.default_time_to_travel_distance

            # ------------------------------------------------------------------------------------------
            # Moving the AI

            # ----------------------------------------
            # Horizontal

            # Update the new position center y (for floating point accuracy)
            self.movement_information_dict["NewPositionCenterX"] += self.movement_information_dict["HorizontalDistanceTimeGradient"] * self.delta_time
            # Set the AI's center
            self.rect.centerx = round(self.movement_information_dict["NewPositionCenterX"])

            # ----------------------------------------
            # Vertical
            # Update the new position center y (for floating point accuracy)
            self.movement_information_dict["NewPositionCenterY"] -= self.movement_information_dict["VerticalDistanceTimeGradient"] * self.delta_time

            # Set the AI's center
            self.rect.centery = round(self.movement_information_dict["NewPositionCenterY"])

    def find_player(self, player_position, current_position, delta_time):

        # Find the angle between the boss and the player (The angle that the center of the player is, relative to the center of boss)
        dx = player_position[0] - current_position[0] 
        dy = player_position[1] - current_position[1]
        self.movement_information_dict["Angle"] = atan2(-dy, dx) % (2 * pi)

        # print(degrees(self.movement_information_dict["Angle"]))

        # Update dictionary with the necessary information
        self.movement_information_dict["PlayersPosition"] = player_position
        self.movement_information_dict["CurrentPosition"] = current_position
        self.movement_information_dict["DeltaTime"] = delta_time
