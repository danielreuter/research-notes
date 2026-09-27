---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: coordinator · kind: handoff · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-27T17:25Z

# Merge request: PR #169 @ 0fcbcd21 (the top-p split reference made total): APPROVE

The lane's handoff is `vllm-coordinator/20260927T1645Z-handoff-from-vllm-cross-call-check-topp-halves.md`. The details are private, at
`private/topp-split-halves-response.md`; this note carries only the verdict.

- **Merges:** clean into main e40fa730. It touches `registry/topp_split.py` (28 lines), `registry/sampling.py` (10 lines) and a new test,
  `tests/program/test_topp_split_halves.py`.
- **No digest moves.** On main and on main + #169: `TopPMaskWordx128256_v1` is `b7202a75…`, `TopPMaskWordx16` is `120f838f…`,
  `TopPMask_v1` is `7ff6257a…`, `GumbelTopPTokenSelect_v1` is `d02d288d…` and `GumbelTokenSelect_v1` is `1248d7b8…`. So row #101's
  Program and manifest are unchanged.
- **Tests:** my jdiff of main against main + #169 over `tests/program`, the lints, by-name, imports and flock's `test_ir_sampling`:
  6 new tests pass; 0 changed outcomes, 0 new failures or skips.
- **A follow-up the lane names:** #125's circuit twin should take each lane's own half's stop bit. That's for #125's owner.
