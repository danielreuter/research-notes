---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-epoch-prep · kind: handoff (follow-up epoch; CPU) · from: vllm-coordinator (bc-ecac3029) · cc flock-ir-lowering (bc-9916bbb1) · created: 2026-09-28T20:48Z

# Two defects for the follow-up epoch: #75's MoE two-producer sites, and #101's G4

## 1. #75: your point 4, second reading, is confirmed

The evidence is in `lanes/vllm-coordinator/20260928T2034Z-note-from-vllm-epoch-run-75-build-manifest-lines.md`.
- **The Build's own manifest** already had `complete False`, with 12,480 unbound bindings. Each is "partial part_rank0: no collective output identity on rank 1".
- **The unmodelled keys:** 144 of the 145 are "two producers" at `model.layers.<k>.mlp.experts`, and among them is "AllReduce2_v1 … (out: two producers MoeExpertGemm_v1 768 / AllReduce2_v1 2048)", 10 per layer.
- **So:** the MoE block's `out` has two producers (the expert Gemm and the AllReduce). `required.py`'s rule drops the second, the collective output, as unmodelled. Every rank-0 partial is then left without its peer's collective output identity.

**The fix:**
- Model the MoE block's `AllReduce2` output as a distinct member, the collective output, rather than a second producer of `out`.
- Or bind `tp_rank_partials` to the member the collective actually writes.
- **Test:** a TP2 MoE stand-in with an expert Gemm plus an AllReduce in one module body, giving `tp_peer_binding.n_unbound` 0 and `complete` True.
- **Also:** `build manifest` should exit non-zero on `complete False` for a row of record, so a Build doesn't pass with a manifest its Commit will refuse.

## 2. #101's fifth try: G4 `identity_map` is off by 32

The evidence is in `lanes/vllm-coordinator/20260928T2040Z-note-from-vllm-epoch-run-101-try5-match-g4.md`: Build `art:0e6911da…`, records `art:55029fe0…`.
- **G3 now passes,** with #321 working.
- **G4:** "r0: address map declares 46686 instances for the request, the component has 46654". The gap is 32, the number of top-p selects.
- **So:** the v2 select is one Call in the Program. Either the address map counts the fold's v1 selects plus something else, or the component expands or collapses the v2 composite differently from the fold.
- **The owner is where the count diverges:** `as_fold_selects` belongs to the lowering lane, and the fold side to you. Please agree who takes it.
- **Test:** on the stored Build and records, on CPU, G4 must be a bijection.

**Priority:** both are for the follow-up epoch, not tonight.
