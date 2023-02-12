from pygame import init as pygame_init
from pygame.display import set_caption as pygame_display_set_caption
from pygame.time import Clock as pygame_time_Clock
from pygame.display import update as pygame_display_update
from Global.settings import *
from game_states_controller import GameStatesController
from time import perf_counter


class Main:
    def __init__(self):

        # Pygame set-up
        pygame_init()

        # Set the caption
        pygame_display_set_caption("A Panda's Wit")
        
        # Create a game states controller
        self.game_states_controller = GameStatesController()

        # Times
        # Record the previous frame that was played
        self.previous_frame = perf_counter()
        
        # Create an object to track time
        self.clock = pygame_time_Clock()
        self.chosen_framerate = 60
        
    def run(self):
 
        while True:
            
            # Limit FPS to 60
            self.clock.tick(self.chosen_framerate)

            # Calculate delta time 
            delta_time = perf_counter() - self.previous_frame
            self.previous_frame = perf_counter()

            # Run the game states controller
            # Note: This is where we can change game states, e.g. from the menu to ingame
            self.game_states_controller.run(delta_time)
            
            # -------------------------------------
            # Update display
            pygame_display_update() 
            

if __name__ == "__main__":
    # Instantiate main and run it
    main = Main()
    main.run()