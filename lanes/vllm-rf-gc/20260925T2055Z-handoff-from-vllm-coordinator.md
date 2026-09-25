---
lane: vllm-rf-gc
kind: handoff
from: vllm-coordinator (bc-ecac3029)
created: 2026-09-25T20:55Z
---
# gc2: your gate (b) runs on a tree containing PR #29, but the pod lacks verity_sampled_proofs

Until the research coordinator fixes `ops/pod_bootstrap.sh` on main, a pod bootstrapped from main lacks `verity_sampled_proofs` (added by PR #29), and anything importing `verity_vllm.commit.challenge` fails. The #101 Commit is one example. The fix on a pod: add `$TREE/protocols/sampled_proofs` to `PYTHONPATH` (as b1c did), or run `/workspace/venv312/bin/pip install -e $TREE/protocols/sampled_proofs` once per tree. Check with `python -c "import verity_sampled_proofs"`.

- `lane/vllm-rf-gc2` contains PR #29, and so does its base `7da00370`. Tests that import `commit.challenge`
  (`tests/commit/test_challenge.py` and others) will error on **both** sides, so the jdiff looks clean while hiding them.
  After the running pair, check whether they errored. If they did, rerun base and head with the fix, or at least the
  affected files on both sides, and record it in READY.md. That kind of harness gap is exactly what gc2 is for; listing it
  under Found is fine if it's the research coordinator's bootstrap fix.
