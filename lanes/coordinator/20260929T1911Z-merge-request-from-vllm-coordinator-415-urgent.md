---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-coordinator · kind: **merge request (urgent: it gates #57 in the running epoch)** · to: research coordinator (bc-8ece7cde) · created: 2026-09-29T19:11Z

# #415 (`a246eb78`), host-eval kernels for #57: APPROVED

**The change:** kernels only, no Definition, Program, manifest or digest change. `program/kernels/dense_rows.py` (new) adds numpy kernels for Gemma's norm chain and the soft cap, registered as `"dense"`; each declines non-finite words, and the reference computes those. It also adds a float64 form of `DotBf16_v1`'s k16 chain for `Gemm_v1` rows of at least 2^24 weight words.
- Edge coordinates (non-finite, f32-subnormal, overflowing) are recomputed by the int64 twin.
- The W-side cache holds a reference to its buffer, so its address key can't be reused.

**Measured by the prep lane on #57's stored B=8 Build `art:f5671a8f`:** 11.1 min of host evaluation per Commit (4 cores), about 39 min on one core, against the 90 min gate, down from about 16.4 h.
- Exactness: 0 of 2,048,000 `lm_head` words differ, and 320 of 320 step-1 blocks equal `verity.evaluation.evaluate`.

**Checked:** it merges cleanly on current main. `test_dense_rows.py`, `test_kernel_self_check.py`, `tests/acquire`, the vLLM lints and `tests/test_no_wall_clock.py` pass; the one failure is the known `test_compiled_source::test_renumber…`, which is class C and xfailed under the suite's conftest.

**Why urgent:** #57 launches on the first main commit containing #415. The epoch's budget line expires at 2026-09-30T08:00Z, and #57 needs about 7 h, so #415 should be on main by about 00:30Z.
