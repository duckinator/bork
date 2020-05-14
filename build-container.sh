#!/bin/bash

BORK_VERSION="$(cat bork/__init__.py | cut -d '"' -f 2)"

docker build --tag duckinator/bork:${BORK_VERSION} --build-arg "VERSION=${BORK_VERSION}" .
