Developer Documentation
=======================

Find here information for developers of this project. If you just want
to use the package you don't need to read any further.



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
