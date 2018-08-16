Developer Documentation
=======================

Find here information for developers of this project. If you just want
to use the package you don't need to read any further.

Deployment
----------

The deployment scenario described relies on a Raspberry Pi that acts as as access point.
The display is connected to it directly. On the Pi runs a systemd-service as described
in the `Raspberry Pi Documentation <https://www.raspberrypi.org/documentation/linux/usage/systemd.md>`_.
The service file ``flipflapflop.service`` must be copied to ``/etc/systemd/system`` can be
started afterwards. It assumes the repository is checked out in ``/home/pi/flipflapflop``.


Creating the documentation
--------------------------

The documentation is made with `Sphinx <http://www.sphinx-doc.org/>`_. 
Therefore the sphinx framework and a third party 
`theme from readthedocs <https://sphinx-rtd-theme.readthedocs.io>`_ 
must be installed.

.. code-block:: bash

   $ pip install -r docgen/requirements.txt

The documentation is created with sphinx and is configured in folder ``docgen``. 
You can use ``make html`` or ``make.bat html`` to create the docucmentation
in ``docgen/_build/html``. It will automaticall be copied to ``docs``.
After pushing to github it will be available 
`there <https://tbs1-bo.github.io/flipflapflop/>`_.

There is a ``gitlab-ci.yml`` script that will only be executed if the project is 
hosted on a gitlab server. The script automatically deploys the documentation
on every commit onto the master branch. An examples can be found 
`here <https://tbs1-bo.gitlab.io/flipflapflop/>`_.

Video Backups
-------------

The videos linked in this documentation are hosted by YouTube. There is a 
mirror of these videos at 
`archive.org <https://archive.org/details/FlipFlapFlop>`_.
