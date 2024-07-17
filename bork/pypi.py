import configparser
from pathlib import Path

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
            repo_config = config[repository_name]
            if self.PYPIRC_KEY in repo_config:
                return repo_config[self.PYPIRC_KEY]

        return self.PYPIRC_DEFAULTS[repository_name][self.PYPIRC_KEY]


def download(repository_name, package, release, file_pattern, directory):
    return Downloader(repository_name).download(package, release, file_pattern,
                                                directory)


class Uploader:
    PYPI_ENDPOINT = "https://upload.pypi.org/legacy/"
    TESTPYPI_ENDPOINT = "https://test.pypi.org/legacy/"

    def __init__(self, files, repository=None):
        if repository == "pypi" or repository is None:
            repository = self.PYPI_ENDPOINT
        elif repository == "testpypi":
            repository = self.TESTPYPI_ENDPOINT
        elif repository.startswith("http://") or repository.startswith("https://"):
            pass # Everything is fine.
        else:
            logger().error("Only the 'pypi' and 'testpypi' repository shorthands are supported.")
            logger().error("Please provide a full URL for custom endpoints, such as <https://pypi.example.org/legacy/>.")
            logger().error("Please open an issue at https://github.com/duckinator/bork if you need help.")
            exit(1)

        if not files:
            logger().error("No files to upload?")
            exit(1)

        self.files = files
        self.repository = repository

    def upload(self, dry_run=True):
        msg_prefix = "Uploading"
        if dry_run:
            logger().warn("Skipping PyPi release since this is a dry run.")
            msg_prefix = "Pretending to upload"

        logger().info("%s %i files to PyPi repository '%s':", msg_prefix, len(self.files), self.repository)
        for file in self.files:
            logger().info("- %s %s", file, "(skipping for dry run)" if dry_run else "")


def upload(repository_name, *globs, dry_run=False):
    files = find_files(globs)
    Uploader(files, repository_name).upload(dry_run)
