from os import getenv
from typing import Optional
from . import trusted_publishing
from .log import logger

from pydantic.dataclasses import dataclass

@dataclass(frozen = True, kw_only = True)
class Credentials:
    github: Optional[str] = None
    pypi:   Optional['Credentials.PyPI'] = None

    @classmethod
    def from_env(cls, pypi_repository=None) -> 'Credentials':
        # TODO: support specifying another env than os.environ?
        return cls(
            github = getenv("BORK_GITHUB_TOKEN"),
            pypi   = cls.PyPI.from_env(pypi_repository),
        )

    @dataclass(frozen = True)
    class PyPI:
        username: str
        password: str

        @classmethod
        def from_trusted_publishing(cls, repository) -> Optional['Credentials.PyPI']:
            if repository is None:
                return None

            logger().debug("trying to get token via Trusted Publishing")
            token = trusted_publishing.get_token(repository)
            if token is not None:
                return cls("__token__", token)

            return None

        # FIXME: Avoid needing to pass around repository, BUT ALSO respect --pypi-repository/--test-pypi
        @classmethod
        def from_env(cls, repository=None) -> Optional['Credentials.PyPI']:
            match getenv("BORK_PYPI_USERNAME"), getenv("BORK_PYPI_PASSWORD"), getenv("BORK_PYPI_TOKEN"):
                case username, password, None if username and password:
                    return cls(username, password)
                case None, None, token if token:
                    return cls("__token__", token)
                case None, None, None:
                    return cls.from_trusted_publishing(repository)

                # Error cases
                case _, password, token if password and token:
                    raise RuntimeError("Cannot specify both BORK_PYPI_{PASSWORD, TOKEN}")
                case (x, None, _) | (None, x, _) if x:
                    raise RuntimeError(
                        "Either both or none of BORK_PYPI_{USERNAME, PASSWORD} must be specified"
                    )

            # mypy cannot check for completeness of pattern matching (yet?)
            raise AssertionError("Accidentally-incomplete pattern matching")
