---
lane: vllm-rf-epoch
kind: handoff
from: vllm-coordinator (bc-ecac3029)
created: 2026-09-25T22:55Z
---
# For the final rebaseline run on merged main: `sampled_proofs` on PYTHONPATH

When you merge main for `rebaseline.py run/write`, the tree contains PR #29. `fee32f05` doesn't cover scripts that export
their own PYTHONPATH (it only sets it inside `pod_bootstrap.sh`). Append `$T/protocols/sampled_proofs` in whatever runs the
regression and Commits there, and log the import check. Your recording tree `ad8050e9` predates PR #29, so the running rows
are unaffected.
