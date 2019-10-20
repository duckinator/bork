from twine.cli import dispatch as twine_upload

from .asset_manager import download_assets
from .filesystem import find_files
from .log import logger
from .pypi_api import get_download_info


class PypiHandler:
    def __init__(self, download_url, upload_url):
        self.download_url = download_url
        self.upload_url = upload_url

    def upload(self, *globs, dry_run=False):
        files = find_files(globs)
        logger().info(
            "Uploading files to PyPI instance '%s': %s",
            self.upload_url,
            ', '.join(("'{}'".format(file) for file in files)),
        )

        if dry_run:
            logger().info('Skipping PyPI upload step since this is a dry run.')
        else:
            twine_upload(['upload', '--repository-url', self.upload_url, *files])

    def download(self, package, release, file_pattern, directory):
        asset_list = get_download_info(self.download_url, package, release,
                                       file_pattern)
        download_assets(asset_list, directory)


PRODUCTION = PypiHandler('https://pypi.org/simple/',
                         'https://upload.pypi.org/legacy/')
TESTING = PypiHandler('https://test.pypi.org/simple/',
                      'https://test.pypi.org/legacy/')
