from Global.generic import Generic
from pygame.sprite import Sprite as pygame_sprite_Sprite
from pygame import Rect as pygame_Rect
from math import pi, cos, sin
from Global.settings import TILE_SIZE
from pygame.image import load as load_image
from pygame.transform import scale as scale_image

class StompController(Generic):

    def __init__(self, scale_multiplier):

        # Series of "nodes", which will spread out to a maximum distance 

        # Starting / minimum radius of each node
        self.minimum_node_radius = 20 / scale_multiplier
            
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

        # Create more stomp nodes:
        for i in range(0, desired_number_of_nodes):

            # Create a stomp node (automatically added to the stomp nodes group when instantiated)
            StompNode(
                    x = center_of_boss_position[0] + (calculated_radius * cos(i * angle_change)), 
                    y = center_of_boss_position[1] + (calculated_radius * sin(i * angle_change)) + 20, # + 20 so that the stomp nodes are positioned below the boss
                    radius = self.minimum_node_radius,
                    angle = i * angle_change # Angle that the node will travel towards
                     ),

class StompNode(pygame_sprite_Sprite):

    # This image is only used for masks
    base_image = load_image("graphics/BossAttacks/StompAttack.png").convert()

    def __init__(self, x, y, radius, angle):

        # Inherit from the pygame.sprite.Sprite class
        pygame_sprite_Sprite.__init__(self)

        # The stomp attack will start below the center of the boss, b
        self.rect = pygame_Rect(x - radius, y - radius, radius * 2, radius * 2)

        # Add the node to the stomp nodes group
        StompController.nodes_group.add(self)

        # ------------------------------------------------------------------------------
        # Movement

        # The total distance travelled (including the horizontal and vertical components)
        desired_distance_travelled = 4 * TILE_SIZE

        # The time for the projectile to cover the desired distance travelled
        time_to_travel_distance_at_final_velocity = 0.5 # t

        # Calculate the horizontal and vertical distance the projectile must travel based on the desired distance travelled
        horizontal_distance = desired_distance_travelled * cos(angle)
        vertical_distance = desired_distance_travelled * sin(angle)

        # Calculate the horizontal and vertical gradients
        self.horizontal_gradient = horizontal_distance / time_to_travel_distance_at_final_velocity
        self.vertical_gradient = vertical_distance / time_to_travel_distance_at_final_velocity

        # The attributes that will hold the new x and y positions of the projectile / node (for more accurate movement as the floating point values are saved)
        self.new_position_centerx = self.rect.centerx
        self.new_position_centery = self.rect.centery

        # ------------------------------------------------------------------------------
        # Other

        # Image used for mask collision
        self.image = scale_image(StompNode.base_image, (radius * 2, radius * 2))

        # The radius of the stomp node
        self.radius = radius

        # The amount of damage that the stomp node deals
        self.damage_amount = 10

    def move(self, delta_time):

        # Moves the projectile / node

        # Horizontal movement
        self.new_position_centerx += self.horizontal_gradient * delta_time
        self.rect.centerx = round(self.new_position_centerx)

        # Vertical movement
        self.new_position_centery += self.vertical_gradient * delta_time
        self.rect.centery = round(self.new_position_centery)