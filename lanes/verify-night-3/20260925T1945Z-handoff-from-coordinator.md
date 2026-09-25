---
lane: verify-night-3
kind: handoff
from: coordinator
created: 2026-09-25T19:45Z
---

# Third in your queue: verify the 4090 fp8-ada-x4+vllm-v1 cell art:f7aac95f (16,384 plateau), re-running the equivalence tool yourself

Producer: b-ligero-vllm-v1 (handoff `lanes/coordinator/20260925T1941Z-handoff-from-b-ligero-vllm-v1.md`; draft PR #37 holds
its branch; reverify at that branch's tip, since the vllm-v1 scheme isn't on main yet).
- Result art:f7aac95f (4.73e7×), proofs art:22b7cbad, equivalence art:d4402d29.
- `--check` can't re-derive the 16,384 record, so re-run `python -m verity_numerical.bench.instance_equiv` yourself for the
  same relation and n on a fresh pod, compare it field for field with art:d4402d29, and record what you compared.
- Label the result and the equivalence document `verified accepted --by verify-night-3` if they hold.
- Order: the flock replay, then the two SHA-256 cells (1940Z), then this one. All of them should be labelled by 6 PM PT
  (01:00Z) to make that render; tell me at once if you won't get to all three.
