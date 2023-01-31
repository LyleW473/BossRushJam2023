import pygame, sys
from Menu.button import Button
from Global.settings import * 

class Menu:
    def __init__(self):

        # Screen
        self.surface = pygame.display.get_surface()
    
        # ------------------------------------------------------------------------------------------------------------------------------------------------

        # Game states

        """ Existing menus:
        - Main
        - Controls
        - Paused
        """

        # Stores the current menu that should be shown to the player
        self.current_menu = "main_menu"
        
        # Store the previous menu so that we can go back to previous menus when the "Back" button is clicked
        self.previous_menu = None 

        # ------------------------------------------------------------------------------------------------------------------------------------------------
        # Mouse
        self.left_mouse_button_released = True # Attribute used to track if the left mouse button is released so that 

        # ------------------------------------------------------------------------------------------------------------------------------------------------
        # Buttons

        # Create the buttons
        self.create_buttons()

    def create_buttons(self):

        # Width and height of buttons
        default_button_measurements = (400, 90)

        # Value for button spacing
        button_spacing =  (0, 150)

        """A dictionary used to contain all the information for each menu:
        - Each menu:
            - The purpose of each button
            - A buttons list to store the created buttons
            - The starting positions of the buttons
            - The button spacing between each 
        """
        self.menu_buttons_dict = {
            
            "main_menu": {"ButtonPurposes": ("Play", "Controls", "Quit"), "ButtonsList": [], "StartingPositions": (screen_width / 2, 450), "ButtonSpacing": button_spacing},
            "paused_menu": {"ButtonPurposes": ("Continue", "Controls", "Quit"), "ButtonsList": [], "StartingPositions": (screen_width / 2, 350), "ButtonSpacing": button_spacing},
            "controls_menu": {"ButtonPurposes": ["Back"], "ButtonsList": [], "StartingPositions": (screen_width / 2, screen_height - 150), "ButtonSpacing": (0, 0)}
                                    }

        # Index of the last button changed (i.e. the buttons' alpha level and size)
        self.index_of_last_button_changed = None

        # ------------------------------------------------------------------------

        # For each menu
        for menu in self.menu_buttons_dict:

            # For each button purpose in the list of button purposes 
            for index, button_purpose in enumerate(self.menu_buttons_dict[menu]["ButtonPurposes"]):
                
                """  Create the button, passing parameters:
                - A rect info dict containing the x and y positions and the measurements of the button 
                - The purpose of the button (e.g. "Play" button)
                - The font of the button text and the size
                - The surface that the button will be drawn onto
                """
                self.menu_buttons_dict[menu]["ButtonsList"].append(
                                            Button(
                                                rect_info_dict = {
                                                                    "x": self.menu_buttons_dict[menu]["StartingPositions"][0], 
                                                                    "y" : self.menu_buttons_dict[menu]["StartingPositions"][1] + (self.menu_buttons_dict[menu]["ButtonSpacing"][1] * index) ,
                                                                    "button_measurements": default_button_measurements}, 
                                                purpose = button_purpose,
                                                text_font = pygame.font.Font("graphics/Fonts/menu_buttons_font.ttf", 50),
                                                surface = self.surface
                                                )
                                            )

    def mouse_position_updating(self):

        # Creates a mouse rect and updates the mouse rect depending on the mouse position 

        # Retrieve the mouse position
        self.mouse_position = pygame.mouse.get_pos()

        # If a mouse rect has not been created already
        if hasattr(self, "mouse_rect") == False:
            # Create the mouse rect
            self.mouse_rect = pygame.Rect(self.mouse_position[0], self.mouse_position[1], 1, 1)
        # If a mouse rect already exists
        else:
            # Update the x and y positions of the mouse rect
            self.mouse_rect.x, self.mouse_rect.y = self.mouse_position[0], self.mouse_position[1]

    def animate_background(self):
        
        # WORK IN PROGRESS

        # Fill the surface with a colour
        self.surface.fill((40, 40, 40))

    def update_buttons(self, menu_buttons_list):

        """
        - Updates delta time of buttons
        - Performs changes on the size and alpha level of the buttons if hovered over
        - Draws the button onto the main surface
        - Highlights the button if hovered over
        - Plays the border animations for the buttons
        """
        
        # Find the index of the button inside the menu buttons list if the mouse is hovering over the button
        button_collision_index = self.mouse_rect.collidelist(menu_buttons_list)

        # Hovering over any button
        if button_collision_index != -1:

            # If no button has been "changed" yet
            if self.index_of_last_button_changed == None:
                # Change the size and alpha level of the current button being hovered over
                menu_buttons_list[button_collision_index].change_button_size(inflate = True)
                menu_buttons_list[button_collision_index].change_alpha_level(increase = True)

                # Save the index of the last button changed inside menu_buttons_List
                self.index_of_last_button_changed = button_collision_index

        # Hovering over empty space
        elif button_collision_index == -1:
            # Reset the size and alpha level of the last button that was "changed"
            self.reset_button_size_and_alpha(menu_buttons_list = menu_buttons_list)

        # For all buttons in the menu's button list
        for button in menu_buttons_list:

            # Update the delta time of the button
            button.delta_time = self.delta_time

            # Draw the button
            button.draw()

            # Highlight the button if the player's mouse is hovering over the button
            button.highlight(mouse_rect = self.mouse_rect)

            # Play the button's border animation
            button.play_border_animations()

    def reset_button_size_and_alpha(self, menu_buttons_list):

        # Resets the last button that was "changed" (i.e. Alpha level increased and button size was increased)

        # If the index of the last button changed is not None
        if self.index_of_last_button_changed != None:
            # Reset the size of the button and the alpha level back to its default
            menu_buttons_list[self.index_of_last_button_changed].change_button_size(inflate = False)
            menu_buttons_list[self.index_of_last_button_changed].change_alpha_level(increase = False)

            # Set the index of the last button changed back to None
            self.index_of_last_button_changed = None

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

        if self.current_menu == "main_menu": 

            # Draw and update the buttons
            self.update_buttons(menu_buttons_list = self.menu_buttons_dict["main_menu"]["ButtonsList"])

            # If the left mouse button is pressed and the left mouse button isn't being pressed already
            if pygame.mouse.get_pressed()[0] == True and self.left_mouse_button_released == True:

                    # Set the left mouse button as not released
                    self.left_mouse_button_released = False   

                    # Look for collisions between the mouse rect and the rect of any button inside the list
                    button_collision = self.mouse_rect.collidelist(self.menu_buttons_dict["main_menu"]["ButtonsList"])

                    # If the player did not click on empty space
                    # Note: This check is so that we check the purpose of the button at index -1
                    if button_collision != -1:

                        # Reset the last changed button to its default "settings"
                        self.reset_button_size_and_alpha(menu_buttons_list = self.menu_buttons_dict["main_menu"]["ButtonsList"])

                        # Check for which button was clicked by looking at the purpose of the button
                        match self.menu_buttons_dict["main_menu"]["ButtonsList"][button_collision].purpose:
                            
                            # If the mouse collided with the "Play" button 
                            case "Play":
                                # Set the current menu to None, which will be detected by the game states controller, moving into the actual game
                                self.current_menu = None

                            # If the mouse collided with the "Controls" button 
                            case "Controls":

                                # Set the previous menu to be this menu so that we can come back to this menu when the "Back" button is clicked
                                self.previous_menu = "main_menu"

                                # Show the controls menu
                                self.current_menu = "controls_menu"

                            # If the mouse collided with the "Quit" button 
                            case "Quit":
                                # Exit the program
                                pygame.quit()
                                sys.exit()

        # ---------------------------------------------
        # Controls menu

        elif self.current_menu == "controls_menu":

            # Draw and update the buttons
            self.update_buttons(menu_buttons_list = self.menu_buttons_dict["controls_menu"]["ButtonsList"])

            # If the left mouse button is pressed and the left mouse button isn't being pressed already
            if pygame.mouse.get_pressed()[0] == 1 and self.left_mouse_button_released == True:

                # Set the left mouse button as not released
                self.left_mouse_button_released = False          

                # Look for collisions between the mouse rect and the rect of any button inside the list
                button_collision = self.mouse_rect.collidelist(self.menu_buttons_dict["controls_menu"]["ButtonsList"])

                # If the player did not click on empty space
                # Note: This check is so that we check the purpose of the button at index -1
                if button_collision != -1:

                    # Reset the last changed button to its default "settings"
                    self.reset_button_size_and_alpha(menu_buttons_list = self.menu_buttons_dict["controls_menu"]["ButtonsList"])

                    # Check for which button was clicked
                    match self.menu_buttons_dict["controls_menu"]["ButtonsList"][button_collision].purpose:
                        
                        # If the mouse collided with the "Back" button
                        case "Back":

                            # Check which menu the controls menu was entered from
                            match self.previous_menu:        

                                # From the main menu
                                case "main_menu":
                                    # Show the main menu
                                    self.current_menu = "main_menu"
                                
                                # From the paused menu
                                case "paused_menu":
                                    # Show the paused menu
                                    self.current_menu = "paused_menu"

        # ---------------------------------------------
        # Paused menu

        elif self.current_menu == "paused_menu":

            # Draw and update the buttons
            self.update_buttons(menu_buttons_list = self.menu_buttons_dict["paused_menu"]["ButtonsList"])

            # If the left mouse button is pressed and the left mouse button isn't being pressed already
            if pygame.mouse.get_pressed()[0] == 1 and self.left_mouse_button_released == True:

                # Set the left mouse button as not released
                self.left_mouse_button_released = False          

                # Look for collisions between the mouse rect and the rect of any button inside the list
                button_collision = self.mouse_rect.collidelist(self.menu_buttons_dict["paused_menu"]["ButtonsList"])

                # If the player did not click on empty space
                # Note: This check is so that we check the purpose of the button at index -1
                if button_collision != -1:

                    # Reset the last changed button to its default "settings"
                    self.reset_button_size_and_alpha(menu_buttons_list = self.menu_buttons_dict["paused_menu"]["ButtonsList"])

                    # Check for which button was clicked
                    match self.menu_buttons_dict["paused_menu"]["ButtonsList"][button_collision].purpose:

                        # If the mouse collided with the "Continue" button
                        case "Continue": 
                            # Stop showing the paused menu
                            self.current_menu = None

                        # If the mouse collided with the "Controls" button
                        case "Controls":
                            # Set the previous menu to be this menu so that we can come back to this menu when the "Back" button is clicked
                            self.previous_menu = "paused_menu"

                            # Show the controls menu
                            self.current_menu = "controls_menu"
                        
                        # If the mouse collided with the "Quit" button 
                        case "Quit":
                            # Exit the program
                            pygame.quit()
                            sys.exit()