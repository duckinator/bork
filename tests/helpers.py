import subprocess
import sys
import tarfile
import zipfile

from click.testing import CliRunner  # type: ignore
import bork.cli


def check_tgz(path):
    assert tarfile.is_tarfile(path)
    # tarfile.open() throws an exception if it's not a tarfile or we used
    # the wrong mode.
    tarfile.open(path, mode='r:gz')
    return True


def check_zipfile(path):
    zf = zipfile.ZipFile(str(path))
    bad_file = zf.testzip()
    assert bad_file is None
    return True


def bork_cli(*args):
    runner = CliRunner()
    return runner.invoke(bork.cli.cli, args)


def bork_check(*args):
    result = bork_cli(*args)
    assert result.exit_code == 0
    return result


def _check_call(cmd, **kwargs):
    # `universal_newlines` is the old name for the `text` kwarg.
    # Since we want 3.6 support, we use that instead.
    return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          universal_newlines=True, check=True, **kwargs)


def check_run(*args):
    return _check_call(*args)


def python_check(*args):
    return _check_call([sys.executable, *args])
