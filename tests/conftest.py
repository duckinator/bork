import shutil
from pathlib import Path

import pytest

from helpers import check_run


def _url_name(url):
    return url.rsplit('/', 1)[1].removesuffix('.git')

@pytest.mark.network
@pytest.fixture(scope="session", ids=_url_name, params=(
    "https://github.com/astronouth7303/ppb-mutant.git",
    "https://github.com/duckinator/bork.git",
    "https://github.com/duckinator/emanate.git",
    "https://github.com/ppb/ppb-vector.git",
))
def project_src(request, tmp_path_factory):
    url = request.param
    dest = tmp_path_factory.mktemp(_url_name(url))
    check_run(['git', 'clone', '--depth', '1', url, dest])
    return dest


@pytest.fixture(scope="function")
def project(project_src, tmp_path):
    return shutil.copytree(project_src, tmp_path, dirs_exist_ok=True)
