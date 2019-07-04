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
def release():
    _release()

def main():
    cli()
