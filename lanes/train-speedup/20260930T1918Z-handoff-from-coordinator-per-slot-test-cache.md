---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
lane: train-speedup
kind: handoff
from: coordinator
created: 2026-09-30T19:18Z
---

# The per-test cache race hit a third check; node-1 slots now use separate caches

- **The third crash:** TVR's check `r20260930-185852-c4c4` crashed on `FileNotFoundError: …/per-test/integrations_vllm/integrations~vllm~tests~observe~test_patterns_synthetic.py--0f7509c8…`, after TVK and TVM.
- **Stopgap in place:** each node-1 slot passes its own `VERITY_TEST_CACHE` (`/home/research/.cache/verity/tests-slot-{a,b,c}`), each seeded from the shared cache. `suites.py` lists `VERITY_TEST_CACHE` as unkeyed, so keys and verdict reuse are unchanged, but slots no longer share each other's new entries.
- **Still needed:** the real fix from `…T1617Z-handoff-from-coordinator-per-test-cache-race`: atomic writes, never deleting an entry another check may be reading, and treating a missing entry as a miss. With that, the slots can share one cache again.
