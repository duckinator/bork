"""Command-line interface for Bork.

Usage:

`bork COMMAND [OPTIONS] [ARGS]`

Options that exist for all commands include:

`--verbose`: enable verbose logging

`--debug`: enable even more verbose logging (sometimes too noisy to be helpful)

**Commands:**

"""

import argparse
import inspect
import logging
import sys

from . import __version__
from . import api
from .filesystem import load_pyproject
from .log import logger


def aliases(_args):
    """
    ### `bork aliases`

    Prints a list of aliases (configured via pyproject.toml).
    """
    alias_list = api.aliases()
    if len(alias_list.keys()) == 0:
        print('No aliases available.')
        return

    for key in alias_list.keys():
        print(key)


def build(args):
    """
    ### `bork build`

    Build the project.
    """

    pyproject = load_pyproject()
    config = pyproject.get('tool', {}).get('bork', {})
    zipapp_cfg = config.get('zipapp', {})
    zipapp_enabled = zipapp_cfg.get('enabled', False)

    api.build()

    if args.zipapp or zipapp_enabled:
        api.build_zipapp(args.zipapp_main)


def clean(_args):
    """
    ### `bork clean`

    Remove files created by `bork build`.
    """
    api.clean()


def download(args):
    """
    ### `bork download [--files FILES] [--directory DIRECTORY] PACKAGE RELEASE`

    Download a release of the specified project.

    Arguments:
        --files=FILES:
            (default `*.pyz`)
            A comma-separated list of filenames to download.
            Supports wildcards (* = everything, ? = any single character).
        --directory=DIRECTORY:
            (default `downloads`)
            The directory to save files in. Created if missing.
        PACKAGE:
            The package to download. Of the format `SOURCE:PACKAGE_NAME`, where
            `PACKAGE_NAME` is the name of the package to download, and `SOURCE`
            is one of `gh`, `github`, `pypi`, or `testpypi`.
        RELEASE:
            The release or tag of the package that you want to download.
    """
    files = args.files
    directory = args.directory
    package = args.PACKAGE
    release_tag = args.RELEASE

    if not sys.flags.dev_mode:
        # Avoid a double-warning if the API's deprecation was shown
        logging.warning("`bork download` is deprecated; its functionality has been split out into Homf")

    api.download(package, release_tag, files, directory)


def release(args):
    """
    ### `bork release [--pypi-repository=REPO | --test-pypi] [--dry-run]`

    Arguments:
        --pypi-repository=REPO:
            (default `pypi`)
            Repository to use. Valid values are pypi, testpypi, or anything
            defined in ".pypirc".

        --test-pypi:
            Equivalent to `--pypi-repository testpypi`

        --dry-run:
            Don't actually release, just show what a release would do.
    """
    pypi_repository = args.pypi_repository
    if args.test_pypi:
        pypi_repository = 'testpypi'
    api.release(pypi_repository, args.dry_run, args.github, args.pypi)


def run(args):
    """
    ### `bork run NAME`

    Run the alias specified by NAME, as defined in pyproject.toml.
    """
    api.run(args.ALIAS)


