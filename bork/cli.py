import sys

import click

from . import build as _build
from . import clean as _clean
from . import download as _download
from . import release as _release
from . import DOWNLOAD_SOURCES


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


# pylint: disable=redefined-outer-name
# NOTE: It's okay to redefine `release` in download(), since it doesn't
#       use release().

@cli.command()
@click.option('--files', default='*.pyz',
              help='Comma-separated list of filenames to download. Supports '
                   'wildcards (* = everything, ? = any single character).')
@click.option('--directory', default='downloads',
              help='Directory to save files in. Created if missing.')
@click.argument('package', nargs=1)
@click.argument('release', nargs=1, default='latest')
def download(files, directory, package, release):
    # NOTE: We change the order of the arguments here, to move away from
    #       what makes sense on a CLI interface to what makes sense in a
    #       Python interface.
    _download(package, release, files, directory)

# pylint: enable=redefined-outer-name


@cli.command()
@click.option('--test-pypi', is_flag=True, default=False,
              help='Release to test.pypi.org instead of pypi.org.')
@click.option('--dry-run', is_flag=True, default=False,
              help="Don't actually release, just show what a release would do.")
def release(test_pypi, dry_run):
    _release(test_pypi, dry_run)


def main():
    verbose = '--verbose' in sys.argv
    if verbose:
        sys.argv.remove('--verbose')

    try:
        cli()
    except Exception as err:  # pylint: disable=broad-except
        # NOTE: Catching something as general as Exception should be okay here.
        if verbose:
            raise err
        exit("bork: error: {}".format(str(err)))
