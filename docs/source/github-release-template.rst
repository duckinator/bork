GitHub Release Template
-----------------------

You can create a template for GitHub releases, named ``.github/BORK_RELEASE_TEMPLATE.md``.

You can reference a few variables using the syntax ``{variable_name}``.

The avialable variables, and what they contain, are:

* ``project_name``: The project name, as specified by the build backend.
* ``owner``: The part before the ``/`` in ``github_repository`` in the :doc:`config`.
* ``repo``: The part after the ``/`` in ``github_repository`` in the :doc:`config`.
* ``tag``: The tag created by the release. This is ``v`` followed by the version number.
* ``changelog``: A generated changelog based on merged Pull Requests since the last release.

An example template might look like:

.. code-block::

   {project_name} {tag} is now available!

   PyPI package: https://pypi.org/project/bork/{version}/
   Docker image: https://hub.docker.com/r/duckinator/bork/

   The ZipApp is available below, as bork.pyz.

   You can help {project_name} by supporting me on [Patreon](https://www.patreon.com/duckinator)!

   ---

   Changes:

   {changelog}
