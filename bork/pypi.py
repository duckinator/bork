from twine.cli import dispatch as twine_upload
from .asset_manager import download_assets
from .filesystem import find_files
from .pypi_api import get_download_info


def upload(*globs, dry_run=False):
    files = find_files(globs, 'PyPI')

    if dry_run:
        print('NOTE: Skipping PyPI upload step since this is a dry run.')
    else:
        twine_upload(["upload", *files])


def download(package, release, file_pattern, directory):
    base_url = 'https://pypi.org/simple'
    asset_list = get_download_info(base_url, package, release, file_pattern)
    download_assets(asset_list, directory)
