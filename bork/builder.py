from pathlib import Path
import subprocess
import sys
# Slight kludge so we can have a function named zipapp().
import zipapp as Zipapp  # noqa: N812

import pep517.build  # type: ignore
import toml

from .filesystem import load_setup_cfg, try_delete
from .log import logger


# The "proper" way to handle the default would be to check python_requires
# in setup.cfg. But, since Bork needs Python 3, there's no point.
DEFAULT_PYTHON_INTERPRETER = '/usr/bin/env python3'


def dist():
    """Build the sdist and wheel distributions."""

    # We can use the pep517 library to add separate source and binary build
    # functions, but I'm leaving that alone unless someone asks for it.
    args = ['--source', '--binary']
    pep517.build.main(pep517.build.parser.parse_args(['.', *args]))


def _package_name():
    setup_cfg = load_setup_cfg()

    if 'metadata' not in setup_cfg or 'name' not in setup_cfg['metadata']:
        raise RuntimeError(
            "The [metadata] section of setup.cfg needs the 'name' key set.",
        )

    return setup_cfg['metadata']['name']


def _python_interpreter(config):
    # To override the default interpreter, add this to your project's setup.cfg:
    #
    # [bork]
    # python_interpreter = /path/to/python
    return config.get('python_interpreter', DEFAULT_PYTHON_INTERPRETER)


def _bdist_file():
    return max(Path.cwd().glob('dist/*.whl'))


def _prepare_zipapp(dest, bdist_file):
    # Prepare zipapp directory.
    try_delete(dest)
    Path(dest).mkdir()
    return subprocess.check_call([
        sys.executable, '-m', 'pip', 'install', '--target', dest, bdist_file
    ])


def version_from_bdist_file():
    return _bdist_file().name.replace('.tar.gz', '').split('-')[1]


def zipapp():
    """
    Build a zipapp for the project.

    dist() should be called before zipapp().
    """

    pyproject = toml.load('pyproject.toml')
    config = pyproject.get('tool', {}).get('bork', {})
    zipapp_cfg = config.get('zipapp', {})
    want_zipapp = zipapp_cfg.get('enabled', False)

    if not want_zipapp:
        return

    name = _package_name()
    dest = str(Path('build', 'zipapp'))
    version = version_from_bdist_file()
    main = zipapp_cfg['main']

    # Output file is dist/<package name>-<package version>.pyz.
    target = 'dist/{}-{}.pyz'.format(name, version)

    _prepare_zipapp(dest, _bdist_file())

    # The `compressed=True` kwarg was added to create_archive in Python 3.7.
    # For older versions, we print a warning.
    if sys.version_info >= (3, 7):
        kwargs = {'compressed': True}
    else:
        kwargs = {}
        logger().warning(
            'Creating compressed ZipApps requires Python 3.7 or newer. '
            "You're using and older version, so your ZipApp (.pyz) files may be larger."
        )

    # pylint has a false positive and thinks the `compressed` kwarg is passed
    # on Python 3.6, so we ignore that error.

    # pylint: disable=unexpected-keyword-arg
    Zipapp.create_archive(dest, target, _python_interpreter(config), main,
        **kwargs)
    # pylint: enable=unexpected-keyword-arg
    if not Path(target).exists():
        raise RuntimeError('Failed to build zipapp: {}'.format(target))
