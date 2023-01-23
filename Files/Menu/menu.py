import pygame, sys
from Menu.button import Button
from Global.settings import * 

class Menu:
    def __init__(self):

        # Screen
        self.screen = pygame.display.get_surface()

        # ------------------------------------------------------------------------------------------------------------------------------------------------
        # Buttons
        # Note: Measurements of all buttons are: (400 x 125) pixels

        # Create the buttons
        self.create_buttons()
    
        # ------------------------------------------------------------------------------------------------------------------------------------------------

        # Game states

        self.show_main_menu = True 
        self.show_controls_menu = False 
        self.show_paused_menu = False 
        
        # Store the previous menu so that we can go back to previous menus when the "Back" button is clicked
        self.previous_menu = None 

        # ------------------------------------------------------------------------------------------------------------------------------------------------
        # Animated background variables
        self.arc_height = 300
        self.arc_width = 800
        self.arc_x = 200
        self.arc_y = (screen_height / 2) - (self.arc_height / 2)
        self.arc_starting_angle = 0.5
        self.arc_finishing_angle = 3.14
        self.arc_angle_increment_speed = 40

        # Dictionaries for the white/red arcs
        self.white_arc_dictionary = {i:[self.arc_x, self.arc_y, self.arc_width - (i * 40), self.arc_height - (i * 15), self.arc_starting_angle + (0.314 * (i * 2)), self.arc_finishing_angle, 1] for i in range(0, 4 + 1)}
        self.red_arc_dictionary = {i:[self.arc_x, self.arc_y, self.arc_width - (i * 40), self.arc_height - (i * 15), self.arc_finishing_angle, self.arc_starting_angle - (0.314 * (i * 2)), 1] for i in range(0, 4 + 1)}
        self.arc_movement_direction = 1 # 1 = Moving right, -1 = Moving left

        # ------------------------------------------------------------------------------------------------------------------------------------------------
        # Mouse
        self.left_mouse_button_released = True # Attribute used to track if the left mouse button is released so that 

    def create_buttons(self):

        # Create lists for all menus in the game
        self.main_menu_buttons = []
        self.controls_menu_buttons = []
        self.paused_menu_buttons = []

        # ------------------------------------------------------------------------
        # Main menu
        play_button = Button((screen_width / 2) - 200 , 200 , pygame.image.load("graphics/MenuButtons/play_button.png"), surface = self.screen)
        controls_button = Button((screen_width / 2) - 200, 400, pygame.image.load("graphics/MenuButtons/controls_button.png"), surface = self.screen)
        quit_button = Button((screen_width / 2) - 200, 600, pygame.image.load("graphics/MenuButtons/quit_button.png"), surface = self.screen)
        
        # Add the buttons to the main menu buttons list
        self.main_menu_buttons.append(play_button)
        self.main_menu_buttons.append(controls_button)
        self.main_menu_buttons.append(quit_button)

        # ------------------------------------------------------------------------
        # Controls menu
        self.back_button = Button((screen_width / 2) - 200, 600, pygame.image.load("graphics/MenuButtons/back_button.png"), surface = self.screen)

        # Add the buttons to the controls menu buttons list
        self.controls_menu_buttons.append(self.back_button)

        # ------------------------------------------------------------------------
        # Paused menu
        continue_button = Button((screen_width / 2) - 200, 200, pygame.image.load("graphics/MenuButtons/continue_button.png"), surface = self.screen)
        controls_button_2 = Button((screen_width / 2) - 200, 400, pygame.image.load("graphics/MenuButtons/controls_button.png"), surface = self.screen)
        quit_button_2 = Button((screen_width / 2) - 200, 600, pygame.image.load("graphics/MenuButtons/quit_button.png"), surface = self.screen)

        # Add the buttons to the paused menu buttons list
        self.paused_menu_buttons.append(continue_button)
        self.paused_menu_buttons.append(controls_button_2)
        self.paused_menu_buttons.append(quit_button_2)

    def mouse_position_updating(self):

        # Retrieve the mouse position
        self.mouse_position = pygame.mouse.get_pos()

        # Define the mouse rect and draw it onto the screen (For collisions with drawing tiles)
        self.mouse_rect = pygame.Rect(self.mouse_position[0], self.mouse_position[1], 1, 1)

    def animate_background(self):

        # Fill the screen with black
        self.screen.fill("black")

        for red_arc, arc_info in self.red_arc_dictionary.items():
            # Draw red arcs onto the screen
            pygame.draw.arc(self.screen, "red", (arc_info[0], arc_info[1], arc_info[2], arc_info[3]), arc_info[4], arc_info[5])

            # If the starting angle is not equal to the finishing angle
            if arc_info[4] != arc_info[5]:
                # Increment the starting and finishing angle
                arc_info[4] += 0.0314 * (self.arc_angle_increment_speed - 10) * self.delta_time
                arc_info[5] += 0.0314 * (self.arc_angle_increment_speed - 10) * self.delta_time

            # Moving the arc across the screen
            arc_info[0] += 50 * self.arc_movement_direction * self.delta_time

            # If the arc has reached the far right or far left of the screen
            if (arc_info[0] >= screen_width + 200) or (arc_info[0] <= 0 - arc_info[2] - 200):
                # Turn around and move towards the other side of the screen
                self.arc_movement_direction *= -1

        for white_arc, arc_info in self.white_arc_dictionary.items():
            # Draw red arcs onto the screen
            pygame.draw.arc(self.screen, "white", (arc_info[0], arc_info[1], arc_info[2], arc_info[3]), arc_info[4], arc_info[5])

            # Spinning the arcs
            # If the starting angle is not equal to the finishing angle
            if arc_info[4] != arc_info[5]:
                # Increment the starting and finishing angle
                arc_info[4] += 0.02 * self.arc_angle_increment_speed * self.delta_time
                arc_info[5] += 0.02 * self.arc_angle_increment_speed * self.delta_time

            # Moving the arc across the screen
            arc_info[0] += 50 * self.arc_movement_direction * self.delta_time

            # If the arc has reached the far right or far left of the screen
            if (arc_info[0] >= screen_width + 200) or (arc_info[0] <= 0 - arc_info[2] - 200):
                # Turn around and move towards the other side of the screen
                self.arc_movement_direction *= -1
    
    def update_buttons(self, menu_state, menu_buttons_list):
        
        # If the player is in x menu
        if menu_state == True:

            # For all buttons in the menu's button list
            for button in menu_buttons_list:
                
                # Update the delta time of the button
                button.delta_time = self.delta_time

                # Draw the button
                button.draw()

                # Play the button's border animation
                button.play_border_animations()
    
    def run(self, delta_time):

        # Update delta time 
        self.delta_time = delta_time

        # Retrieve the mouse position and update the mouse rect
        self.mouse_position_updating()

        # Check if the left mouse button has been released, and if it has, set the attribute to True
        if pygame.mouse.get_pressed()[0] == 0:
            self.left_mouse_button_released = True

        # Show the background animations for the menus
        self.animate_background()

        # ---------------------------------------------
        # Main menu

        if self.show_main_menu == True: 

            # Draw and update the buttons
            self.update_buttons(menu_state = self.show_main_menu, menu_buttons_list = self.main_menu_buttons)

            # If the left mouse button is pressed and the left mouse button isn't being pressed already
            if pygame.mouse.get_pressed()[0] == 1 and self.left_mouse_button_released == True:

                    # Set the left mouse button as not released
                    self.left_mouse_button_released = False   

                    # Look for collisions between the mouse rect and the rect of any button inside the list
                    button_collision = self.mouse_rect.collidelist(self.main_menu_buttons)

                    # Check for which button was clicked
                    match button_collision:

                        # If the mouse collided with the "Play" button 
                        case 0:
                            # Set all menus to False, which will be detected by the game states controller, moving into the actual game
                            self.show_main_menu = False
                            self.show_controls_menu = False
                            self.show_paused_menu = False

                        # If the mouse collided with the "Controls" button 
                        case 1:
                            # Set the previous menu to be this menu so that we can come back to this menu when the "Back" button is clicked
                            self.previous_menu = "Main"

                            # Show the controls menu
                            self.show_main_menu = False
                            self.show_controls_menu = True
                        
                        # If the mouse collided with the "Quit" button 
                        case 2:
                            # Exit the program
                            pygame.quit()
                            sys.exit()

        # ---------------------------------------------
        # Controls menu

        elif self.show_controls_menu == True:

            # Draw and update the buttons
            self.update_buttons(menu_state = self.show_controls_menu, menu_buttons_list = self.controls_menu_buttons)

            # If the left mouse button is pressed and the left mouse button isn't being pressed already
            if pygame.mouse.get_pressed()[0] == 1 and self.left_mouse_button_released == True:

                # Set the left mouse button as not released
                self.left_mouse_button_released = False          

                # Look for collisions between the mouse rect and the rect of any button inside the list
                button_collision = self.mouse_rect.collidelist(self.controls_menu_buttons)

                # Check for which button was clicked
                match button_collision:

                    # If the mouse collided with the "Back" button
                    case 0:

                        # Check which menu the controls menu was entered from
                        match self.previous_menu:        

                            # From the main menu
                            case "Main":
                                # Show the main menu again
                                self.show_main_menu = True
                            
                            # From the paused menu
                            case "Paused":
                                # Show the paused menu again
                                self.show_paused_menu = True

                        # Stop showing the controls menu
                        self.show_controls_menu = False

        # ---------------------------------------------
        # Paused menu

        elif self.show_paused_menu == True:

            # Draw and update the buttons
            self.update_buttons(menu_state = self.show_paused_menu, menu_buttons_list = self.paused_menu_buttons)

            # If the left mouse button is pressed and the left mouse button isn't being pressed already
            if pygame.mouse.get_pressed()[0] == 1 and self.left_mouse_button_released == True:

                # Set the left mouse button as not released
                self.left_mouse_button_released = False          

                # Look for collisions between the mouse rect and the rect of any button inside the list
                button_collision = self.mouse_rect.collidelist(self.paused_menu_buttons)

                # Check for which button was clicked
                match button_collision:

                     # If the mouse collided with the "Continue" button
                    case 0: 
                        # Stop showing the paused menu
                        self.show_paused_menu = False

                    # If the mouse collided with the "Controls" button
                    case 1:
                        # Set the previous menu to be this menu so that we can come back to this menu when the "Back" button is clicked
                        self.previous_menu = "Paused"

                        # Show the controls menu
                        self.show_paused_menu = False
                        self.show_controls_menu = True

                    # If the mouse collided with the "Quit" button 
                    case 2:
                        # Exit the program
                        pygame.quit()
                        sys.exit()