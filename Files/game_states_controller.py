import pygame, sys, string
from Global.settings import *
from Menu.menu import Menu
from Level.game import Game

class GameStatesController():
    def __init__(self):

        # Screen
        self.screen = pygame.display.get_surface()
        self.full_screen = True

        # Game states
        self.menu = Menu()
        self.game = Game() # The actual level
        
        # Attribute so that we only load the level once, and not every frame
        self.level_loaded = False

    def load_level(self, chosen_level_number):
        # Note: Load level is here because in the future, a level select menu may be added (which will be inside the Menu class), so we need to retrieve the level selected from the Menu class and then pass it to the actual level (i.e. Game)
        
        # If we haven't loaded the level for the game yet
        if self.level_loaded == False:

            # ------------------------------------------------------------------------
            # Loading the tile map from the level tile maps text file

            # Open the text file which holds 
            with open("Files/Level/level_tile_maps.txt", "r") as level_tile_maps_file:
                
                for line_number, tile_map in enumerate(level_tile_maps_file.readlines()):
                    # If the line number is equal to the chosen level minus one (This is because the tile maps are zero indexed in order)
                    if line_number == (chosen_level_number - 1):
                        # [1:-1] to get rid of the "?" separator and the "\n" line break for each tile map
                        tile_map_to_convert = tile_map[1:-1]

            # ----------------------------------------------------------------------------------------
            # Convert the tile map into a series of tile numbers, so that inside the level, we can create objects 


            non_transformed_tile_map = [] # Holds the tile map of the tile's numbers
            tile_number = "" # Used as some tiles may have double digit tile numbers
            row_of_tiles_list = [] # Used to hold all the tiles in one row

            # For all characters in the tile map
            for i in range(0, len(tile_map_to_convert)):
                
                # Identify what the character is
                match tile_map_to_convert[i]:

                    # Comma separator
                    case ",":
                    
                        # Add the row of tiles to the final tile map
                        non_transformed_tile_map.append(row_of_tiles_list)

                        # Empty the row of tiles list
                        row_of_tiles_list = []

                    # Exclamation mark separator
                    case "!":
                        # Add the tile number to the row of tiles 
                        row_of_tiles_list.append(int(tile_number))

                        # Reset the tile number
                        tile_number = ""

                    # If it is neither a comma separator or an exclamation mark separator
                    case _: # Can also be "case other"
                        tile_number += tile_map_to_convert[i]

            # Create the level's object tile map, which is a tile map consisting of the objects (the actual game tile map)
            self.game.create_objects_tile_map(non_transformed_tile_map)

            # Set the level loaded attribute to True
            self.level_loaded = True
            
    def event_loop(self):

        # Event handler
        for event in pygame.event.get():

            # Identify the type of event
            match event.type:
                
                # Exit button on the window clicked
                case pygame.QUIT:

                    # If the exit button was pressed
                    if event.type == pygame.QUIT:
                        # Close the program
                        pygame.quit()
                        sys.exit()

                # Key presses
                case pygame.KEYDOWN:

                    # ------------------------------------------------------------
                    # Universal events
                    
                    # Find which key was pressed
                    match event.key:
                        
                        # "f" key
                        case pygame.K_f:
                            
                            # Changing from full screen to windowed mode
                            if self.full_screen == True:
                                
                                # Change to windowed mode
                                self.screen = pygame.display.set_mode((screen_width, screen_height - 50), flags = pygame.RESIZABLE, depth = 32) # -50 so the title bar is visible when exiting full screen
                                self.full_screen = False

                            # Changing from windowed to full screen mode
                            elif self.full_screen == False:
                                
                                # Change to full screen mode
                                pygame.display.set_mode(flags = pygame.FULLSCREEN, depth = 32)
                                self.full_screen = True

                    # ------------------------------------------------------------
                    # In-game / Level events

                    if self.game.running == True:
                        
                        # Find which key was pressed
                        match event.key:

                            # "Esc" key
                            case pygame.K_ESCAPE:

                                # Set the mouse cursor back to visible
                                pygame.mouse.set_visible(True)
                    
                                # Show the paused menu
                                self.game.running = False
                                self.menu.show_paused_menu = True
                                    
    def run(self, delta_time):
        
        # Run the event loop
        self.event_loop()

        # If none of the menus are being shown
        if self.menu.show_main_menu == False and self.menu.show_controls_menu == False and self.menu.show_paused_menu == False:

            # If this attribute is False (This would be the case if the player went into the Paused menu and then clicked the "Continue" button)
            if self.game.running == False:
                
                # Hide the mouse cursor
                pygame.mouse.set_visible(False)
                
                # Set the game's running attribute to True
                self.game.running = True

            # Load the level (Has conditions which will only perform this if the level hasn't been loaded into the game yet)
            self.load_level(chosen_level_number = 1)

            # Run the game
            self.game.run(delta_time)


        # Otherwise    
        else:
            # Run the menus
            self.menu.run(delta_time)


