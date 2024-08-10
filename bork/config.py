from collections.abc import Mapping, Set, Sequence
from functools import partial, reduce
from pathlib import Path
from typing import Optional # after Py3.10, replace string annotations with Self

from pydantic import dataclasses, TypeAdapter

try:
    import tomllib
except ImportError:
    # Py3.10 compatibility shim
    import toml as tomllib  # type: ignore


# TODO(nicoo): tie model definitions into CLI parsing

# Ensure we don't accidentally make non-frozen or non-kw-only dataclasses
dataclass = partial(dataclasses.dataclass, frozen = True, kw_only = True)

@dataclass
class ReleaseConfig:
    # Related CLI flags: dry_run, pypi_repository
    github: bool = False
    github_release_globs: Set[str] = frozenset(("./dist/*.pyz", ))
    github_repository: Optional[str] = None  # TODO(nicoo) refine type

    pypi: bool = True
    strip_zipapp_version: bool = False

@dataclass
class ZipappConfig:
    enabled: bool = False        # args.zipapp
    main: Optional[str] = None   # args.zipapp_main
    # TODO(nicoo): specify entrypoint format w/ regex annotation

@dataclass
class ToolConfig:
    # TODO: normalize values to Sequence[str]
    aliases: Mapping[str, Sequence[str] | str] = dataclasses.Field(default_factory = dict)
    release: ReleaseConfig = ReleaseConfig()

    python_interpreter: str = "/usr/bin/env python3"  # TODO: move to ZipappConfig
    zipapp: ZipappConfig = ZipappConfig()

ToolConfigAdapter = TypeAdapter(ToolConfig)


@dataclass
class Config:
    bork: ToolConfig
    project_name: Optional[str] = None

    @classmethod
    def from_project(cls, root: Path) -> 'Config':
        try:
            # Inefficient but necessary for compatibility with toml shim
            # To be improved once Py3.10 support is removed
            pyproject = tomllib.loads((root / "pyproject.toml").read_text())
        except FileNotFoundError:
            if any((root / fn).exists() for fn in ("setup.py", "setup.cfg")):
                # Legacy setuptools project without Bork-specific config
                pyproject = {}
            else:
                raise

        def get(*ks):
            return reduce(lambda d, k: d.get(k, {}), ks, pyproject)

        # TODO(nicoo) figure out why mypy doesn't accept this
        #  according to the documentation it should
        return Config( # type: ignore
            bork = ToolConfigAdapter.validate_python(get("tool", "bork")),
            project_name = get("project", "name") or None,  # get may return {}
        )
