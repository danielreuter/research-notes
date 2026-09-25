---
lane: sp1-committed
kind: handoff
from: red-team-standard-hash
created: 2026-09-25T08:20Z
---

# red-team SH: relation-committed/v1 and -vllm/v1: PASS on the guest and tree check; the roots are prover-chosen (R2), so add an instance-set root check

Reviewed d12770c3. Full note: `lanes/coordinator/20260925T0820Z-handoff-from-red-team-standard-hash.md`. Evidence:
art:b11bc6eecb1cbc31144091cfccf8adf774bad527e008a377177eca230b7354fb.

I found nothing wrong in the guest (it hashes the checked bytes, positionally), in the dx/dw publication, in the bindings,
domains and id re-derived from the range, in the vk pin, or in the vllm-v1 framing.

The gap: `committed-verify` accepts whatever roots the statement carries. A statement naming the frozen fp8-ada set's
[0, 1) with the roots of an all-zero VU (y = 0, which the honest guest accepts) passes `check`.

Suggested fix: give `committed-verify` (and vector_run's verify step) an `--instances` recomputation, i.e. the verifier's
own native commit of [lo, hi) of the frozen set, and compare its roots with the statement's. Your `commit()` already
computes this; it is just not used on the verify side. Core-only roots over the true rows equal your Python reference's
(checked for fp8-ada VU 0).
