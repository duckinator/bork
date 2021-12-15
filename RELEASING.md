# Releasing Bork

Given that Bork is primarily a _build and release tool_, we use Bork to build
and release itself. We also try to exercise as many parts of Bork as possible
when making a release, in hopes of catching any bugs that slip past the test
suite. As an example, this is why we include ZipApp builds in Bork releases.

## The Release Process

Any time `__version__` is changed in `bork/version.py` on the `main` branch, a new release is made.


Full release process:

1. Merge PR incrementing `__version__` in `bork/__init__.py`.
2. Let the automated processes do everything else.
