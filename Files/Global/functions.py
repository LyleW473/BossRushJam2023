def draw_text(text, text_colour, font, x, y, surface):
    text_image = font.render(text, True, text_colour)
    surface.blit(text_image, (x, y))
    
