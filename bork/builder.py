from pathlib import Path
import subprocess
import sys
# Slight kludge so we can have a function named zipapp().
import zipapp as Zipapp  # noqa: N812

import build

from .filesystem import load_setup_cfg, load_pyproject, try_delete
# from .log import logger


# The "proper" way to handle the default would be to check python_requires
# in setup.cfg. But, since Bork needs Python 3, there's no point.
DEFAULT_PYTHON_INTERPRETER = '/usr/bin/env python3'


def dist():
    """Build the sdist and wheel distributions."""

    builder = build.ProjectBuilder('.')
    builder.build('sdist', './dist/')
    builder.build('wheel', './dist/')


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

    pyproject = load_pyproject()
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

    Zipapp.create_archive(dest, target, _python_interpreter(config), main,
        compressed=True)
    if not Path(target).exists():
        raise RuntimeError('Failed to build zipapp: {}'.format(target))
