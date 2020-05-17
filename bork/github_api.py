import json
from pathlib import Path
import subprocess
import urllib

from .log import logger


class GithubApi:
    def __init__(self, owner, repo, token):
        self.owner = owner
        self.repo = repo
        self.token = token

    def create_release_with_file(self, tag_name, commitish, local_file,
                                 remote_file):
        response1 = self.create_release(tag_name, commitish)
        upload_url = json.loads(response1)['upload_url']
        # Is there a better way to do this `upload_url.replace(...)`?
        upload_url = upload_url.replace('{?name,label}', '')
        response2 = self.add_release_asset(upload_url, local_file, remote_file)
        return response2

    def create_release(self, tag_name, commitish, body=None, prerelease=False):
        if commitish is None:
            commitish = self.run('git', 'rev-parse', 'HEAD')

        if body is None:
            body = tag_name + ' release.'

        logger().info('Creating GitHub release %s. (commit=%s)', tag_name, commitish)

        request = {
            'tag_name': tag_name,
            'target_commitish': commitish,
            'name': tag_name,
            'body': body,
            'draft': False,
            'prerelease': prerelease,
        }
        url = '/repos/{}/{}/releases'.format(self.owner, self.repo)
        response = self._api_post(url, request)
        return response

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
        return response

    # pylint: enable=too-many-arguments

    def _api_get(self, endpoint, headers=None, server=None):
        return self._api_post(endpoint, None, headers, server, 'GET')
