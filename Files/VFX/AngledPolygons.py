import pygame, random, math

class AngledPolygons:

    def __init__(self, surface):

        self.surface = surface

        # Dictionary to hold all the polygons created
        self.polygons_dict = {}

        # Number of polygons created, used as the key for each polygon created
        self.polygons_created = 0

        # Colour palettes for the different polygons
        self.polygons_colour_palettes = {
                                        "Shooting": ((255, 225, 93), (244, 157, 26), (220, 53, 53)),

                                        "Leaves": ( (125, 206, 19), (91, 179, 24), (43, 122, 11)), 

                                        "ShatteredBambooPieces": ( (143, 151, 74), (217, 160, 102), (75, 105, 47), (153, 229, 80))
                                        
                                        }


        # Attribute set to True whenever the user wants to switch the colour palette
        self.switch_colour_palette = False

    def create_polygons(self, origin_point = None, look_angle = None, hypot_length = 50, polygon_sides_angle_change = 15, distance_to_travel = 3, time_to_travel_distance = 0.5, colour_palette = None, blend_rgb_add_boolean = None):  

        # ------------------------------------------------------------------
        # Creating the polygon

        # The length from the top point of the polygon to the other opposite side 
        polygon_hypot = hypot_length

        # The angle that the polygon points towards from the x axis
        angle = math.radians(look_angle)


        # The random angle change for each polygon point
        left_point_angle = angle - math.radians(polygon_sides_angle_change)
        right_point_angle = angle + math.radians(polygon_sides_angle_change)

        # The length from the polygon's origin point to the left and right point
        left_point_length = hypot_length / 3
        right_point_length = hypot_length / 3

        # Creating the polygon points
        self.points_list = [                          
                            [0, 0],
                            [(polygon_hypot * math.cos(angle)), - (polygon_hypot * math.sin(angle))],
                            [(left_point_length * math.cos(left_point_angle)), - (left_point_length * math.sin(left_point_angle))],
                            [(right_point_length * math.cos(right_point_angle)), - (right_point_length * math.sin(right_point_angle))],
                            
        ]

        # Calculate the largest and smallest x and y positions
        # Note: The lambda function is so that only the x or y positions are compared
        largest_x_pos =  max(self.points_list, key = lambda x: x[0])[0]
        smallest_x_pos = min(self.points_list, key = lambda x: x[0])[0]
        largest_y_pos = max(self.points_list, key = lambda x: x[1])[1]
        smallest_y_pos = min(self.points_list, key = lambda x: x[1])[1]

        # The width would be the largest x pos minus the smallest x pos
        polygon_width = largest_x_pos - smallest_x_pos

        # The width would be the largest y pos minus the smallest y pos
        polygon_height = largest_y_pos - smallest_y_pos

        # ------------------------------------------------------------------
        # Correcting co-ordinates so that the polygon is drawn properly onto the polygon surface

        # If any x pos or y pos is negative, "add" that amount to all other positions
        if smallest_x_pos < 0:
            for i in range(0, len(self.points_list)):
                # If it is a negative number, subtracting would add the number
                self.points_list[i][0] -= smallest_x_pos
        
        if smallest_y_pos < 0:
            for i in range(0, len(self.points_list)):
                # If it is a negative number, subtracting would add the number
                self.points_list[i][1] -= smallest_y_pos

        # ------------------------------------------------------------------
        # Ordering the points inside of the list to draw the polygon correctly
    
        """
        Angles:
        - 0 < theta < 180 for polygons that point upwards
            - 0 < theta < 90 for polygons that point upwards to the right
            - 90 < theta < 180 for polygons that point upwards to the left

        - 180 < theta < 360 for polygons that point downwards
            - 180 < theta < 270 for polygons that point downwards to the left
            - 270 < theta < 360 for polygons that point downwards to the right

        - For points 0, 90, 180, 270, 360:
            - Polygon points directly: Right, Up, Left, Down, Right

        Notes:
        - The points must be in clockwise order
        - The following algorithm will draw the polygon starting from the origin point (So the first point in the list will always the origin point)
        """

        # Find whether the polygon is pointing "more" towards the x axis or the y axis
        dx = self.points_list[1][0] - self.points_list[0][0]
        dy = self.points_list[1][1] - self.points_list[0][1]

        # If the polygon is pointing more towards the x axis
        if abs(dx) >= abs(dy):
            
            # If the polygon is pointing left
            if dx < 0:
                # Sort the list in descending x pos
                self.ordered_points_list = sorted(self.points_list, key = lambda x: x[0], reverse = True)

                # Swap the last 2 items (This ensures that the list is in clockwise order)
                self.ordered_points_list[3], self.ordered_points_list[2] = self.ordered_points_list[2], self.ordered_points_list[3]

            # If the polygon is pointing right
            elif dx > 0: 
                # Sort the list in ascending x pos
                self.ordered_points_list = sorted(self.points_list, key = lambda x: x[0], reverse = False)

                # Swap the last 2 items (This ensures that the list is in clockwise order)
                self.ordered_points_list[3], self.ordered_points_list[2] = self.ordered_points_list[2], self.ordered_points_list[3]

        # If the polygon is pointing more towards the y axis
        elif abs(dy) > abs(dx):
            
            # If the polygon is pointing down
            if dy > 0:
                
                # Sort the list in ascending y pos
                self.ordered_points_list = self.points_list[:1] + sorted(self.points_list[1:], key = lambda x: x[1])
                self.ordered_points_list[3], self.ordered_points_list[2] = self.ordered_points_list[2], self.ordered_points_list[3]

            # If the polygon is pointing up
            elif dy < 0:
                # Sort the list in descending y pos
                self.ordered_points_list = self.points_list[:1] + sorted(self.points_list[1:], key = lambda x: x[1], reverse = True)
                self.ordered_points_list[3], self.ordered_points_list[2] = self.ordered_points_list[2], self.ordered_points_list[3]
    
        # -----------------------------------------------------------------
        # Adding additional polygon functionality e.g. movement
        # Declare the distance the polygon must travel before disappearing and the time 
        distance_polygon_must_travel_to_disappear = distance_to_travel

        """ Dictionary to store all of the polygons' information
        - id = Used to remove the polygon from the list once it has travelled the full distance
        - distance_travelled = Holds the distance travelled on the x and y axis
        - gradients = The gradients / rate of change of the x and y co-ordinates based on the distance the polygon needs to travel and the time period given
        - dimensions_list = The ordered list of all the points of the polygon. "Dimensions" because the polygon needs to be drawn at starting at (0, 0) of the polygon surface.
        - drawing_position = The position (i.e. co-ordinate) that the polygon surface will be drawn at
        - "
        """ 
        self.polygons_dict[self.polygons_created] = {
            "id": self.polygons_created,
            "distance_travelled": [0, 0],
            "distance_polygon_must_travel_to_disappear": distance_polygon_must_travel_to_disappear,
            "gradients": ((distance_polygon_must_travel_to_disappear * math.cos(angle))/ time_to_travel_distance, (distance_polygon_must_travel_to_disappear * math.sin(angle)) / time_to_travel_distance),
            "colour": self.polygons_colour_palettes[colour_palette][random.randint(0, len(self.polygons_colour_palettes[colour_palette]) - 1)],
            "polygon_surface": pygame.Surface((polygon_width, polygon_height)),
            "dimensions_list": self.ordered_points_list,
            "drawing_position" : origin_point,
            "blend_rgb_add_boolean": blend_rgb_add_boolean
            }


        # Increment the number of polygons created
        self.polygons_created += 1

    def draw(self, camera_position, delta_time):     
        
        # Loop through the dictionary of each polygon
        for polygon_points_dict in self.polygons_dict.copy().values():
            

            # If the polygon has not travelled the complete distance
            if math.sqrt((polygon_points_dict["distance_travelled"][0] ** 2) + (polygon_points_dict["distance_travelled"][1] ** 2)) < polygon_points_dict["distance_polygon_must_travel_to_disappear"]:

                # Increasing the x position of the polygon
                polygon_points_dict["drawing_position"][0] += polygon_points_dict["gradients"][0] * delta_time
                polygon_points_dict["distance_travelled"][0] += abs(polygon_points_dict["gradients"][0] * delta_time)

                # Increasing the y position of the polygon
                polygon_points_dict["drawing_position"][1] -= polygon_points_dict["gradients"][1] * delta_time
                polygon_points_dict["distance_travelled"][1] += abs(polygon_points_dict["gradients"][1] * delta_time)

                # Draw the polygon onto the polygon surface
                polygon_points_dict["polygon_surface"].set_colorkey("black")
                polygon_points_dict["polygon_surface"].fill("black")
                pygame.draw.polygon(polygon_points_dict["polygon_surface"], polygon_points_dict["colour"], polygon_points_dict["dimensions_list"])

                # Draw the polygon surface onto the main surface, with the special flag
                """ The destination subtracts the dx and dy ,between the drawing position and the origin point, from the drawing position
                This is so that the polygon surface is drawn at the correct position that clearly illustrates which direction the polygon is pointing towards"""


                # Draw the polygon surface onto the main surface, with the special flag
                """ The destination subtracts the dx and dy ,between the drawing position and the origin point, from the drawing position
                This is so that the polygon surface is drawn at the correct position that clearly illustrates which direction the polygon is pointing towards"""

                # If we should not blend the surfaces together
                if polygon_points_dict["blend_rgb_add_boolean"] == False:
                    self.surface.blit(
                                    source = polygon_points_dict["polygon_surface"], 
                                    dest = (
                                            (polygon_points_dict["drawing_position"][0] - polygon_points_dict["dimensions_list"][0][0]) - camera_position[0],
                                            (polygon_points_dict["drawing_position"][1] - polygon_points_dict["dimensions_list"][0][1]) - camera_position[1]
                                            ),

                                    )
                # If we should blend the surfaces together
                elif polygon_points_dict["blend_rgb_add_boolean"] == True:
                    self.surface.blit(
                                    source = polygon_points_dict["polygon_surface"], 
                                    dest = (
                                            (polygon_points_dict["drawing_position"][0] - polygon_points_dict["dimensions_list"][0][0]) - camera_position[0],
                                            (polygon_points_dict["drawing_position"][1] - polygon_points_dict["dimensions_list"][0][1]) - camera_position[1]
                                            ),
                                    special_flags = pygame.BLEND_RGBA_ADD
                                    )

            # If the polygon has travelled the complete distance
            else:
                # Delete the polygon from the polygons dictionary
                self.polygons_dict.pop(polygon_points_dict["id"])