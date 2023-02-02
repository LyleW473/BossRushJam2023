from Global.generic import Generic

class SikaDeerBoss(Generic):

    # ImagesDict = ?? (This is set when the boss is instantiated)
    # Example: Stomp : [Image list]


    def __init__(self, x, y):
        
        # The starting image when spawned
        starting_image = SikaDeerBoss.ImagesDict["Stomp"][0]

        # Inherit from the Generic class, which has basic attributes and methods.
        Generic.__init__(self, x = x , y = y, image = starting_image)

        # Spawn the boss at the middle of the tile, with the bottom of the boss being at the bottom of the tile
        self.rect.midbottom = (x, y)


        # self.delta_time = 0

        # # Health
        # self.health = 4000


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
                                            "DurationTimer": 6000 # Timer used to check 

                                             },

                                    # "Charge": { 
                                    #           "Damage": 30,
                                              
                                        

                                    #           }
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

        # print(SikaDeerBoss.ImagesDict)

        # # Adding animation timers for each behaviour pattern
        # for action in self.behaviour_patterns_dict.keys():
        #     # If the key is not "CurrentAction":
        #     if action != "CurrentAction":
        #         # Set a new key:value pair for the time between each animation frame
        #         self.behaviour_patterns_dict[action]["TimeBetweenAnimFrames"] = self.behaviour_patterns_dict[action]["Duration"] / len(SikaDeerBoss.ImagesDict[action])

        #         # Set the animation frame timer to start at the time between each animation frame
        #         self.behaviour_patterns_dict[action]["AnimationFrameTimer"] = self.behaviour_patterns_dict[action]["TimeBetweenAnimFrames"] 


        print(self.behaviour_patterns_dict)

    def play_animations(self):

        # Temporary variable for the current action
        current_action = self.behaviour_patterns_dict["CurrentAction"]

        # -----------------------------------
        # Set image

        # The current animation list
        current_animation_list = SikaDeerBoss.ImagesDict[self.behaviour_patterns_dict["CurrentAction"]]
        # The current animation image
        self.image = current_animation_list[self.animation_index]

        # -----------------------------------
        # Updating animation

        # Find which action is being performed and update the animation index based on that
        # match current_action:

        #     case "Stomp":
        if current_action == "Stomp":
                
                # If the stomp attack has not been completed
                if self.behaviour_patterns_dict[current_action]["DurationTimer"] > 0:
                    
                    # If the current animation index is not the last index inside the animation list and the animation frame timer has finished counting
                    if self.animation_index < (len(SikaDeerBoss.ImagesDict[current_action]) - 1) and (self.behaviour_patterns_dict[current_action]["AnimationFrameTimer"]) <= 0:
                        
                        # If this animation is one of the keyframes where the boss has stomped
                        if (self.animation_index == 0 and self.behaviour_patterns_dict[current_action]["DurationTimer"] != self.behaviour_patterns_dict[current_action]["Duration"]) \
                            or self.animation_index == 5:

                            # Create a stomp attack
                            self.stomp()
                            print("STOMP", self.animation_index, self.behaviour_patterns_dict[current_action]["DurationTimer"], self.behaviour_patterns_dict[current_action]["Duration"])

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

        # Update animation frame timers
        self.behaviour_patterns_dict[current_action]["AnimationFrameTimer"] -= 1000 * self.delta_time
        self.behaviour_patterns_dict["Stomp"]["DurationTimer"] -= 1000 * self.delta_time


    def stomp(self):
        print("")


    def run(self):
        
        # Play animations
        self.play_animations()


    
                


                


