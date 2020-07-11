# Releasing Bork

Given that Bork is primarily a _build and release tool_, we use Bork to release
itself. We also try to exercise as many parts of Bork as possible when making
a release, in hopes of catching any bugs that slip past the test suite.

This is why we bother with the 30MB ZipApp (`.pyz`) release even though we
 expect nobody to use it.

## The Release Process

Any time `__version__` is changed in `bork/__init__.py`, a new release is made.

At the moment (2020-07-11), these two assumptions are not yet enforced:

1. `bork/__init__.py` will only be changed when updating the value of `__version__`.
2. `__version__` will only increment over time, never decrement.


Full release process:

1. Merge PR incrementing `__version__` in `bork/__init__.py`.
2. Go to https://cirrus-ci.com/github/duckinator/bork/master , and navigate to the appropriate build
3. Run the paused `Release` task, when possible.
4. Go to https://github.com/duckinator/bork/releases for the appropriate commit with the appropriate tag (`v` followed by the version), create a release with the ZipApp (`.pyz`) file.

Steps 2-4 will be automated, but unfortunately this has not occurred yet.
