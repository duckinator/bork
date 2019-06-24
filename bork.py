#!/usr/bin/env python3

import configparser
from pathlib import Path
import sys
import zipapp

import pep517.build
import twine

# The "proper" way to handle the default would be to check python_requires
# in setup.cfg. But, since Bork needs Python 3, there's no point.
DEFAULT_PYTHON_INTERPRETER = "/usr/bin/env python3"

def print_help():
    print("Usage: bork build SOURCE_DIR")
    print("       bork clean SOURCE_DIR")
    print("       bork release [--pypi] [--github]")

def load_setup_cfg(source_dir):
    setup_cfg_path = Path(source_dir, 'setup.cfg').resolve()
    setup_cfg = configparser.ConfigParser()
    setup_cfg.read(setup_cfg_path)
    return setup_cfg


def build_pep517(args):
    source_dir = args[0]
    pep517.build.main(pep517.build.parser.parse_args(source_dir))

def build_zipapp(args):
    source_dir = args[0]
    config = load_setup_cfg(source_dir)
    name = config['metadata']['name']

    source = str(Path(source_dir, name))

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
    main = config['bork']['zipapp_entrypoint']

    zipapp.create_archive(source, target, interpreter, main)
    if not Path(target).exists():
        raise Exception("Failed to build zipapp: {}".format(target))

def build(args):
    if len(args) < 1:
        print_help()
        exit(1)

    build_pep517(args)
    build_zipapp(args)

def clean(args):
    if len(args) == 1:
        source_dir = args[0]
    else:
        source_dir = '.'

    # TODO: Delete ./build ./dist ./<name>.egg-info
    pass

def release(args):
    pass


def main(argv=None):
    if argv is None:
        argv = sys.argv

    if len(argv) < 2 or "-h" in argv or "--help" in argv:
        print_help()
        exit(1)

    command = argv[1]
    args = argv[2:]

    if command == "build":
        build(args)
    elif command == "build-pep517":
        build_pep517(args)
    elif command == "build-zipapp":
        build_zipapp(args)
    elif command == "clean":
        clean(args)
    elif command == "release":
        release(args)
    else:
        print_help()

if __name__ == "__main__":
    main()
