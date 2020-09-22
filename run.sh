#!/bin/sh

cd "$(dirname $0)"
. "./env/bin/activate"

python runner.py "$@"
