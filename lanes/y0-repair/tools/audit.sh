# y0-repair's lock update on vy-nebius-1 (research run --cwd source): the shipped commit, clean, in this lane's own tree
# (its warm .lake), then `audit.py --build --update --owner @proofs --no-replay --no-runs verity/Security` under the node's
# audit Lean slot. Reports go to $RESEARCH_RUN_DIR/lean-audit, with the updated lock copied beside them.
set -uo pipefail
SRC=$PWD
D=/workspace/research/scratch/y0-repair-95d4
O="$RESEARCH_RUN_DIR/lean-audit"
mkdir -p "$O"
export PATH="$HOME/.elan/bin:$PATH"
[ -d "$D/tree/.git" ] || { echo "no scratch tree: run build.sh first"; exit 10; }
cd "$D/tree"
git fetch -q "$SRC" HEAD && git checkout -q -f --detach FETCH_HEAD && git clean -fdq -e .lake || exit 11
if [ -n "$(git status --porcelain)" ]; then git status --short; echo "tree not clean"; exit 12; fi
git log --oneline -1 | tee "$O/head.txt"
python3 tools/check/lean_slot.py --pool audit --by y0-repair -- \
  python3 tools/lean/audit.py --build --update --owner @proofs --no-replay --no-runs --out "$O" verity/Security \
  > "$O/audit.log" 2>&1
rc=$?
tail -60 "$O/audit.log"
cp verity/Security/lean-audit.json "$O/lean-audit.json"
git diff --stat | tee "$O/diffstat.txt"
echo "AUDIT_RC=$rc" | tee "$O/rc.txt"
exit $rc
