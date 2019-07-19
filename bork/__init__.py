from pathlib import Path

from . import builder
from . import github
from . import pypi
from .filesystem import load_setup_cfg, try_delete


DOWNLOAD_SOURCES = {
    'gh': github,
    'github': github,
    'pypi': pypi.PRODUCTION,
    'pypi-test': pypi.TESTING,
}


def build():
    config = load_setup_cfg()
    if 'bork' in config:
        config = config['bork']

        if 'zipapp' in config:
            want_zipapp = config['zipapp'].lower() == 'true'
        else:
            want_zipapp = 'zipapp_main' in config
    else:
        want_zipapp = False

    builder.dist()

    if want_zipapp:
        builder.zipapp()


def clean():
    try_delete("./build")
    try_delete("./dist")
    for name in Path.cwd().glob('*.egg-info'):
        if name.is_dir():
            try_delete(name)


def download(package, release_tag, file_pattern, directory):
    if file_pattern is None or len(file_pattern) == 0:
        raise Exception('--files requires a value.')

    if ':' not in package:
        raise Exception('Invalid package/repository -- no source given.')

    source, package = package.split(':')

    if source not in DOWNLOAD_SOURCES.keys():
        raise Exception('Invalid package/repository -- unknown source given.')

    source = DOWNLOAD_SOURCES[source]
    source.download(package, release_tag, file_pattern, directory)


def release(test_pypi, dry_run):
    if test_pypi:
        pypi_instance = pypi.TESTING
    else:
        pypi_instance = pypi.PRODUCTION
    pypi_instance.upload('./dist/*.tar.gz', './dist/*.whl', dry_run=dry_run)

    print('')
    print('')

    # if 'github' in args:
    #     github.upload('./dist/*.pyz', dry_run=dry_run)
