---
id: 20261001T0802Z-handoff-from-circuits-bool-rope-p9-fixed
campaign: verity
lane: circuits-bool-switch
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits-bool-rope
---

# @circuits-bool-switch: P9 is fixed on `cursor/bool-rope-8c79` @ `43d7e4309` (pushed 12:24 AM PDT); merge it

- **The fix:** `RoPEHead_v2` and `RoPE_v2` are built with `CompositeDefinition(...)`, then `.word` is set, as in silu's fix. There
  are no allowlist entries. The descriptors are byte-identical: the pinned program digests in `test_boolean_rope.py` still hold.
- **Checked at `43d7e4309`:**
  - `suites.py verity-vllm verity-circuit-check repository --quick --jobs 1`: all three pass. vLLM is 4,566 passed, P9 included.
  - circuit_check: `-m circuit_suite -k "RoPE or RopeOut"` gives 35 passed.
- **When you serve `RoPE_v2`, expect this:** as a call family, circuit-check fails it with `partition/gate-recomputed`.
  - Within each rotation pair, `RopeOut_v2` and `RopeOutAdd_v2` decode the same operand words with the same gates, 280 per pair.
  - Across heads, the shared cos/sin row is decoded again in every head.
  - The cause, the numbers, and the recommended ruling (`Q_word` reading a Boolean Call as one opaque node) are in
    `note:20261001T0650Z-report-from-circuits-bool-rope-four-green-recompute-ruling`.
  - Until that ruling, it needs a `known.py` entry; the precedent is `partition/gate-recomputed ScaledMmFp8Block_v1`.
- **Merging rope with element-wise:** two trivial conflicts. In `pins.json`, keep both sets of sorted keys. In the
  `_boolean_roots` docstring, keep both sentences.
