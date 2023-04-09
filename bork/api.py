import os
from pathlib import Path
from signal import Signals
import subprocess
import sys

import pep517  # type:ignore

from . import builder
from . import github
from . import pypi
from .filesystem import try_delete, load_pyproject
from .log import logger


DOWNLOAD_SOURCES = {
    'gh': github,
    'github': github,
    'pypi': pypi.Downloader('pypi'),
    'testpypi': pypi.Downloader('testpypi'),
    'pypi-test': pypi.Downloader('testpypi'),  # for backwards compatibility
}


def aliases():
    """Returns a list of the aliases defined in pyproject.toml."""
    pyproject = load_pyproject()
    return pyproject.get('tool', {}).get('bork', {}).get('aliases', {})


def build():
    """Build the project."""
    try:
        builder.dist()
        builder.zipapp()

    except FileNotFoundError as e:
        if e.filename != 'pyproject.toml':
            raise e

        setup = lambda ext: Path.cwd() / f"setup.{ext}"

        if setup("cfg").exists() or setup("py").exists():
            msg = """If you use setuptools, the following should be sufficient:

	[build-system]
	requires = ["setuptools > 42", "wheel"]
	build-backend = "setuptools.build_meta" """

        else:
            msg = "Please refer to your build system's documentation."

        logger().error(
            "You need a 'pyproject.toml' file describing which buildsystem to "
            "use, per PEP 517. %s", msg
        )

        raise e


def clean():
    """Removes artifacts generated by `bork clean`.

    (Specifically: `./build`, `./dist`, and any `*.egg-info` files.)
    """
    try_delete('./build')
    try_delete('./dist')
    for name in Path.cwd().glob('*.egg-info'):
        if name.is_dir():
            try_delete(name)


def dependencies():
    """Returns the list of dependencies for the project."""
    return pep517.meta.load('.').metadata.get_all('Requires-Dist')


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
    if file_pattern is None or len(file_pattern) == 0:
        raise ValueError('file_pattern must be non-empty.')

    if ':' not in package:
        raise ValueError('Invalid package/repository -- no source given.')

    source, package = package.split(':')

    if source not in DOWNLOAD_SOURCES.keys():
        raise ValueError('Invalid package/repository -- unknown source given.')

    downloader = DOWNLOAD_SOURCES[source]
    downloader.download(package, release_tag, file_pattern, directory) # type:ignore


def release(repository_name, dry_run):
    """Uploads build artifacts to a PyPi instance or GitHub, as configured
    in pyproject.toml.

    Arguments:
        repository_name:
            The name of the PyPi repository. (You probably want 'pypi'.)

        dry_run:
            If True, don't actually release, just show what a release would do.
    """
    pyproject = load_pyproject()
    bork_config = pyproject.get('tool', {}).get('bork', {})
    release_config = bork_config.get('release', {})
    github_token = os.environ.get('BORK_GITHUB_TOKEN', None)
    version = builder.version_from_bdist_file()

    project_name = bork_config.get('project_name', None)

    strip_zipapp_version = release_config.get('strip_zipapp_version', False)
    globs = release_config.get('github_release_globs', ['./dist/*.pyz'])

    release_to_github = release_config.get('github', False)
    release_to_pypi = release_config.get('pypi', True)

    if not release_to_github and not release_to_pypi:
        print('Configured to release to neither PyPi nor GitHub?')

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
        raise RuntimeError("No such alias: '{}'".format(alias)) from error

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
            msg = "command '{}' exited due to signal {} ({})".format(
                error.cmd, signal.name, signal.value,
            )

        else:
            msg = "bork: command '{}' exited with error code {}".format(
                error.cmd, error.returncode,
            )

        raise RuntimeError(msg) from error
