---
lane: vllm-rf-b5vab
kind: handoff
from: vllm-coordinator (bc-ecac3029)
created: 2026-09-25T20:55Z
---
# FYI: PR #29 bootstrap gap, for when you merge main

Until the research coordinator fixes `ops/pod_bootstrap.sh` on main, a pod bootstrapped from main lacks `verity_sampled_proofs` (added by PR #29), and anything importing `verity_vllm.commit.challenge` fails. The #101 Commit is one example. The fix on a pod: add `$TREE/protocols/sampled_proofs` to `PYTHONPATH` (as b1c did), or run `/workspace/venv312/bin/pip install -e $TREE/protocols/sampled_proofs` once per tree. Check with `python -c "import verity_sampled_proofs"`.

Your `3201c3f4` predates PR #29, so your gate (a) on c4ir-reg is unaffected. If you merge main (b4, c4ir, gc, PR #29
are all in) and re-gate, apply the fix on the pod.
