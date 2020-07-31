import json
from pathlib import Path
import subprocess
import urllib.request

from .log import logger


class GithubApi:
    """
    Basic wrapper for the GitHub API.

    Usage:
        gh = GithubApi('duckinator', 'bork', '<token>')
        gh.create_release('TEST-RELEASE', assets={'dist/bork-4.0.5.pyz': 'bork.pyz'})
    """

    def __init__(self, owner, repo, token):
        self.owner = owner
        self.repo = repo
        self.token = token

    def publish(self, release):
        url = '/' + release['url'].split('/', 3)[3]
        return self._api_patch(url, {'draft': False})

    # pylint: disable=too-many-arguments
    def create_release(self, tag_name, commitish=None, body=None, draft=True,
                       prerelease=False, assets=None):
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
            body = f'{self.repo} {tag_name}.'

        if draft:
            draft_indicator = ' as a draft'
        else:
            draft_indicator = ''
        logger().info('Creating GitHub release %s%s. (commit=%s)', tag_name,
                      draft_indicator, commitish)

        request = {
            'tag_name': tag_name,
            'target_commitish': commitish,
            'name': f'{self.repo} {tag_name}',
            'body': body,
            'draft': draft,
            'prerelease': prerelease,
        }
        url = '/repos/{}/{}/releases'.format(self.owner, self.repo)
        response = self._api_post(url, request)

        upload_url = response['upload_url'].split('{?')[0]

        if assets:
            for local_file, name in assets.items():
                self.add_release_asset(upload_url, local_file, name)

        return response
    # pylint: enable=too-many-arguments

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
