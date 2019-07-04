import configparser
from pathlib import Path
import shutil
import sys
import zipapp

import pep517.build

from . import github_uploader
from . import pypi_uploader

# The "proper" way to handle the default would be to check python_requires
# in setup.cfg. But, since Bork needs Python 3, there's no point.
DEFAULT_PYTHON_INTERPRETER = "/usr/bin/env python3"


def load_setup_cfg():
    setup_cfg = configparser.ConfigParser()
    setup_cfg.read('setup.cfg')
    return setup_cfg

def build_dist():
    """Build the sdist and wheel distributions."""
    # TODO: Determine what can be passed via `args`, and expose it in a nicer API.
    args = []
    pep517.build.main(pep517.build.parser.parse_args('.', *args))

# FIXME: zipapps are broken as fuck.
def build_zipapp():
    """Build a zipapp for the project."""

    if not 'metadata' in config or not 'name' in config['metadata']:
        print("The [metadata] section of setup.cfg needs to have the 'name' key set.", file=sys.stderr)
        exit(1)

    config = load_setup_cfg()
    name = config['metadata']['name']

    # The code is assumed to be in ./<name>
    source = str(Path(name))

    # TODO: Get version info -- this is more complex, since it can be in many places.
    #target = "dist/{}-{}.pyz".format(name, version)
    target = "dist/{}.pyz".format(name)

    # To override the default interpreter, add this to your project's setup.cfg:
    #
    # [bork]
    # python_interpreter = /path/to/python
    if 'bork' in config and 'python_interpreter' in config['bork']:
        interpreter = config['bork']['python_interpreter']
    else:
        interpreter = DEFAULT_PYTHON_INTERPRETER

    # TODO: Allow the ability to specify which console_script entrypoint to
    #       use, instead of duplicating it.
    main = config['bork']['zipapp_main']

    zipapp.create_archive(source, target, interpreter, main)
    if not Path(target).exists():
        raise Exception("Failed to build zipapp: {}".format(target))

def build():
    config = load_setup_cfg()
    if 'bork' in config:
        config = config['bork']
        want_zipapp = (config.get('zipapp', 'false').lower() == 'true') or ('zipapp_main' in config.keys())
    else:
        want_zipapp = False

    build_dist()

    if want_zipapp:
        raise Exception("zipapp builds are broken as hell, sorry. :(")
        #build_zipapp()

def _try_delete(path):
    if Path(path).is_dir():
        shutil.rmtree(path)
    elif Path(path).exists():
        raise Exception("{} is not a directory".format(path))

def clean():
    config = load_setup_cfg()
    name = config['metadata']['name']

    _try_delete("./build")
    _try_delete("./dist")
    _try_delete("./{}.egg-info".format(name))

def release():
    pypi_uploader.upload('./dist/*.tar.gz', './dist/*.whl')

    #if 'github' in args:
    #    github_uploader.upload('./dist/*.pyz')
