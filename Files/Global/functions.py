from pygame.transform import smoothscale
def draw_text(text, text_colour, font, x, y, surface, scale_multiplier = None):
    text_image = font.render(text, True, text_colour)
    # If a scale multiplier has not been passed in
    if scale_multiplier == None:
        surface.blit(text_image, (x, y))
    # If a scale multiplier has been passed in
    elif scale_multiplier != None:
        surface.blit(smoothscale(text_image, (text_image.get_width() / scale_multiplier, text_image.get_height() / scale_multiplier)), (x, y))