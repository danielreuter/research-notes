---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-rf-normtap · kind: handoff · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-27T00:30Z

# `max_scaled`: a follow-up PR after #95, as an appended `MS` stream class. This replaces my 00:15Z note. CPU only until root approves the estimate.

Root wants it planned as a follow-up, so keep #95 to the guarded max and finish it first.

- **Plan:** `internal/lanes/vllm-coordinator/20260927T0030Z-plan-max-scaled-tap.md`. It covers the design, the acceptance
  criteria, the per-row counts and the estimate.
- **Design change from my 00:15Z note.** Use a new stream class `MS` appended after FIN, with `SRC_BITS["MS"] = 64`, one
  f32 per (slab, row, block), allocated and written only under the same opt-in flag. Don't add a ninth ROW word: it would
  shift O and FIN and ROW's stride, and break thread-leaf mode, `unrank` and the regenerator. With the flag off, the
  layout digest and every byte are unchanged.
- **Store the register the exp2 FMA consumes,** not a recomputed product.
- **Now, on CPU (no pods):** the kernel, layout and IR changes and the CPU tests, on a branch stacked on #95. Then a
  WAIT checkpoint.
- **Pods:** only after root approves the estimate (about $8 expected, $10 cap: L40S about 3 h, H100 about 1.25 h, gate
  (b) about 0.6 h). I'll post the approval here.
