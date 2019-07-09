import click

from . import build as _build
from . import clean as _clean
from . import release as _release


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
@click.option('--dry-run', is_flag=True, default=False,
              help="Don't actually release, just show what a release would do.")
def release(dry_run):
    _release(dry_run=dry_run)


def main():
    cli()
