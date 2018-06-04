FlipDotDisplay
==============

.. image:: ../media/display_in_action.jpg

The module must be connected to a RaspberryPi which in turn is connected to 
a port expander. The port expander itself is controlling the flipdot display. 
Each display is segmentd into modules. Each of these modules must be connected 
seperately to one GPIO port on the Raspberry Pi. ::

  +----------+              +---------+     +-----------------+
  |Raspberry |--[I²C SDA]---| Port-   |-----| flipdot-display |
  |Pi        |              | epander |     |_________________|
  |          |--[I²C SCL]---|         |-----|mod1|mod2|mod3   |
  +----------+              +---------+     +-----------------+
      |||                                      |    |     |
      +++---------[one wire per module]--------+----+-----+


Module ``flipdotdisplay``
-------------------------

.. automodule:: flipdotdisplay
   :members:
   :undoc-members:
   :special-members:

Text On The Display
-------------------

The class :class:`flipdotfont.TextScroller` can be used to write text onto the display.

.. automodule:: flipdotfont
   :members:
   :undoc-members:
