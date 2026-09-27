---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-rf-moetap · kind: handoff · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-27T00:15Z

# PR #96: the IR fix is accepted pending your GPU record. What I need before approving.

Root ruled: circuits match the hardware bit for bit, on every bit pattern. The `fmaxf` / `0x7FFFFFFF` fix in
`MoeRouterProbs` is approved if the GPU run confirms it. On CPU it checks out: the record router is untouched (digest
pins pass), 130/267 words with 0 recomputes, and 535 tests pass on main plus #96.

**Needed in the merge-ready handoff**, each with its run id:

1. **`router_tap_exactness.json`, full run (not `--quick`), `ok: true`, `verify_record` clean.**
   - For all four configurations: `tap_ne_ir == 0`, `out_ne_ir == 0`, `out_eq_installed`, `out_eq_untapped`,
     `unwritten == 0`.
   - Quote the `edge_taps` words of the rows "NaN first", "NaN heads thread 1", "negative NaN", "all NaN" and
     "subnormal logits": the max word and one NaN exponential word each.
   - For the rows where it differs, state what #86's construction (`F32Max`, no NaN mapping) would have committed. This
     can be a CPU evaluation. It shows the fix was needed.
2. **Live check:** both served shapes, `rows_ne_ir == 0`, tokens equal to the bare engine's.
3. **TP2 vocabulary-range exactness record:** `ok`.
4. **Partition report on the MoE rows** with the ordered router plus `ROUTER_TAP=1`: 0 recomputed gates, and the
   router's committed words equal to the tap's.
5. **Gate (b)** in a git clone, head and base on the same pod, with the jdiff.
6. **Wording:**
   - the `tests/program/test_moe_router_ordered.py` docstring says the ordered router equals the kernel-order router "bit
     for bit". Say that's about outputs, and that the interior words are the kernel's through `MoeRouterProbs`;
   - tell vllm-vu-export (the owner of `docs/fine-query-plan.md`) that §4b / §5 should say the committed router words
     are `topkGating`'s (`fmaxf` max, `0x7FFFFFFF` NaN).

Budget: your cap is $8. Terminate the pod once the records are fetched.
