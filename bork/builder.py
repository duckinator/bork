from pathlib import Path
import shutil
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


def version_from_sdist_file():
    sdist = max(Path.cwd().glob('dist/*.tar.gz')).name
    return sdist.replace('.tar.gz', '').split('-')[1]


def _prepare_zipapp_directory(source, dest, name):
    ignore = shutil.ignore_patterns('**/__pycache__/**')
    try_delete(dest)
    Path(dest).mkdir()
    realdest = Path(dest, name)
    shutil.copytree(source, realdest, ignore=ignore)

    return Path(realdest).is_dir()


def _zipapp_add_deps(dest):
    config = load_setup_cfg()
    deps = None
    if 'options' in config:
        options = config['options']
        if 'install_requires' in options:
            deps = options['install_requires'].strip().split('\n')
            deps = list(map(str.strip, deps))

    if not deps:
        return

    cmd = [sys.executable, '-m', 'pip', 'install', '--target', dest] + deps
    subprocess.check_call(cmd)


# BAD ASSUMPTION: We assume dist() is called before zipapp().
def zipapp():
    """Build a zipapp for the project."""

    pyproject = toml.load('pyproject.toml')
    config = pyproject.get('tool', {}).get('bork', {})
    zipapp_cfg = config.get('zipapp', {})
    want_zipapp = zipapp_cfg.get('enabled', False)

    if not want_zipapp:
        return

    setup_cfg = load_setup_cfg()

    if 'metadata' not in setup_cfg or 'name' not in setup_cfg['metadata']:
        raise RuntimeError(
            "The [metadata] section of setup.cfg needs the 'name' key set.",
        )

    name = setup_cfg['metadata']['name']

    # The code is assumed to be in ./<name>
    orig_source = str(Path(name))
    source = str(Path('build', 'zipapp'))

    version = version_from_sdist_file()

    # Output file is dist/<package name>-<package version>.pyz.
    target = 'dist/{}-{}.pyz'.format(name, version)

    # To override the default interpreter, add this to your project's setup.cfg:
    #
    # [bork]
    # python_interpreter = /path/to/python
    interpreter = config.get('python_interpreter', DEFAULT_PYTHON_INTERPRETER)

    # This is where GitHub issue #9 ("Allow specifying console_script
    # entrypoint") would likely be implemented.
    main = zipapp_cfg['main']

    _prepare_zipapp_directory(orig_source, source, name)
    _zipapp_add_deps(source)

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

    # pylint has a false positive and thinks the `compressed` kwarg is always passed.
    Zipapp.create_archive(source, target, interpreter, main, **kwargs)  # pylint: disable=unexpected-keyword-arg
    if not Path(target).exists():
        raise RuntimeError('Failed to build zipapp: {}'.format(target))