def _arg_parser():
    parser = argparse.ArgumentParser(
            prog="bork",
            description="A build and release tool for Python projects, with ZipApp support.")
    parser.add_argument("--version", action="store_true",
                        help="Print version information and exit.")
    parser.add_argument("--verbose", "--debug", action="store_true",
                        help="Enable verbose logging.")

    subparsers = parser.add_subparsers(title="Commands")
    aliasesp = subparsers.add_parser("aliases",
                                     help="Prints the aliases configured via pyproject.toml.")
    aliasesp.set_defaults(func=aliases)

    buildp = subparsers.add_parser("build", help="Build the project.")
    buildp.set_defaults(func=build)
    buildp.add_argument("--zipapp", action="store_true",
                        help="Always build a zipapp.")
    buildp.add_argument("--no-zipapp", dest="zipapp", action="store_false",
                        help="Never build to zipapp.")
    buildp.set_defaults(zipapp=None)
    buildp.add_argument("--zipapp-main", action="store",
                        help="Entrypoint for the ZipApp. Format is: module.submodule:function")
    buildp.set_defaults(zipapp_main=None)

    cleanp = subparsers.add_parser("clean", help="Remove files generated by `bork build`.")
    cleanp.set_defaults(func=clean)

    downloadp = subparsers.add_parser("download",
                                      help="Download a release of the specified project.")
    downloadp.add_argument("--files", action="store", default="*.pyz",
                          help="Comma-separated list of filenames to download."
                               "Supports wildcards (* = everything, ? = any single character).")
    downloadp.add_argument("--directory", action="store", default="downloads",
                           help="Directory to save files in. Created if missing. "
                                "(Default: `downloads`)")
    downloadp.add_argument("PACKAGE",
                           help="The package to download. Format: `SOURCE:PACKAGE_NAME`, where"
                                " `PACKAGE_NAME` is the name of the package to download, and "
                                "`SOURCE` is one of `gh`, `github`, `pypi`, or `testpypi`.")
    downloadp.add_argument("RELEASE", action="store", nargs='?', default="latest",
                           help="The release or tag to download.")
    downloadp.set_defaults(func=download)


    releasep = subparsers.add_parser("release", help="Publish a built project.")
    releasep.add_argument("--pypi-repository", default="pypi",
                         help="Repository to use. Valid values are pypi, "
                              "testpypi, or anything defined in '.pypirc'.")
    releasep.add_argument("--test-pypi", action="store_true",
                         help="Release to test.pypi.org instead of pypi.org.\n"
                              "Equivalent to '--pypi-repository testpypi'.")
    releasep.add_argument("--dry-run", action="store_true",
                         help="Don't actually release, just show what a release would do.")

    releasep.add_argument("--github", action="store_true",
                        help="Release to GitHub, ignoring pyproject.toml.")
    releasep.add_argument("--no-github", dest="github", action="store_false",
                        help="Don't release to GitHub, ignoring pyproject.toml.")
    releasep.set_defaults(github=None)

    releasep.add_argument("--pypi", action="store_true",
                        help="Release to PyPi, ignoring pyproject.toml.")
    releasep.add_argument("--no-pypi", dest="pypi", action="store_false",
                        help="Don't release to GitHub, ignoring pyproject.toml.")
    releasep.set_defaults(pypi=None)

    releasep.set_defaults(func=release)

    runp = subparsers.add_parser("run", help="Run the specified alias.")
    runp.add_argument("ALIAS")
    runp.set_defaults(func=run)

    return parser


def main(cmd_args=None):
    """
    Command-line entrypoint for bork.

    `cmd_args` should be either `None` or equivalent to `sys.argv[1:]`.
    """
    if sys.version_info < (3, 10):
        print('ERROR: Bork requires Python 3.10 or newer', file=sys.stderr)

    logging.captureWarnings(True)

    cmd_args = cmd_args or sys.argv[1:]
    if len(cmd_args) == 0:
        cmd_args = ["--help"]
    args = _arg_parser().parse_args(cmd_args)

    if args.version:
        print(f"bork v{__version__}")
        sys.exit()

    try:
        # pylint: disable=import-outside-toplevel
        import coloredlogs  # type: ignore
        # pylint: enable=import-outside-toplevel

        coloredlogs.install(
            level=logging.DEBUG if args.verbose else logging.INFO,
            fmt='%(name)s %(levelname)s %(message)s',
        )

    except ModuleNotFoundError:
        logging.basicConfig(
            level=logging.INFO if args.verbose else logging.WARNING,
            format='%(name)s %(levelname)s %(message)s',
        )

    try:
        args.func(args)
    except RuntimeError as err:
        thrower = inspect.trace()[-1]
        log = logger(thrower)

        (log.exception if args.verbose else log.error)(str(err))

        sys.exit(1)
