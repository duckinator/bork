import configparser
from pathlib import Path

from twine.cli import dispatch as twine_dispatch  # type: ignore

from .asset_manager import download_assets
from .filesystem import find_files
from .log import logger
from .pypi_api import get_download_info


class Downloader:  # pylint: disable=too-few-public-methods
    # In the future, if we decide this should be public functionality,
    # this lets us choose a better key name with minimal impact.
    PYPIRC_KEY = '_bork-download-endpoint'

    PYPIRC_DEFAULTS = {
        'pypi': {
            PYPIRC_KEY: 'https://pypi.org/simple/',
        },
        'testpypi': {
            PYPIRC_KEY: 'https://test.pypi.org/simple/',
        },
    }

    def __init__(self, repository_name):
        self.repository_url = self._download_url(repository_name)

    def download(self, package, release, file_pattern, directory):
        asset_list = get_download_info(self.repository_url, package, release,
                                       file_pattern)
        download_assets(asset_list, directory)

    def _download_url(self, repository_name):
        path = Path('~/.pypirc').expanduser()
        config = configparser.ConfigParser()
        if path.exists():
            config.read(str(path))

        if repository_name in config:
            repo_config = config.get(repository_name, None)
            if self.PYPIRC_KEY in repo_config:
                return repo_config[self.PYPIRC_KEY]

        return self.PYPIRC_DEFAULTS[repository_name][self.PYPIRC_KEY]


def download(repository_name, package, release, file_pattern, directory):
    return Downloader(repository_name).download(package, release, file_pattern,
                                                directory)


def upload(repository_name, *globs, dry_run=False):
    files = find_files(globs)
    logger().info(
        "Uploading files to PyPI instance '%s': %s",
        repository_name,
        ', '.join(("'{}'".format(file) for file in files)),
    )

    if dry_run:
        logger().warning('Skipping PyPI upload step since this is a dry run.')
    else:
        twine_dispatch(['upload', '--repository', repository_name, *files])
