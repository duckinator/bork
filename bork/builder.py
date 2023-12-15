import configparser
from pathlib import Path
import subprocess
import sys
# Slight kludge so we can have a function named zipapp().
import zipapp as Zipapp  # noqa: N812

import build

from .filesystem import load_pyproject, try_delete
# from .log import logger


# The "proper" way to handle the default would be to check python_requires
# in setup.cfg. But, since Bork needs Python 3, there's no point.
DEFAULT_PYTHON_INTERPRETER = '/usr/bin/env python3'


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


def _setup_cfg_package_name():
    setup_cfg = configparser.ConfigParser()
    setup_cfg.read('setup.cfg')

    if 'metadata' not in setup_cfg or 'name' not in setup_cfg['metadata']:
        raise RuntimeError(
            "You need to set project.name in pyproject.toml OR metadata.name in setup.cfg"
        )

    return setup_cfg['metadata']['name']


def _python_interpreter(config):
    # To override the default interpreter, add this to your project's setup.cfg:
    #
    # [bork]
    # python_interpreter = /path/to/python
    return config.get('python_interpreter', DEFAULT_PYTHON_INTERPRETER)


def _bdist_file():
    return max(Path.cwd().glob('dist/*.whl'))


def _prepare_zipapp(dest, bdist_file):
    # Prepare zipapp directory.
    try_delete(dest)
    Path(dest).mkdir(parents=True)
    return subprocess.check_call([
        sys.executable, '-m', 'pip', 'install', '--target', dest, bdist_file
    ])


def version_from_bdist_file():
    return _bdist_file().name.replace('.tar.gz', '').split('-')[1]


def zipapp():
    """
    Build a zipapp for the project.

    dist() should be called before zipapp().
    """

    pyproject = load_pyproject()
    config = pyproject.get('tool', {}).get('bork', {})
    zipapp_cfg = config.get('zipapp', {})
    want_zipapp = zipapp_cfg.get('enabled', False)

    if not want_zipapp:
        return

    # If the project name is specified in pyproject.toml, use it.
    # Otherwise, try getting it from setup.cfg.
    name = pyproject.get('project', {}).get('name', None)
    if name is None:
        name = _setup_cfg_package_name()
    dest = str(Path('build', 'zipapp'))
    version = version_from_bdist_file()
    main = zipapp_cfg['main']

    # Output file is dist/<package name>-<package version>.pyz.
    target = f"dist/{name}-{version}.pyz"

    _prepare_zipapp(dest, _bdist_file())

    Zipapp.create_archive(dest, target, _python_interpreter(config), main,
        compressed=True)
    if not Path(target).exists():
        raise RuntimeError(f"Failed to build zipapp: {target}")
