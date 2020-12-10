import os
from pathlib import Path
from signal import Signals
import subprocess
import sys

import toml

from . import builder
from . import github
from . import pypi
from .filesystem import try_delete
from .log import logger


DOWNLOAD_SOURCES = {
    'gh': github,
    'github': github,
    'pypi': pypi.Downloader('pypi'),
    'testpypi': pypi.Downloader('testpypi'),
    'pypi-test': pypi.Downloader('testpypi'),  # for backwards compatibility
}


def aliases():
    pyproject = toml.loads(Path('pyproject.toml').read_text())
    return pyproject.get('tool', {}).get('bork', {}).get('aliases', {})


def build():
    builder.dist()
    builder.zipapp()


def clean():
    try_delete('./build')
    try_delete('./dist')
    for name in Path.cwd().glob('*.egg-info'):
        if name.is_dir():
            try_delete(name)


def download(package, release_tag, file_pattern, directory):
    if file_pattern is None or len(file_pattern) == 0:
        raise ValueError('file_pattern must be non-empty.')

    if ':' not in package:
        raise ValueError('Invalid package/repository -- no source given.')

    source, package = package.split(':')

    if source not in DOWNLOAD_SOURCES.keys():
        raise ValueError('Invalid package/repository -- unknown source given.')

    source = DOWNLOAD_SOURCES[source]
    source.download(package, release_tag, file_pattern, directory)


def release(repository_name, dry_run):
    pyproject = toml.load('pyproject.toml')
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
    pyproject = toml.load('pyproject.toml')

    try:
        command = pyproject['tool']['bork']['aliases'][alias]
    except KeyError as error:
        raise RuntimeError("No such alias: '{}'".format(alias)) from error

    logger().info("Running '%s'", command)

    try:
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
