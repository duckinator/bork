from pathlib import Path
import shutil

import pytest

from helpers import chdir, check_run


def _src_name(src):
    if isinstance(src, Path):
        return src.name

    _, name = src.rsplit("/", 1)
    return name.removesuffix(".git")


test_dir = Path(__file__).parent

@pytest.fixture(scope="session", ids=_src_name, params=(
    test_dir / 'fixtures' / 'minimal-package',
    test_dir / 'fixtures' / 'poetry-package',
    test_dir / 'fixtures' / 'hatch-package',
    pytest.param(Path(__file__).parent.parent, marks=pytest.mark.slow),  # bork's source tree
    ) + tuple(pytest.param(url, marks=(pytest.mark.network, pytest.mark.slow)) for url in (
    "https://github.com/astronouth7303/ppb-mutant.git",
    "https://github.com/duckinator/emanate.git",
    "https://github.com/duckinator/homf.git",
    "https://github.com/ppb/ppb-vector.git",
)))
def project_src(request, tmp_path_factory):
    """Provide a source tree, which is cached over the whole pytest run.

    This fixture is parameterized over all the source trees that are built during tests,
    making any test (or fixture) that uses it parameterized itself.
    """
    if isinstance(request.param, Path):
        return request.param

    url = request.param
    dest = tmp_path_factory.mktemp(_src_name(url))
    check_run(['git', 'clone', '--depth', '1', url, dest])
    return dest


@pytest.fixture(scope="function")
def project(project_src, tmp_path):
    """Provide a fresh copy of a source tree, which is discarded after the current test."""
    shutil.copytree(project_src, tmp_path, dirs_exist_ok=True)
    with chdir(tmp_path):
        yield tmp_path


@pytest.fixture
def tmppath(tmpdir):
    "Work around the incompatibility of `pytest.LocalPath` and `pathlib.Path`"
    return Path(tmpdir)
