from pathlib import Path

from twine.cli import dispatch as twine_upload

def upload(*globs):
    files = []

    for glob in globs:
        matches = map(str, Path().glob(glob))
        files += list(matches)

    print("")
    print("Uploading to PyPI:")
    for filename in files:
        print("- {}".format(filename))
    print("")

    twine_upload(["upload", *files])

