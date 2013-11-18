#!/usr/bin/env bash

cat <<"END"
language: python
python:
  - 2.7
install: pip install tox
script: tox -e $ENV
env:
END

tox --list | (
  while read i ; do
    echo "  - ENV=$i"
  done
)
