from Global.generic import Generic
from Level.Bosses.AI import AI
from Global.settings import TILE_SIZE, FULL_DEATH_ANIMATION_DURATION
from random import choice as random_choice
from Global.functions import change_image_colour, change_image_colour_v2, draw_text
from pygame.mask import from_surface as pygame_mask_from_surface
from pygame.image import load as load_image
from pygame.transform import scale as scale_image
from os import listdir as os_listdir
from Level.Bosses.BossAttacks.chilli_attacks import ChilliProjectileController
from Level.Bosses.BossAttacks.dive_bomb_attack import DiveBombAttackController
from math import sin, cos, radians
from pygame.font import Font as pygame_font_Font
from Level.effect_text import EffectText
from pygame import Surface as pygame_Surface
from pygame.draw import rect as pygame_draw_rect
from pygame.draw import circle as pygame_draw_circle

class GoldenMonkeyBoss(Generic, AI):

    # ImagesDict = ?? (This is set when the boss is instantiated)
    # Example: Chase : [Direction][Image list]
    
    # Characteristics
    knockback_damage = 20
    maximum_health = 20000
    maximum_energy_amount = 100
    

    # SUVAT variables
    suvat_dict = { 
                # The default distance travelled
                "DefaultDistanceTravelled": 3 * TILE_SIZE,

                # Time to travel the horizontal/vertical distance at the final veloctiy
                "DefaultHorizontalTimeToTravelDistanceAtFinalVelocity": 0.52,
                "DefaultVerticalTimeToTravelDistanceAtFinalVelocity": 0.52,

                # Time to reach / accelerate to the final horizontal/vertical velocity
                "DefaultHorizontalTimeToReachFinalVelocity": 0.15,
                "DefaultVerticalTimeToReachFinalVelocity": 0.15,

                # The distance the AI has to be away from the player to stop chasing them
                "DistanceThreshold": 5 

                }

    def __init__(self, x, y, surface, scale_multiplier):

        # Surface that the boss is drawn onto
        self.surface = surface 
        
        # The starting image when spawned (Used as the starting image and ending image for the boss at the start of the game and when the player dies)
        self.starting_image = GoldenMonkeyBoss.ImagesDict["Sleep"][0]

        # Inherit from the Generic class, which has basic attributes and methods.
        Generic.__init__(self, x = x , y = y, image = self.starting_image)

        # Spawn the boss at the middle of the tile, with the bottom of the boss being at the bottom of the tile
        # Note: Do this before inheriting the AI class so that the rect positions are the same
        self.rect.midbottom = (x, y)

        # Inherit from the AI class
        AI.__init__(self, max_health = GoldenMonkeyBoss.maximum_health, knockback_damage = GoldenMonkeyBoss.knockback_damage, suvat_dict = GoldenMonkeyBoss.suvat_dict)

        """ List of "hidden" added attributes
        self.delta_time
        self.camera_position
        self.players_position
        self.neighbouring_tiles_dict
        self.camera_shake_events_list # A list of the camera shake events used to add the "Stomp" camera shake effect
        """

        # The current action that the boss is performing
        self.current_action = "Chase"
        
        # The amount of energy that the boss starts with
        self.energy_amount = GoldenMonkeyBoss.maximum_energy_amount

        # To delay actions right after spawning, set the cooldown timer to a desired amount of time and add it to this list, so that the cooldown timers can be updated
        self.previous_actions_dict = {
                                    "SpiralAttack": None 
                                    }

        # A dictionary containing information relating to the behaviour of the Sika deer boss
        self.behaviour_patterns_dict = {

                                    "Chase": { 
                                            "FullAnimationDuration": 600,

                                            "ChilliThrowingCooldown": 260,
                                            "ChilliThrowingCooldownTimer": None
                                              },
                                    
                                    "SpiralAttack": {
                                                    "EnergyDepletionAmount": 30,
                                                    "Duration": 6000,
                                                    "DurationTimer": None,
                                                    "SpiralChilliSpawningCooldown": 60, # Cooldown between each chilli spawned in the spiral attack (50 chillis)
                                                    "SpiralChilliSpawningCooldownTimer": None, 

                                                    "Cooldown": 10000,
                                                    "CooldownTimer": 10000, # Start the cooldown timer at 10 seconds after being spawned

                                                    # Animation
                                                    "FullAnimationDuration": 150,
                                                    
                                                    # Moving the boss around a point in a circle
                                                    "SpiralAttackSpinPivotPoint": None,
                                                    "SpiralAttackSpinPivotDistance": 15,
                                                    "SpiralAttackSpinAngle": 0, # The angle the boss will be compared to its pivot point
                                                    "SpiralAttackSpinAngleTimeGradient": 360 / 1.2,
                                                    "SpiralAttackSpinNewAngle": 0,
                                                    "SpiralAttackSpinNewCenterPositions": None
                                                    },

                                    "Sleep": {
                                        "Duration": 5000,
                                        "DurationTimer": None,
                                        "FullAnimationDuration": 1200,
                                        "PlayerDamageMultiplierWhenBossIsSleeping": 1.75
                                            },

                                    
                                    # DiveBomb attack

                                    "DiveBomb":{

                                                "CurrentDiveBombStage": None,
                                                "Cooldown": 6000,
                                                "CooldownTimer": None, # This will be set after the attack has completed (Change this number if you want to delay when the boss can first divebomb attack)
                                                "EnergyDepletionAmount": 25,

                                                "Launch": {
                                                            "Duration": 700, 
                                                            "DurationTimer": None

                                                            },
                                                "Target": {
                                                        "Duration": 2000, #3000,
                                                        "DurationTimer": None
                                                        },

                                                "Land": {
                                                        "Duration": 700, 
                                                        "DurationTimer": None
                                                        },
                                            },

                                    "Death": {
                                            "Images": None

                                            }
                                    
                                        }
        
        # -------------------------------------------------
        # Chilli projectiles and spiral attack 

        # Controller to create chilli projectiles and chilli projectile attacks
        self.chilli_projectile_controller = ChilliProjectileController()

        # If the chilli projectile controller does not have this attribute
        if hasattr(ChilliProjectileController, "spiral_attack_angle_time_gradient") == False:
            # Set the time it takes for the attack to do one full rotation to be the half the duration of the attack
            ChilliProjectileController.spiral_attack_angle_time_gradient = 360 /( (self.behaviour_patterns_dict["SpiralAttack"]["Duration"] / 1000) / 3)

        # -------------------------------------------------
        # Divebomb attack
           
        self.dive_bomb_attack_controller = DiveBombAttackController(
            x = self.rect.x, 
            y = self.rect.y, 
            damage_amount = self.extra_information_dict["KnockbackDamage"] * 1.5,
            knockback_multiplier = 1.5
            )


        # ----------------------------------------------------------------------------------
        # Declare the animation attributes
        self.declare_animation_attributes()

        # ----------------------------------------------------------------------------------
        # Sleep text

        """ Notes: 
        - The game UI is responsible for drawing the text and updating it 
        - The rest of the info e.g. gradients are inside the GameUI's effect text info dict
        """
        self.sleep_effect_text_info_dict = {
                                    "Font": pygame_font_Font("graphics/Fonts/frenzy_mode_value_font.ttf", 30),
                                    "Text": "Z",
                                    "DisplayTime": 850,
                                    "DefaultAlphaLevel": 185,
                                    "Colour": "white",
                                    "CreationCooldownTime": 300,
                                    "CreationCooldownTimer": None
                                    }
        
        # Font size for creating alpha surfaces
        self.sleep_effect_text_info_dict["FontSize"] =  pygame_font_Font("graphics/Fonts/frenzy_mode_value_font.ttf", 30).size("Z") 

        # If EffectText does not have an effect text list yet
        # Note: This is because effect text is also created in the game UI
        if hasattr(EffectText, "effect_text_list") == False:
            EffectText.effect_text_list = []

    # ----------------------------------------------------------------------------------
    # Animations

    def declare_animation_attributes(self):

        # Declares the animation attributes

        # Set the animation index as 0
        self.animation_index = 0         

        # --------------------------
        # Chasing

        # The time between each frame should be how long each chase animation cycle should last, divided by the total number of animation frames
        # Note: All chase animations have the same number of frames regardless of the direction
        self.behaviour_patterns_dict["Chase"]["TimeBetweenAnimFrames"] = self.behaviour_patterns_dict["Chase"]["FullAnimationDuration"] / (len(GoldenMonkeyBoss.ImagesDict["Chase"]["Down"]))

        # Set the animation frame timer to start as the time between animation frames
        self.behaviour_patterns_dict["Chase"]["AnimationFrameTimer"] = self.behaviour_patterns_dict["Chase"]["TimeBetweenAnimFrames"]

        # --------------------------
        # Spiral attack

        # Note: All directions have the same number of animation frames

        # The time between each frame should be how long each target animation cycle should last, divided by the total number of animation frames
        self.behaviour_patterns_dict["SpiralAttack"]["TimeBetweenAnimFrames"] = self.behaviour_patterns_dict["SpiralAttack"]["FullAnimationDuration"] / (len(GoldenMonkeyBoss.ImagesDict))

        # Set the animation frame timer to start as the time between animation frames
        self.behaviour_patterns_dict["SpiralAttack"]["AnimationFrameTimer"] = self.behaviour_patterns_dict["SpiralAttack"]["TimeBetweenAnimFrames"]

        # --------------------------
        # Sleep

        # The time between each frame should be how long the "Sleep" animation lasts, divided by the total number of animation frames
        self.behaviour_patterns_dict["Sleep"]["TimeBetweenAnimFrames"] = self.behaviour_patterns_dict["Sleep"]["FullAnimationDuration"] / (len(GoldenMonkeyBoss.ImagesDict["Sleep"]))

        # Set the animation frame timer to start as the time between animation frames
        self.behaviour_patterns_dict["Sleep"]["AnimationFrameTimer"] = self.behaviour_patterns_dict["Sleep"]["TimeBetweenAnimFrames"]

        # --------------------------
        # DiveBomb

        # The time between each frame should be how long "Launch" state is active for, divided by the total number of animation frames
        self.behaviour_patterns_dict["DiveBomb"]["Launch"]["TimeBetweenAnimFrames"] = self.behaviour_patterns_dict["DiveBomb"]["Launch"]["Duration"] / (len(GoldenMonkeyBoss.ImagesDict["DiveBomb"]["Launch"]))
        # Set the animation frame timer to start as the time between animation frames
        self.behaviour_patterns_dict["DiveBomb"]["Launch"]["AnimationFrameTimer"] = self.behaviour_patterns_dict["DiveBomb"]["Launch"]["TimeBetweenAnimFrames"]

        # The time between each frame should be how long "Land" state is active for, divided by the total number of animation frames
        self.behaviour_patterns_dict["DiveBomb"]["Land"]["TimeBetweenAnimFrames"] = self.behaviour_patterns_dict["DiveBomb"]["Land"]["Duration"] / (len(GoldenMonkeyBoss.ImagesDict["DiveBomb"]["Land"]))
        # Set the animation frame timer to start as the time between animation frames
        self.behaviour_patterns_dict["DiveBomb"]["Land"]["AnimationFrameTimer"] = self.behaviour_patterns_dict["DiveBomb"]["Land"]["TimeBetweenAnimFrames"]

    def play_animations(self):

        # --------------------------------------------------------
        # Set the current animation image and change the colour if there are any effects

        # If the boss is alive
        if self.current_action != "Death":

            # If the current action is "Chase"
            if self.current_action == "Chase":
                
                # The current direction the monkey is facing
                current_direction = self.find_look_direction()

                # The current animation list
                current_animation_list = GoldenMonkeyBoss.ImagesDict[self.current_action][current_direction]

                # The current animation image
                current_animation_image = current_animation_list[self.animation_index]

            # If the current action is "SpiralAttack" or "Sleep"
            elif self.current_action == "SpiralAttack" or self.current_action == "Sleep":
                
                # The current animation list
                current_animation_list = GoldenMonkeyBoss.ImagesDict[self.current_action]

                # The current animation image
                current_animation_image = current_animation_list[self.animation_index]

            # If the current action is "DiveBomb"
            elif self.current_action == "DiveBomb":
                
                # If the current divebomb stage is not "Target"
                if self.behaviour_patterns_dict["DiveBomb"]["CurrentDiveBombStage"] != "Target":
                    # The current animation list (e.g. ["DiveBomb"]["Land"])
                    current_animation_list = GoldenMonkeyBoss.ImagesDict[self.current_action][self.behaviour_patterns_dict["DiveBomb"]["CurrentDiveBombStage"]]
                    # The current animation image
                    current_animation_image = current_animation_list[self.animation_index]

                # If the current divebomb stage is "Target"
                elif self.behaviour_patterns_dict["DiveBomb"]["CurrentDiveBombStage"] == "Target":
                    # Set the image and image list to be anything (This is because the boss will not be in frame, so it does not matter)
                    current_animation_list = GoldenMonkeyBoss.ImagesDict[self.current_action]["Land"]
                    current_animation_image = GoldenMonkeyBoss.ImagesDict[self.current_action]["Land"][0]

            # If the boss has been damaged (red and white version)
            if self.extra_information_dict["DamagedFlashEffectTimer"] != None:
                
                # Reduce the colour of the image all the way down to black
                """Note: This is because yellow is made up of red and green, so the colours must be reduced all the way down first to actually see the red (otherwise the only colour visible would be white
                and the default colours)
                """
                current_animation_image = change_image_colour_v2(current_animation_image = current_animation_image, desired_colour = (0, 0, 0))

                # Set the current animation image to be a flashed version of the current animation image (a white flash effect)
                current_animation_image = change_image_colour(current_animation_image = current_animation_image, desired_colour = random_choice(((255, 255, 255), (255, 0, 0))))

        # If the boss is not alive
        elif self.current_action == "Death":
            # Set the current animation list
            current_animation_list = self.behaviour_patterns_dict["Death"]["Images"]

            # Set the current animation image
            current_animation_image = self.behaviour_patterns_dict["Death"]["Images"][self.animation_index]

            # If the boss has been damaged (white version)
            if self.extra_information_dict["DamagedFlashEffectTimer"] != None:
                # Set the current animation image to be a flashed version of the current animation image (a white flash effect)
                current_animation_image = change_image_colour(current_animation_image = current_animation_image, desired_colour = random_choice(((255, 255, 255), (40, 40, 40))))
                
        # Set the image to be the current animation image
        self.image = current_animation_image

        # --------------------------------------------------------
        # Updating animation

        # Find which action is being performed and update the animation index based on that
        # If the current action is to "Chase" or "SpiralAttack" or "Sleep"
        if self.current_action == "Chase" or self.current_action == "SpiralAttack" or self.current_action == "Sleep":
            
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

        # If the current action is "Death"
        elif self.current_action == "Death":

            # If the current animation index is not the last index inside the animation list and the animation frame timer has finished counting
            if self.animation_index < (len(current_animation_list) - 1) and (self.behaviour_patterns_dict[self.current_action]["AnimationFrameTimer"]) <= 0:
                # Go the next animation frame
                self.animation_index += 1

                # Reset the timer (adding will help with accuracy)
                self.behaviour_patterns_dict[self.current_action]["AnimationFrameTimer"] += self.behaviour_patterns_dict[self.current_action]["TimeBetweenAnimFrames"]
        
        # If the current action is "DiveBomb"
        elif self.current_action == "DiveBomb":

            # Current divebomb stage
            current_stage = self.behaviour_patterns_dict["DiveBomb"]["CurrentDiveBombStage"]
            
            # If the current stage is not "Target"
            if current_stage != "Target":

                # If the current animation index is not the last index inside the animation list and the animation frame timer has finished counting
                if self.animation_index < (len(current_animation_list) - 1) and (self.behaviour_patterns_dict[self.current_action][current_stage]["AnimationFrameTimer"]) <= 0:
                    # Go the next animation frame
                    self.animation_index += 1

                    # Reset the timer (adding will help with accuracy)
                    self.behaviour_patterns_dict[self.current_action][current_stage]["AnimationFrameTimer"] += self.behaviour_patterns_dict[self.current_action][current_stage]["TimeBetweenAnimFrames"]
            
        # --------------------------------------------------------
        # Additional for sleeping
        
        # Creates sleep effect text
        self.create_sleep_text()

        # -----------------------------------
        # Updating timers
        
        # If the current action isn't "DiveBomb"
        if self.current_action != "DiveBomb":
            # Decrease the animation frame timers
            self.behaviour_patterns_dict[self.current_action]["AnimationFrameTimer"] -= 1000 * self.delta_time

        # If the current action is "DiveBomb"
        elif self.current_action == "DiveBomb":
            # If the current divebomb stage is not "Target" ("Target" does not have an animation")
            if current_stage != "Target":
                # Decrease the animation frame timers
                self.behaviour_patterns_dict[self.current_action][current_stage]["AnimationFrameTimer"] -= 1000 * self.delta_time

        # Update damage flash effect timer
        self.update_damage_flash_effect_timer()

    def create_sleep_text(self):
        
        # Creates sleep effect text when the boss is in the sleep state (effect text is always updated by the game UI)

        # If enough time has passed since the last sleep effect text was created
        if self.sleep_effect_text_info_dict["CreationCooldownTimer"] == None:
            
            # Position of the text
            text_position_x = (self.rect.midtop[0] + 3) - self.camera_position[0]
            text_position_y = ((self.rect.midtop[1] - (self.sleep_effect_text_info_dict["FontSize"][1] / 2)) + 12) - self.camera_position[1]

            # Alpha surface
            new_alpha_surface = pygame_Surface(self.sleep_effect_text_info_dict["FontSize"])
            new_alpha_surface.set_colorkey("black")
            new_alpha_surface.set_alpha(self.sleep_effect_text_info_dict["DefaultAlphaLevel"])

            # Create the effect text (Automatically added to the effect text group)
            EffectText(
                        x = text_position_x,
                        y = text_position_y,
                        colour = self.sleep_effect_text_info_dict["Colour"],
                        display_time = self.sleep_effect_text_info_dict["DisplayTime"], 
                        text = self.sleep_effect_text_info_dict["Text"],
                        font = self.sleep_effect_text_info_dict["Font"],
                        alpha_surface = new_alpha_surface,
                        alpha_level = self.sleep_effect_text_info_dict["DefaultAlphaLevel"],
                        type_of_effect_text = "Sleep"
                        )

            # Set the creation timer cooldown to start
            self.sleep_effect_text_info_dict["CreationCooldownTimer"] = self.sleep_effect_text_info_dict["CreationCooldownTime"]

    def update_sleep_effect_text_timer(self):

        # Timer for the spawning of chillis whilst chasing the plyaer

        # If there is a timer set for the chilli spawning for the spiral attack
        if self.sleep_effect_text_info_dict["CreationCooldownTimer"] != None:

            # If the spawning cooldown timer has not finished counting down
            if self.sleep_effect_text_info_dict["CreationCooldownTimer"] > 0:
                # Decrease the timer
                self.sleep_effect_text_info_dict["CreationCooldownTimer"] -= 1000 * self.delta_time
            
            # If the spawning cooldown timer has finished counting down
            if self.sleep_effect_text_info_dict["CreationCooldownTimer"] <= 0:
                # Reset the timer back to None
                self.sleep_effect_text_info_dict["CreationCooldownTimer"] = None

    # ----------------------------------------------------------------------------------
    # Gameplay

    def decide_action(self):

        # The main "brain" of the deer boss, which will decide on what action to perform

        # Find the player (To continuously update the look angle)
        """Note: This is done because even if the boss other attacks will also need the current look angle """
        self.find_player(current_position = self.rect.center, player_position = self.players_position, delta_time = self.delta_time)

        # If the energy amount is greater than 0
        if self.energy_amount > 0:

            # If the current action is "Chase"
            if self.current_action == "Chase":

                # Create a list of all the actions that the AI can currently perform, if the action's cooldown timer is None
                action_list = [action for action in self.behaviour_patterns_dict.keys() if (action == "SpiralAttack" or action == "DiveBomb") and self.behaviour_patterns_dict[action]["CooldownTimer"] == None]

                # If there are any possible actions that the boss can perform (other than "Chase") and the boss has not performed an action recently
                if len(action_list) > 0 and self.extra_information_dict["NoActionTimer"] == None:

                    # Reset the animation index whenever we change the action
                    self.animation_index = 0

                    # Choose a random action from the possible actions the boss can perform and set it as the current action
                    self.current_action = "DiveBomb" #random_choice(action_list)

                    # If the current action that was chosen was "SpiralAttack", and "SpiralAttack" duration timer has not been set to start counting down yet
                    if self.current_action == "SpiralAttack" and self.behaviour_patterns_dict["SpiralAttack"]["DurationTimer"] == None:

                        # --------------------------------------------
                        # Chillis

                        # Set the duration timer to start counting down
                        self.behaviour_patterns_dict["SpiralAttack"]["DurationTimer"] = self.behaviour_patterns_dict["SpiralAttack"]["Duration"] 

                        # Set the chilli projectile controllers center position so that chilli projectiles can spawn from the center of the boss
                        self.chilli_projectile_controller.boss_center_position = self.rect.center

                        # Set the rotation direction for this spiral attack (1 = clockwise, -1 = anti-clockwise)
                        self.chilli_projectile_controller.spiral_attack_angle_time_gradient *= random_choice([-1, 1])

                        # --------------------------------------------
                        # Spin
                        
                        # Set the pivot point to be the current center of the boss 
                        self.behaviour_patterns_dict["SpiralAttack"]["SpiralAttackSpinPivotPoint"] = self.rect.center

                        # Alter the angle time gradient of the spin, so that the boss can rotate around the pivot point clockwise or anti clockwise
                        self.behaviour_patterns_dict["SpiralAttack"]["SpiralAttackSpinAngleTimeGradient"] *= random_choice([-1, 1])


                    # If the current action that was chosen was "DiveBomb" and the current divebomb stage is set to None (meaning the attack has not started yet)
                    elif self.current_action == "DiveBomb" and self.behaviour_patterns_dict["DiveBomb"]["CurrentDiveBombStage"] == None:
                        
                        # Set the divebomb stage to be Launch
                        self.behaviour_patterns_dict["DiveBomb"]["CurrentDiveBombStage"] = "Launch"
                        
                        # Set the "Launch" duration timer to start counting down
                        self.behaviour_patterns_dict["DiveBomb"]["Launch"]["DurationTimer"] = self.behaviour_patterns_dict["DiveBomb"]["Launch"]["Duration"]
                
                # If there are no possible actions that the boss can perform or the boss has performed an action recently
                elif len(action_list) == 0 or self.extra_information_dict["NoActionTimer"] != None: 
                    
                    # Move the boss (i.e. Chase the player)
                    self.move()

                    # If the boss has not thrown a chilli recently
                    if self.behaviour_patterns_dict["Chase"]["ChilliThrowingCooldownTimer"] == None:
                        
                        # The angle the projectile will travel at
                        projectile_angle = self.movement_information_dict["Angle"]
                        
                        # Create a chilli projectile and throw it at the player
                        self.chilli_projectile_controller.create_chilli_projectile(
                                        x_pos = self.rect.centerx + (ChilliProjectileController.displacement_from_center_position * cos(projectile_angle)),
                                        y_pos = (self.rect.centery - (ChilliProjectileController.displacement_from_center_position * sin(projectile_angle))) + ChilliProjectileController.additional_y_displacement_to_position_under_boss,
                                        angle = projectile_angle,
                                        damage_amount = ChilliProjectileController.base_damage
                                                                                    )

                        # Set the cooldown timer to start counting down
                        self.behaviour_patterns_dict["Chase"]["ChilliThrowingCooldownTimer"] = self.behaviour_patterns_dict["Chase"]["ChilliThrowingCooldown"] 

                    # Update the cooldown for throwing chillis whilst chasing the player
                    self.update_chilli_throwing_cooldown_timer()

            # If the current action is "SpiralAttack"
            if self.current_action == "SpiralAttack":

                # -------------------------------------------------------------------------------------------------
                # Chilli spiral attack
                
                # If enough time has passed since the last set of chilli projectiles were sent out
                if self.behaviour_patterns_dict["SpiralAttack"]["SpiralChilliSpawningCooldownTimer"] == None:
                    # Perform the spiral attack
                    self.chilli_projectile_controller.create_spiral_attack()
                    # Start the cooldown for the chilli spawning
                    self.behaviour_patterns_dict["SpiralAttack"]["SpiralChilliSpawningCooldownTimer"] = self.behaviour_patterns_dict["SpiralAttack"]["SpiralChilliSpawningCooldown"]

                # Always increase the spiral attack angle
                self.chilli_projectile_controller.increase_spiral_attack_angle(delta_time = self.delta_time)

                # Update the spiral chilli spawning cooldown timer
                self.update_spiral_chilli_spawning_cooldown_timer()

                # --------------------------------------------
                # Pivoting around the original center point

                # Increase the angle
                self.behaviour_patterns_dict["SpiralAttack"]["SpiralAttackSpinNewAngle"] += self.behaviour_patterns_dict["SpiralAttack"]["SpiralAttackSpinAngleTimeGradient"] * self.delta_time
                self.behaviour_patterns_dict["SpiralAttack"]["SpiralAttackSpinAngle"] = round(self.behaviour_patterns_dict["SpiralAttack"]["SpiralAttackSpinNewAngle"])

                # Calculate the horizontal and vertical distnaces the player should be away from the pivot point
                displacement_x = (self.behaviour_patterns_dict["SpiralAttack"]["SpiralAttackSpinPivotDistance"] * cos(radians(self.behaviour_patterns_dict["SpiralAttack"]["SpiralAttackSpinAngle"])))
                displacement_y = (self.behaviour_patterns_dict["SpiralAttack"]["SpiralAttackSpinPivotDistance"] * sin(radians(self.behaviour_patterns_dict["SpiralAttack"]["SpiralAttackSpinAngle"])))
                
                # Calculate the new center position of the boss
                self.behaviour_patterns_dict["SpiralAttack"]["SpiralAttackSpinNewCenterPositions"] = (
                                                                            self.behaviour_patterns_dict["SpiralAttack"]["SpiralAttackSpinPivotPoint"][0] + displacement_x ,
                                                                            self.behaviour_patterns_dict["SpiralAttack"]["SpiralAttackSpinPivotPoint"][1] + displacement_y 
                                                                                                    )
                
                # Set the center of the boss to be the same as the new center positions
                self.rect.centerx = self.behaviour_patterns_dict["SpiralAttack"]["SpiralAttackSpinNewCenterPositions"][0]
                self.rect.centery = self.behaviour_patterns_dict["SpiralAttack"]["SpiralAttackSpinNewCenterPositions"][1]

            # # If the current action is "DiveBomb"
            # elif self.current_action == "DiveBomb":
                

        # If the boss has 0 or less than 0 energy
        elif self.energy_amount <= 0:
            
            # If the current action is not already "Sleep" (meaning this is the first time this if check was entered)
            if self.current_action != "Sleep":
                # Set the current action to "Sleep"
                self.current_action = "Sleep"
                # Set the animation index back to 0
                self.animation_index = 0
                # Set the sleep duration timer to start counting down
                self.behaviour_patterns_dict["Sleep"]["DurationTimer"] = self.behaviour_patterns_dict["Sleep"]["Duration"]


    def update_and_draw_divebomb_circles(self, delta_time):

        # If the current dive bomb stage is "Target"
        if self.behaviour_patterns_dict["DiveBomb"]["CurrentDiveBombStage"] == "Target":
            
            # Fill the dive bomb attack controller's alpha surface with black
            self.dive_bomb_attack_controller.alpha_surface.fill("black")

                # Draw the circles onto the alpha surface
                # Note: The center 
            pygame_draw_circle(
                            surface = self.dive_bomb_attack_controller.alpha_surface, 
                            color = (180, 0, 0), 
                            center = (self.dive_bomb_attack_controller.maximum_circle_radius, self.dive_bomb_attack_controller.maximum_circle_radius), 
                            radius = self.dive_bomb_attack_controller.maximum_circle_radius, 
                            width = 0
                            )

            pygame_draw_circle(
                            surface = self.dive_bomb_attack_controller.alpha_surface, 
                            color = (225, 0, 0), 
                            center = (self.dive_bomb_attack_controller.maximum_circle_radius, self.dive_bomb_attack_controller.maximum_circle_radius), 
                            radius = self.dive_bomb_attack_controller.growing_circle_radius, 
                            width = 0
                            )
                            
            pygame_draw_circle(
                            surface = self.dive_bomb_attack_controller.alpha_surface, 
                            color = (255, 0, 0), 
                            center = (self.dive_bomb_attack_controller.maximum_circle_radius, self.dive_bomb_attack_controller.maximum_circle_radius), 
                            radius = min(0, self.dive_bomb_attack_controller.growing_circle_radius - 20),
                            width = 0
                            )

            # Blit the center of the alpha surface at the landing position (Which would be the center of the player)
            self.surface.blit(
                            self.dive_bomb_attack_controller.alpha_surface, 
                            (
                            (self.dive_bomb_attack_controller.landing_position[0] - self.dive_bomb_attack_controller.maximum_circle_radius) - self.camera_position[0],
                            (self.dive_bomb_attack_controller.landing_position[1] - self.dive_bomb_attack_controller.maximum_circle_radius)  - self.camera_position[1]
                            )
                            )

            # Increase the radius of the smaller, growing circle and change the alpha level of the alpha surface
            self.dive_bomb_attack_controller.change_visual_effects(
                                proportional_time_remaining = self.behaviour_patterns_dict["DiveBomb"]["Target"]["DurationTimer"] / self.behaviour_patterns_dict["DiveBomb"]["Target"]["Duration"],
                                delta_time = delta_time
                                                                            )

            # Outline
            pygame_draw_circle(
                            surface = self.surface, 
                            color = (0, 0, 0), 
                            center = (self.dive_bomb_attack_controller.landing_position[0] - self.camera_position[0], self.dive_bomb_attack_controller.landing_position[1] - self.camera_position[1]), 
                            radius = self.dive_bomb_attack_controller.maximum_circle_radius, 
                            width = 3
                            )

            # self.dive_bomb_attack_controller.draw(surface= self.surface, x = self.dive_bomb_attack_controller.rect.x - self.camera_position[0], y = self.dive_bomb_attack_controller.rect.y - self.camera_position[1])
    # ----------------------------------------------------------------------------------
    # Timer updating

    def update_duration_timers(self):

        # Updates the duration timer of the current action 
        # If the duration timer is over, the action is added to the previous actions list so that their cooldown timer can be updated
        
        # If the current action is not "Chase" (Chase does not have a duration timer) or "DiveBomb" (DiveBomb has multiple stages)
        if self.current_action != "Chase" and self.current_action != "DiveBomb":
            
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

                # If the current action is not "Sleep"
                # Note: "Sleep" does not have a cooldown
                if self.current_action != "Sleep":
                    # Add the current action to the previous actions dict so that its cooldown timer can count down
                    self.previous_actions_dict[self.current_action] = None

                # -----------------------------------------------------------------------------------
                # Additional resets depending on the action

                # If the current action is "SpiralAttack"
                if self.current_action == "SpiralAttack":

                    # Set the current action back to Chase
                    self.current_action = "Chase"

                    # Set the no action timer to start counting down
                    self.extra_information_dict["NoActionTimer"] = self.extra_information_dict["NoActionTime"]

                    # Set the cooldown timer to start counting down
                    self.behaviour_patterns_dict["SpiralAttack"]["CooldownTimer"] = self.behaviour_patterns_dict["SpiralAttack"]["Cooldown"]

                    # Reduce the amount of energy that the boss has
                    self.energy_amount -= self.behaviour_patterns_dict["SpiralAttack"]["EnergyDepletionAmount"]

                    # --------------------------------------
                    # Spin

                    # Reset the angles for the spin pivoting
                    self.behaviour_patterns_dict["SpiralAttack"]["SpiralAttackSpinAngle"] = 0
                    self.behaviour_patterns_dict["SpiralAttack"]["SpiralAttackSpinNewAngle"] = 0

                    # Set the position of the boss to be the original position again
                    self.rect.center = self.behaviour_patterns_dict["SpiralAttack"]["SpiralAttackSpinPivotPoint"]
                    # Reset the pivot point back to None
                    self.behaviour_patterns_dict["SpiralAttack"]["SpiralAttackSpinPivotPoint"] = None

                # If the current action is "Sleep"
                elif self.current_action == "Sleep":
                    # Set the current action back to Chase
                    self.current_action = "Chase"

                    # Set the energy amount back to the maximum amount
                    self.energy_amount = GoldenMonkeyBoss.maximum_energy_amount

        # If the current action is "DiveBomb"
        elif self.current_action == "DiveBomb":
            
            # Current DiveBomb stage
            current_stage = self.behaviour_patterns_dict["DiveBomb"]["CurrentDiveBombStage"] 

            # If the current action's duration timer has not finished counting down
            if self.behaviour_patterns_dict["DiveBomb"][current_stage]["DurationTimer"] > 0:
                # Decrease the timer
                self.behaviour_patterns_dict["DiveBomb"][current_stage]["DurationTimer"] -= 1000 * self.delta_time
            
            # If the current action's duration timer has finished counting down
            if self.behaviour_patterns_dict["DiveBomb"][current_stage]["DurationTimer"] <= 0:
                # Reset the duration timer back to None
                self.behaviour_patterns_dict["DiveBomb"][current_stage]["DurationTimer"] = None

                # Reset the animation index
                self.animation_index = 0

                # Identify the current divebomb stage
                match current_stage:

                    case "Launch":

                        # Set the next stage to be "Target"
                        self.behaviour_patterns_dict["DiveBomb"]["CurrentDiveBombStage"] = "Target"

                        # Set the divebomb "Target" duration timer to start counting down
                        self.behaviour_patterns_dict["DiveBomb"]["Target"]["DurationTimer"] = self.behaviour_patterns_dict["DiveBomb"]["Target"]["Duration"]

                        # Set the divebomb's end position (where to land) to be the center of the player
                        self.dive_bomb_attack_controller.landing_position = self.players_position
                        
                        # Set the divebomb attack controller's center to be the same as the player (for the image to also be centered for mask collisions)
                        self.dive_bomb_attack_controller.rect.center = self.players_position

                        # Modify the movement infomration dict's new center positions so that when the boss lands, it won't teleport back to its old position
                        self.movement_information_dict["NewPositionCenterX"] = self.dive_bomb_attack_controller.landing_position[0]
                        self.movement_information_dict["NewPositionCenterY"] = self.dive_bomb_attack_controller.landing_position[1]

                        # Take the boss off the map
                        self.rect.center = (10000, 10000)

                    case "Target":

                        # Set the next stage to be "Land"
                        self.behaviour_patterns_dict["DiveBomb"]["CurrentDiveBombStage"] = "Land"

                        # Set the divebomb "Land" duration timer to start counting down
                        self.behaviour_patterns_dict["DiveBomb"]["Land"]["DurationTimer"] = self.behaviour_patterns_dict["DiveBomb"]["Land"]["Duration"]

                        # Set the boss to be at the landing position
                        self.rect.center = self.dive_bomb_attack_controller.landing_position

                        # Update the angle between the boss and the player, so that the player gets knocked back properly
                        self.find_player(player_position = self.players_position, current_position = self.dive_bomb_attack_controller.landing_position, delta_time = self.delta_time) 

                        # Reset the divebomb attributes of the divebobm attack controller
                        self.dive_bomb_attack_controller.reset_divebomb_attributes()

                    case "Land":
                        # Set the current action back to "Chase"
                        self.current_action = "Chase"

                        # Set the next stage to be None
                        self.behaviour_patterns_dict["DiveBomb"]["CurrentDiveBombStage"] = None

                        # Set the cooldown timer to start counting down
                        self.behaviour_patterns_dict["DiveBomb"]["CooldownTimer"] = self.behaviour_patterns_dict["DiveBomb"]["Cooldown"]

                        # Set the no action timer to start counting down
                        self.extra_information_dict["NoActionTimer"] = self.extra_information_dict["NoActionTime"]
                        
                        # Add the divebomb action to the previous actions dict so that its cooldown timer can count down
                        self.previous_actions_dict["DiveBomb"] = None

                        # Reduce the amount of energy that the boss has
                        self.energy_amount -= self.behaviour_patterns_dict["DiveBomb"]["EnergyDepletionAmount"]

    def update_spiral_chilli_spawning_cooldown_timer(self):

        # Timer for the spawning of chillis during the spiral attack

        # If there is a timer set for the chilli spawning for the spiral attack
        if self.behaviour_patterns_dict["SpiralAttack"]["SpiralChilliSpawningCooldownTimer"] != None:

            # If the spawning cooldown timer has not finished counting down
            if self.behaviour_patterns_dict["SpiralAttack"]["SpiralChilliSpawningCooldownTimer"] > 0:
                # Decrease the timer
                self.behaviour_patterns_dict["SpiralAttack"]["SpiralChilliSpawningCooldownTimer"] -= 1000 * self.delta_time
            
            # If the spawning cooldown timer has finished counting down
            if self.behaviour_patterns_dict["SpiralAttack"]["SpiralChilliSpawningCooldownTimer"] <= 0:
                # Reset the timer back to None
                self.behaviour_patterns_dict["SpiralAttack"]["SpiralChilliSpawningCooldownTimer"] = None

    def update_chilli_throwing_cooldown_timer(self):

        # Timer for the spawning of chillis whilst chasing the plyaer

        # If there is a timer set for the chilli spawning for the spiral attack
        if self.behaviour_patterns_dict["Chase"]["ChilliThrowingCooldownTimer"] != None:

            # If the spawning cooldown timer has not finished counting down
            if self.behaviour_patterns_dict["Chase"]["ChilliThrowingCooldownTimer"] > 0:
                # Decrease the timer
                self.behaviour_patterns_dict["Chase"]["ChilliThrowingCooldownTimer"] -= 1000 * self.delta_time
            
            # If the spawning cooldown timer has finished counting down
            if self.behaviour_patterns_dict["Chase"]["ChilliThrowingCooldownTimer"] <= 0:
                # Reset the timer back to None
                self.behaviour_patterns_dict["Chase"]["ChilliThrowingCooldownTimer"] = None

    
    def run(self):
        # print(self.current_action, self.behaviour_patterns_dict["DiveBomb"]["CurrentDiveBombStage"])

        # Always update / move / draw the chilli projectiles
        self.chilli_projectile_controller.update_chilli_projectiles(
                                                                    delta_time = self.delta_time,
                                                                    camera_position = self.camera_position,
                                                                    surface = self.surface
                                                                    )

        # If the boss has spawned and the camera panning has been completed
        if self.extra_information_dict["CanStartOperating"] == True:

            # Decide the action that the boss should perform
            self.decide_action()

            # Check if the boss' health is less than 0
            if self.extra_information_dict["CurrentHealth"] <= 0:
                
                # If current action has not been set to "Death" the boss does not have a death animation images list yet
                if self.current_action != "Death" or self.behaviour_patterns_dict["Death"]["Images"]  == None:

                    """Note: Do not set self.extra_information_dict["CanStartOperating"] to False, otherwise the death animation will not play"""
                    
                    # Reset the animation index
                    self.animation_index = 0

                    # Set the current action to death
                    self.current_action = "Death"

                    # Load and scale the death animation images 
                    self.behaviour_patterns_dict["Death"]["Images"] = [scale_image(
                        load_image(f"graphics/Misc/DeathAnimation/{i}.png").convert_alpha(), ((load_image(f"graphics/Misc/DeathAnimation/{i}.png").convert_alpha().get_width() * 2, load_image(f"graphics/Misc/DeathAnimation/{i}.png").convert_alpha().get_height() * 2)))  
                        for i in range(0, len(os_listdir("graphics/Misc/DeathAnimation")))]

                    # Set up the animation speed and timer
                    self.behaviour_patterns_dict["Death"]["FullAnimationDuration"] = FULL_DEATH_ANIMATION_DURATION
                    self.behaviour_patterns_dict["Death"]["TimeBetweenAnimFrames"] = self.behaviour_patterns_dict["Death"]["FullAnimationDuration"] / len(self.behaviour_patterns_dict["Death"]["Images"])
                    self.behaviour_patterns_dict["Death"]["AnimationFrameTimer"] = self.behaviour_patterns_dict["Death"]["TimeBetweenAnimFrames"]

            # Play animations
            self.play_animations()

            # Create / update a mask for pixel - perfect collisions
            self.mask = pygame_mask_from_surface(self.image)

            # If the boss is alive
            if self.extra_information_dict["CurrentHealth"] > 0:

                # Update the duration timers
                self.update_duration_timers()

                # Update the cooldown timers
                self.update_cooldown_timers()

                # Update the knockback collision idle timer
                self.update_knockback_collision_idle_timer(delta_time = self.delta_time)

                # If the current action is not "Sleep"
                if self.current_action != "Sleep":
                    # Update the no action timer (meaning the boss cannot perform any other actions other than chasing)
                    self.update_no_action_timer(delta_time = self.delta_time)

                # If the current action is "Sleep"
                elif self.current_action == "Sleep":
                    # Update the sleep effect text timer
                    self.update_sleep_effect_text_timer()

        # Draw the boss 
        """ Notes: 
        - Additional positions to center the image (this is because the animation images can vary in size)
        - This is down here because the chilli projectiles should be drawn under the boss 
        """
        self.draw(
            surface = self.surface, 
            x = (self.rect.x - ((self.image.get_width() / 2)  - (self.rect.width / 2))) - self.camera_position[0], 
            y = (self.rect.y - ((self.image.get_height() / 2) - (self.rect.height / 2))) - self.camera_position[1]
                )
        pygame_draw_rect(self.surface, "green", (self.rect.x - self.camera_position[0], self.rect.y - self.camera_position[1], self.rect.width, self.rect.height), 1)