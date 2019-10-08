from distutils.version import LooseVersion
import fnmatch
import json
from urllib.request import urlopen

from .asset_manager import download_assets
from .log import logger
# from .filesystem import find_files


def upload(*globs, dry_run=False):
    # files = find_files(globs)
    # logger().info("Uploading files to Github: %s",
    #               ', '.join(("'{}'".format(file) for file in files)),
    # )
    #
    # if dry_run:
    #     logger().info('Skipping GitHub upload step since this is a dry run.')
    # else:
    #     pass

    raise NotImplementedError('github.upload() is not yet implemented')


def _relevant_asset(asset, file_pattern):
    file_patterns = file_pattern.split(',')
    for pattern in file_patterns:
        if fnmatch.fnmatch(asset['name'], pattern):
            return True
    return False


def _get_release_info(repo, name, draft=False, prerelease=False):
    if '/' not in repo:
        raise ValueError(
            "repo must be of format <user>/<repo>, got '{}'".format(repo),
        )

    log = logger()
    url = 'https://api.github.com/repos/{}/releases'.format(repo)
    req = urlopen(url).read().decode()
    data = json.loads(req)
    releases = []

    for release in data:
        if not draft and release['draft']:
            log.info("Discarding draft release '%s'", release['name'])
        elif not prerelease and release['prerelease']:
            log.info("Discarding prerelease '%s'", release['name'])
        else:
            releases.append(release)

    try:
        if name == 'latest':
            release = max(
                releases,
                key=lambda x: LooseVersion(x['tag_name'].lstrip('v')),
            )
            log.info("Selected release '%s' as latest", release['name'])
        else:
            release = list(filter(lambda x: x['tag_name'] == name, releases))[0]

    except (IndexError, ValueError) as e:
        raise RuntimeError("No such Github release: '{}'".format(name)) from e

    return release


def download(repo, release, file_pattern, directory):
    release_info = _get_release_info(repo, release, file_pattern)
    assets = filter(lambda x: _relevant_asset(x, file_pattern),
                    release_info['assets'])
    download_assets(assets, directory, url_key='browser_download_url')
