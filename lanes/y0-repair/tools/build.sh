# y0-repair's scratch build on vy-nebius-1 (research run --cwd source): the shipped commit, plus inputs/wip.patch when sent,
# in this lane's own tree; `lake build` of verity/Security/Proofs under the node's audit Lean slot, then `lake env lean` on
# each inputs/*.lean probe. Logs go to $RESEARCH_RUN_DIR/out/.
set -uo pipefail
SRC=$PWD
D=/workspace/research/scratch/y0-repair-95d4
O="$RESEARCH_RUN_DIR/out"; I="$RESEARCH_RUN_DIR/inputs"
mkdir -p "$D" "$O"
export PATH="$HOME/.elan/bin:$PATH"
if [ ! -d "$D/tree/.git" ]; then git clone -q "$SRC" "$D/tree" || exit 10; fi
cd "$D/tree"
git fetch -q "$SRC" HEAD && git checkout -q -f --detach FETCH_HEAD && git clean -fdq -e .lake || exit 11
git log --oneline -1 | tee "$O/head.txt"
if [ -f "$I/wip.patch" ]; then git apply --whitespace=nowarn "$I/wip.patch" || exit 12; git status --short | tee "$O/patched.txt"; fi
if [ ! -e "$D/.setup-done" ]; then
  for p in verity/Security verity/Security/Proofs; do bash tools/lean/setup.sh "$p" > "$O/setup-$(basename $p).log" 2>&1; done
  touch "$D/.setup-done"
fi
cd verity/Security/Proofs
python3 "$D/tree/tools/check/lean_slot.py" --status > "$O/slots.txt" 2>&1
T=${BUILD_TARGETS:-}
python3 "$D/tree/tools/check/lean_slot.py" --pool audit --by y0-repair -- lake build $T > "$O/build.log" 2>&1
rc=$?
echo "BUILD_RC=$rc" | tee "$O/rc.txt"
grep -E '^(error|✖)|error:' "$O/build.log" | head -80
tail -5 "$O/build.log"
for f in "$I"/*.lean; do
  [ -f "$f" ] || continue
  b=$(basename "$f" .lean)
  lake env lean "$f" > "$O/probe-$b.log" 2>&1; prc=$?
  echo "PROBE $b RC=$prc" | tee -a "$O/rc.txt"
  head -c 20000 "$O/probe-$b.log"
done
exit $rc
