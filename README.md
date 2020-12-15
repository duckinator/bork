# bork [![Build Status][build-status-img]][build-status-link] [![PyPI][pypi-version-img]][pypi-version-link]

A frontend for building and releasing [PEP 517](https://www.python.org/dev/peps/pep-0517/) compliant projects, including support for generating a [ZipApp](https://docs.python.org/3/library/zipapp.html).

Includes a basic task runner, in the form of `bork run <task name>`. Tasks
are defined in your `pyproject.toml` file.

Bork requires Python 3.6 or newer.

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
[tool.bork]
# GitHub Releases will have names that are "{project_name} {tag}".
# The default is the repository name -- e.g., if your repo is at "foo/bar-baz",
# the default would be "bar-baz".
# This lets you change that, so it looks nicer. (E.g., "Bar Baz".)
project_name = "<nicely formatted project name>"

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

As an example [from Emanate](https://github.com/duckinator/emanate/blob/master/pyproject.toml),
if you put this in pyproject.toml:

```toml
[tool.bork.aliases]
# Runs *only* pylint. (Not the actual tests.)
lint = "pytest -k 'pylint' --pylint --verbose"
# Runs tests and pylint.
test = "pytest --pylint --verbose"
test-only = "pytest --verbose"
docs = "env PYTHONPATH=./ pdoc3 --html --output-dir ./html --force emanate"
```

Then you can run `bork aliases` to get the list of aliases:

```
~/emanate$ bork aliases
lint
test
test-only
docs
~/emanate$
```

And run `bork run <alias>` to run that alias:

```
~/emanate$ bork run docs
./html/emanate/index.html
./html/emanate/cli.html
./html/emanate/config.html
./html/emanate/version.html
~/emanate$
```

## Contributing

Bug reports and pull requests are welcome on GitHub at https://github.com/duckinator/bork. This project is intended to be a safe, welcoming space for collaboration, and contributors are expected to adhere to the
[code of conduct](https://github.com/duckinator/bork/blob/master/CODE_OF_CONDUCT.md).

The code for Bork is available under the [MIT License](http://opensource.org/licenses/MIT).
