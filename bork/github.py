import fnmatch
import json
from pathlib import Path
from urllib.request import urlopen
import sys

# from .filesystem import find_files


def upload(*globs, dry_run=False):
    # files = find_files(globs, 'GitHub')

    # if dry_run:
    #     print('NOTE: Skipping GitHub upload step since this is a dry run.')
    # else:
    #     pass

    raise NotImplementedError('github_uploader.upload()')


def _relevant_asset(asset, file_pattern):
    file_patterns = file_pattern.split(',')
    for pattern in file_pattern:
        if fnmatch.fnmatch(asset['name'], pattern):
            return True
    return False


def _get_download_info(repo, release, file_pattern):
    if '/' not in repo:
        raise Exception('repo must be of format <user>/<repo>')

    url = 'https://api.github.com/repos/{}/releases'.format(repo)
    req = urlopen(url).read().decode()
    data = json.loads(req)

    if release == 'latest':
        current_release = sorted(data, key=lambda x: x['created_at'])[-1]
    else:
        current_release = list(filter(lambda x: x['tag_name'] == release, data))[0]

    all_assets = current_release['assets']

    assets = filter(lambda x: _relevant_asset(x, file_pattern), all_assets)

    return assets


def download(repo, release, file_pattern, directory):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)

    asset_list = _get_download_info(repo, release, file_pattern)

    for asset in asset_list:
        name = asset['name']
        url = asset['url']
        path = directory / name

        contents = urlopen(url).read()

        path.write_bytes(contents)
        print(str(path))
