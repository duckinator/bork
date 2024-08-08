from .filesystem import load_pyproject, try_delete
from .log import logger
import build
import contextlib
import importlib
from pathlib import Path
import subprocess
import sys
import tempfile
# Slight kludge so we can have a function named zipapp().
import zipapp as Zipapp  # noqa: N812


class NeedsBuildError(Exception):
    pass


# The "proper" way to handle the default would be to check python_requires
# in pyproject.toml. But, since Bork needs Python 3, there's no point.
DEFAULT_PYTHON_INTERPRETER = '/usr/bin/env python3'

@contextlib.contextmanager
def prepared_environment(srcdir, outdir):
    """Usage:
        with prepared_environment(".", "./dist") as (env, builder):
            # ...
    """
    with build.env.DefaultIsolatedEnv() as env:
        builder = build.ProjectBuilder.from_isolated_env(env, srcdir)
        # Install deps from `project.build_system_requires`
        env.install(builder.build_system_requires)
        # Yield env and builder.
        yield (env, builder)

def dist(backend_settings=None):
    """Build the sdist and wheel distributions.

    :param backend_settings: Passed as ``config_settings`` to
        ``build.ProjectBuilder.get_requires_for_build(distribution, config_settings)`` and
        ``build.ProjectBuilder.build(distribution, outdir, config_settings)
    """

    srcdir = "."
    outdir = "./dist"

    with build.env.DefaultIsolatedEnv() as env:
        builder = build.ProjectBuilder.from_isolated_env(env, srcdir)
        # Install deps from `project.build_system_requires`
        env.install(builder.build_system_requires)

        results = {}
        for distribution in ["sdist", "wheel"]:
            # Install deps that are required to build the distribution.
            env.install(builder.get_requires_for_build(distribution, backend_settings or {}))

            results[distribution] = builder.build(distribution, outdir, backend_settings or {})
        return results


def metadata():
    srcdir = "."
    outdir = "./dist"

    with prepared_environment(srcdir, outdir) as (env, builder):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(builder.metadata_path(tmpdir))
            return importlib.metadata.Distribution.at(path).metadata

def _python_interpreter(config):
    # To override the default interpreter, add this to your project's pyproject.toml:
    #
    # [bork]
    # python_interpreter = /path/to/python
    return config.get('python_interpreter', DEFAULT_PYTHON_INTERPRETER)


def _bdist_file():
    files = list(Path.cwd().glob('dist/*.whl'))
    if not files:
        raise NeedsBuildError
    return max(files)


def _prepare_zipapp(dest, bdist_file):
    # Prepare zipapp directory.
    try_delete(dest)
    Path(dest).mkdir(parents=True)
    return subprocess.check_call([
        sys.executable, '-m', 'pip', 'install', '--target', dest, bdist_file
    ])


def version_from_bdist_file():
    return _bdist_file().name.replace('.tar.gz', '').split('-')[1]


def zipapp(zipapp_main):
    """
    Build a zipapp for the project.

    dist() should be called before zipapp().
    """

    log = logger()

    log.info("Building ZipApp.")

    pyproject = load_pyproject()
    config = pyproject.get('tool', {}).get('bork', {})
    zipapp_cfg = config.get('zipapp', {})

    name = metadata()['name']
    dest = str(Path('build', 'zipapp'))
    version = version_from_bdist_file()
    main = zipapp_main or zipapp_cfg['main']

    # Output file is dist/<package name>-<package version>.pyz.
    target = f"dist/{name}-{version}.pyz"

    _prepare_zipapp(dest, _bdist_file())

    Zipapp.create_archive(dest, target, _python_interpreter(config), main,
        compressed=True)
    if not Path(target).exists():
        raise RuntimeError(f"Failed to build zipapp: {target}")
    log.info("Finished building ZipApp.")
