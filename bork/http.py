#import urllib.request
import urllib3

from . import version
from .log import logger

MAX_RETRIES = False

def _request(url, fields, headers, method, auth):
    log = logger()

    user_agent = f"bork/{version.__version__} (+https://github.com/duckinator/bork)"

    http = urllib3.PoolManager()
    headers = urllib3.util.make_headers(user_agent=user_agent, basic_auth=":".join(auth))
    response = http.request(method, url, fields=fields, headers=headers, retries=MAX_RETRIES)

    if 399 < response.status < 500:
        raise RuntimeError(response.data.decode())

    log.debug(response.getheaders())

    log.debug("%s %s returned %i", method, response.geturl(), response.status)

    if response.status == 200:
        log.info("Upload successful!")
    else:
        log.info(response.data.decode().strip())

    return response

def get(url, headers={}, auth=None):
    return _request(url, None, headers, "GET", auth)

def post(url, fields=None, headers=None, auth=None):
    if headers is None:
        headers = {}

    headers["Content-Type"] = "application/x-www-form-urlencoded"
    return _request(url, fields, headers, "POST", auth)
