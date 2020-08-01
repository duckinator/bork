import os
from pathlib import Path

import pytest
from helpers import bork_check, check_run


def _repo_test(tmpdir, repo):
    os.chdir(tmpdir)
    check_run(['git', 'clone', '--depth', '1', repo, str(Path(tmpdir, 'repo'))])
    os.chdir('repo')
    bork_check('clean')
    bork_check('build')
    bork_check('release', '--dry-run')


@pytest.mark.network
@pytest.mark.slow
def test_repo_ppb_vector(tmpdir):
    _repo_test(tmpdir, 'https://github.com/ppb/ppb-vector.git')


@pytest.mark.network
@pytest.mark.slow
def test_repo_emanate(tmpdir):
    _repo_test(tmpdir, 'https://github.com/duckinator/emanate.git')


@pytest.mark.network
@pytest.mark.slow
def test_repo_bork(tmpdir):
    _repo_test(tmpdir, 'https://github.com/duckinator/bork.git')


@pytest.mark.network
@pytest.mark.slow
def test_repo_ppb_mutant(tmpdir):
    _repo_test(tmpdir, 'https://github.com/astronouth7303/ppb-mutant.git')
