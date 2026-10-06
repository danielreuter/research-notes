set -uo pipefail
SRC=$PWD
D=/workspace/research/scratch/y0-repair-95d4
O="$RESEARCH_RUN_DIR/out"; I="$RESEARCH_RUN_DIR/inputs"
mkdir -p "$O"
export PATH="$HOME/.elan/bin:$PATH"
[ -d "$D/tree/.git" ] || { echo "no scratch tree: run build.sh first"; exit 10; }
cd "$D/tree"
git fetch -q "$SRC" HEAD && git checkout -q -f --detach FETCH_HEAD && git clean -fdq -e .lake || exit 11
git log --oneline -1 | tee "$O/head.txt"
if [ -f "$I/wip.patch" ]; then git apply --whitespace=nowarn "$I/wip.patch" || exit 12; git status --short | tee "$O/patched.txt"; fi
cd verity/Security/Proofs
rc=0
for m in ${TARGETS:-}; do
  lake build "$m" > "$O/build-$m.log" 2>&1; r=$?
  echo "BUILD $m RC=$r" | tee -a "$O/rc.txt"
  grep -E 'error' "$O/build-$m.log" | head -40
  grep -A30 -E '^error:|: error:' "$O/build-$m.log" | head -200
  [ $r -eq 0 ] || { rc=$r; break; }
done
exit $rc
