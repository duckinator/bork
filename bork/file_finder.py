from pathlib import Path


def find_files(globs, service):
    files = []

    for glob in globs:
        matches = map(str, Path().glob(glob))
        files += list(matches)

    print('Uploading to {}:'.format(service))
    for filename in files:
        print('- {}'.format(filename))

    return files
