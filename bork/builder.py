import zipapp

import pep517.build


# The "proper" way to handle the default would be to check python_requires
# in setup.cfg. But, since Bork needs Python 3, there's no point.
DEFAULT_PYTHON_INTERPRETER = "/usr/bin/env python3"


def dist():
    """Build the sdist and wheel distributions."""

    # We can use the pep517 library to add separate source and binary build
    # functions, but I'm leaving that alone unless someone asks for it.
    args = ['--source', '--binary']
    pep517.build.main(pep517.build.parser.parse_args(['.', *args]))


def zipapp():
    """Build a zipapp for the project."""

    config = load_setup_cfg()

    if 'metadata' not in config or 'name' not in config['metadata']:
        print("The [metadata] section of setup.cfg needs the 'name' key set.",
              file=sys.stderr)
        exit(1)

    name = config['metadata']['name']

    # The code is assumed to be in ./<name>
    source = str(Path(name))

    # When we have version info, use the following line instead:
    # target = "dist/{}-{}.pyz".format(name, version)
    target = "dist/{}.pyz".format(name)

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

    zipapp.create_archive(source, target, interpreter, main)
    if not Path(target).exists():
        raise Exception("Failed to build zipapp: {}".format(target))

