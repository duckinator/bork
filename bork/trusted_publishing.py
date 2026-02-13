from . import version
from .log import logger
import json
import os
import urllib.request
from urllib.parse import urlsplit


# FIXME: Dedupe request/get/post with bork/github_api.py.

def request(method, url, data, headers):
    if headers is None:
        headers = {}

    if isinstance(data, (dict, list)):
        data = json.dumps(data).encode()

    headers['User-Agent'] = f"bork/{version.__version__} (+https://github.com/duckinator/bork)"

    req = urllib.request.Request(url, data=data,
                                 headers=headers, method=method)

    with urllib.request.urlopen(req) as res:
        response = res.read().decode()

    return response

def get(url, headers={}):
    return request('GET', url, None, headers)

def post(url, data, headers={}):
    return request('POST', url, data, headers)


class TrustedPublishingError(Exception):
    pass

class TrustedPublishingProvider:
    """
    Base class for all Trusted Publishing providers.
    """

    def __init__(self, audience):
        self.audience = audience

    @staticmethod
    def detected():
        """Are we running on the provider this class represents?"""
        raise NotImplementedError

    def get_token(self, repository):
        """Perform the whole song and dance to get a token."""
        url = urlsplit(repository)._replace(path="/_/oidc/mint-token").geturl()
        data = json.loads(post(url, {"token": self.get_ambient_credential()}))
        return data["token"]

    def get_ambient_credential(self):
        """Get the "ambient credential" from the provider."""
        raise NotImplementedError

class GithubTrustedPublishing(TrustedPublishingProvider):
    @staticmethod
    def detected():
        """Are we running on GitHub CI?"""
        return bool(os.environ.get("CI") and os.environ.get("GITHUB_ACTION"))

    def get_ambient_credential(self):
        token = os.environ.get("ACTIONS_ID_TOKEN_REQUEST_TOKEN")
        url = os.environ.get("ACTIONS_ID_TOKEN_REQUEST_URL")

        if not token:
            raise TrustedPublishingError("Expected ACTIONS_ID_TOKEN_REQUEST_TOKEN environment variable to be defined.")

        if not url:
            raise TrustedPublishingError("Expected ACTIONS_ID_TOKEN_REQUEST_URL environment variable to be defined.")

        url += "&audience=" + self.audience

        headers = {"Authorization": f"bearer {token}"}

        data = json.loads(get(url, headers))
        oidc_token = data['value']
        return oidc_token


PROVIDERS = [GithubTrustedPublishing]

def get_token(repository):
    """Given the URL for a repository, get a token to publish to that repository."""
    log = logger()

    audience = get_audience(repository)
    for provider in PROVIDERS:
        if provider.detected():
            log.debug(f"found Trusted Publisher: {provider.__name__}")
            return provider(audience).get_token(repository)
    log.debug("couldn't find any known Trusted Publisher")
    return None

def get_audience(repository):
    """Given the full URL for a repository, determine the OIDC audience."""
    url = urlsplit(repository)._replace(path="/_/oidc/audience").geturl()
    audience = json.loads(get(url))["audience"]
    logger().debug(f"repository {repository!r} has audience {audience!r}")
    return audience
