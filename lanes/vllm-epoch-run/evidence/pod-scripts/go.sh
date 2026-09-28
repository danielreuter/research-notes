#!/bin/bash
# go.sh SHA [BUNDLE]: the GO steps on the VM (section-1 environment exported), before any launch_row.sh.
#   1 the GO sha: fetched from origin (or from BUNDLE), and it is main's tip or on main (fails otherwise)
#   2 evidence/epoch_sha; the clean --source tree /workspace-wt/epoch-<sha8>; the branch worktree /workspace-wt/epoch-run on
#     cursor/epoch-run-expected-2622 at the sha (the `expected/` and known_roots commits)
#   3 CPU sanity on the GO tree: the query of record is Q_word_v1, `rebaseline digests` exists, the S-stack's defaults are on
#     (NORM_TAP / GUARDED_MAX_TAP / ROUTER_TAP / VOCAB_TAP = 1), the #101 gate-limit family is known to word.gate_limits
#   4 watch_pods.sh in tmux session epoch-watch (the fail-fast terminations and the status file)
set -eu
SHA=${1:?GO sha}; BUNDLE=${2:-}
H=$(cd "$(dirname "$0")" && pwd); LANE=$RESEARCH_NOTES/lanes/vllm-epoch-run
cd /workspace
if [ -n "$BUNDLE" ]; then git fetch -q "$BUNDLE" "$SHA"; else git fetch -q origin main; fi
SHA=$(git rev-parse --verify "$SHA^{commit}")
[ -n "$BUNDLE" ] || git merge-base --is-ancestor "$SHA" origin/main || { echo "GO sha $SHA is not on origin/main"; exit 2; }
echo "$SHA" > "$LANE/evidence/epoch_sha"
WT=/workspace-wt/epoch-${SHA:0:8}
[ -d "$WT" ] || git worktree add -q --detach "$WT" "$SHA"
[ "$(git -C "$WT" rev-parse HEAD)" = "$SHA" ] && [ -z "$(git -C "$WT" status --porcelain)" ] || { echo "$WT is not clean at $SHA"; exit 2; }
[ -d /workspace-wt/epoch-run ] || git worktree add -q -b cursor/epoch-run-expected-2622 /workspace-wt/epoch-run "$SHA"
echo "tree $WT, branch $(git -C /workspace-wt/epoch-run rev-parse --abbrev-ref HEAD) @ $(git -C /workspace-wt/epoch-run rev-parse --short HEAD)"
cd "$WT/integrations/vllm"
PYTHONPATH=.:../../packages/verity/src:../../tools/research/src:../../protocols/sampled_proofs python3 - <<'EOF'
from verity_vllm.query.required import QUERY_OF_RECORD
from verity_vllm.pipeline import cli
from verity_vllm.query import word
from tests.regression import rebaseline
assert QUERY_OF_RECORD.startswith("Q_word_v1"), QUERY_OF_RECORD
o = cli.parse("row", ["run", "x__bf16__l40s__tp1__b1__i1__o2__mixed__greedy__bi-eager", "B0", "r", "v"], {})
bad = {k: getattr(o.commit, k) for k in ("norm_tap", "guarded_max_tap", "router_tap", "vocab_tap") if getattr(o.commit, k) != "1"}
assert not bad, f"an epoch default is off on the GO tree: {bad}"
lim = word.gate_limits("GumbelTopPTokenSelect_v2=110000000")
print(f"sanity PASS: {QUERY_OF_RECORD}; taps on; rebaseline digests {'present' if hasattr(rebaseline, 'digests') else 'absent (row_digests.py stands in)'}; gate limits {lim}")
EOF
tmux -f /exec-daemon/tmux.portal.conf has-session -t epoch-watch 2>/dev/null \
  || tmux -f /exec-daemon/tmux.portal.conf new-session -d -s epoch-watch \
     "env STORE=$STORE RESEARCH_NOTES=$RESEARCH_NOTES RESEARCH_MACHINES_D=$RESEARCH_MACHINES_D bash $H/watch_pods.sh 8 >> $LANE/evidence/watch.log 2>&1"
echo "watcher: $(tmux -f /exec-daemon/tmux.portal.conf ls 2>/dev/null | grep epoch-watch)"
