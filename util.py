"""This module contains helper methods for the handling of flipdotdisplays.
"""

import pygame

pygame.font.init()

def draw_surface_on_fdd(surface: pygame.Surface, flipdotdisplay):
    """Draw the surface onto the display. You need to invoke show()
    afterwards to make it visible. Black pixels (rgb 0,0,0) are considered
    black and turned off, other colors are considered pixels turned on.
    The clipping area of the  surface can be modified to draw only part
    of the surface. A demo application is available in
    demos.PygameSurfaceDemo."""
    cx, cy, cw, ch = surface.get_clip()
    for y in range(ch):
        for x in range(cw):
            r, g, b, a = surface.get_at((cx + x, cy + y))
            ison = not (r == g == b == 0)
            flipdotdisplay.px(x, y, ison)


def draw_text_on_fdd(text, fontname, fontsize, flipdotdisplay):
    """Draw text on a display.

    >>> import net
    >>> import util
    >>> fdd = net.RemoteDisplay("taylorpi.local")
    Remote display will send data to taylorpi.local on port 10101
    >>> util.draw_text_on_fdd("Hallo", "Arial", 9, fdd)
    >>> fdd.show()
    """
    font = pygame.font.SysFont(fontname, fontsize, bold=False, italic=False)
    surf = font.render(text, False, (255, 255, 255),
                       None)
    draw_surface_on_fdd(surf, flipdotdisplay)
