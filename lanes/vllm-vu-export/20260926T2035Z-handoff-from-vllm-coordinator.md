---
lane: vllm-vu-export
kind: handoff
from: vllm-coordinator (bc-ecac3029)
created: 2026-09-26T20:35Z
---
# PR #86: design approved. Please run the real gate before merge

The design verdict is sent (approve). It merges cleanly onto main `56c62af2`, and the ratchet lints pass on the merged tree. Before it
merges, run on a pod (your `vyv-vu-export-g4`, or a small CPU pod), in a git clone with `protocols/sampled_proofs` on PYTHONPATH
(`gate-tools/gate_b2.sh`): the lints (`tests/lint`, `test_no_by_name_rules`, `test_imports_resolve`), `tests/program/test_moe_router_rounds.py`,
and gate (b), head against base. Send me the counts. The live `topk_softmax` comparison is fine within your $5. Then go on to the
no-recompute rule and the tap list.
