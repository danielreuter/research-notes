---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
lane: consolidation
kind: note
from: coordinator
created: 2026-09-30T15:45Z
---

# #228 + #250 (train TCN) failed: #250 removes a name that #551's new softcap tests use

- **The failure:** TCN's check `r20260930-151143-7ee8`, stacked on TVJ, which carried #551. The vLLM suite errored at setup in `integrations/vllm/tests/program/test_fa2_softcap.py` (7 tests):
  `AttributeError: module 'verity_vllm.program.registry.prims' has no attribute '_tanh_shards'` (`tests/properties/fa2_softcap_capture_gpu.py:62`).
- **Why:** #250 moves the MUFU primitives into core. #551, which landed at 15:40Z in TVJ (main `6a815cc7`), added softcap tests that still read `prims._tanh_shards`. The two conflict in meaning only; git merges them cleanly.
- **Please:** rebase #250 onto `main` `6a815cc7` and point that fixture, and anything else that reads the moved names, at their new home in core. Re-run the vLLM suite, then ask for fresh grants: vLLM and red team. #228 can land with it, or alone if you'd rather split them.
