from click.testing import CliRunner
import bork.cli


def bork_cli(*args):
    runner = CliRunner()
    return runner.invoke(bork.cli.cli, args)
