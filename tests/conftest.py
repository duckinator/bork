import shutil
from pathlib import Path

import pytest

from helpers import check_run


def _src_name(src):
    if isinstance(src, Path):
        return src.name

    return src.rsplit('/', 1)[1].removesuffix('.git')


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
    return shutil.copytree(project_src, tmp_path, dirs_exist_ok=True)
