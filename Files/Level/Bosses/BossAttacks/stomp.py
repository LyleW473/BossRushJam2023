from Global.generic import Generic
from pygame.sprite import Sprite as pygame_sprite_Sprite
from pygame import Rect as pygame_Rect
from math import pi, cos, sin

class StompController(Generic):

    def __init__(self, scale_multiplier):

        # Series of "nodes", which will spread out to a maximum distance 

        # Starting / minimum radius of each node
        self.minimum_node_radius = 10 / scale_multiplier
            
        # Maximum radius of each node
        self.maximum_node_radius = 32 / scale_multiplier


    
    def create_stomp_nodes(self, center_of_boss_position):

        # Given a desired number of "nodes" and the radius of each node, calculate the circumference and diameter
        desired_number_of_nodes = 16
        radius_of_each_node = self.minimum_node_radius 

        # Equation: Radius of each node = (circumference / number of nodes) / 2, rearranged to calculate circumference
        calculated_circumference = 2 * radius_of_each_node * desired_number_of_nodes

        # Equation: Circumference = pi x diameter, rearranged to find diameter
        calculated_diameter = calculated_circumference / pi

        # Radius = 1/2 * diameter
        calculated_radius = calculated_diameter / 2

        # The angle change between each node should be 2pi / the number of nodes
        angle_change = (2 * pi / desired_number_of_nodes)

        # pygame_draw_circle(self.surface, "red", center = center_of_boss_position, radius = calculated_radius)

        # Dictionary used to update the 
        self.nodes_dict = {len(StompController.nodes_group) : {
                                                    "Node": StompNode(
                                                            x = center_of_boss_position[0] + (calculated_radius * cos(i * angle_change)), 
                                                            y = center_of_boss_position[1] + (calculated_radius * sin(i * angle_change)) + 20, # + 20 so that the stomp nodes are positioned below the boss
                                                            radius = self.minimum_node_radius
                                                            ),
                                                    "Angle": i * angle_change # Angle used to calculate the movement of the node
                                                    }

                                                    for i in range(0, desired_number_of_nodes)}

class StompNode(pygame_sprite_Sprite):

    def __init__(self, x, y, radius):

        # Inherit from the pygame.sprite.Sprite class
        pygame_sprite_Sprite.__init__(self)

        # # The stomp attack will start at the center of the boss
        # self.rect = pygame_Rect(x - radius * 2, y - radius * 2, radius * 2, radius * 2)
        self.rect = pygame_Rect(x - radius, y - radius, radius * 2, radius * 2)

        # The radius of the stomp node
        self.radius = radius

        # Add the node to the stomp nodes group
        StompController.nodes_group.add(self)
