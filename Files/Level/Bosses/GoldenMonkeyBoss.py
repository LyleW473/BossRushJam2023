from Global.generic import Generic
from Level.Bosses.AI import AI
from Global.settings import TILE_SIZE, FULL_DEATH_ANIMATION_DURATION
from random import choice as random_choice
from Global.functions import change_image_colour
from pygame.mask import from_surface as pygame_mask_from_surface
from pygame.image import load as load_image
from pygame.transform import scale as scale_image
from os import listdir as os_listdir


class GoldenMonkeyBoss(Generic, AI):

    # ImagesDict = ?? (This is set when the boss is instantiated)
    # Example: Chase : [Direction][Image list]
    
    # Characteristics
    knockback_damage = 15
    maximum_health = 20000
    

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
        self.starting_image = GoldenMonkeyBoss.ImagesDict["Chase"]["Down"][0]

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

        # A dictionary containing information relating to the behaviour of the Sika deer boss
        self.behaviour_patterns_dict = {

                                    "Chase": { 
                                            "FullAnimationDuration": 600
                                              },

                                    "Death": {
                                            "Images": None


                                            }
                                        }
        
        # ----------------------------------------------------------------------------------
        # Declare the animation attributes
        self.declare_animation_attributes()

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

                # If the boss has been damaged (red and white version)
            if self.extra_information_dict["DamagedFlashEffectTimer"] != None:
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

        # If the current action is to "Chase" 
        if self.current_action == "Chase":
            
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

        # -----------------------------------
        # Updating timers
        
        # Decrease the animation frame timers
        self.behaviour_patterns_dict[self.current_action]["AnimationFrameTimer"] -= 1000 * self.delta_time

        # Update damage flash effect timer
        self.update_damage_flash_effect_timer()

    def decide_action(self):

        # The main "brain" of the deer boss, which will decide on what action to perform


        # Find the player (To continuously update the look angle)
        """Note: This is done because even if the boss other attacks will also need the current look angle """
        self.find_player(current_position = self.rect.center, player_position = self.players_position, delta_time = self.delta_time)

        # If the current action is "Chase"
        if self.current_action == "Chase":

            # Create a list of all the actions that the AI can currently perform, if the action's cooldown timer is None
            action_list = [action for action in self.behaviour_patterns_dict.keys() if (action != "Chase" and action != "Death") and self.behaviour_patterns_dict[action]["CooldownTimer"] == None]

            # If there are any possible actions that the boss can perform (other than "Chase") and the boss has not performed an action recently
            if len(action_list) > 0 and self.extra_information_dict["NoActionTimer"] == None:

                # Reset the animation index whenever we change the action
                self.animation_index = 0

            # If there are no possible actions that the boss can perform or the boss has performed an action recently
            elif len(action_list) == 0 or self.extra_information_dict["NoActionTimer"] != None: 
                # Move the boss (i.e. Chase the player)
                self.move()

    def run(self):

        # Draw the boss 
        # Note: Additional positions to center the image (this is because the animation images can vary in size)
        self.draw(
            surface = self.surface, 
            x = (self.rect.x - ((self.image.get_width() / 2)  - (self.rect.width / 2))) - self.camera_position[0], 
            y = (self.rect.y - ((self.image.get_height() / 2) - (self.rect.height / 2))) - self.camera_position[1]
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

            # Update the knockback collision idle timer
            self.update_knockback_collision_idle_timer(delta_time = self.delta_time)
