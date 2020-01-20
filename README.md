# bork [![Build Status][build-status-img]][build-status-link] [![PyPI][pypi-version-img]][pypi-version-link]

A frontend for building and releasing [PEP 517](https://www.python.org/dev/peps/pep-0517/) compliant projects, including support for generating a [ZipApp](https://docs.python.org/3/library/zipapp.html).

Bork requires Python 3.5 or newer.

[build-status-img]: https://api.cirrus-ci.com/github/duckinator/bork.svg
[build-status-link]: https://cirrus-ci.com/github/duckinator/bork

[pypi-version-img]: https://img.shields.io/pypi/v/bork
[pypi-version-link]: https://pypi.org/project/bork

## Installation

```
$ pip3 install bork
```

<!--
Or download [the latest zipapp
releases](https://github.com/duckinator/bork/releases/latest/download/bork.pyz)
-->

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
$ bork download pypi-test:whaledo 1.0.1 --files '*.whl'
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

## Contributing

Bug reports and pull requests are welcome on GitHub at https://github.com/duckinator/bork. This project is intended to be a safe, welcoming space for collaboration, and contributors are expected to adhere to the [Contributor Covenant](http://contributor-covenant.org) code of conduct.

## License

The gem is available as open source under the terms of the [MIT License](http://opensource.org/licenses/MIT).

## Code of Conduct

Everyone interacting in the bork project’s codebases, issue trackers, chat rooms and mailing lists is expected to follow the [code of conduct](https://github.com/duckinator/bork/blob/master/CODE_OF_CONDUCT.md).
