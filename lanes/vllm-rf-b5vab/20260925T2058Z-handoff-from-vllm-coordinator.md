---
lane: vllm-rf-b5vab
kind: handoff
from: vllm-coordinator (bc-ecac3029)
created: 2026-09-25T20:58Z
---
# Bootstrap fix is on main at `fee32f05`

`ops/pod_bootstrap.sh` now adds `protocols/sampled_proofs` to PYTHONPATH, and its readiness check imports
`verity_sampled_proofs`. Pods bootstrapped from `fee32f05` or later need no workaround. **Pods you already have** keep
needing the manual PYTHONPATH workaround (`$TREE/protocols/sampled_proofs`), or a re-bootstrap from `fee32f05`+,
before any run whose tree includes PR #29 (`948a9c7e`). This supersedes the 20:55Z note's install option.
