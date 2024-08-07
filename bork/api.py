from functools import partial
import os
from pathlib import Path
from signal import Signals
import subprocess
import sys
from warnings import warn

from . import builder
from .filesystem import try_delete, load_pyproject
from .log import logger


def aliases():
    """Returns a list of the aliases defined in pyproject.toml."""
    pyproject = load_pyproject()
    return pyproject.get('tool', {}).get('bork', {}).get('aliases', {})


def build():
    """Build the project."""
    builder.dist()

def build_zipapp(zipapp_main=None):
    """Build the project as a ZipApp."""
    builder.zipapp(zipapp_main)


def clean():
    """Removes artifacts generated by `bork.api.build()`.

    (Specifically: `./build`, `./dist`, and any `*.egg-info` files.)
    """
    try_delete('./build')
    try_delete('./dist')
    for name in Path.cwd().glob('*.egg-info'):
        if name.is_dir():
            try_delete(name)


def download(package, release_tag, file_pattern, directory):
    """Saves files from the designated package, to the specified directory.

    The format for `package` is `<SOURCE>:<NAME>`, where:

    - `<SOURCE>` is one of: `gh`/`github`, `pypi`, or `testpypi`.
    - `<NAME>` is the identifier for the package on the specified source.

    E.g., Bork would be `gh:duckinator/bork` or `pypi:bork`.

    **NOTE:** `pypi-test` is a deprecated alias of `testpypi`, and will be
    removed in a future version.

    Arguments:
        package:
            Package to download files for, in the format `<SOURCE>:<NAME>`.

        release_tag:
            The version or tag to download.

        file_pattern:
            Any files matching this pattern will be downloaded.

            (Wildcards: `*` matches anything, `?` matches any single character.)

        directory:
            The directory where files are saved.
            This directory is created, if needed.
    """
    from homf.api import github, pypi  # type: ignore

    warn(
        "`bork.api.download` has been split out into Homf",
        DeprecationWarning,
        stacklevel = 2,
    )

    if file_pattern is None or len(file_pattern) == 0:
        raise ValueError('file_pattern must be non-empty.')

    if ':' not in package:
        raise ValueError('Invalid package/repository -- no source given.')

    source, package = package.split(':', 1)

    match source:
        case 'github' | 'gh':
            download = github.download
        case 'pypi':
            download = pypi.download
        case 'testpypi' | 'pypi-test':
            download = partial(pypi.download, repository_url = "https://test.pypi.org/simple/")
        case _:
            raise ValueError('Invalid package/repository -- unknown source given.')

    download(package, release_tag, file_pattern, directory) # type:ignore


def release(repository_name, dry_run, github_release_override=None, pypi_release_override=None):
    """Uploads build artifacts to a PyPi instance or GitHub, as configured
    in pyproject.toml.

    Arguments:
        repository_name:
            The name of the PyPi repository. (You probably want 'pypi'.)

        dry_run:
            If True, don't actually release, just show what a release would do.

        github_release_override:
            If True, enable GitHub releases; if False, disable GitHub releases;
            if None, respect the configuration in pyproject.toml.

        py_release_override:
            If True, enable PyPi releases; if False, disable PyPi releases;
            if None, respect the configuration in pyproject.toml.
    """
    from . import github, pypi
    pyproject = load_pyproject()
    bork_config = pyproject.get('tool', {}).get('bork', {})
    release_config = bork_config.get('release', {})
    github_token = os.environ.get('BORK_GITHUB_TOKEN', None)
    try:
        version = builder.version_from_bdist_file()
    except builder.NeedsBuildError:
        raise RuntimeError("No wheel files found. Please run 'bork build' first.")

    project_name = pyproject.get('project', {}).get('name', None)

    strip_zipapp_version = release_config.get('strip_zipapp_version', False)
    globs = release_config.get('github_release_globs', ['./dist/*.pyz'])

    release_to_github = release_config.get('github', False)
    release_to_pypi = release_config.get('pypi', True)

    if github_release_override is not None:
        release_to_github = github_release_override

    if pypi_release_override is not None:
        release_to_pypi = pypi_release_override

    if not release_to_github and not release_to_pypi:
        raise RuntimeError('Configured to release to neither PyPi nor GitHub?')

    if release_to_github:
        github_repository = release_config.get('github_repository', None)

        if github_token is None:
            logger().error('No GitHub token specified. Use the BORK_GITHUB_TOKEN '
                'environment variable to set it.')

            if dry_run:
                logger().error('When not using --dry-run, this error is fatal.')
            else:
                sys.exit(1)

        config = github.GithubConfig(github_token, github_repository, project_name)
        github_release = github.GithubRelease(
            config, tag=f'v{version}', commitish=None, body=None,
            globs=globs,
            dry_run=dry_run, strip_zipapp_version=strip_zipapp_version)
        github_release.prepare()

    if release_to_pypi:
        pypi.upload(repository_name, './dist/*.tar.gz', './dist/*.whl',
                    dry_run=dry_run)

    if release_to_github:
        github_release.publish()


def run(alias):
    """Run the alias specified by `alias`, as defined in pyproject.toml."""
    pyproject = load_pyproject()

    try:
        commands = pyproject['tool']['bork']['aliases'][alias]
    except KeyError as error:
        raise RuntimeError(f"No such alias: '{alias}'") from error

    logger().info("Running '%s'", commands)

    if isinstance(commands, str):
        commands = [commands]
    elif isinstance(commands, list):
        pass
    else:
        raise TypeError(f"commands must be str or list, was {type(commands)}")

    try:
        for command in commands:
            print(command)
            subprocess.run(command, check=True, shell=True)

    except subprocess.CalledProcessError as error:
        if error.returncode < 0:
            signal = Signals(- error.returncode)
            msg = f"command '{error.cmd}' exited due to signal {signal.name} ({signal.value})"

        else:
            msg = f"bork: command '{error.cmd}' exited with error code {error.returncode}"

        raise RuntimeError(msg) from error
