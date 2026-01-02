import displayprovider

class VirtualDisplay(displayprovider.DisplayBase):
    """
    Virtual display that can hold multiple smaller displays.
    Smaller displays can be combined into a larger virtual display by
    specifying the offset of each smaller display within the virtual display.

    E.g. three displays of size 4x3, 5x3, and 10x3 can be combined into a
    virtual display of size 10x6 by placing the first display at (0,0) in the 
    top left corner, the second display at (5,0), and the third display 
    at (0,3).

    ::
    
        1111.22222
        1111.22222
        1111.22222
        3333333333
        3333333333
        3333333333
    """

    def __init__(self, width, height):
        """
        Create virtual display with given dimension.
        """
        super().__init__(width, height)
        print("Creating virtual display: width", width, "height", height)

        self.xy2display = {}

    def add_display(self, display, x_offset, y_offset):
        "Add a display at given offset within the virtual display."
        assert 0 <= x_offset + display.width <= self.width, "x_offset out of bounds"
        assert 0 <= y_offset + display.height <= self.height, "y_offset out of bounds"
        
        print("Adding display", display.__class__.__name__, "at", x_offset, y_offset)

        self.xy2display[(x_offset, y_offset)] = display

    def _display_at(self, x, y):
        """
        Return display placed at given coordinates in virtual display and the 
        offset of the display within the virtual display. 
        Return None if no display is present.
        """
        for (x_offset, y_offset), display in self.xy2display.items():
            if x_offset <= x < x_offset + display.width and \
               y_offset <= y < y_offset + display.height:
                return display, (x_offset, y_offset)

    def px(self, x, y, val):
        "Set pixel at (x,y) to val (True/False) in virtual display."
        assert 0 <= x < self.width, "Pixel x out of bounds"
        assert 0 <= y < self.height, "Pixel y out of bounds"
        assert val in (True, False), "Pixel value must be True or False"

        display_pos = self._display_at(x, y)
        if display_pos is None:
            return  # no display at this position
        
        display, (x_offset, y_offset) = display_pos
        if display is not None:
            dx = x - x_offset
            dy = y - y_offset
            display.px(dx, dy, val)

    def show(self):
        "Update all displays within the virtual display."

        for display in self.xy2display.values():
            display.show()

    def clear(self):
        for display in self.xy2display.values():
            display.clear()

    def print_layout(self):
        "Print the virtual display to console for debugging purposes."

        displays = list(self.xy2display.values())
        for y in range(self.height):
            for x in range(self.width):                
                display_pos = self._display_at(x, y)                
                if display_pos is None:
                    print(".", end="")
                else:
                    display, _ = display_pos
                    idx = displays.index(display)
                    print(idx, end="")

            print()
        
        for i, d in enumerate(displays):
            print(f"{i}: {d.__class__.__name__} ({d.width}x{d.height})")

def test_virtual_display():
    from displayprovider import DisplayBase
    
    """
    1111.22222
    1111.22222
    1111.22222
    3333333333
    3333333333
    3333333333
    """
    vd = VirtualDisplay(10, 6)

    d1 = DisplayBase(4, 3)
    d2 = DisplayBase(5, 3)
    d3 = DisplayBase(10, 3)

    vd.add_display(d1, 0, 0)
    vd.add_display(d2, 5, 0)
    vd.add_display(d3, 0, 3)

    vd.print_layout()

    # set some pixels
    vd.px(0, 0, True)
    vd.px(3, 2, True)
    vd.px(4, 0, True)
    vd.px(9, 2, True)
    vd.px(0, 3, True)
    vd.px(9, 5, True)

    vd.show()

if __name__ == "__main__":
    test_virtual_display()
