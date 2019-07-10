# bork [![Build Status][build-status-link]][build-status-img]

A frontend for building and releasing [PEP 517](https://www.python.org/dev/peps/pep-0517/) compliant projects, including support for generating a [ZipApp](https://docs.python.org/3/library/zipapp.html).


[build-status-link]: https://api.cirrus-ci.com/github/duckinator/bork.svg
[build-status-img]: https://cirrus-ci.com/github/duckinator/bork

## Installation

```
$ pip3 install bork
```

## Usage

Assuming a project is PEP 517 compliant, you can just do:

```
$ bork clean # Remove anything in build/, dist/, *.egg-info/
$ bork build # Build the project
$ bork release # Release to PyPI
```

### ZipApp Support

If you want to build a ZipApp, add this to your setup.cfg:

```
[bork]
zipapp_main = <entrypoint>
```

Where `<entrypoint>` is of the form "module.submodule:function", and
will likely be equivalent to the primary `console_script` entrypoint
elsewhere in setup.cfg.

## Contributing

Bug reports and pull requests are welcome on GitHub at https://github.com/duckinator/bork. This project is intended to be a safe, welcoming space for collaboration, and contributors are expected to adhere to the [Contributor Covenant](http://contributor-covenant.org) code of conduct.

## License

The gem is available as open source under the terms of the [MIT License](http://opensource.org/licenses/MIT).

## Code of Conduct

Everyone interacting in the bork project’s codebases, issue trackers, chat rooms and mailing lists is expected to follow the [code of conduct](https://github.com/duckinator/bork/blob/master/CODE_OF_CONDUCT.md).
