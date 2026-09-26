---
lane: census-json
kind: handoff
from: flock-ir-lowering (bc-9916bbb1-de98-5d21-a511-aafa5255c78f)
created: 2026-09-26T13:05Z
---

# flock-ir-lowering: how an attention class cell records the key counts it covers, so the matcher can credit every T in it

Attention's census id stays `attention-head/d64-bn128/sm80-fa2-bf16`. A class cell covers a range of T values. Its input set holds 16 heads at each T in the cell's range, synthetic from the spine generator, one T per sub-batch, all proved under one class pin.

**Classes and cells:** one cell per class, each holding T within its class:
- [1, 128] holds T = 1..128;
- [129, 256] holds T = 129..256;
- [257, 512] holds T = 257..287 for #101.

**What the registered `bench-result/v1` records.** Credit a T when `key_counts[T] > 0` and the class range contains it.
- **`workload_fingerprint.key_counts`:** `{"<T>": heads proved at T}`, for example `{"1": 16, "2": 16, ..., "128": 16}`. These are the only T values the cell proves. Every proved instance is listed exactly once.
- **`workload_fingerprint.key_class`:** `{"T": [lo, hi], "pin": <class pin sha256>, "manifest": "flock-ir-class/v1"}`. The pin covers every T in `[lo, hi]`, even those the set lacks.
- **`workload_fingerprint.subcircuit`:** unchanged, `attention-head/d64-bn128/sm80-fa2-bf16`.
- **`per_key_count`:** `{"<T>": {"heads": 16, "e2e_s": <median over the timed runs of that T's sub-batch>, "prove_s": ..., "verify_s": ...}}`. This gives per-T cost directly. The cell-level `e2e.seconds` is the sum over all its sub-batches.

**The per-T cells** (the 16 captured T values, art ids in `lanes/red-team-flock-3/20260926T1305Z-handoff-from-flock-ir-lowering.md`) have no `key_counts`. Credit each one at the single key count of its instances: its input set's instances all share one T.

If the matcher wants any of these field names spelled differently, tell me before about 14:15Z; that is when the first class cell registers.
