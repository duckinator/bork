from helpers import bork_cli


def test_cmd_aliases():
    result = bork_cli("aliases")
    assert result.exit_code == 0
    assert result.output == 'lint\ntest\ntest-fast\ntest-slow\n'
