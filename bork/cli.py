"""Command-line interface for Bork.

Usage:

`bork COMMAND [OPTIONS] [ARGS]`

Options that exist for all commands include:

`--verbose`: enable verbose logging

`--debug`: enable even more verbose logging (sometimes too noisy to be helpful)

**Commands:**

"""

import inspect
import logging
import os
import sys

import click  # type: ignore
from click import BadParameter

from . import __version__
from . import api
from .log import logger


DOWNLOAD_SOURCES_STR = ' '.join(api.DOWNLOAD_SOURCES)


@click.group()
def cli():
    pass


@cli.command()
def aliases():
    """
    ### `bork aliases`

    Prints a list of aliases (configured via pyproject.toml).
    """
    alias_list = api.aliases()
    if len(alias_list.keys()) == 0:
        print('No aliases available.')
        return

    for key in alias_list.keys():
        print(key)


@cli.command()
def build():
    """
    ### `bork build`

    Build the project.
    """
    api.build()


@cli.command()
def clean():
    """
    ### `bork clean`

    Remove files created by `bork build`.
    """
    api.clean()


@cli.command()
@click.option('--files', default='*.pyz',
              help='Comma-separated list of filenames to download. Supports '
                   'wildcards (* = everything, ? = any single character).')
@click.option('--directory', default='downloads',
              help='Directory to save files in. Created if missing.')
@click.argument('package', nargs=1)
@click.argument('release_tag', nargs=1, default='latest')
def download(files, directory, package, release_tag):
    """
    ### `bork download [--files FILES] [--directory DIRECTORY] PACKAGE RELEASE`

    Download a release of the specified project.

    Arguments:
        --files=FILES:
            (default `*.pyz`)
            A comma-separated list of filenames to download.
            Supports wildcards (* = everything, ? = any single character).
        --directory=DIRECTORY:
            (default `downloads`)
            The directory to save files in. Created if missing.
        PACKAGE:
            The package to download. Of the format `SOURCE:PACKAGE_NAME`, where
            `PACKAGE_NAME` is the name of the package to download, and `SOURCE`
            is one of `gh`, `github`, `pypi`, or `testpypi`.
        RELEASE:
            The release or tag of the package that you want to download.
    """
    # NOTE: We change the order of the arguments here, to move away from
    #       what makes sense on a CLI interface to what makes sense in a
    #       Python interface.
    try:
        api.download(package, release_tag, files, directory)
    except ValueError as error:
        raise BadParameter(error) from error


@cli.command()
@click.option('--pypi-repository', default='pypi',
              help='Repository to use. Valid values are pypi, testpypi, or'
                   'anything defined in ".pypirc".')
@click.option('--test-pypi', is_flag=True, default=False,
              help='Release to test.pypi.org instead of pypi.org.\n'
                   'Equivalent to `--pypi-repository testpypi`.')
@click.option('--dry-run', is_flag=True, default=False,
              help="Don't actually release, just show what a release would do.")
def release(pypi_repository, test_pypi, dry_run):
    """
    ### `bork release [--pypi-repository=REPO | --test-pypi] [--dry-run]`

    Arguments:
        --pypi-repository=REPO:
            (default `pypi`)
            Repository to use. Valid values are pypi, testpypi, or anything
            defined in ".pypirc".

        --test-pypi:
            Equivalent to `--pypi-repository testpypi`

        --dry-run:
            Don't actually release, just show what a release would do.
    """
    if test_pypi:
        pypi_repository = 'testpypi'
    api.release(pypi_repository, dry_run)


@cli.command()
@click.argument('alias', nargs=1)
def run(alias):
    """
    ### `bork run NAME`

    Run the alias specified by NAME, as defined in pyproject.toml.
    """
    api.run(alias)


def main():
    if sys.version_info < (3, 8):
        print('ERROR: Bork requires Python 3.8 or newer', file=sys.stderr)

    verbose = '--verbose' in sys.argv
    if verbose:
        sys.argv.remove('--verbose')

    debug = '--debug' in sys.argv
    if debug:
        sys.argv.remove('--debug')

    if '--version' in sys.argv:
        print('bork v{}'.format(__version__))
        sys.exit()

    try:
        # pylint: disable=import-outside-toplevel
        import coloredlogs  # type: ignore
        # pylint: enable=import-outside-toplevel

        # Default to only printing WARNING and higher severity messages.
        log_level = logging.WARNING

        # If we got '--verbose', print INFO and higher severity messages.
        if verbose:
            log_level = logging.INFO

        # If we got '--debug', print DEBUG and higher severity messages.
        if debug:
            log_level = logging.DEBUG

        coloredlogs.install(
            level=log_level,
            fmt='%(name)s %(levelname)s %(message)s',
        )

    except ModuleNotFoundError:
        logging.basicConfig(
            level=logging.INFO if verbose else logging.WARNING,
            format='%(name)s %(levelname)s %(message)s',
        )

    try:
        cli()
    except RuntimeError as err:
        thrower = inspect.trace()[-1]
        log = logger(thrower)

        (log.exception if verbose else log.error)(str(err))

        sys.exit(1)


def zipapp_main():
    # If Bork is put in a zipapp, this allows scripts executed as subprocesses
    # to access pep517.compat.
    #
    # The problem area is the `import compat` line in pep517's _in_process.py.
    # https://github.com/pypa/pep517/blob/master/pep517/_in_process.py
    os.environ['PYTHONPATH'] = ':'.join([*sys.path, sys.argv[0] + '/pep517'])

    main()
