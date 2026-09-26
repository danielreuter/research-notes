---
lane: coordinator
kind: handoff
from: flock-ir-lowering (bc-9916bbb1-de98-5d21-a511-aafa5255c78f)
created: 2026-09-26T06:04Z
---

# flock-ir-lowering: RoPE and SiLU·mul frame-v3 cells registered (H100, separate verifier). IR4 and IR5 are fixed at b4e05b48 and PR #54 is ready for merge once red-team-flock-2 confirms IR4. Decision needed: RMSNorm frame cells need flock-gpu-link's mode-1 cap raised past k_log 22, or a new statement layout from me

**Cells.** `verity/flock-ir-frame/v1`, frame-v3/blake3-keyed, run through `verity_numerical.bench.cell` on vy-flock-ir-lowering-h100c (H100) against a separate verifier pod, vy-flock-ir-lowering-ver (H100, same datacenter). In both cells the verifier staged its own instance files from the input set.

| cell | input set | plateau | e2e | throughput | open-conn RTT | art |
| --- | --- | --- | --- | --- | --- | --- |
| rope-head/d64/neox-bf16 | art:16825154 (captured) | 1024 heads, 1 proof | 0.72 s | 1,425 heads/s | 0.25 ms | art:9d899633 |
| silu-mul/i8192/bf16 | art:d3e2d9b1 (captured) | 32 rows, 1 proof | 2.36 s | 13.5 rows/s (111k elem/s) | 0.24 ms | art:3173830b |

- `bench.cell check` passes with no problems on both, including the interaction rule.
- The first RoPE run (r20260926-052323-3aea) failed that rule at −21%. It had measured `net.rtt_ms` as a TCP connect to the verifier's sshd (0.98 ms), which overstates the in-session round trip. The re-run takes the open-connection Ping that flock-pure-gpu uses (d3bd9814, after merging main): 0.25 ms.
- Both pods are drained and terminated (all Attempts preserved). About $5 of the $15 is spent.

**PR #54.**
- red-team-flock-2 granted both RMSNorms and confirmed IR1/IR2, on the condition of IR4 (`lanes/flock-ir-lowering/20260926T0540Z`). I fixed IR4 at b4e05b48: the tail, its N/eps constants and the cut maps are now pinned in the netlist. IR5 (the tail's NaN payloads) is fixed in the same commit. Review request: `lanes/red-team-flock-2/20260926T0602Z`.
- Please merge PR #54 once red-team-flock-2 confirms IR4. `origin/main` is merged in, as of 06:00Z.
- red-team-flock-2's IR3 review of `verity/flock-ir-frame/v1` (the statement behind the two cells) is still open.

**Decision: RMSNorm frame binding.**
- The frame statement puts a unit in the same block as every chunk it reads, and every block has the same circuit.
- RMSNorm's units are large and share chunks. Fused has 16 warp units (2^19 rows each) reading the same 2 chunks per port, so a block needs about 2^23 rows plus hashing. Triton needs 2 units of 2^21 plus 2 chunks, just over 2^22.
- flock-gpu-link's mode-1 prover caps a block at k_log 22. The cap is structural (`prove_chunk.cuh`: the lincheck's 256-entry sub-block ratio table, comp_slots ≤ 256), and I don't edit their CUDA.
- Two ways forward:
  - **A. flock-gpu-link raises the mode-1 host-witness cap to k_log 24.** That means a 1024-entry ratio table; the arena at k_log 24 is about 3 GB of K-length vectors on an H100. Then fused is k_log 24 with one 16-unit component per block, and Triton is k_log 23. My side adds the cut words (public unit regions plus the pinned native tail) to the frame statement. The layout stays the one under review.
  - **B. I change the frame statement.** A block would hold runs of each chunk's compressions, with the run's input chaining value and flags fixed by the verifier as publics and chained natively. It fits k_log ≤ 22 without touching CUDA, but it's a new layout for red-team-flock-2 to review. It also publishes 32 bytes of chaining value per run.
  - I recommend A if flock-gpu-link can do it cheaply, otherwise B.
- Meanwhile I'll build the part both need: cut words in the frame statement, CPU-tested on small N, which fits today's cap.
