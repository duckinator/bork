from pathlib import Path
import shutil

try:
    import tomllib
except ImportError:
    import toml as tomllib  # type: ignore


def load_pyproject():
    """
    Loads the pyproject.toml data.

    Will synthesize data if a legacy setuptools project is detected.
    """
    try:
        pyproject = Path.cwd() / 'pyproject.toml'
        return tomllib.loads(pyproject.read_text())  # Mildly inefficient, but portable

    except FileNotFoundError:
        if Path('setup.py').exists() or Path('setup.cfg').exists():
            # Legacy project, use setuptools' legacy backend
            # (This backend is specified in PEP517)
            return {
                'build-system': {
                    'build-backend': 'setuptools.build_meta:__legacy__',
                    'requires': ['setuptools>=42'],
                },
            }
        # Can't figure out what kind of project it is.
        raise


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
