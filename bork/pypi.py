import hashlib
import os
from pathlib import Path

from . import builder
from .filesystem import find_files, wheel_file_info
from .log import logger
from .http import post


class Uploader:
    PYPI_ENDPOINT = "https://upload.pypi.org/legacy/"
    TESTPYPI_ENDPOINT = "https://test.pypi.org/legacy/"

    def __init__(self, files, repository=None):
        log = logger()

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
            log.error("Only the 'pypi' and 'testpypi' repository shorthands are supported.")
            log.error("For custom endpoints, provide a full URL.")
            log.error("Open an issue at https://github.com/duckinator/bork if you need help.")
            exit(1)

        if not files:
            log.error("No files to upload?")
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

        if self.username is None and self.password is None:
            raise RuntimeError(
                "BORK_PYPI_USERNAME and BORK_PYPI_PASSWORD environment variables are undefined.\n\n"
                "If you used Bork prior to v9.0.0, these variables used to be TWINE_USERNAME and "
                "TWINE_PASSWORD. You can use the same values.")

        response = post(url, form, auth=(self.username, self.password))
        return response

    def upload(self, *, dry_run = True, metadata = None):
        log = logger()

        msg_prefix = "Uploading"
        if dry_run:
            msg_prefix = "Pretending to upload"

        if metadata is None:
            # Pure sadness, more hardcoded paths and another rebuild  >_>'
            with builder.prepare(Path.cwd(), Path("dist")) as b:
                metadata = b.metadata()

        log.info("%s %i files to PyPi repository '%s'.", msg_prefix, len(self.files),
                self.repository)
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


def upload(repository_name, *globs, **kwargs):
    files = find_files(globs)
    Uploader(files, repository_name).upload(**kwargs)
