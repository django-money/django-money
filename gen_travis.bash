#!/usr/bin/env bash

cat <<"END"
language: python
python:
  - 2.7
install: pip install tox
script: tox -e $ENV
env:
END

if [[ $1 == "--all" ]] ; then
  tox --list | (
    while read i ; do
      echo "  - ENV=$i"
    done
  )
else
  # a few representative envs...
  cat <<"END"
  - ENV=py27-django15-pmlatest
  - ENV=py27-django16-pmlatest
  - ENV=py33-django15-pmpython3
  - ENV=py33-django16-pmpython3
END
fi
