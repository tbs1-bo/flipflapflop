FlipDotDisplay
==============

.. image:: ../media/display_in_action.jpg

Module ``fffserial``
--------------------

The serial module relies on an ardiuno connected to the display that runs
the :download:`firmware <../arduino/fffarduino_nano/fffarduino_nano.ino>`:: 

  +----------+              +---------+     +-----------------+
  |Raspberry |--[serial]----| Arduino |-----| flipdot-display |
  |Pi        |              |         |     |                 |
  +----------+              +---------+     +-----------------+

.. automodule:: fffserial
   :members:
   :undoc-members:
   :special-members:


Module ``flipdotdisplay``
-------------------------

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

.. automodule:: flipdotdisplay
   :members:
   :undoc-members:
   :special-members:

Module ``util``
---------------

.. automodule:: util
   :members:
   


Text On The Display
-------------------

The class :class:`flipdotfont.TextScroller` can be used to write text onto the display.
Another way to bring text onto the dispoay is by using :func:`util.draw_text_on_fdd`.

.. automodule:: flipdotfont
   :members:
   :undoc-members:
