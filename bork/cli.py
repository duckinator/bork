import sys

from . import build_pep517, build_zipapp
from . import build, clean, release

def print_help():
    print("Usage: bork build")
    print("       bork clean")
    print("       bork release [pypi] [github]")

def main(argv=None):
    if argv is None:
        argv = sys.argv

    if len(argv) < 2 or "-h" in argv or "--help" in argv:
        print_help()
        exit(1)

    command = argv[1]
    args = argv[2:]

    if command == "build":
        build(args)
    elif command == "build-pep517":
        build_pep517(args)
    elif command == "build-zipapp":
        build_zipapp(args)
    elif command == "clean":
        clean(args)
    elif command == "release":
        release(args)
    else:
        print_help()
