from Global.generic import Generic
from Level.Bosses.BossAttacks.stomp import StompController
from pygame.draw import rect as pygame_draw_rect
from pygame.draw import line as pygame_draw_line
from pygame import Rect as pygame_Rect
from pygame.draw import circle as pygame_draw_circle
from pygame.mask import from_surface as pygame_mask_from_surface
from Global.functions import change_image_colour
from random import choice as random_choice
from pygame import Surface as pygame_Surface

class SikaDeerBoss(Generic):

    # ImagesDict = ?? (This is set when the boss is instantiated)
    # Example: Stomp : [Image list]


    def __init__(self, x, y, surface, scale_multiplier):

        # Surface that the boss is drawn onto
        self.surface = surface 
        
        # The starting image when spawned
        starting_image = SikaDeerBoss.ImagesDict["Stomp"][0]

        # Inherit from the Generic class, which has basic attributes and methods.
        Generic.__init__(self, x = x , y = y, image = starting_image)

        # Spawn the boss at the middle of the tile, with the bottom of the boss being at the bottom of the tile
        self.rect.midbottom = (x, y)

        """ List of "hidden" added attributes
        self.delta_time
        self.camera_position
        """
        
        # A dictionary containing information relating to the behaviour of the Sika deer boss
        self.behaviour_patterns_dict = {
                                    # The current action that the boss is performing
                                    "CurrentAction": "Stomp",

                                    # # Actions that the boss can perform
                                    # "Walk": {
                                    #         "MovementSpeed": 10
                                    #         },


                                    "Stomp": {
                                            "Damage": 20,
                                            "Speed": 150, # Speed that the stomp wave travels in milliseconds 
                                            "Duration": 6000, # How long the attack will be performed
                                            "DurationTimer": 6000, # Timer used to check if the attack is over

                                             },

                                    # "Charge": { 
                                    #           "Damage": 30,
                                              
                                        

                                    #           }
                                    }

        # A dictionary containing extra information about the Sika deer boss
        self.extra_information_dict = {    
                                        # Health
                                        "CurrentHealth": 7500,
                                        "MaximumHealth": 7500,

                                        # Damage flash effect
                                        "DamagedFlashEffectTime": 100, # The time that the flash effect should play when the player is damaged
                                        "DamagedFlashEffectTimer": None
                                        
                                      }
        
        # ---------------------------------------------------
        # Animations

        self.animation_index = 0         

        # --------------------------
        # Stomping 
        number_of_stomps = 20 

        # Each full cycle of the stomp animation has 2 stomps 
        # Note: (number_of_stomps + 1) because the first animation frame does not count as a stomp, so add another one
        number_of_animation_cycles = (number_of_stomps + 1) / 2

        # The time between each frame should be how long the stomp attakc lasts, divided by the total number of animation frames, depending on how many cycles there are 
        self.behaviour_patterns_dict["Stomp"]["TimeBetweenAnimFrames"] = self.behaviour_patterns_dict["Stomp"]["Duration"] / (len(SikaDeerBoss.ImagesDict["Stomp"]) * number_of_animation_cycles)

        # Set the animation frame timer to start at 0, this is so that the first animation frame does not count as a stomp
        self.behaviour_patterns_dict["Stomp"]["AnimationFrameTimer"] = 0

        # Stomp controller used to create stomp nodes and update each individual stomp node
        self.stomp_controller = StompController(scale_multiplier = scale_multiplier)

        print(self.behaviour_patterns_dict)
    
    # ----------------------------------------------------------------------------------
    # Animations

    def play_animations(self):

        # Temporary variable for the current action
        current_action = self.behaviour_patterns_dict["CurrentAction"]

        # -----------------------------------
        # Set image

        # The current animation list
        current_animation_list = SikaDeerBoss.ImagesDict[self.behaviour_patterns_dict["CurrentAction"]]
        # The current animation image
        current_animation_image = current_animation_list[self.animation_index]

        # If the boss has been damaged
        if self.extra_information_dict["DamagedFlashEffectTimer"] != None:
            # Set the current animation image to be a flashed version of the current animation image (a white flash effect)
            current_animation_image = change_image_colour(current_animation_image = current_animation_image, desired_colour = random_choice(((255, 255, 255), (255, 0, 0))))
        
        # Set the image to be the current animation image
        self.image = current_animation_image

        # -----------------------------------
        # Updating animation

        # Find which action is being performed and update the animation index based on that
        # match current_action:

        #     case "Stomp":

        # If the current action is to "Stomp"
        if current_action == "Stomp":
                
                # If the stomp attack has not been completed
                if self.behaviour_patterns_dict[current_action]["DurationTimer"] > 0:
                    
                    # If the current animation index is not the last index inside the animation list and the animation frame timer has finished counting
                    if self.animation_index < (len(SikaDeerBoss.ImagesDict[current_action]) - 1) and (self.behaviour_patterns_dict[current_action]["AnimationFrameTimer"]) <= 0:
                        
                        # If this animation is one of the keyframes where the boss has stomped
                        if (self.animation_index == 0 and self.behaviour_patterns_dict[current_action]["DurationTimer"] != self.behaviour_patterns_dict[current_action]["Duration"]) \
                            or self.animation_index == 5:
                            
                            # Create stomp attack nodes
                            self.stomp_controller.create_stomp_nodes(center_of_boss_position = (self.rect.centerx, self.rect.centery), desired_number_of_nodes = 12)

                            # print("STOMP", self.animation_index, self.behaviour_patterns_dict[current_action]["DurationTimer"], self.behaviour_patterns_dict[current_action]["Duration"])

                        # Go the next animation frame
                        self.animation_index += 1

                        # Reset the timer (adding will help with accuracy)
                        self.behaviour_patterns_dict[current_action]["AnimationFrameTimer"] += self.behaviour_patterns_dict[current_action]["TimeBetweenAnimFrames"] 

                    # If the current animation index is at the last index inside the animation list and the animation frame timer has finished counting
                    if self.animation_index == (len(SikaDeerBoss.ImagesDict[current_action]) - 1) and (self.behaviour_patterns_dict[current_action]["AnimationFrameTimer"] <= 0):
                        # Go the the first animation frame (reset the animation)
                        self.animation_index = 0

                        # Reset the timer (adding will help with accuracy)
                        self.behaviour_patterns_dict[current_action]["AnimationFrameTimer"] = self.behaviour_patterns_dict[current_action]["TimeBetweenAnimFrames"]

                # If the stomp attack has been completed
                elif self.behaviour_patterns_dict[current_action]["DurationTimer"] <= 0:
                    
                    # Change to a different behaviour

                    # Reset the animation index
                    self.animation_index = 0

        # -----------------------------------
        # Update animation frame timers

        self.behaviour_patterns_dict[current_action]["AnimationFrameTimer"] -= 1000 * self.delta_time
        self.behaviour_patterns_dict["Stomp"]["DurationTimer"] -= 1000 * self.delta_time

        # Update damage flash effect timer
        self.update_damage_flash_effect_timer()

    def update_damage_flash_effect_timer(self):
        
        # Updates the damage flash effect timer

        # If there has been a timer set for the damage flash effect
        if self.extra_information_dict["DamagedFlashEffectTimer"] != None:

            # If the timer has not finished counting
            if self.extra_information_dict["DamagedFlashEffectTimer"] > 0:
                # Decrease the timer
                self.extra_information_dict["DamagedFlashEffectTimer"] -= 1000 * self.delta_time
            
            # If the timer has finished counting
            if self.extra_information_dict["DamagedFlashEffectTimer"] <= 0:
                # Set the damage flash effect timer back to None
                self.extra_information_dict["DamagedFlashEffectTimer"] = None

    def update_and_draw_stomp_attacks(self):
        
        # If there are any stomp attack nodes inside the stomp nodes
        if len(StompController.nodes_group) > 0:

            # For each stomp attack in the group
            for stomp_attack_node in StompController.nodes_group:
                
                # If the stomp attack node has not been reflected
                if stomp_attack_node.reflected == False:
                    # First circle (Lightest colour)
                    pygame_draw_circle(surface = self.surface, color = (63, 42, 39), center = (stomp_attack_node.rect.centerx - self.camera_position[0], stomp_attack_node.rect.centery - self.camera_position[1]), radius = stomp_attack_node.radius, width = 0)

                    # Outline (Darkest colour)
                    pygame_draw_circle(surface = self.surface, color = 	(40, 32, 30), center = (stomp_attack_node.rect.centerx - self.camera_position[0], stomp_attack_node.rect.centery - self.camera_position[1]), radius = stomp_attack_node.radius, width = int(stomp_attack_node.radius / 3))

                    # Second circle (Middle colour)
                    pygame_draw_circle(surface = self.surface, color = 	(93, 72, 67), center = (stomp_attack_node.rect.centerx - self.camera_position[0], stomp_attack_node.rect.centery - self.camera_position[1]), radius = stomp_attack_node.radius * (0.45), width = 0)
                    
                # If the stomp attack node has not been reflected
                elif stomp_attack_node.reflected == True:
                    
                    # First circle (Lightest colour)
                    pygame_draw_circle(surface = self.surface, color = (63 + 90, 42, 39), center = (stomp_attack_node.rect.centerx - self.camera_position[0], stomp_attack_node.rect.centery - self.camera_position[1]), radius = stomp_attack_node.radius, width = 0)

                    # Outline (Darkest colour)
                    pygame_draw_circle(surface = self.surface, color = 	(40 + 90, 32, 30), center = (stomp_attack_node.rect.centerx - self.camera_position[0], stomp_attack_node.rect.centery - self.camera_position[1]), radius = stomp_attack_node.radius, width = int(stomp_attack_node.radius / 3))

                    # Second circle (Middle colour)
                    pygame_draw_circle(surface = self.surface, color = 	(93 + 90, 72, 67), center = (stomp_attack_node.rect.centerx - self.camera_position[0], stomp_attack_node.rect.centery - self.camera_position[1]), radius = stomp_attack_node.radius * (0.45), width = 0)
                    


                # # The center of the rectangle is at the position calculated when the node was created
                # pygame_draw_rect(surface = self.surface, color = "red", rect = (stomp_attack_node.rect.x - self.camera_position[0], stomp_attack_node.rect.y - self.camera_position[1], stomp_attack_node.rect.width, stomp_attack_node.rect.height), width = 1)

                # Move the stomp attack node
                stomp_attack_node.move(delta_time = self.delta_time)

                # If the current radius of the stomp attack node is less than the maximum node radius set
                if stomp_attack_node.radius < self.stomp_controller.maximum_node_radius:
                    # Increase the radius of the current rect
                    stomp_attack_node.increase_size(delta_time = self.delta_time)

    def run(self):
        
        pygame_draw_rect(self.surface, "green", pygame_Rect(self.rect.x - self.camera_position[0], self.rect.y - self.camera_position[1], self.rect.width, self.rect.height), 1)
        pygame_draw_line(self.surface, "white", (0 - self.camera_position[0], self.rect.centery - self.camera_position[1]), (self.surface.get_width() - self.camera_position[0], self.rect.centery - self.camera_position[1]))
        pygame_draw_line(self.surface, "white", (self.rect.centerx - self.camera_position[0], 0 - self.camera_position[1]), (self.rect.centerx - self.camera_position[0], self.surface.get_height() - self.camera_position[1]))

        # Update and draw the stomp attacks
        self.update_and_draw_stomp_attacks()

        # Draw the boss
        self.draw(surface = self.surface, x = self.rect.x - self.camera_position[0], y = self.rect.y - self.camera_position[1])
        
        # Play animations
        self.play_animations()
                
        # Create / update a mask for pixel - perfect collisions
        self.mask = pygame_mask_from_surface(self.image)

                


