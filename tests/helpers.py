import os
import subprocess
import sys
import tarfile
import zipfile
from contextlib import contextmanager
from pathlib import Path

def check_tgz(path):
    assert tarfile.is_tarfile(path)
    # tarfile.open() throws an exception if it's not a tarfile or we used
    # the wrong mode.
    with tarfile.open(path, mode='r:gz') as _:
        pass
    return True


def check_zipfile(path):
    with zipfile.ZipFile(str(path)) as zf:
        bad_file = zf.testzip()
    assert bad_file is None
    return True


def _check_call(cmd, **kwargs):
    return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          text=True, check=True, **kwargs)


def check_run(*args):
    return _check_call(*args)


def python_check(*args):
    return _check_call([sys.executable, *args])


def bork_check(*args):
    return python_check("-m", "bork", *args)


@contextmanager
def chdir(path):
    cwd = Path.cwd()

    os.chdir(path)
    yield
    os.chdir(cwd)
