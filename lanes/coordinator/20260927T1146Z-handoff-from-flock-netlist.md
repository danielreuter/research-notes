---
id: coordinator/20260927T1146Z-handoff-from-flock-netlist
campaign: verity
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: PR #83 @ abca66e8
cursor:
  subagentId: "bc-ff572e70-b0e7-5094-85be-13ff9ddc4d6a"
---

# Estimate: one more pod session (about $2.5, at most $3.5; about 90 min) to GPU-check the new converge and re-record GEMM and attention

**Why.**
- `d16c544e` reorders the host witness's `converge`, which every GPU template goes through, including the two-phase path the
  RMSNorm and SiLU cells use.
- On CPU its inputs equal the old ones on RoPE, both RMSNorms, attention and GEMM, including with the units' outputs given.
  But attention's CPU proofs, and RMSNorm's `tail_swapped` case, run out of memory on this VM.
- It makes `converge` 2.8× faster for GEMM and 1.8× for attention, so the headline cells improve.

**Plan.**
1. Pods: an L40S and a same-DC CPU verifier, found by the same poller as this morning.
2. GPU selftests of RMSNorm Triton, SiLU·mul, attention and GEMM at the current tip: about 60 min.
3. Re-record the GEMM and attention cells: about 20 min.
4. Drain.

**Cost.** About $2.5, at most $3.5. Spend so far is about $33 of $150.

**Headline.** The new GEMM and attention arts would replace `art:4a80e8cb` and `art:02cb7df9`; same pins, faster witness.
Starting now; say if you'd rather I skip it.
