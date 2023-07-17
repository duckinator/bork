# bork [![Build Status][build-status-img]][build-status-link] [![PyPI][pypi-version-img]][pypi-version-link] [![Documentation Status](https://readthedocs.org/projects/bork/badge/?version=latest)](https://bork.readthedocs.io/en/latest/?badge=latest)

A frontend for building and releasing [PEP 517](https://www.python.org/dev/peps/pep-0517/) compliant projects, including support for generating a [ZipApp](https://docs.python.org/3/library/zipapp.html).

Includes a basic task runner, in the form of `bork run <task name>`. Tasks
are defined in your `pyproject.toml` file.

Bork requires Python 3.8 or newer.

[build-status-img]: https://api.cirrus-ci.com/github/duckinator/bork.svg
[build-status-link]: https://cirrus-ci.com/github/duckinator/bork

[pypi-version-img]: https://img.shields.io/pypi/v/bork
[pypi-version-link]: https://pypi.org/project/bork

## Installation

```
$ pip3 install bork
```

Or download [the latest zipapp
releases](https://github.com/duckinator/bork/releases/latest/download/bork.pyz)

## Usage

Example usage information is provided below. Additional documentation can be found at [bork.readthedocs.io](https://bork.readthedocs.io/).

### Downloading Existing Builds

To download a release from GitHub:

```
$ bork download gh:duckinator/emanate # download latest .pyz for Emanate
$ bork download gh:duckinator/emanate --directory bin/ # put files in ./bin
$ bork download gh:ppb/pursuedpybear --files '*.tar.gz' # download latest .tar.gz file
```

To download a wheel from a PyPi release:

```
$ bork download pypi:emanate 6.0.0 --files '*.whl'
```


To download a wheel from a release on PyPi's test instance:

```
$ bork download testpypi:whaledo 1.0.1 --files '*.whl'
```

### Building and Releasing

Assuming a project is PEP 517 compliant, you can just do:

```
$ bork clean # Remove anything in build/, dist/, *.egg-info/
$ bork build # Build the project
$ bork release # Release to PyPI
```

### ZipApp Support

If you want to build a ZipApp, add this to your pyproject.toml:

```
[tool.bork.zipapp]
enabled = true
main = "<entrypoint>"
```

Where `<entrypoint>` is of the form "module.submodule:function", and
may be equivalent to a `console_script` entrypoint in setup.cfg.

**NOTE**: ZipApps will only be compressed when using Python 3.7 and later. This means ZipApps created with older versions may be significantly larger.

### Uploading To GitHub Releases

If you want to upload assets to GitHub Releases, you can
add the following configuration to your pyproject.toml:

```
[project]
name = "<project name>"

[tool.bork.release]
# If true, release to PyPi; otherwise, don't.
pypi = true
# If true, release to GitHub; otherwise, don't.
github = true # release to GitHub
# GitHub repository, e.g. "duckinator/bork".
github_repository = "<owner>/<repo>"
# List of file globs to include in GitHub Releases.
github_release_globs = ["dist/*.pyz", "dist/*.whl"]
# If true, zipapps are named "<name>.pyz", otherwise "<name>-<version>.pyz".
strip_zipapp_version = true
```

## Aliases (Basic task runner)

Bork includes a very basic task runner, for single-line commands.

As an example, here is what Bork uses:

```toml
[tool.bork.aliases]
lint = [
    "pylint bork tests",
    "mypy bork",
]
# Runs all tests.
test = "pytest --verbose"
# Runs fast tests.
test-fast = "pytest --verbose -m 'not slow'"
# Runs slow tests.
test-slow = "pytest --verbose -m slow"
# Build docs
docs = "mkdocs build"
```

Then you can run `bork aliases` to get the list of aliases:

```
~/bork$ bork aliases
lint
test
test-fast
test-slow
~/bork$
```

And run `bork run <alias>` to run that alias:

```
~/bork$ bork run docs
mkdocs build
INFO     -  Cleaning site directory
INFO     -  Building documentation to directory: /usr/home/puppy/bork/site
INFO     -  Documentation built in 0.25 seconds
~/bork$
```

## Contributing

Bug reports and pull requests are welcome on GitHub at https://github.com/duckinator/bork. This project is intended to be a safe, welcoming space for collaboration, and contributors are expected to adhere to the
[code of conduct](https://github.com/duckinator/bork/blob/master/CODE_OF_CONDUCT.md).

The code for Bork is available under the [MIT License](http://opensource.org/licenses/MIT).
