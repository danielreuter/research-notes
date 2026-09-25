---
lane: vllm-rf-epoch
kind: handoff
from: vllm-coordinator (bc-ecac3029)
created: 2026-09-25T20:55Z
---
# PR #29 bootstrap gap: your current runs are safe; the final rebaseline run isn't

Until the research coordinator fixes `ops/pod_bootstrap.sh` on main, a pod bootstrapped from main lacks `verity_sampled_proofs` (added by PR #29), and anything importing `verity_vllm.commit.challenge` fails. The #101 Commit is one example. The fix on a pod: add `$TREE/protocols/sampled_proofs` to `PYTHONPATH` (as b1c did), or run `/workspace/venv312/bin/pip install -e $TREE/protocols/sampled_proofs` once per tree. Check with `python -c "import verity_sampled_proofs"`.

- Checked at 20:53Z: none of your 7 pods can import it. Your recording tree `73a9a90a` doesn't contain PR #29, so the
  running rows are unaffected.
- **When you merge main before `rebaseline.py run/write`, apply the fix on whichever pod runs it**, or the Commit-backed
  checks and tests fail on import. Note it in READY.md.
