import pytest
from helpers import chdir, bork_check, python_check, check_zipfile, check_tgz


@pytest.mark.network
def test_download_pyz(tmpdir):
    with chdir(tmpdir):
        # Download a pyz file from GitHub, saved to ./downloads, and check
        # that it can be run with Python.
        bork_check("download", "gh:duckinator/emanate", "v7.0.0")
        python_check("downloads/emanate-7.0.0.pyz", "--help")

        # Download a pyz file for a specific version from GitHub, saved to ./bin
        bork_check("download", "gh:duckinator/emanate", "v7.0.0", "--directory", "bin/")
        python_check("bin/emanate-7.0.0.pyz", "--help")

@pytest.mark.network
def test_download_tgz(tmpdir):
    with chdir(tmpdir):
        # Download a .tar.gz file from GitHub, saved to ./downloads
        bork_check("download",
                   "gh:ppb/pursuedpybear", "v0.6.0",
                   "--files", "*.tar.gz",
                   "--directory", "downloads")
        assert check_tgz("downloads/ppb-0.6.0.tar.gz")

@pytest.mark.network
@pytest.mark.parametrize("repo,pkg,version", (
    ("pypi", "emanate", "6.0.0"),
    ("pypi-test", "whaledo", "1.0.1")
))
def test_download_whl(tmpdir, repo, pkg, version):
    with chdir(tmpdir):
        # Download a .whl file from PyPi, and verify it's uncorrupted.
        bork_check("download", f"{repo}:{pkg}", version, "--files", "*.whl")
        assert check_zipfile(f"downloads/{pkg}-{version}-py3-none-any.whl")
