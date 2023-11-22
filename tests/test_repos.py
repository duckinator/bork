import pytest
from helpers import bork_check

# pylint: disable=unused-argument
# the `project` feature is used implicitly, as it changes the working directory

@pytest.mark.slow
def test_repo(project):
    bork_check('clean')
    bork_check('build')
    bork_check('release', '--dry-run')
