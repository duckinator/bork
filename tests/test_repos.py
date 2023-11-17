import os

import pytest
from helpers import bork_check


@pytest.mark.slow
def test_repo(project):
    os.chdir(project)
    bork_check('clean')
    bork_check('build')
    bork_check('release', '--dry-run')
