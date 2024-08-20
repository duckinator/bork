from pathlib import Path
import shutil
import re


def find_files(globs):
    files = []

    for glob in globs:
        matches = map(str, Path().glob(glob))
        files += list(matches)

    return files

def try_delete(path):
    if Path(path).is_dir():
        shutil.rmtree(path)
    elif Path(path).exists():
        raise RuntimeError(f"'{path}' is not a directory")


_WHEEL_FILENAME_REGEX = re.compile(
    r'^(?P<distribution>.+)-(?P<version>.+)(-(?P<build>.+))?-(?P<pyversion>.+)-(?P<abi>.+)-(?P<platform>.+).whl$',
    re.VERBOSE,
)
def wheel_file_info(path):
    return re.match(_WHEEL_FILENAME_REGEX, Path(path).name).groupdict()
