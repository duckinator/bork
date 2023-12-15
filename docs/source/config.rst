Configuration
=============

Bork is configured using pyproject.toml.

Build System/Backend
--------------------

You always need to specify the ``[build-system]`` table. This should be
configured according to the build backend you're using.

If you are not using Bork to create ZipApps, this should be the only configuration
that Bork requires. The build system (aka "backend") you use will likely
want at least ``project.name`` and ``project.version`` or equivalent. See
"Recommended pyproject.toml Configuration" below.

`Python Packaging User Guide: Writing your pyproject.toml`_
explains this well if you're using Hatchling, Setuptools, Flit, or PDM.
The information for Hatchling and Setuptool are also included below.

For Setuptools, this looks like:

.. code-block::

      [build-system]
      requires = ["setuptools >= 61", "wheel"]
      build-backend = "setuptools.build_meta"

If you are working on an existing Setuptools project with ``setup.py`` or
``setup.cfg``, creating a ``pyproject.toml`` file with those contents should
be enough to start using Bork and other `PEP 517`_-compliant frontends.

For Hatchling it looks like:

.. code-block::

      [build-system]
      requires = ["hatchling"]
      build-backend = "hatchling.build"


Recommended pyproject.toml Configuration
----------------------------------------

In addition to the ``[build-system]`` configuration, it is recommended to
include at least ``project.name`` and ``project.version`` (or equivalent).
Some systems (e.g. Poetry) require the values to be specified in a different way.

If you wish to have these values defined in pyproject.toml directly, it
will look like this:

.. code-block::

      [project]
      name = "some-project-name"
      version = "0.0.1"

For more advanced configurations, check
`Python Packaging User Guide: Writing your pyproject.toml`_ or open a
`GitHub Discussion for Bork`_.


ZipApps
-------

To have Bork build a ZipApp, you need the entire recommended configuration
described above.

You also need to:

* enable ZipApp functionality
* specify the main function/entrypoint.

For `Emanate <https://github.com/duckinator/emanate>`_, which has the ZipApp
call the `emanate.cli.main()` function, this looks like:

.. code-block::

      [tool.bork.zipapp]
      enabled = true
      main = "emanate.cli:main"


Releasing to PyPi and GitHub
----------------------------

Configuring the release process for Bork happens in the ``[tool.bork.release]``
table in ``pyproject.toml``.

As an example, Bork releases itself on PyPi and GitHub, and uses this configuration:

.. code-block::

      [tool.bork.release]
      pypi = true
      github = true
      github_repository = "duckinator/bork"
      strip_zipapp_version = true

Here's what each option does:

* ``pypi``: If true, release to PyPi using the project name reported by the build system.
* ``github``: If true, release to GitHub using the specified ``github_repository``.
* ``github_repository``: The name of the GitHub repository to publish releases to.
* ``strip_zipapp_version``: If true, remove the version number from the ZipApp name.

Setting ``strip_zipapp_version`` to true is recommended, because it means the
latest ZipApp is always available at the same URL.

For Bork, this URL is: https://github.com/duckinator/bork/releases/latest/download/bork.pyz

You can provide a template for GitHub Releases by providing a :doc:`github-release-template`.

Aliases
-------

Aliases can be configured in the ``[tool.bork.aliases]`` section of ``pyproject.toml``.

Each alias can be either a string (one command) or a list of strings (multiple
commands, ran one at a time, stopping if any of them fail).

An example configuration (if your code is in a directory named ``example-project``)
might look something like this:

.. code-block::

      [tool.bork.aliases]
      lint = [
          "pylint example-project tests",
          "mypy example-project",
      ]
      test = "pytest --verbose"


.. _Python Packaging User Guide\: Writing your pyproject.toml: https://packaging.python.org/en/latest/guides/writing-pyproject-toml/
.. _GitHub Discussion for Bork: https://github.com/duckinator/bork/discussions
.. _PEP 517: https://peps.python.org/pep-0517/
