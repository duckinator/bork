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


@cli.command()
@click.option('--files', default='*.pyz',
              help='Comma-separated list of filenames to download. ' +
                   'Wildcards supported (* = everything, ? = any single ' +
                   ' character).')
@click.option('--directory', default='downloads',
              help='Directory to save files in. Created if missing.')
@click.argument('repo', nargs=1)
@click.argument('release', nargs=1, default='latest')
def download(files, directory, repo, release):
    # NOTE: We change the order of the arguments here, to move away from
    #       what makes sense on a CLI interface to what makes sense in a
    #       Python interface.
    _download(repo, release, files, directory)


@cli.command()
@click.option('--dry-run', is_flag=True, default=False,
              help="Don't actually release, just show what a release would do.")
def release(dry_run):
    _release(dry_run=dry_run)


def main():
    cli()
