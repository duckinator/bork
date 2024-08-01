from pathlib import Path
from typing import Optional

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
                 tag: str, commitish: Optional[str] = None,
                 body: Optional[str] = None, globs=None,
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
            return release_template_path.read_text(encoding='utf-8')
        return None
