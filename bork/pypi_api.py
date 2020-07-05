import fnmatch
from html.parser import HTMLParser
import re
from typing import Dict
from urllib.request import urlopen


class SimplePypiParser(HTMLParser):
    files: Dict[str, str] = {}
    in_anchor = False
    current_url = None

    def handle_starttag(self, tag, attrs):
        if tag != 'a':
            return

        self.in_anchor = True
        for attr in attrs:
            if attr[0] == 'href':
                self.current_url = attr[1]

    def handle_endtag(self, tag):
        if tag == 'a':
            self.in_anchor = False
            self.current_url = None

    def handle_data(self, data):
        if not self.in_anchor:
            return

        data = data.strip()
        self.files[data] = self.current_url

    def error(self, message):
        raise RuntimeError('{}: {}'.format(self.__class__.__name__, message))


def _normalize(name):
    return re.sub(r'[-_.]+', '-', name).lower()


def _matches_pattern(filename, file_pattern):
    file_patterns = file_pattern.split(',')

    for pattern in file_patterns:
        if fnmatch.fnmatch(filename, pattern):
            return True
    return False


def _matches_version(filename, version):
    # If it's of the form vX.X.X where X is always a number, remove the
    # leading v.
    # This means that for common versioning styles, the exact content
    # of a GitHub tag can be passed in here.
    if re.match(r'^v[\d.]+$', version):
        return _matches_version(filename, version[1:])

    # HACK: Change .tar.gz to .tgz so we can just remove the last .<blah>.
    filename = filename.replace('.tar.gz', '.tgz')
    filename = '.'.join(filename.split('.')[0:-1])

    file_version = filename.split('-')[1]

    return fnmatch.fnmatch(file_version, version)


def get_download_info(base_url, package, release, file_pattern):
    results = []

    # Normalize base_url so it never ends with a forward slash.
    if base_url.endswith('/'):
        base_url = base_url[:-1]

    html = urlopen('{}/{}/'.format(base_url, package)).read().decode()
    parser = SimplePypiParser()
    parser.feed(html)
    files = parser.files

    keys = list(files.keys()).copy()
    for name in keys:
        if not _matches_pattern(name, file_pattern):
            continue

        if not _matches_version(name, release):
            continue

        # If we get here, we have a valid version.
        results.append({'name': name, 'url': files[name]})

    return results
