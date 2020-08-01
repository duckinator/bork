import json
from pathlib import Path
import subprocess
import urllib.request

import packaging.version

from .log import logger


class GithubApi:
    """
    Basic wrapper for the GitHub API.

    Usage:
        gh = GithubApi('duckinator', 'bork', '<token>')
        gh.create_release('TEST-RELEASE', assets={'dist/bork-4.0.5.pyz': 'bork.pyz'})
    """

    def __init__(self, owner, repo, project_name, token):
        self.owner = owner
        self.repo = repo
        self.token = token
        self.project_name = project_name
        self._last_release = None

    def publish(self, release):
        url = '/' + release['url'].split('/', 3)[3]
        return self._api_patch(url, {'draft': False})

    # pylint: disable=too-many-arguments,too-many-locals
    def create_release(self, tag_name, name=None, commitish=None, body=None, draft=True,
                       prerelease=None, assets=None):
        """
        `tag_name` is the name of the tag.
        `commitish` is a commit hash, branch, tag, etc.
        `body` is the body of the commit.
        `draft` indicates whether it should be a draft release or not.
        `prerelease` indicates whether it should be a prerelease or not.
        `assets` is a dict mapping local file paths to the uploaded asset name.
        """
        if commitish is None:
            commitish = self.run('git', 'rev-parse', 'HEAD')

        if body is None:
            body = '{repo} {tag}'

        if name is None:
            name = '{project_name} {tag}'

        if draft:
            draft_indicator = ' as a draft'
        else:
            draft_indicator = ''
        logger().info('Creating GitHub release %s%s. (commit=%s)', tag_name,
                      draft_indicator, commitish)

        if prerelease is None:
            prerelease = packaging.version.parse(tag_name).is_prerelease

        format_dict = {
            'project_name': self.project_name,
            'owner': self.owner,
            'repo': self.repo,
            'tag': tag_name,
            'tag_name': tag_name,
            'version': packaging.version.parse(tag_name).public,
        }

        # Don't fetch more data unless needed.
        if 'changelog' in body:
            format_dict['changelog'] = self.changelog()

        request = {
            'tag_name': tag_name,
            'target_commitish': commitish,
            'name': name.format(**format_dict),
            'body': body.format(**format_dict),
            'draft': draft,
            'prerelease': prerelease,
        }
        url = '/repos/{}/{}/releases'.format(self.owner, self.repo)
        response = self._api_post(url, request)

        upload_url = response['upload_url'].split('{?')[0]

        if assets:
            for local_file, asset_name in assets.items():
                self.add_release_asset(upload_url, local_file, asset_name)

        return response
    # pylint: enable=too-many-arguments,too-many-locals

    def changelog(self):
        prs = self._api_get(f'/repos/{self.owner}/{self.repo}/pulls?state=closed')
        prs = filter(self._relevant_to_changelog, prs)
        summaries = map(self._format_for_changelog, prs)
        return "\n".join(summaries)

    @staticmethod
    def _format_for_changelog(pr):
        return f'* {pr["title"]} (#{pr["number"]} by @{pr["user"]["login"]})'

    def _relevant_to_changelog(self, pr):
        if not pr or not pr['merged_at']:
            return False

        if pr['merged_at'] > self.last_release['created_at']:
            return True

        return False

    @property
    def last_release(self):
        if not self._last_release:
            self._last_release = self._api_get(
                f'/repos/{self.owner}/{self.repo}/releases')[0]
        return self._last_release

    def add_release_asset(self, upload_url, local_file, name):
        logger().info('Adding asset %s to release (original file: %s).',
                      name, local_file)

        data = Path(local_file).read_bytes()

        headers = {
            'Content-Type': 'application/octet-stream',
        }

        url = '{}?name={}'.format(upload_url, name)
        response = self._api_post(url, data, headers=headers, server='')
        return response

    @staticmethod
    def run(*command):
        return subprocess.check_output(command).decode().strip()

    # pylint: disable=too-many-arguments

    def _api_post(self, endpoint, data, headers=None, server=None, method=None):
        if method is None:
            method = 'POST'
        if headers is None:
            headers = {}
        if server is None:
            server = 'https://api.github.com'

        headers['Authorization'] = 'token ' + self.token
        headers['Accept'] = 'application/vnd.github.v3+json'

        if isinstance(data, (dict, list)):
            data = json.dumps(data).encode()

        req = urllib.request.Request(server + endpoint, data=data,
                                     headers=headers, method=method)
        logger().debug('%s %s', req.method, req.full_url)

        response = urllib.request.urlopen(req).read().decode()
        return json.loads(response)

    # pylint: enable=too-many-arguments

    def _api_get(self, endpoint, headers=None, server=None):
        return self._api_post(endpoint, None, headers, server, 'GET')

    def _api_patch(self, endpoint, data, headers=None, server=None):
        return self._api_post(endpoint, data, headers, server, 'PATCH')
