from distutils.version import LooseVersion
import fnmatch
import json
from urllib.request import urlopen

from .asset_manager import download_assets
from .filesystem import find_files
# from .github_api import GithubApi
from .log import logger


def upload(*globs, dry_run=False, strip_zipapp_version=False):
    log = logger()

    files = find_files(globs)

    log.info('Uploading files to Github.')
    for filename in files:
        if strip_zipapp_version and filename.endswith('.pyz'):
            dest_filename = '-'.join(filename.split('-')[:-1]) + '.pyz'
            log.info('- %s as %s', filename, dest_filename)
        else:
            dest_filename = filename
            log.info('- %s', filename)

    if dry_run:
        log.warning('Skipping GitHub upload step since this is a dry run.')
        return

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
    releases = json.loads(req)

    try:
        if name == 'latest':
            # Filter out prereleases and drafts (unless specified in the arguments)
            releases = (
                r for r in releases
                if (draft or not r['draft'])
                and (prerelease or not r['prerelease'])  # noqa: W503
            )
            # Find the latest
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
