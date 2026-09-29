#!/usr/bin/env bash
# Acceptance check for lean/submissions/pouw-accountable-compute: the vendored files are main's, the library builds, the
# #print axioms list matches AXIOMS.txt, and Verity's Lean audit passes (every declaration, the pins, kernel replay).
# Prints ALL CHECKS PASSED. Needs sha256sum and a Verity checkout at origin/main b4fd93e9 or later: VERITY_CHECKOUT=<dir>
# (the vendored files are diffed against it, and its tools/lean/audit.py runs the audit; the pins' records are in that
# audit's format, which the store's older copy of tools/lean, 6746f408, prints differently). POUW_LEAN_AUDIT overrides
# the audit script.
set -uo pipefail
cd "$(dirname "$0")"
export PATH="$HOME/.elan/bin:$PATH"
fail() { echo "CHECK FAILED: $1" >&2; exit 1; }

echo "== vendored files (VENDORED-FROM)"
grep -E '^[0-9a-f]{64}  ' VENDORED-FROM | sha256sum --quiet -c - || fail "a vendored file differs from its recorded digest"
if [ -n "${VERITY_CHECKOUT:-}" ]; then
  for f in $(grep -oE 'FlockSoundness/[^ ]+\.lean' VENDORED-FROM); do
    cmp -s "$f" "$VERITY_CHECKOUT/backends/flock/verifier/lean/soundness/$f" || fail "$f differs from $VERITY_CHECKOUT"
  done
  echo "   identical to $VERITY_CHECKOUT"
fi

echo "== build"
lake build > /dev/null || fail "lake build"

echo "== axioms (Check.lean against AXIOMS.txt)"
ax=$(mktemp)
lake env lean Check.lean > "$ax" 2>&1 || { rm -f "$ax"; fail "Check.lean"; }
cmp -s "$ax" AXIOMS.txt || { diff "$ax" AXIOMS.txt >&2; rm -f "$ax"; fail "AXIOMS.txt"; }
grep -v '\[propext, Classical.choice, Quot.sound\]' "$ax" && { rm -f "$ax"; fail "a nonstandard axiom"; }
rm -f "$ax"

echo "== Verity's Lean audit (every declaration, pins, kernel replay)"
audit_py=${POUW_LEAN_AUDIT:-${VERITY_CHECKOUT:-/nonexistent}/tools/lean/audit.py}
[ -f "$audit_py" ] || fail "no Verity tools/lean/audit.py at $audit_py: set VERITY_CHECKOUT (or POUW_LEAN_AUDIT)"
alog=$(mktemp)
python3 "$audit_py" . > "$alog" 2>&1 || { tail -40 "$alog" >&2; rm -f "$alog"; fail "audit.py"; }
grep -E '^AUDIT ' "$alog" | sed 's/^/   /' | cut -c1-200
rm -f "$alog"

echo "ALL CHECKS PASSED"
