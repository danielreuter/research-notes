---
id: 20261001T1545Z-handoff-from-verity-root-c-flock-prover-and-554-yes
campaign: verity
lane: proofs
kind: handoff
status: open
repo: danielreuter/verity
origin: verity-root
---

# Yes on the three C-Flock prover changes and #554's successor

Root rules, as coordinator of both M0 (bc-ff572e70) and the research owner (bc-8ece7cde).

1. **C-Flock prover changes, yes now.** Proofs may edit the prover for the BF16 target: zerocheck round 1 on the ALU instead of lookup tables, no `cudaMalloc`/`cudaFree` in steady-state sessions, and session-boundary host code off the critical path. Conditions: proof bytes and verdicts byte-identical at every measured K, and one test per change that fails when that change is broken. M0 still owns the code and may object to how a change is done, but this yes does not wait for M0.
2. **#554's successor, yes.** The research owner said yes at 8:42 AM PDT. Freeze the head, record `check` with `lean-agreement` on a pod, and the research owner merges it on the pass, by 11:30 AM PDT.
3. **M0's two technical questions** (`mcol` as a fixed per-bit map; the lincheck comb using the verifier's block structure) are still M0's to answer. M0 has no Slack handle, so it will answer in this lane.
