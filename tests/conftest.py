import shutil
import sys
from pathlib import Path

import pytest

from helpers import chdir, check_run


if sys.version_info >= (3, 9):
    removesuffix = str.removesuffix
else:
    def removesuffix(s: str, suffix: str) -> str:
        if not s.endswith(suffix):
            return s
        return s[:-len(suffix)]


def _src_name(src):
    if isinstance(src, Path):
        return src.name

    return removesuffix(src, '.git').rsplit('/', 1)[1]


# pylint: disable=redefined-outer-name
# would trigger on any fixture which uses another fixture defined in the same file

@pytest.fixture(scope="session", ids=_src_name, params=(
    Path(__file__).parent / 'fixtures' / 'minimal-package',
    ) + tuple(pytest.param(url, marks=pytest.mark.network) for url in (
    "https://github.com/astronouth7303/ppb-mutant.git",
    "https://github.com/duckinator/bork.git",
    "https://github.com/duckinator/emanate.git",
    "https://github.com/ppb/ppb-vector.git",
)))
def project_src(request, tmp_path_factory):
    if isinstance(request.param, Path):
        return request.param

    url = request.param
    dest = tmp_path_factory.mktemp(_src_name(url))
    check_run(['git', 'clone', '--depth', '1', url, dest])
    return dest


@pytest.fixture(scope="function")
def project(project_src, tmp_path):
    shutil.copytree(project_src, tmp_path, dirs_exist_ok=True)
    with chdir(tmp_path):
        yield tmp_path
