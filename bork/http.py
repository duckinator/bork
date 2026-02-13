#import urllib.request
import urllib3

from . import version

MAX_RETRIES = False

def request(method, url, fields, auth):
    user_agent = f"bork/{version.__version__} (+https://github.com/duckinator/bork)"

    http = urllib3.PoolManager()
    headers = urllib3.util.make_headers(user_agent=user_agent, basic_auth=":".join(auth))
    response = http.request(method, url, fields=fields, headers=headers, retries=MAX_RETRIES)

    if 399 < response.status < 500:
        raise RuntimeError(response.data.decode())

    return response

def get(url, auth=None):
    return request("GET", url, None, auth)

def post(url, fields=None, auth=None):
    return request("POST", url, fields, auth)
