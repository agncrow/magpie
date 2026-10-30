#!/bin/bash
# Magpie's whole suite against a crow binary, from this repository's root:
# each package's test blocks and its example in both modes, the parity
# programs (interpreted against compiled), the example app served in both
# modes, and the doors and the log driven from outside (tests/doors.py).
# Usage: ./test.sh [path to crow]   (the crow on the PATH by default)
set -u
CROW=${1:-crow}
CROW=$(command -v "$CROW" || echo "$CROW")
cd "$(dirname "$0")" || exit 1
failed=()
step() {
    local name=$1
    shift
    echo "== $name"
    "$@" || failed+=("$name")
    echo
}
step packages "$CROW" test --packages
step parity "$CROW" test --parity
step served "$CROW" test --served
step doors python3 tests/doors.py "$CROW"
if [ ${#failed[@]} -eq 0 ]; then
    echo "✓ magpie: every step passes ($CROW)"
else
    echo "✗ magpie: ${failed[*]} failed ($CROW)"
    exit 1
fi
