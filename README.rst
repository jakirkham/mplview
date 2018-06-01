===============================
mplview
===============================


.. image:: https://img.shields.io/pypi/v/mplview.svg
        :target: https://pypi.python.org/pypi/mplview
        :alt: PyPI

.. image:: https://img.shields.io/conda/vn/conda-forge/mplview.svg
        :target: https://anaconda.org/conda-forge/mplview
        :alt: conda-forge

.. image:: https://img.shields.io/travis/jakirkham/mplview/master.svg
        :target: https://travis-ci.org/jakirkham/mplview
        :alt: Travis CI

.. image:: https://readthedocs.org/projects/mplview/badge/?version=latest
        :target: https://mplview.readthedocs.io/en/latest/?badge=latest
        :alt: Read the Docs

.. image:: https://coveralls.io/repos/github/jakirkham/mplview/badge.svg
        :target: https://coveralls.io/github/jakirkham/mplview
        :alt: Coveralls

.. image:: https://img.shields.io/github/license/jakirkham/mplview.svg
        :target: ./LICENSE.txt
        :alt: License


A simple, embeddable Matplotlib-based image viewer.


* Free software: BSD 3-Clause
* Documentation: https://mplview.readthedocs.io.


Example
-------

Typically ``mplview`` is used within the context of the Jupyter Notebook.
Though it can also be used with any interactive GUI backend that ``matplotlib``
provides. Below is a brief example of how this works in the Jupyter Notebook
with some dummy data. Similar usage can be applied to other contexts.

.. code:: python

    # Run the following in your Notebook
    #
    # %matplotlib notebook

    import numpy as np
    import matplotlib.pyplot as plt
    from mplview.core import MatplotlibViewer

    arr = np.random.random((25, 30, 35))

    mplsv = plt.figure(FigureClass=MatplotlibViewer)
    mplsv.set_images(
        arr,
        vmin=0.0,
        vmax=1.0
    )

The array provided to set the images must provide a reasonable subset of the
NumPy array interface (primarily slicing and coercion to NumPy Arrays). This
allows other array types to be used for visualization easily (e.g. Dask
Arrays).


Credits
---------

This package was created with Cookiecutter_ and the `nanshe-org/nanshe-cookiecutter`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`nanshe-org/nanshe-cookiecutter`: https://github.com/nanshe-org/nanshe-cookiecutter
