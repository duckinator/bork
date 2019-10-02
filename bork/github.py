import fnmatch
import json
from urllib.request import urlopen

from .asset_manager import download_assets
# from .filesystem import find_files


def upload(*globs, dry_run=False):
    # files = find_files(globs, 'GitHub')

    # if dry_run:
    #     print('NOTE: Skipping GitHub upload step since this is a dry run.')
    # else:
    #     pass

    raise NotImplementedError('github.upload() is not yet implemented')


def _relevant_asset(asset, file_pattern):
    file_patterns = file_pattern.split(',')
    for pattern in file_patterns:
        if fnmatch.fnmatch(asset['name'], pattern):
            return True
    return False


def _get_download_info(repo, release, file_pattern):
    if '/' not in repo:
        raise ValueError(
            "repo must be of format <user>/<repo>, got '{}'".format(repo),
        )

    url = 'https://api.github.com/repos/{}/releases'.format(repo)
    req = urlopen(url).read().decode()
    data = json.loads(req)

    if release == 'latest':
        release = sorted(data, key=lambda x: x['created_at'])[-1]
    else:
        release = list(filter(lambda x: x['tag_name'] == release, data))[0]

    all_assets = release['assets']

    assets = filter(lambda x: _relevant_asset(x, file_pattern), all_assets)

    return assets


def download(repo, release, file_pattern, directory):
    asset_list = _get_download_info(repo, release, file_pattern)
    download_assets(asset_list, directory, url_key='browser_download_url')
