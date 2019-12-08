import inspect
import logging
import sys

import click
from click import BadParameter

from . import __version__
from . import api
from .log import logger


DOWNLOAD_SOURCES_STR = ' '.join(api.DOWNLOAD_SOURCES)


@click.group()
def cli():
    pass


@cli.command()
def build():
    api.build()


@cli.command()
def clean():
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
    # NOTE: We change the order of the arguments here, to move away from
    #       what makes sense on a CLI interface to what makes sense in a
    #       Python interface.
    try:
        api.download(package, release_tag, files, directory)
    except ValueError as error:
        raise BadParameter(error)


@cli.command()
@click.option('--test-pypi', is_flag=True, default=False,
              help='Release to test.pypi.org instead of pypi.org.')
@click.option('--dry-run', is_flag=True, default=False,
              help="Don't actually release, just show what a release would do.")
def release(test_pypi, dry_run):
    api.release(test_pypi, dry_run)


@cli.command()
@click.argument('alias', nargs=1)
def run(alias):
    api.run(alias)


def main():
    verbose = '--verbose' in sys.argv
    if verbose:
        sys.argv.remove('--verbose')

    if '--version' in sys.argv:
        print("bork v{}".format(__version__))
        sys.exit()

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
