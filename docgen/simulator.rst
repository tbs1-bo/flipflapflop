FlipDot-Simulator
=================

See the simulator in action in the following videos.

.. image:: ../media/simulator_video_thumbnail.png
   :target: https://www.youtube-nocookie.com/embed/ed5-gVciz3I?rel=0

.. image:: ../media/clock_video_thumbnail.png
   :target: https://www.youtube-nocookie.com/embed/2X3LfF__rnQ?rel=0

Installation
------------

The simulator relies on the 
`pygame framework <https://www.pygame.org/docs/>`_. 
Therefore this has to be installed before - ``pip`` can be used for this.::

    $ pip install pygame

More information about this process is available on the pygame-website.

Next the source code must be downloaded from the project page at
`github <https://github.com/tbs1-bo/flipflapflop/archive/master.zip>`_.
The archive must be extracted into an empty directory. Create a file
``flipdotsim_example.py`` with the content listed in the example section
below and run it with ``python flipdotsim_example.py``.

Example
-------

.. literalinclude:: flipdotsim_example.py
   :linenos:


Module Description
------------------

.. automodule:: flipdotsim
   :members:
   :undoc-members:
   :exclude-members: test_flipdot_sim, main

Simulator (godot version)
-------------------------

There is another simulator that relies on the `godot game engine
<https://www.godotengine.org/>`_. A standalone version for Windows
and Linux is available from the `projects releases page 
<https://github.com/tbs1-bo/flipflapflop/releases>`_.

After startup the simulator can be controlled by cursor keys
(moving the display) and page up/down for scaling the map.

The simulator conforms to the protocol described in the 
:doc:`net` module: send a sequence of 1s and 0s (in ASCII)
to port 10101 of the server.

Simulator (pyxel version)
-------------------------

There is another simulator that relies on the `pyxel game engine
<https://github.com/kitao/pyxel>`_. Therefore in order to use it 
pyxel must be installed.::

    $ pip install pyxel

.. automodule:: pyxel_sim
   :members:
   :undoc-members:
   :exclude-members: test_flipdot_sim, main
