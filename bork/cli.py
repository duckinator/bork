import inspect
import logging
import sys

import click
from click import BadParameter

from . import build as _build
from . import clean as _clean
from . import download as _download
from . import release as _release
from . import run as _run
from . import DOWNLOAD_SOURCES  # noqa: I100
from .log import logger


DOWNLOAD_SOURCES_STR = ' '.join(DOWNLOAD_SOURCES)


@click.group()
def cli():
    pass


@cli.command()
def build():
    _build()


@cli.command()
def clean():
    _clean()


@cli.command()
@click.option('--files', default='*.pyz',
              help='Comma-separated list of filenames to download. Supports '
                   'wildcards (* = everything, ? = any single character).')
@click.option('--directory', default='downloads',
              help='Directory to save files in. Created if missing.')
@click.argument('package', nargs=1)
@click.argument('release_tag', nargs=1, default='latest')
def download(files, directory, package, release_tag):
    # NOTE: We change the order of the arguments here, to move away from
    #       what makes sense on a CLI interface to what makes sense in a
    #       Python interface.
    try:
        _download(package, release_tag, files, directory)
    except ValueError as error:
        raise BadParameter(error)


@cli.command()
@click.option('--test-pypi', is_flag=True, default=False,
              help='Release to test.pypi.org instead of pypi.org.')
@click.option('--dry-run', is_flag=True, default=False,
              help="Don't actually release, just show what a release would do.")
def release(test_pypi, dry_run):
    _release(test_pypi, dry_run)


@cli.command()
@click.argument('alias', nargs=1)
def run(alias):
    _run(alias)


def main():
    verbose = '--verbose' in sys.argv
    if verbose:
        sys.argv.remove('--verbose')

    try:
        import coloredlogs  # pylint: disable=import-outside-toplevel
        coloredlogs.install(
            level=logging.INFO if verbose else logging.WARNING,
            fmt="%(name)s %(levelname)s %(message)s",
        )

    except ModuleNotFoundError:
        logging.basicConfig(
            level=logging.INFO if verbose else logging.WARNING,
            format="%(name)s %(levelname)s %(message)s",
        )

    try:
        cli()
    except RuntimeError as err:
        thrower = inspect.trace()[-1]
        log = logger(thrower)

        (log.exception if verbose else log.error)(str(err))

        sys.exit(1)
