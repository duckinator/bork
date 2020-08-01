import os

import pytest
from helpers import bork_check, python_check, check_zipfile, check_tgz


@pytest.mark.network
def test_download(tmpdir):
    os.chdir(tmpdir)

    # Download a pyz file from GitHub, saved to ./downloads, and check
    # that it can be run with Python.
    bork_check("download", "gh:duckinator/emanate", "v7.0.0")
    python_check("downloads/emanate-7.0.0.pyz", "--help")

    # Download a pyz file for a specific version from GitHub, saved to ./bin
    bork_check("download", "gh:duckinator/emanate", "v7.0.0", "--directory", "bin/")
    python_check("bin/emanate-7.0.0.pyz", "--help")

    # Download a .tar.gz file from GitHub, saved to ./downloads
    bork_check("download",
               "gh:ppb/pursuedpybear", "v0.6.0",
               "--files", "*.tar.gz",
               "--directory", "downloads")
    assert check_tgz("downloads/ppb-0.6.0.tar.gz")

    # Download a .whl file from PyPi, and verify it's uncorrupted.
    bork_check("download", "pypi:emanate", "v6.0.0", "--files", "*.whl")
    assert check_zipfile("downloads/emanate-6.0.0-py3-none-any.whl")

    # Download a .whl file from PyPi's test instance, and verify it's uncorrupted.
    bork_check("download", "pypi-test:whaledo", "1.0.1", "--files", "*.whl")
    assert check_zipfile("downloads/whaledo-1.0.1-py3-none-any.whl")
