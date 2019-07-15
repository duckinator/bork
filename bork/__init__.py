from pathlib import Path

from . import builder
from . import github
from . import pypi
from .filesystem import load_setup_cfg, try_delete


DOWNLOAD_SOURCES = {
    'gh': github,
    'github': github,
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


def download(repo, release, file_pattern, directory):
    if file_pattern is None or len(file_pattern) == 0:
        raise Exception('--files requires a value.')

    if ':' not in repo:
        raise Exception('Invalid repository -- no source specified.')

    source, repo = repo.split(':')

    if source not in DOWNLOAD_SOURCES.keys():
        raise Exception('Invalid repository -- invalid source specified.')

    source = DOWNLOAD_SOURCES[source]
    source.download(repo, release, file_pattern, directory)


def release(dry_run=False):
    pypi.upload('./dist/*.tar.gz', './dist/*.whl', dry_run=dry_run)

    print('')
    print('')

    # if 'github' in args:
    #     github.upload('./dist/*.pyz', dry_run=dry_run)
