"""Bork's package-building abstraction

This module provides an abstraction for building various kind of artefacts from a Python package, in isolation:
* `Built Metadata`_ ;
* `Python source distributions`_, a.k.a. *sdist* ;
* `Built distributions`_ in the standard `wheel`_ format ;
* :py:mod:`zipapp`s.

It is used by invoking the :py:func:`prepare` `context manager`_,
which sets up an isolated build environment and yields a :py:class:`Builder`
whose methods are then called to build the desired artefacts.

This module is meant to be independent of global state, including:
* current working directory ;
* pre-existing contents of the artefacts directory.


Example
"""""""
.. code:: python
with bork.builder.prepare(src_dir, artefacts_dir) as b:
    b.build("wheel")
    b.zipapp()

    meta = b.metadata()
    with (artefacts_dir / f"{meta['name']}-{meta['version']}.json").open("w") as meta_file:
        json.dump(meta.json, meta_file)
::

.. _Built distributions: https://packaging.python.org/en/latest/glossary/#term-Built-Distribution
.. _Built Metadata: https://packaging.python.org/en/latest/glossary/#term-Built-Metadata
.. _Python source distributions: https://packaging.python.org/en/latest/glossary/#term-Source-Distribution-or-sdist
.. _context manager: https://docs.python.org/3/library/stdtypes.html#typecontextmanager
.. _wheel: https://packaging.python.org/en/latest/glossary/#term-Wheel
"""

from .config import Config
from .log import logger
from .utils import scoped_cache

import build

from abc import ABC, abstractmethod
from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Literal, Mapping
from zipfile import ZipFile
import importlib, importlib.metadata
import re, subprocess, sys, zipapp


# The "proper" way to handle the default would be to check python_requires
# in pyproject.toml. But, since Bork needs Python 3, there's no point.
DEFAULT_PYTHON_INTERPRETER = '/usr/bin/env python3'


DistributionKind = Literal["sdist", "wheel"]
BuildSettings = Mapping[str, str | Sequence[str]]

class Builder(ABC):
    @abstractmethod
    def metadata(self) -> importlib.metadata.PackageMetadata:
        "Build the package's wheel metadata"

    @abstractmethod
    def build(self, dist: DistributionKind, *, settings: BuildSettings = {}) -> Path:
        """Build a given distribution of the package

        :param dist: The distribution to be built, must be one of ``"sdist"`` or ``"wheel"``.
        :param settings: Configuration settings for the build backend.
        :returns: The :py:class:`pathlib.Path` to the built artefact.
        """

    @abstractmethod
    def zipapp(self, main: str | None) -> Path:
        """Build a :py:mod:`zipapp` containing the package and its runtime dependencies

        :param main: The name of a callable used as the zipapp's entry point.
                     It must be in the form ``"pkg.mod:func"``, or ``None``
                     in which case the source tree must contain a ``__main__.py``;
                     see :py:func:`zipapp.create_archive`.
        :returns: The :py:class:`pathlib.Path` to the executable archive.
        """


_WHEEL_FILENAME_REGEX = re.compile(
    r"(?P<distribution>.+)-(?P<version>.+)"
    r"(-(?P<build_tag>.+))?-(?P<python_tag>.+)"
    r"-(?P<abi_tag>.+)-(?P<platform_tag>.+)\.whl"
)


@contextmanager
def prepare(src: Path, dst: Path) -> Iterator[Builder]:
    """Context manager for performing builds in an isolated environments.

    :param src: The :py:class:`pathlib.Path` of the source tree to be built.
    :param dst: The :py:class:`pathlib.Path` to the directory where to store built artefacts.
                It will be created if it does not yet exist.
    :returns: A concrete :py:class:`Builder`
    """
    @scoped_cache
    @dataclass(frozen = True)
    class Bob(Builder):
        src: Path
        dst: Path
        env: build.env.IsolatedEnv
        bld: build.ProjectBuilder

        def build(self, dist):
            logger().info(f"Building {dist}")
            self.env.install(
                self.bld.get_requires_for_build(dist)
            )
            return Path(self.bld.build(
                dist, self.dst,
                metadata_directory = self._metadata_path if isinstance(self._metadata_path, Path) else None
            ))

        @scoped_cache.skip  # This is just a wrapper for metadata_path
        def metadata(self) -> importlib.metadata.PackageMetadata:
            return importlib.metadata.PathDistribution(
                self.metadata_path()
            ).metadata

        def metadata_path(self) -> Path:
            log = logger()
            out_dir = Path(self.env.path) / 'metadata'

            def from_wheel() -> Path:
                whl_path = self.build("wheel")
                whl_parse = _WHEEL_FILENAME_REGEX.fullmatch(whl_path.name)
                assert whl_parse, f"Invalid wheel filename '{whl_path.name}'"

                log.info("Extracting metadata from wheel")
                distinfo = f"{whl_parse['distribution']}-{whl_parse['version']}.dist-info/"
                with ZipFile(whl_path) as whl:
                    whl.extractall(
                        out_dir,
                        members = (fn for fn in whl.namelist() if fn.startswith(distinfo)),
                    )

                return out_dir / distinfo


            if "wheel" in self._build:
                # A wheel was already built, let's extract its metadata
                return from_wheel()

            metadata = self.bld.prepare("wheel", out_dir)
            if metadata is not None:
                return Path(metadata)

            log.debug("Package metadata cannot be built alone, building wheel")
            return from_wheel()

        def zipapp(self, main):
            log = logger()
            log.info(f"Building zipapp with entrypoint '{main}'")

            log.debug("Loading configuration")
            config = Config.from_project(self.src)

            log.debug("Loading metadata")
            meta = self.metadata()
            dst = self.dst / f"{meta['name']}-{meta['version']}.pyz"

            with TemporaryDirectory() as tmp:
                # Install the wheel we just built, including all dependencies
                wheel = self.build("wheel")

                log.info(f"Installing '{wheel}'")
                subprocess.check_call((
                    sys.executable, '-m', 'pip', 'install',
                    '--target', tmp,
                    wheel
                ))

                log.info(f"Creating zipapp archive '{dst}'")
                zipapp.create_archive(
                    source = tmp,
                    target = dst,
                    interpreter = config.bork.python_interpreter,
                    main = main or config.bork.zipapp.main,  # TODO error if main is None and there's no __main__.py
                    compressed = True,
                )

            if not dst.exists():
                raise RuntimeError(f"Failed to build zipapp: {dst}")

            log.info(f"Zipapp '{dst}' successfully built")
            return dst


    src, dst = src.resolve(), dst.resolve()

    with build.env.DefaultIsolatedEnv() as env:
        builder = build.ProjectBuilder.from_isolated_env(env, src)
        env.install(builder.build_system_requires)

        yield Bob(src, dst, env, builder)


# TODO: remove last caller (api.release)
def version_from_bdist_file():
    files = list(Path.cwd().glob('dist/*.whl'))
    if not files:
        raise NeedsBuildError

    return max(files).name.replace('.tar.gz', '').split('-')[1]

class NeedsBuildError(Exception):
    pass
