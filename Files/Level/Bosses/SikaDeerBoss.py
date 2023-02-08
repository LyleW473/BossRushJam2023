from Global.generic import Generic
from Level.Bosses.BossAttacks.stomp import StompController
from pygame.draw import rect as pygame_draw_rect
from pygame.draw import line as pygame_draw_line
from pygame import Rect as pygame_Rect
from pygame.draw import circle as pygame_draw_circle
from pygame.mask import from_surface as pygame_mask_from_surface
from Global.functions import change_image_colour
from random import choice as random_choice
from Level.Bosses.AI import AI
from pygame.image import load as load_image
from pygame.transform import scale as scale_image
from Global.functions import play_death_animation
from os import listdir as os_listdir
from pygame.draw import ellipse as pygame_draw_ellipse
from math import degrees, cos, sin
from Global.settings import TILE_SIZE

class SikaDeerBoss(Generic, AI):

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
        # Note: Do this before inheriting the AI class so that the rect positions are the same
        self.rect.midbottom = (x, y)

        # Inherit from the AI class
        AI.__init__(self)

        """ List of "hidden" added attributes
        self.delta_time
        self.camera_position
        self.players_position
        self.neighbouring_tiles_dict
        """

        # Stomp controller used to create stomp nodes and update each individual stomp node
        self.stomp_controller = StompController(scale_multiplier = scale_multiplier)

        # The current action that the boss is performing
        self.current_action = "Chase"


        # To delay actions right after spawning, set the cooldown timer to a desired amount of time and add it to this list, so that the cooldown timers can be updated
        self.previous_actions_dict = {
                                    "Stomp": None, 
                                    "Target": None
                                    }
        
        # A dictionary containing information relating to the behaviour of the Sika deer boss
        self.behaviour_patterns_dict = {

                                    # Additional actions that the boss can perform, other than chase

                                    "Stomp": {
                                            # Note: Changing the number of stomps and the duration will affect how fast each wave of stomps is spawned
                                            "NumberOfStomps": 12,
                                            "Duration": 3000, 
                                            "DurationTimer": None, # Timer used to check if the attack is over

                                            "Cooldown": 10000, 
                                            "CooldownTimer": 10000, # Delayed cooldown to when the boss can first use the stomp attackddd

                                            # The variation of the stomp for one entire stomp attack
                                            "StompAttackVariation": 0
                                             },

                                    "Chase": { 
                                            "FullAnimationDuration": 700
                                              
                                    
                                              },

                                    # Target and charge
                                    "Target": { 
                                            "Duration": 1000,
                                            "DurationTimer": None,
                                            "CooldownTimer": 1000,  # This will be set to be the charge cooldown after the attack has completed (Change this number if you want to delay when the boss can first charge attack)
                                            "Cooldown": 50000, # Set to random number, this will be changed once the charge attack has finished
                                            "FullAnimationDuration": 150,
                                            },

                                    "Charge": {

                                            "Duration": 2000, # The maximum duration that the boss will charge for
                                            "DurationTimer": None,
                                            "Cooldown": 12000,
                                            "CooldownTimer": None,
                                            "FullAnimationDuration": 150,
                                            
                                            "ChargeDirection": None,
                                            "ChargeAngle": None,
                                            "EnterStunnedStateBoolean": False, # A boolean value that represents whether the boss has collided with the player during the charge attack"

                                            # Movement (Keep the time values to be less than the full charge duration)
                                            "ChargeDistanceTravelled": 10 * TILE_SIZE,
                                            "HorizontalTimeToTravelDistanceAtFinalVelocity": 0.15, 
                                            "VerticalTimeToTravelDistanceAtFinalVelocity": 0.15, 
                                            "HorizontalTimeToReachFinalVelocity": 0.25,
                                            "VerticalTimeToReachFinalVelocity": 0.25,


                                                },
                                    # Stunned
                                    "Stunned": {
                                            "Duration": 4000,
                                            "DurationTimer": None,
                                            "FullAnimationDuration": 1000,
                                            "StunnedDamageAmount": 100

                                            },

                                    "Death": {
                                            "Images": None

                                            }
                                    }
        
        # Declare the animation attributes
        self.declare_animation_attributes()

        # A dictionary containing extra information about the Sika deer boss
        self.extra_information_dict = {    
                                        # Health
                                        "CurrentHealth": 20000,
                                        "MaximumHealth": 20000,

                                        # Damage flash effect
                                        "DamagedFlashEffectTime": 100, # The time that the flash effect should play when the boss is damaged
                                        "DamagedFlashEffectTimer": None,

                                        # Knockback damage
                                        "KnockbackDamage": 20,
                                        
                                      }
        

    # ----------------------------------------------------------------------------------
    # Animations

    def declare_animation_attributes(self):

        # Declares the animation attributes

        # Set the animation index as 0
        self.animation_index = 0         

        # --------------------------
        # Stomping 

        # Each full cycle of the stomp animation has 2 stomps 
        # Note: (number_of_stomps + 1) because the first animation frame does not count as a stomp, so add another one
        number_of_animation_cycles = (self.behaviour_patterns_dict["Stomp"]["NumberOfStomps"] + 1) / 2

        # The time between each frame should be how long the stomp attack lasts, divided by the total number of animation frames, depending on how many cycles there are 
        self.behaviour_patterns_dict["Stomp"]["TimeBetweenAnimFrames"] = self.behaviour_patterns_dict["Stomp"]["Duration"] / (len(SikaDeerBoss.ImagesDict["Stomp"]) * number_of_animation_cycles)

        # Set the animation frame timer to start at 0, this is so that the first animation frame does not count as a stomp
        self.behaviour_patterns_dict["Stomp"]["AnimationFrameTimer"] = 0

        # --------------------------
        # Chasing

        # The time between each frame should be how long each chase animation cycle should last, divided by the total number of animation frames
        self.behaviour_patterns_dict["Chase"]["TimeBetweenAnimFrames"] = self.behaviour_patterns_dict["Chase"]["FullAnimationDuration"] / (len(SikaDeerBoss.ImagesDict["Chase"]))

        # Set the animation frame timer to start as the time between animation frames
        self.behaviour_patterns_dict["Chase"]["AnimationFrameTimer"] = self.behaviour_patterns_dict["Chase"]["TimeBetweenAnimFrames"]

        # --------------------------
        # Targeting

        # Note: All directions have the same number of animation frames

        # The time between each frame should be how long each target animation cycle should last, divided by the total number of animation frames
        self.behaviour_patterns_dict["Target"]["TimeBetweenAnimFrames"] = self.behaviour_patterns_dict["Target"]["FullAnimationDuration"] / (len(SikaDeerBoss.ImagesDict["Target"]["Up"]))

        # Set the animation frame timer to start as the time between animation frames
        self.behaviour_patterns_dict["Target"]["AnimationFrameTimer"] = self.behaviour_patterns_dict["Target"]["TimeBetweenAnimFrames"]

        # --------------------------
        # Charging
        # Note: All directions have the same number of animation frames

        # The time between each frame should be how long the charge attack animation lasts, divided by the total number of animation frames
        self.behaviour_patterns_dict["Charge"]["TimeBetweenAnimFrames"] = self.behaviour_patterns_dict["Charge"]["FullAnimationDuration"] / (len(SikaDeerBoss.ImagesDict["Charge"]["Up"]))

        # Set the animation frame timer to start as the time between animation frames
        self.behaviour_patterns_dict["Charge"]["AnimationFrameTimer"] = self.behaviour_patterns_dict["Charge"]["TimeBetweenAnimFrames"]

        # --------------------------
        # Stunned

        # The time between each frame should be how long the stunned animation lasts, divided by the total number of animation frames
        self.behaviour_patterns_dict["Stunned"]["TimeBetweenAnimFrames"] = self.behaviour_patterns_dict["Stunned"]["FullAnimationDuration"] / (len(SikaDeerBoss.ImagesDict["Stunned"]))

        # Set the animation frame timer to start as the time between animation frames
        self.behaviour_patterns_dict["Stunned"]["AnimationFrameTimer"] = self.behaviour_patterns_dict["Stunned"]["TimeBetweenAnimFrames"]

    def find_look_direction(self):

        # Finds the look direction of the boss
        
        # The offset should be 360 divided by 8 (because of 8 directional movement), divided by 2
        segment_offset = (360 / 8) / 2

        match self.movement_information_dict["Angle"]:
            # Right
            case _ if (0 <= degrees(self.movement_information_dict["Angle"]) < segment_offset) or ((360 - segment_offset) <= degrees(self.movement_information_dict["Angle"]) < 360):
                current_look_direction = "Right"
            # UpRight
            case _ if (segment_offset <= degrees(self.movement_information_dict["Angle"]) < segment_offset + 45):
                current_look_direction = "Up Right"
            # Up
            case _ if (90 - segment_offset) <= degrees(self.movement_information_dict["Angle"]) < (90 + segment_offset):
                current_look_direction = "Up"
            # UpLeft
            case _ if (90 + segment_offset) <= degrees(self.movement_information_dict["Angle"]) < (90 + segment_offset + 45):
                current_look_direction = "Up Left"
            # Left
            case _ if (180 - segment_offset) <= degrees(self.movement_information_dict["Angle"]) < (180 + segment_offset):
                current_look_direction = "Left"
            # DownLeft
            case _ if (180 + segment_offset) <= degrees(self.movement_information_dict["Angle"]) < (180 + segment_offset + 45):
                current_look_direction = "Down Left"
            # Down
            case _ if (270 - segment_offset) <= degrees(self.movement_information_dict["Angle"]) < (270 + segment_offset):
                current_look_direction = "Down" 
            # DownRight
            case _ if (270 + segment_offset) <= degrees(self.movement_information_dict["Angle"]) < (270 + segment_offset + 45):
                current_look_direction = "Down Right"

        # Return the current look direction
        return current_look_direction

    def play_animations(self):

        # -----------------------------------
        # Set image

        # If the current action is not "Target" and not "Charge"
        if self.current_action != "Target" and self.current_action != "Charge":
            # The current animation list
            current_animation_list = SikaDeerBoss.ImagesDict[self.current_action]
            # The current animation image
            current_animation_image = current_animation_list[self.animation_index]
        
        # If the current action is "Target" or "Charge"
        elif self.current_action == "Target" or self.current_action == "Charge":
            
            # Only do this if the current action is "Target"
            if self.current_action == "Target":
                # Find the player (To continuously update the look angle)
                self.find_player(current_position = self.rect.center, player_position = self.players_position, delta_time = self.delta_time)

            # Find the current look direction
            current_look_direction = self.find_look_direction()

            # The current animation list
            current_animation_list = SikaDeerBoss.ImagesDict[self.current_action][current_look_direction]

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

        # If the current action is to "Stomp"
        if self.current_action == "Stomp":
                
                # If the stomp attack has not been completed
                if self.behaviour_patterns_dict[self.current_action]["DurationTimer"] > 0:
                    
                    # If the current animation index is not the last index inside the animation list and the animation frame timer has finished counting
                    if self.animation_index < (len(current_animation_list) - 1) and (self.behaviour_patterns_dict[self.current_action]["AnimationFrameTimer"]) <= 0:
                        
                        # If this animation is one of the keyframes where the boss has stomped
                        if (self.animation_index == 0 and self.behaviour_patterns_dict[self.current_action]["DurationTimer"] != self.behaviour_patterns_dict[self.current_action]["Duration"]) \
                            or self.animation_index == 5:
                        
                            # Start the stomp attack
                            self.stomp_attack()

                            # print("STOMP", self.animation_index, self.behaviour_patterns_dict[self.current_action]["DurationTimer"], self.behaviour_patterns_dict[self.current_action]["Duration"])

                        # Go the next animation frame
                        self.animation_index += 1

                        # Reset the timer (adding will help with accuracy)
                        self.behaviour_patterns_dict[self.current_action]["AnimationFrameTimer"] += self.behaviour_patterns_dict[self.current_action]["TimeBetweenAnimFrames"] 

                    # If the current animation index is at the last index inside the animation list and the animation frame timer has finished counting
                    if self.animation_index == (len(current_animation_list) - 1) and (self.behaviour_patterns_dict[self.current_action]["AnimationFrameTimer"] <= 0):
                        # Go the the first animation frame (reset the animation)
                        self.animation_index = 0

                        # Reset the timer (adding will help with accuracy)
                        self.behaviour_patterns_dict[self.current_action]["AnimationFrameTimer"] += self.behaviour_patterns_dict[self.current_action]["TimeBetweenAnimFrames"]

                # If the stomp attack has been completed
                elif self.behaviour_patterns_dict[self.current_action]["DurationTimer"] <= 0:
                    
                    # Change to a different behaviour

                    # Reset the animation index
                    self.animation_index = 0

        # If the current action is to "Chase" 
        elif self.current_action == "Chase":
            
            # If the current animation index is not the last index inside the animation list and the animation frame timer has finished counting
            if self.animation_index < (len(current_animation_list) - 1) and (self.behaviour_patterns_dict[self.current_action]["AnimationFrameTimer"]) <= 0:
                # Go the next animation frame
                self.animation_index += 1

                # Reset the timer (adding will help with accuracy)
                self.behaviour_patterns_dict[self.current_action]["AnimationFrameTimer"] += self.behaviour_patterns_dict[self.current_action]["TimeBetweenAnimFrames"]

            # If the current animation index is at the last index inside the animation list and the animation frame timer has finished counting
            if self.animation_index == (len(current_animation_list) - 1) and (self.behaviour_patterns_dict[self.current_action]["AnimationFrameTimer"] <= 0):
                # Go the the first animation frame (reset the animation)
                self.animation_index = 0

                # Reset the timer (adding will help with accuracy)
                self.behaviour_patterns_dict[self.current_action]["AnimationFrameTimer"] += self.behaviour_patterns_dict[self.current_action]["TimeBetweenAnimFrames"]

        # If the current action is to "Target"
        elif self.current_action == "Target":

            # If the current animation index is not the last index inside the animation list and the animation frame timer has finished counting
            if self.animation_index < (len(current_animation_list) - 1) and (self.behaviour_patterns_dict[self.current_action]["AnimationFrameTimer"]) <= 0:
                # Go the next animation frame
                self.animation_index += 1

                # Reset the timer (adding will help with accuracy)
                self.behaviour_patterns_dict[self.current_action]["AnimationFrameTimer"] += self.behaviour_patterns_dict[self.current_action]["TimeBetweenAnimFrames"]

            # If the current animation index is at the last index inside the animation list and the animation frame timer has finished counting
            if self.animation_index == (len(current_animation_list) - 1) and (self.behaviour_patterns_dict[self.current_action]["AnimationFrameTimer"] <= 0):
                # Go the the first animation frame (reset the animation)
                self.animation_index = 0

                # Reset the timer (adding will help with accuracy)
                self.behaviour_patterns_dict[self.current_action]["AnimationFrameTimer"] += self.behaviour_patterns_dict[self.current_action]["TimeBetweenAnimFrames"]

        # If the current action is to "Charge"
        elif self.current_action == "Charge":

            # If the current animation index is not the last index inside the animation list and the animation frame timer has finished counting
            if self.animation_index < (len(current_animation_list) - 1) and (self.behaviour_patterns_dict[self.current_action]["AnimationFrameTimer"]) <= 0:
                # Go the next animation frame
                self.animation_index += 1

                # Reset the timer (adding will help with accuracy)
                self.behaviour_patterns_dict[self.current_action]["AnimationFrameTimer"] += self.behaviour_patterns_dict[self.current_action]["TimeBetweenAnimFrames"]

        # If the current action is to "Stunned"
        elif self.current_action == "Stunned":

            # If the current animation index is not the last index inside the animation list and the animation frame timer has finished counting
            if self.animation_index < (len(current_animation_list) - 1) and (self.behaviour_patterns_dict[self.current_action]["AnimationFrameTimer"]) <= 0:
                # Go the next animation frame
                self.animation_index += 1

                # Reset the timer (adding will help with accuracy)
                self.behaviour_patterns_dict[self.current_action]["AnimationFrameTimer"] += self.behaviour_patterns_dict[self.current_action]["TimeBetweenAnimFrames"]

            # If the current animation index is at the last index inside the animation list and the animation frame timer has finished counting
            if self.animation_index == (len(current_animation_list) - 1) and (self.behaviour_patterns_dict[self.current_action]["AnimationFrameTimer"] <= 0):
                # Go the the first animation frame (reset the animation)
                self.animation_index = 0

                # Reset the timer (adding will help with accuracy)
                self.behaviour_patterns_dict[self.current_action]["AnimationFrameTimer"] += self.behaviour_patterns_dict[self.current_action]["TimeBetweenAnimFrames"]

        # -----------------------------------
        # Updating timers relating to abilities
        
        # Decrease the animation frame timer
        self.behaviour_patterns_dict[self.current_action]["AnimationFrameTimer"] -= 1000 * self.delta_time

        # Update damage flash effect timer
        self.update_damage_flash_effect_timer()

    # ----------------------------------------------------------------------------------
    # Timer updating

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

    def update_duration_timers(self):

        # Updates the duration timer of the current action 
        # If the duration timer is over, the action is added to the previous actions list so that their cooldown timer can be updated

        # If the current action is not "Chase" (Chase does not have a duration timer)
        if self.current_action != "Chase":
            
            # If the current action's duration timer has not finished counting down
            if self.behaviour_patterns_dict[self.current_action]["DurationTimer"] > 0:
                # Decrease the timer
                self.behaviour_patterns_dict[self.current_action]["DurationTimer"] -= 1000 * self.delta_time
            
            # If the current action's duration timer has finished counting down
            if self.behaviour_patterns_dict[self.current_action]["DurationTimer"] <= 0:
                # Reset the duration timer back to None
                self.behaviour_patterns_dict[self.current_action]["DurationTimer"] = None

                # Reset the animation index
                self.animation_index = 0

                # If the current action is not "Stunned"
                if self.current_action != "Stunned":
                    # Set the cooldown timer of the previous action to start counting down
                    self.behaviour_patterns_dict[self.current_action]["CooldownTimer"] = self.behaviour_patterns_dict[self.current_action]["Cooldown"]

                    # Add the current action to the previous actions dict so that its cooldown timer can count down
                    self.previous_actions_dict[self.current_action] = None

                # If the current action is "Target"
                if self.current_action == "Target":

                    # Set the "Charge" duration timer to start counting down
                    self.behaviour_patterns_dict["Charge"]["DurationTimer"] = self.behaviour_patterns_dict["Charge"]["Duration"]

                    # Set the current charge direction (so that the boss cannot change direction whilst charging)
                    self.behaviour_patterns_dict["Charge"]["ChargeDirection"] = self.find_look_direction()

                    # Store the current charge angle (for calculations for movement)
                    self.behaviour_patterns_dict["Charge"]["ChargeAngle"] = self.movement_information_dict["Angle"]

                    # Reset the horizontal and vertical velocity (V, A and S are updated during the charge attack)
                    self.movement_information_dict["HorizontalSuvatU"] = 0
                    self.movement_information_dict["VerticalSuvatU"] = 0
                            
                    # Set the current action to Charge
                    self.current_action = "Charge"

                # If the current action is "Charge
                elif self.current_action == "Charge":

                    # Set the "Target" cooldown timer to be the same as the "Charge" cooldown timer (This is because the attack sequence starts with "Target" and then "Charge")
                    self.behaviour_patterns_dict["Target"]["CooldownTimer"] = self.behaviour_patterns_dict["Charge"]["CooldownTimer"]

                    # Reset the current charge direction back to None
                    self.behaviour_patterns_dict["Charge"]["ChargeDirection"] = None

                    # If "EnterStunnedStateBoolean" was set to True, i.e. the boss collided a building tile
                    if self.behaviour_patterns_dict["Charge"]["EnterStunnedStateBoolean"] == True:
                        
                        # Set the current action to "Stunned"
                        self.current_action = "Stunned"

                        # Set "EnterStunnedStateBoolean" back to False
                        self.behaviour_patterns_dict["Charge"]["EnterStunnedStateBoolean"] = False
                    
                    # If "EnterStunnedStateBoolean" is set to False, i.e. the boss did not collide with a building tile
                    elif self.behaviour_patterns_dict["Charge"]["EnterStunnedStateBoolean"] == False:
                        print("SET BACK TO CHASE")
                        # Set the current action back to Chase
                        self.current_action = "Chase"

                # If the current action isn't "Target" or "Charge"
                elif self.current_action != "Target" or self.current_action != "Charge":
                        
                    # Set the current action back to Chase
                    # Note: When changed back to Chase, the "decide_action" method will be able to change to any other action
                    #### Could call decide_action here to switch between actions without going back to Chase
                    self.current_action = "Chase"

    def update_cooldown_timers(self):
        
        # Updates the cooldown timers of any action inside the previous actions dictionary

        # If there are any previous actions
        if len(self.previous_actions_dict) > 0:

            # For each key inside the keys of the previous actions dictionary (The value is the length of the dictionary before it was added)
            for previous_action in self.previous_actions_dict.copy().keys():
                
                # If the timer has not finished counting
                if self.behaviour_patterns_dict[previous_action]["CooldownTimer"] > 0:
                    # Decrease the cooldown timer
                    self.behaviour_patterns_dict[previous_action]["CooldownTimer"] -= 1000 * self.delta_time

                # If the timer has finished counting 
                if self.behaviour_patterns_dict[previous_action]["CooldownTimer"] <= 0:
                    # Reset the timer back to None
                    self.behaviour_patterns_dict[previous_action]["CooldownTimer"] = None

                    # Pop the previous action out of the previous actions dictionary
                    self.previous_actions_dict.pop(previous_action)

    # ----------------------------------------------------------------------------------
    # Gameplay

    def update_and_draw_stomp_attacks(self):
        
        # If there are any stomp attack nodes inside the stomp nodes
        if len(StompController.nodes_group) > 0:

            # For each stomp attack in the group
            for stomp_attack_node in StompController.nodes_group:
                
                # ---------------------------------------------------------------------------
                # Drawing the stomp attack node
                
                # ---------------------------------
                # Assigning the colours

                # If the stomp attack node has not been reflected
                if stomp_attack_node.reflected == False:
                    
                    # Set the circle colours to be the default colours
                    circle_colours = ((63, 42, 39), (40, 32, 30), (93, 72, 67)) 

                # If the stomp attack node has not been reflected
                elif stomp_attack_node.reflected == True:
                    
                     # Set the circle colours to be the reflected colours
                    circle_colours = ((63 + stomp_attack_node.reflected_additive_colour[1], 42, 39), (40 + stomp_attack_node.reflected_additive_colour[1], 32, 30), (93 + stomp_attack_node.reflected_additive_colour[1], 72, 67)) 

                    # Change the value of the reflected colour
                    stomp_attack_node.change_reflected_colour_value(delta_time = self.delta_time)

                # ---------------------------------
                # Drawing the circles

                # First circle (Lightest colour)
                pygame_draw_circle(surface = self.surface, color = circle_colours[0], center = (stomp_attack_node.rect.centerx - self.camera_position[0], stomp_attack_node.rect.centery - self.camera_position[1]), radius = stomp_attack_node.radius, width = 0)

                # Outline (Darkest colour)
                pygame_draw_circle(surface = self.surface, color = 	circle_colours[1], center = (stomp_attack_node.rect.centerx - self.camera_position[0], stomp_attack_node.rect.centery - self.camera_position[1]), radius = stomp_attack_node.radius, width = int(stomp_attack_node.radius / 3))

                # Second circle (Middle colour)
                pygame_draw_circle(surface = self.surface, color = 	circle_colours[2], center = (stomp_attack_node.rect.centerx - self.camera_position[0], stomp_attack_node.rect.centery - self.camera_position[1]), radius = stomp_attack_node.radius * (0.45), width = 0)
                

                # # The center of the rectangle is at the position calculated when the node was created
                # pygame_draw_rect(surface = self.surface, color = "red", rect = (stomp_attack_node.rect.x - self.camera_position[0], stomp_attack_node.rect.y - self.camera_position[1], stomp_attack_node.rect.width, stomp_attack_node.rect.height), width = 1)

                # ---------------------------------------------------------------------------
                # Other

                # Move the stomp attack node
                stomp_attack_node.move(delta_time = self.delta_time)

                # If the current radius of the stomp attack node is less than the maximum node radius set
                if stomp_attack_node.radius < self.stomp_controller.maximum_node_radius:
                    # Increase the radius of the current rect
                    stomp_attack_node.increase_size(delta_time = self.delta_time)

    def stomp_attack(self):

        # Performs the stomp attack

        # If there are no stomp attack nodes (i.e. the start of the stomp attack)
        if len(StompController.nodes_group) == 0:
            # Choose a random variation of the stomp attack
            self.extra_information_dict["StompAttackVariation"] = random_choice( (0, 1, 1, 2))
    
        # Create stomp attack nodes
        self.stomp_controller.create_stomp_nodes(center_of_boss_position = (self.rect.centerx, self.rect.centery), desired_number_of_nodes = 12, attack_variation=  self.extra_information_dict["StompAttackVariation"])

    def chase_player(self):

        # Finds and chases the player

        # Find the player (for angles and movement)
        self.find_player(current_position = self.rect.center, player_position = self.players_position, delta_time = self.delta_time)

        # Move the boss
        self.move()

    def decide_action(self):

        # The main "brain" of the deer boss, which will decide on what action to perform
        
        # If the current action is chasing
        if self.current_action == "Chase":
            
            # Create a list of all the actions that the AI can currently perform, if the action's cooldown timer is None
            action_list = [action for action in self.behaviour_patterns_dict.keys() if (action == "Stomp" or action == "Target") and self.behaviour_patterns_dict[action]["CooldownTimer"] == None]

            # If there are any possible actions that the boss can perform
            if len(action_list) > 0:

                # Reset the animation index whenever we change the action
                self.animation_index = 0

                # Choose a random action from the possible actions the boss can perform and set it as the current action
                self.current_action = random_choice(action_list)

                print("SET TO", self.current_action, self.animation_index)

                # If the current action that was chosen was "Target", and target duration timer has not been set to start counting down yet
                if self.current_action == "Target" and self.behaviour_patterns_dict["Target"]["DurationTimer"] == None:
                    # Set the duration timer to start counting down
                    self.behaviour_patterns_dict["Target"]["DurationTimer"] = self.behaviour_patterns_dict["Target"]["Duration"] 

                # If the current action is to "Stomp"
                elif self.current_action == "Stomp":
                    # Set the duration timer to start counting down
                    self.behaviour_patterns_dict[self.current_action]["DurationTimer"] = self.behaviour_patterns_dict["Stomp"]["Duration"]

                    # Reset the movement acceleration
                    self.reset_movement_acceleration(horizontal_reset = True, vertical_reset = True)

            # If there are no possible actions that the boss can perform
            elif len(action_list) == 0: 
                # Continue chasing the player
                self.chase_player()
        
        # If the current action is to charge
        elif self.current_action == "Charge":

            # Charge attack the player
            self.charge_attack()

    def charge_attack(self):

        # Responsible for changing the movement speed of the boss so that the charge attack is faster than the default movement speed
        # Note: These will be reset back to the default values when the current action is set back to "Chase"


        # ------------------------------------------------------------------------------
        # Movement  

        # ----------------------------------------
        # Horizontal

        # Set the horizontal distance travelled based on the current angle that the player is to the AI
        # print(self.behaviour_patterns_dict["Charge"]["ChargeDirection"], self.movement_information_dict["HorizontalSuvatU"])
        horizontal_distance_travelled_at_final_velocity = (self.behaviour_patterns_dict["Charge"]["ChargeDistanceTravelled"] * cos(self.behaviour_patterns_dict["Charge"]["ChargeAngle"]))

        # Equation = (2s - at^2) / 2t
        self.movement_information_dict["HorizontalSuvatV"] = (2 * horizontal_distance_travelled_at_final_velocity) / (2 * self.behaviour_patterns_dict["Charge"]["HorizontalTimeToTravelDistanceAtFinalVelocity"])
        # Set the current acceleration of the AI depending on the current velocity of the player
        self.movement_information_dict["HorizontalSuvatA"] = (self.movement_information_dict["HorizontalSuvatV"] - self.movement_information_dict["HorizontalSuvatU"]) / self.behaviour_patterns_dict["Charge"]["HorizontalTimeToReachFinalVelocity"]
        

        # ----------------------------------------
        # Vertical

        # Set the vertical distance travelled based on the current angle that the player is to the AI
        vertical_distance_travelled_at_final_velocity = (self.behaviour_patterns_dict["Charge"]["ChargeDistanceTravelled"] * sin(self.behaviour_patterns_dict["Charge"]["ChargeAngle"]))

        # Equation = (2s - at^2) / 2t
        self.movement_information_dict["VerticalSuvatV"] = (2 * vertical_distance_travelled_at_final_velocity) / (2 * self.behaviour_patterns_dict["Charge"]["VerticalTimeToTravelDistanceAtFinalVelocity"])

        # Set the current acceleration of the AI depending on the current velocity of the player
        self.movement_information_dict["VerticalSuvatA"] = (self.movement_information_dict["VerticalSuvatV"] - self.movement_information_dict["VerticalSuvatU"]) / self.behaviour_patterns_dict["Charge"]["VerticalTimeToReachFinalVelocity"]

        # Move the boss
        self.move()

    def run(self):
        
        # Update and draw the stomp attacks (always do this so that even when the boss is dead, these are still updated)
        self.update_and_draw_stomp_attacks()

        # If the boss' health is greater than 0
        if self.extra_information_dict["CurrentHealth"] > 0:
        
            # Decide the action that the boss should perform
            self.decide_action()

            pygame_draw_rect(self.surface, "green", pygame_Rect(self.rect.x - self.camera_position[0], self.rect.y - self.camera_position[1], self.rect.width, self.rect.height), 1)
            pygame_draw_line(self.surface, "white", (0 - self.camera_position[0], self.rect.centery - self.camera_position[1]), (self.surface.get_width() - self.camera_position[0], self.rect.centery - self.camera_position[1]))
            pygame_draw_line(self.surface, "white", (self.rect.centerx - self.camera_position[0], 0 - self.camera_position[1]), (self.rect.centerx - self.camera_position[0], self.surface.get_height() - self.camera_position[1]))

            # Draw the boss 
            # Note: Additional positions to center the image (this is because the animation images can vary in size)
            self.draw(
                surface = self.surface, 
                x = (self.rect.x - ((self.image.get_width() / 2)  - (self.rect.width / 2))) - self.camera_position[0], 
                y = (self.rect.y - ((self.image.get_height() / 2) - (self.rect.height / 2))) - self.camera_position[1]
                    )

            # Play animations
            self.play_animations()

            # Create / update a mask for pixel - perfect collisions
            self.mask = pygame_mask_from_surface(self.image)

            # Update the duration timers
            self.update_duration_timers()

            # Update the cooldown timers
            self.update_cooldown_timers()

            # Update the knockback collision idle timer
            self.update_knockback_collision_idle_timer(delta_time = self.delta_time)

            # TEMPORARY
            for tile in self.neighbouring_tiles_dict.keys():
                pygame_draw_rect(self.surface, "white", (tile.rect.x - self.camera_position[0], tile.rect.y - self.camera_position[1], tile.rect.width, tile.rect.height))

        # If the boss' health is less than 0
        if self.extra_information_dict["CurrentHealth"] <= 0:
            
            # If the boss does not have a death animation images list yet
            if self.behaviour_patterns_dict["Death"]["Images"]  == None:
                
                # Reset the animation index
                self.animation_index = 0

                # Set the current action to death
                self.current_action = "Death"

                # Load and scale the death animation images 
                self.behaviour_patterns_dict["Death"]["Images"] = [scale_image(
                    load_image(f"graphics/Misc/DeathAnimation/{i}.png").convert_alpha(), ((load_image(f"graphics/Misc/DeathAnimation/{i}.png").convert_alpha().get_width() * 2, load_image(f"graphics/Misc/DeathAnimation/{i}.png").convert_alpha().get_height() * 2)))  
                    for i in range(0, len(os_listdir("graphics/Misc/DeathAnimation")))]

                # Set up the animation speed and timer
                self.behaviour_patterns_dict["Death"]["FullAnimationDuration"] = 800
                self.behaviour_patterns_dict["Death"]["TimeBetweenAnimFrames"] = self.behaviour_patterns_dict["Death"]["FullAnimationDuration"] / len(self.behaviour_patterns_dict["Death"]["Images"])
                self.behaviour_patterns_dict["Death"]["AnimationFrameTimer"] = self.behaviour_patterns_dict["Death"]["TimeBetweenAnimFrames"]
            
            # Set the current animation image and blit position
            current_animation_image = self.behaviour_patterns_dict["Death"]["Images"][self.animation_index]
            blit_position = ((self.rect.midbottom[0] - self.camera_position[0]) - (current_animation_image.get_width() / 2), (self.rect.midbottom[1] - self.camera_position[1]) - (current_animation_image.get_height())) 

            # Only when the death animation is complete
            if self.animation_index == (len(self.behaviour_patterns_dict["Death"]["Images"]) - 1):
                # Update damage flash effect timer
                self.update_damage_flash_effect_timer()
                # If the player shoots the skull
                if self.extra_information_dict["DamagedFlashEffectTimer"] != None:
                    # Set the current animation image to be a flashed version of the current animation image (a white flash effect)
                    current_animation_image = change_image_colour(current_animation_image = current_animation_image, desired_colour =  (255, 255, 255))

            # Create / update a mask for pixel - perfect collisions
            self.mask = pygame_mask_from_surface(current_animation_image)

            # Draw a shadow ellipse underneath the boss
            pygame_draw_ellipse(
                surface = self.surface, 
                color = (35, 35, 35), 
                rect = ((self.rect.centerx - self.camera_position[0]) - 20, 
                ((self.rect.centery + 20) - self.camera_position[1]) - 20, 40, 40), 
                width = 0)

            # Draw the death animation
            self.surface.blit(current_animation_image, blit_position)

            # If the end of the animation has not been reached yet
            if self.animation_index < (len(self.behaviour_patterns_dict["Death"]["Images"]) - 1):
                # Play the death animation
                self.animation_index, self.behaviour_patterns_dict["Death"]["AnimationFrameTimer"] = play_death_animation(
                                                                                                                current_animation_index = self.animation_index, 
                                                                                                                current_animation_list = self.behaviour_patterns_dict["Death"]["Images"],
                                                                                                                animation_frame_timer = self.behaviour_patterns_dict["Death"]["AnimationFrameTimer"],
                                                                                                                time_between_animation_frames = self.behaviour_patterns_dict["Death"]["TimeBetweenAnimFrames"]
                                                                                                                )


                # Decrease the death animation frame timer
                self.behaviour_patterns_dict["Death"]["AnimationFrameTimer"] -= 1000 * self.delta_time


