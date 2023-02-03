from pygame.transform import smoothscale
from pygame import Surface as pygame_Surface
from pygame import BLEND_RGB_ADD as pygame_BLEND_RGB_ADD

def draw_text(text, text_colour, font, x, y, surface, scale_multiplier = None):

    # Render the text as an image
    text_image = font.render(text, True, text_colour)

    # If a scale multiplier has not been passed in
    if scale_multiplier == None:
        surface.blit(text_image, (x, y))
    # If a scale multiplier has been passed in
    elif scale_multiplier != None:
        surface.blit(smoothscale(text_image, (text_image.get_width() / scale_multiplier, text_image.get_height() / scale_multiplier)), (x, y))

def change_image_colour(current_animation_image, desired_colour = (255, 255, 255)): # Default colour is white

        # Create a new surface which will be blended with the current (animation) image to make an image change colour
        colour_layer = pygame_Surface(current_animation_image.get_size()).convert_alpha()

        # Fill the colour layer with the desired colour
        colour_layer.fill(desired_colour)
        
        # Set the current (animation) image to be a copy of the current (animation) image (so that the original image is not overwritten)
        current_animation_image = current_animation_image.copy()
        
        # Blit the colour layer onto the current (animation) image, with the special flag pygame_BLEND_RGB_ADD to add the RGB values
        current_animation_image.blit(colour_layer, (0, 0), special_flags = pygame_BLEND_RGB_ADD)

        # Return the coloured animation image (The result should be an image that has a different colour on top)
        return current_animation_image