from bork.config import Config

def test_config_compat(project_src):
    "Check the new config model can validate known-good projects"
    assert Config.from_project(project_src)
