from bork.config import Config
from helpers import bork_check, python_check

def test_repo(project):
    bork_check('clean')
    bork_check('build')
    bork_check('release', '--dry-run')

    if not Config.from_project(project).bork.zipapp.enabled:
        return

    match tuple((project / "dist").glob("*.pyz")):
        case []:
            assert False, "No zipapp was produced"
        case [zipapp]:
            python_check(zipapp, "--version")
        case _:
            assert False, "Multiple zipapps were produced?  O_o"
