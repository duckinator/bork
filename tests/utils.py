from contextlib import contextmanager
from pathlib import Path
import os

@contextmanager
def cd(d: Path, *, mkdir: bool = False):
    # TODO(nicoo) get that check working
    # if not d.is_dir() or (mkdir and not d.exists()):
    #     raise ValueError(f"cd: '{d}' is not a directory")

    prev_wd = Path.cwd()
    if mkdir:
        d.mkdir(exist_ok = True)

    try:
        os.chdir(d)
        yield
    finally:
        os.chdir(prev_wd)
