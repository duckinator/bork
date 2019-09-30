import os
from pathlib import Path
import sys
import toml

from . import builder
from . import github
from . import pypi
from .filesystem import try_delete


DOWNLOAD_SOURCES = {
    'gh': github,
    'github': github,
    'pypi': pypi.PRODUCTION,
    'pypi-test': pypi.TESTING,
}


def build():
    pyproject = toml.load('pyproject.toml')
    config = pyproject.get('tool', {}).get('bork', {})
    zipapp = config.get('zipapp', {})
    want_zipapp = zipapp.get('enabled', False)

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


def run(alias):
    pyproject = toml.load('pyproject.toml')
    config = pyproject.get('tool', {}).get('bork', {})
    aliases = config.get('aliases', {})

    if alias not in aliases.keys():
        sys.exit("bork: no such alias: '{}'".format(alias))

    command = aliases[alias]
    os.system(command)
