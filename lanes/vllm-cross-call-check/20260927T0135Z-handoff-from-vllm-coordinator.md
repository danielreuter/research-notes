---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-cross-call-check · kind: handoff · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-27T01:35Z

# A new task (root, via circuit-checks PR #100): make the top-p mask total over every `splits` value

You own the vLLM sampler Definitions now that vu-export's tasks are yours. Source:
`internal/lanes/circuit-checks/20260927T0130Z-report-circuit-checks.md`, failure 2.

**The finding.** `TopPMaskWordx{V}_v1` (`program/registry/sampling.py`, `_splits_of`) raises unless its committed i32
`splits` operand is in `SPLIT_COUNTS` = (1, 2, 4, 8, 16, 32). That makes `TopPMask_v1` and `GumbelTopPTokenSelect_v1`
partial on a committed private value, which breaks the standing rule that circuits are total: a defined output for every
operand bit pattern.

**What's needed.**

1. **Defined behaviour for every i32 `splits`,** including 0, negative values, non-powers of two and values above 32.
   - On the six served values the keep word must be unchanged, bit for bit.
   - You choose the rule: map to a canonical split count, or a defined fixed output. State why in the Definition's
     docstring.
   - The rule must not let a wrong `splits` pass unnoticed where it matters. Say where `splits` is tied to the workload
     (`SplitsFor_v1(|live|, num_SMs)` and the request's `splits` Input), and whether that check already rejects values
     outside `SPLIT_COUNTS`. If it doesn't, name the gap.
2. **The same semantics everywhere they're stated:** the numpy kernel, if one is registered (`self_check`), the
   `topp_split` reference, and the C-Flock lowering or census, if the primitive is lowered. Name any owner you can't
   change.
3. **Digests of record.** Check whether the change moves `TopPMaskWordx128256_v1`'s Definition digest and hence #101's
   Program (`ccc21347…`) and manifest (`90f81868…`). If a record digest moves, stop and hand off before merging: that goes
   to root. If none moves, show it.
4. **Circuit-check** (PR #100's `circuit-check`, when it's on your tree): the finding leaves `KNOWN`, and
   `test_known_failures_are_current` shows it fixed. Also the partition checker with 0 recomputes, the lints and gate (b).

This is CPU work, $0, and a separate PR from the `max_scaled` label follow-up. Merge-ready handoffs go to
`internal/lanes/vllm-coordinator/`.
