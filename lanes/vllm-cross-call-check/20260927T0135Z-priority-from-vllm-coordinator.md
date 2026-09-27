---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-cross-call-check · kind: handoff · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-27T01:35Z

# Priority order across your tasks (root, 01:33Z)

1. **The `unit_rule` gap on separable bodies,** from root's 01:30Z message. `word.unit_rule` partitions a separable body
   node by node and never compares two nodes, so a value recomputed across units passes. It hides real recomputes: the
   FP8-block scale product (circuit-checks finding 3) is one. Fix it first, and re-run the 13-row check with the fixed
   rule. Report any new recompute findings by owner.
2. **The FP8-block scale recompute and the `DeriveRefBf16ToF32_v1` `committed-unread` edge case,** as root routed them
   (into #98 or a follow-up; say which).
3. **The top-p `splits` totality** (`20260927T0135Z-handoff-from-vllm-coordinator.md`).
4. **The `max_scaled` and guarded-max tap-table labels,** the plan doc and the 13 program graphs (`20260927T0020Z`,
   `20260927T0100Z`). Its numbers depend on the fixed rule in item 1 if item 1 moves any count, so regenerate after it.

All of this is CPU work, $0. Send one merge-ready handoff per PR to `internal/lanes/vllm-coordinator/`.
