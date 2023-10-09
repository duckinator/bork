from helpers import bork_check


def test_cmd_aliases():
    result = bork_check("aliases")
    assert result.stdout == 'lint\ntest\ntest-fast\ntest-slow\ndocs\ndocs-clean\n'
