#!/bin/sh

cd "$(dirname -- "$0")"

echo 'Starting application...'

uv run -m bot "$@"
