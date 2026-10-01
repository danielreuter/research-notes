---
lane: circuits-bool-rope
kind: report
created: 2026-10-01T08:01Z
status: open
---

CHECKPOINT 43d7e4309 (08:02Z) [open] inbox: switch's P9 handoff - fixed in 43d7e4309 (CompositeDefinition, no allowlist); handoff to circuits-bool-switch sent
CHECKPOINT 43d7e4309 (08:01Z) [open] inbox: no-ROM ruling - RoPE reads no table and makes no MUFU Call; proofs split - branch is on the frozen proofs-ir head 46c768b2c (not on main yet, no rebase); element-wise - no local copies: RopeOut_v2 traces the same core fp builders F32Mul_v3/F32Fma_v3 trace, inline (sub-Calling them is 2,430+4,485 ANDs plus the cast vs 2,966, and adds 32-bit interiors); merge with bool-elementwise has two trivial conflicts (pins.json sorted keys, _boolean_roots docstring)
CHECKPOINT 43d7e4309 (08:01Z) [open] RoPE family Boolean on cursor/bool-rope-8c79 @43d7e4309: RopeOut_v2/RopeOutAdd_v2 2,966 ANDs each, RoPE_v2 q 1,708,416 / k 569,472; agrees with the words (22^4 specials + 90k/half, 81k heads per served shape); circuit-check green incl. served shapes (art:803fc1b9); as Calls fail gate-recomputed (shared operand decode) - ruling needed, see lanes/circuits/20261001T0650Z-report-from-circuits-bool-rope-four-green-recompute-ruling
