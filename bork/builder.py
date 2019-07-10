from pathlib import Path
import shutil
import subprocess
import sys
# Slight kludge so we can have a function named zipapp().
import zipapp as Zipapp

import pep517.build

from .filesystem import load_setup_cfg, try_delete


# The "proper" way to handle the default would be to check python_requires
# in setup.cfg. But, since Bork needs Python 3, there's no point.
DEFAULT_PYTHON_INTERPRETER = "/usr/bin/env python3"


def dist():
    """Build the sdist and wheel distributions."""

    # We can use the pep517 library to add separate source and binary build
    # functions, but I'm leaving that alone unless someone asks for it.
    args = ['--source', '--binary']
    pep517.build.main(pep517.build.parser.parse_args(['.', *args]))


def version_from_sdist_file():
    sdist = sorted(Path.cwd().glob('dist/*.tar.gz'))[-1].name
    sdist = sdist.replace('.tar.gz', '')
    sdist = sdist.split('-')[1]
    return sdist


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
            deps = options['install_requires'].strip().split("\n")
            deps = list(map(str.strip, deps))

    if not deps:
        return

    cmd = [sys.executable, '-m', 'pip', 'install', '--target', dest] + deps
    subprocess.check_call(cmd)


# BAD ASSUMPTION: We assume dist() is called before zipapp().
def zipapp():
    """Build a zipapp for the project."""

    config = load_setup_cfg()

    if 'metadata' not in config or 'name' not in config['metadata']:
        print("The [metadata] section of setup.cfg needs the 'name' key set.",
              file=sys.stderr)
        exit(1)

    name = config['metadata']['name']

    # The code is assumed to be in ./<name>
    orig_source = str(Path(name))
    source = str(Path('build', 'zipapp'))

    version = version_from_sdist_file()

    # Output file is dist/<package name>-<package version>.pyz.
    target = "dist/{}-{}.pyz".format(name, version)

    # To override the default interpreter, add this to your project's setup.cfg:
    #
    # [bork]
    # python_interpreter = /path/to/python
    if 'bork' in config and 'python_interpreter' in config['bork']:
        interpreter = config['bork']['python_interpreter']
    else:
        interpreter = DEFAULT_PYTHON_INTERPRETER

    # This is where GitHub issue #9 ("Allow specifying console_script
    # entrypoint") would likely be implemented.
    main = config['bork']['zipapp_main']

    _prepare_zipapp_directory(orig_source, source, name)
    _zipapp_add_deps(source)

    Zipapp.create_archive(source, target, interpreter, main)
    if not Path(target).exists():
        raise Exception("Failed to build zipapp: {}".format(target))
