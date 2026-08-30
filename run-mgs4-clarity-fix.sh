#!/bin/sh
# Linux / Steam Deck / macOS launcher. Equivalent of Run-MGS4-Clarity-Fix.bat.
set -eu
DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
PY=python3
command -v python3 >/dev/null 2>&1 || PY=python
exec "$PY" "$DIR/mgs4ecf.py" --interactive "$@"
