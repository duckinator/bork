import configparser
import hashlib
import os
from pathlib import Path

from . import builder
from .asset_manager import download_assets
from .filesystem import find_files, wheel_file_info
from .log import logger
from .pypi_api import get_download_info
from .http import post


class Downloader:  # pylint: disable=too-few-public-methods
    # In the future, if we decide this should be public functionality,
    # this lets us choose a better key name with minimal impact.
    PYPIRC_KEY = '_bork-download-endpoint'

    PYPIRC_DEFAULTS = {
        'pypi': {
            PYPIRC_KEY: 'https://pypi.org/simple/',
        },
        'testpypi': {
            PYPIRC_KEY: 'https://test.pypi.org/simple/',
        },
    }

    def __init__(self, repository_name):
        self.repository_url = self._download_url(repository_name)

    def download(self, package, release, file_pattern, directory):
        asset_list = get_download_info(self.repository_url, package, release,
                                       file_pattern)
        download_assets(asset_list, directory)

    def _download_url(self, repository_name):
        path = Path('~/.pypirc').expanduser()
        config = configparser.ConfigParser()
        if path.exists():
            config.read(str(path))

        if repository_name in config:
            repo_config = config[repository_name]
            if self.PYPIRC_KEY in repo_config:
                return repo_config[self.PYPIRC_KEY]

        return self.PYPIRC_DEFAULTS[repository_name][self.PYPIRC_KEY]


def download(repository_name, package, release, file_pattern, directory):
    return Downloader(repository_name).download(package, release, file_pattern,
                                                directory)


class Uploader:
    PYPI_ENDPOINT = "https://upload.pypi.org/legacy/"
    TESTPYPI_ENDPOINT = "https://test.pypi.org/legacy/"

    def __init__(self, files, repository=None):
        if repository == "pypi" or repository is None:
            repository = self.PYPI_ENDPOINT
        elif repository == "testpypi":
            repository = self.TESTPYPI_ENDPOINT
        elif repository.startswith("http://"):
            logger().error("Configured to use insecure repository: %s", repository)
            exit(1)
        elif repository.startswith("https://"):
            pass # Everything is fine.
        else:
            logger().error("Only the 'pypi' and 'testpypi' repository shorthands are supported.")
            logger().error("Please provide a full URL for custom endpoints, such as <https://pypi.example.org/legacy/>.")
            logger().error("Please open an issue at https://github.com/duckinator/bork if you need help.")
            exit(1)

        if not files:
            logger().error("No files to upload?")
            exit(1)

        self.files = files
        self.repository = repository

        self.username = os.environ.get("BORK_PYPI_USERNAME", None)
        self.password = os.environ.get("BORK_PYPI_PASSWORD", None)

    def _upload_file(self, url, file, metadata):
        file_contents = Path(file).read_bytes()
        file_digest = hashlib.sha256(file_contents).hexdigest()

        if file.endswith(".whl"):
            file_type = "bdist_wheel"
            pyversion = wheel_file_info(file)["pyversion"]
        else:
            file_type = "sdist"
            pyversion = "source"

        md = metadata

        wanted_fields = [
            "summary",
            "description", "description_content_type",
            "keywords", "home_page", "download_url",
            "author", "author_email", "maintainer", "maintainer_email",
            "license", "classifier",
            "requires_dist", "requires_python", "requires_external",
            "project_url",
        ]

        other_fields = []
        for key in md.keys():
            if key not in wanted_fields:
                continue

            values = md[key]
            if not isinstance(values, list):
                values = [values]

            for value in values:
                other_fields.append((key, value))

        form = [
            (":action", "file_upload"),
            ("protocol_version", "1"),
            ("content", (Path(file).name, file_contents)),
            ("sha256_digest", file_digest),
            ("filetype", file_type),
            ("pyversion", pyversion),

            # Required "core metadata" fields.
            # These are set here to trigger a hard error if they're missing.
            ("metadata_version", md["metadata_version"]),
            ("name", md["name"]),
            ("version", md["version"]),

            # Remaining "core metadata" fields.
            *other_fields
            ]
        response = post(url, form, auth=(self.username, self.password))
        return response

    def upload(self, dry_run=True):
        log = logger()

        msg_prefix = "Uploading"
        if dry_run:
            msg_prefix = "Pretending to upload"

        metadata = builder.metadata().json

        log.info("%s %i files to PyPi repository '%s'.", msg_prefix, len(self.files), self.repository)
        for file in self.files:
            filename = Path(file).name
            if dry_run:
                log.info("SUCCESS - Pretended to upload %s!", file)
                continue

            response = self._upload_file(self.repository, file, metadata)
            if response.status == 200:
                log.info("SUCCESS - %s uploaded to %s", filename, self.repository)
            else:
                log.info("FAILED  - %s couldn't be uploaded to %s", filename, self.repository)
                log.info(response.data.decode().strip())


def upload(repository_name, *globs, dry_run=False):
    files = find_files(globs)
    Uploader(files, repository_name).upload(dry_run)
