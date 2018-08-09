import pygame


def draw_surface_on_fdd(flipdotdisplay, surf:pygame.Surface):
    """Draw the surface onto the display. You need to invoke show() 
    afterwards to make it visible. Black pixels (rgb 0,0,0) are considered
    black and turned off, other colors are considered pixels turned on. 
    The clipping area of the  surface can be modified to draw only part 
    of the surface. A demo application is available in 
    demos.PygameSurfaceDemo."""
    cx,cy,cw,ch = surf.get_clip()
    for y in range(ch):
        for x in range(cw):
            r,g,b,a = surf.get_at((cx+x, cy+y))
            ison = not (r == g == b == 0)
            flipdotdisplay.px(x, y, ison)
