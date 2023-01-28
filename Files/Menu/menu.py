import pygame, sys
from Menu.button import Button
from Global.settings import * 

class Menu:
    def __init__(self):

        # Screen
        self.surface = pygame.display.get_surface()

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
        # Mouse
        self.left_mouse_button_released = True # Attribute used to track if the left mouse button is released so that 

        # ----------------------------------------------------------------------------------
        # Button highlighting

        self.button_highlighting_info_dict = {
                                                "maximum_highlight_colour": (255, 255, 255),
                                                "minimum_highlight_colour": (60, 60, 60), 
                                                "highlight_colour": [255, 255, 255],
                                                "highlight_decrease": True,
                                                "highlight_width": 10,
                                                "highlight_gradient": 0
        }
        # Settings for how long the button highlight takes to decrease and increase
        button_highlight_decrease_time = 1.75 * (1000) # Time in milliseconds
        self.button_highlighting_info_dict["highlight_gradient"] = (max(self.button_highlighting_info_dict["minimum_highlight_colour"]) - max(self.button_highlighting_info_dict["maximum_highlight_colour"])) / button_highlight_decrease_time

    def create_buttons(self):

        # Width and height of buttons
        default_button_measurements = (400, 90)

        # Values are: x pos, y pos, button spacing 
        default_positions = (screen_width / 2, 300)

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
            
            "main_menu": {"ButtonPurposes": ("Play", "Controls", "Quit"), "ButtonsList": [], "StartingPositions": default_positions, "ButtonSpacing": button_spacing},
            "paused_menu": {"ButtonPurposes": ("Continue", "Controls", "Quit"), "ButtonsList": [], "StartingPositions": default_positions, "ButtonSpacing": button_spacing},
            "controls_menu": {"ButtonPurposes": ["Back"], "ButtonsList": [], "StartingPositions": (default_positions[0], screen_height - 150), "ButtonSpacing": (0, 0)}
                                    }
        # ------------------------------------------------------------------------

        # For each menu
        for menu in self.menu_buttons_dict:

            # For each button purpose in the list of button purposes 
            for index, button_purpose in enumerate(self.menu_buttons_dict[menu]["ButtonPurposes"]):
                
                """  Create the button, passing parameters:
                - A rect info dict containing the x and y positions and the measurements of the button 
                - The purpose of the button (e.g. "Play" button)
                - The surface that the button will be drawn onto
                """
                self.menu_buttons_dict[menu]["ButtonsList"].append(
                                            Button(
                                                rect_info_dict = {
                                                                    "x": self.menu_buttons_dict[menu]["StartingPositions"][0], 
                                                                    "y" : self.menu_buttons_dict[menu]["StartingPositions"][1] + (self.menu_buttons_dict[menu]["ButtonSpacing"][1] * index) ,
                                                                    "button_measurements": default_button_measurements}, 
                                                purpose = button_purpose,
                                                surface = self.surface
                                                )
                                            )

    def mouse_position_updating(self):

        # Retrieve the mouse position
        self.mouse_position = pygame.mouse.get_pos()

        # Define the mouse rect and draw it onto the screen (For collisions with drawing tiles)
        self.mouse_rect = pygame.Rect(self.mouse_position[0], self.mouse_position[1], 1, 1)

    def animate_background(self):

        # Fill the screen with black
        self.surface.fill("black")

    def highlight_button(self, menu_buttons_list):
        
        # If the mouse rect is colliding with a button (-1 means empty space)
        index_of_button_to_highlight = self.mouse_rect.collidelist(menu_buttons_list)
        if index_of_button_to_highlight != -1:

            # If we should decrease the highlight colour
            if self.button_highlighting_info_dict["highlight_decrease"] == True:

                # If the current highlight colour is less than or equal to the minimum highlight colour
                if tuple(self.button_highlighting_info_dict["highlight_colour"]) <= self.button_highlighting_info_dict["minimum_highlight_colour"]:
                    # Start increasing the highlight colour
                    self.button_highlighting_info_dict["highlight_decrease"] = False

                # If the current highlight colour is not the same as the minimum highlight colour
                else:
                    for index, highlight_colour in enumerate(self.button_highlighting_info_dict["highlight_colour"]):

                        # If decreasing the current highlight colour is greater than the minimum highlight colour, decrease the highlight colour 
                        if highlight_colour + (self.button_highlighting_info_dict["highlight_gradient"] * (self.delta_time * 1000)) > self.button_highlighting_info_dict["minimum_highlight_colour"][index]:
                            # The gradient is negative so add to decrease the colour
                            self.button_highlighting_info_dict["highlight_colour"][index] += self.button_highlighting_info_dict["highlight_gradient"] * (self.delta_time * 1000)

                        # If decreasing the current highlight colour is less than the minimum highlight colour
                        else:
                            # Set the current highlight colour to be the minimum highlight colour and exit the for loop
                            self.button_highlighting_info_dict["highlight_colour"] = list(self.button_highlighting_info_dict["minimum_highlight_colour"])
                            break
            
            # If we should increase the highlight colour
            else:
                
                # If the current highlight colour is greater than or equal to the maximum highlight colour
                if tuple(self.button_highlighting_info_dict["highlight_colour"]) >= self.button_highlighting_info_dict["maximum_highlight_colour"]:
                    # Start decreasing the highlight colour
                    self.button_highlighting_info_dict["highlight_decrease"] = True
                
                # If the current highlight colour is not the same as the maximum highlight colour
                else:
                    for index, highlight_colour in enumerate(self.button_highlighting_info_dict["highlight_colour"]):

                        # If increasing the current highlight colour is greater than the maximum highlight colour, increase the highlight colour 
                        if highlight_colour - (self.button_highlighting_info_dict["highlight_gradient"] * (self.delta_time * 1000)) < self.button_highlighting_info_dict["maximum_highlight_colour"][index]:
                            # The gradient is negative so subtract to increase the colour
                            self.button_highlighting_info_dict["highlight_colour"][index] -= self.button_highlighting_info_dict["highlight_gradient"] * (self.delta_time * 1000)
                        
                        # If increasing the current highlight colour is greater than the maximum highlight colour
                        else:
                            self.button_highlighting_info_dict["highlight_colour"] = list(self.button_highlighting_info_dict["maximum_highlight_colour"])
                            break

            # Temporary variables for readability
            # The button is inflated with the highlight width x 2 so that the highlight will be highlighting the border of the button
            button_to_highlight = menu_buttons_list[index_of_button_to_highlight]
            inflated_button_to_highlight_rect = button_to_highlight.rect.inflate(
                                                                        self.button_highlighting_info_dict["highlight_width"] * 2,
                                                                        self.button_highlighting_info_dict["highlight_width"] * 2)


            # Draw the highlight border "rect"
            pygame.draw.rect(
                            surface = self.surface, 
                            color = self.button_highlighting_info_dict["highlight_colour"], 
                            rect = inflated_button_to_highlight_rect, 
                            width = self.button_highlighting_info_dict["highlight_width"]
                            )
        
        # If the player's mouse is not on any of the buttons
        else:
            # If the current highlight colour is not the same as the maximum highlight colour
            if tuple(self.button_highlighting_info_dict["highlight_colour"]) != self.button_highlighting_info_dict["maximum_highlight_colour"]:
                # Set the current highlight colour to be the same as the maximum highlight colour 
                self.button_highlighting_info_dict["highlight_colour"] = list(self.button_highlighting_info_dict["maximum_highlight_colour"])
        
    def update_buttons(self, menu_state, menu_buttons_list):
        
        # If the player is in x menu
        if menu_state == True:

            # Highlight the button if the player's mouse is hovering over the button
            self.highlight_button(menu_buttons_list = menu_buttons_list)
            
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
            self.update_buttons(menu_state = self.show_main_menu, menu_buttons_list = self.menu_buttons_dict["main_menu"]["ButtonsList"])

            # If the left mouse button is pressed and the left mouse button isn't being pressed already
            if pygame.mouse.get_pressed()[0] == True and self.left_mouse_button_released == True:

                    # Set the left mouse button as not released
                    self.left_mouse_button_released = False   

                    # Look for collisions between the mouse rect and the rect of any button inside the list
                    button_collision = self.mouse_rect.collidelist(self.menu_buttons_dict["main_menu"]["ButtonsList"])

                    # Check for which button was clicked by looking at the purpose of the button
                    match self.menu_buttons_dict["main_menu"]["ButtonsList"][button_collision].purpose:
                        
                        # If the mouse collided with the "Play" button 
                        case "Play":
                            # Set all menus to False, which will be detected by the game states controller, moving into the actual game
                            self.show_main_menu = False
                            self.show_controls_menu = False
                            self.show_paused_menu = False

                        # If the mouse collided with the "Controls" button 
                        case "Controls":

                            # Set the previous menu to be this menu so that we can come back to this menu when the "Back" button is clicked
                            self.previous_menu = "Main"

                            # Show the controls menu
                            self.show_main_menu = False
                            self.show_controls_menu = True
                        
                        # If the mouse collided with the "Quit" button 
                        case "Quit":
                            # Exit the program
                            pygame.quit()
                            sys.exit()

        # ---------------------------------------------
        # Controls menu

        elif self.show_controls_menu == True:

            # Draw and update the buttons
            self.update_buttons(menu_state = self.show_controls_menu, menu_buttons_list = self.menu_buttons_dict["controls_menu"]["ButtonsList"])

            # If the left mouse button is pressed and the left mouse button isn't being pressed already
            if pygame.mouse.get_pressed()[0] == 1 and self.left_mouse_button_released == True:

                # Set the left mouse button as not released
                self.left_mouse_button_released = False          

                # Look for collisions between the mouse rect and the rect of any button inside the list
                button_collision = self.mouse_rect.collidelist(self.menu_buttons_dict["controls_menu"]["ButtonsList"])

                # Check for which button was clicked
                match self.menu_buttons_dict["controls_menu"]["ButtonsList"][button_collision].purpose:

                    # If the mouse collided with the "Back" button
                    case "Back":

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
            self.update_buttons(menu_state = self.show_paused_menu, menu_buttons_list = self.menu_buttons_dict["paused_menu"]["ButtonsList"])

            # If the left mouse button is pressed and the left mouse button isn't being pressed already
            if pygame.mouse.get_pressed()[0] == 1 and self.left_mouse_button_released == True:

                # Set the left mouse button as not released
                self.left_mouse_button_released = False          

                # Look for collisions between the mouse rect and the rect of any button inside the list
                button_collision = self.mouse_rect.collidelist(self.menu_buttons_dict["paused_menu"]["ButtonsList"])

                # Check for which button was clicked
                match self.menu_buttons_dict["paused_menu"]["ButtonsList"][button_collision].purpose:

                     # If the mouse collided with the "Continue" button
                    case "Continue": 
                        # Stop showing the paused menu
                        self.show_paused_menu = False

                    # If the mouse collided with the "Controls" button
                    case "Controls":
                        # Set the previous menu to be this menu so that we can come back to this menu when the "Back" button is clicked
                        self.previous_menu = "Paused"

                        # Show the controls menu
                        self.show_paused_menu = False
                        self.show_controls_menu = True

                    # If the mouse collided with the "Quit" button 
                    case "Quit":
                        # Exit the program
                        pygame.quit()
                        sys.exit()