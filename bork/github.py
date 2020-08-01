import fnmatch
import json
from pathlib import Path
from urllib.request import urlopen

import packaging.version

from .asset_manager import download_assets
from .filesystem import find_files
from .github_api import GithubApi
from .log import logger


class GithubConfig:  # pylint: disable=too-few-public-methods
    def __init__(self, token: str, repository: str, project_name: str):
        owner, repo = repository.split('/')
        self.token = token
        self.owner = owner
        self.repo = repo

        if project_name is None:
            project_name = self.repo

        self.project_name = project_name


class GithubRelease:  # pylint: disable=too-many-instance-attributes
    # pylint: disable=too-many-arguments
    def __init__(self, config: GithubConfig,
                 tag: str, commitish: str = None,
                 body: str = None, globs=None,
                 dry_run=False, prerelease=None, strip_zipapp_version=False):
        self.log = logger()

        self.owner = config.owner
        self.repo = config.repo
        self.token = config.token
        self.project_name = config.project_name

        self.tag_name = tag
        self.commitish = commitish
        self.body = body

        if self.body is None:
            self.body = self.release_template()

        self.prerelease = prerelease

        self.globs = globs
        if self.globs is None:
            self.globs = []

        self.dry_run = dry_run
        self.strip_zipapp_version = strip_zipapp_version

        self.github = None
        self.release = None

        self.assets = self._build_asset_list(find_files(globs))
    # pylint: enable=too-many-arguments

    def _build_asset_list(self, files):
        results = {}
        for file_path in files:
            filename = file_path.split('/')[-1]
            if self.strip_zipapp_version and filename.endswith('.pyz'):
                asset_name = '-'.join(filename.split('-')[:-1]) + '.pyz'
            else:
                asset_name = filename
            results[file_path] = asset_name
        return results

    def prepare(self):
        self.log.info('Preparing release for GitHub.')

        for (filename, asset_name) in self.assets.items():
            self.log.info('- %s as %s', filename, asset_name)

        if self.dry_run:
            self.log.warning(
                'Skipping creating draft GitHub release since this is a dry run.')
            return

        self.github = GithubApi(self.owner, self.repo, self.project_name, self.token)
        self.release = self.github.create_release(
            self.tag_name, commitish=self.commitish, body=self.body,
            draft=True, prerelease=self.prerelease,
            assets=self.assets)

    def publish(self):
        if self.dry_run:
            self.log.warning(
                'Skipping publishing GitHub release since this is a dry run.')
            return

        self.github.publish(self.release)

    @staticmethod
    def release_template():
        release_template_path = Path('.github/BORK_RELEASE_TEMPLATE.md')
        if release_template_path.exists():
            return release_template_path.read_text()
        return None


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
                key=lambda x: packaging.version.parse(x['tag_name']).public,
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
