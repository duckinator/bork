from twine.cli import dispatch as twine_upload
from . import file_finder


def upload(dry_run=False, *globs):
    files = file_finder.find_files(globs, 'PyPI')

    if dry_run:
        print('NOTE: Skipping PyPI upload step since this is a dry run.')
    else:
        twine_upload(["upload", *files])
