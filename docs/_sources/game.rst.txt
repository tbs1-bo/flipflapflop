Games
=====

FlipDot-Displays can be used to play funny games on.

Rogueflip
---------

The demo game *rogueflip* is inspired by text-console based dungeon games 
named 'roguelike'. The following video shows the game in action.

.. image:: ../media/simulator_video_thumbnail.jpg
   :target: https://www.youtube-nocookie.com/embed/ed5-gVciz3I?rel=0

Level Description
^^^^^^^^^^^^^^^^^

Each Level can be painted with a tool like GIMP. It must be exported as
`PNM-file <https://de.wikipedia.org/wiki/Portable_Anymap#Pixmap>`_ afterwards.
In this format the image dimension is described first. After that each line 
contains a color value - one for red, green and blue respectively. The image 
dimension must be a multiple of the dimension of the flipdot display.

This :download:`example game world <../ressources/rogueflip_world.pnm>` can be 
opened with GIMP.


Module Description
^^^^^^^^^^^^^^^^^^

.. automodule:: rogueflip
   :members:
   :undoc-members:
