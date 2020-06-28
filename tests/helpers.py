from click.testing import CliRunner  # noqa: I202
import bork.cli


def bork_cli(*args):
    runner = CliRunner()
    return runner.invoke(bork.cli.cli, args)
