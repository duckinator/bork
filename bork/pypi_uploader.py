from twine.cli import dispatch as twine_upload

def pypi_upload(*globs):
    files = []

    for glob in globs:
        matches = map(str, Path().glob(glob))
        files += list(matches)

    print("Uploading to PyPI:")
    for filename in files:
        print("- {}".format(filename))

    #twine(["upload", *files])

