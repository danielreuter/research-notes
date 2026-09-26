---
lane: coordinator
kind: handoff
from: flock-ir-lowering (bc-9916bbb1-de98-5d21-a511-aafa5255c78f)
created: 2026-09-26T07:20Z
---

# flock-ir-lowering: option B is done. `verity/flock-ir-frame/v2` (c53d9148) fits both RMSNorms under the existing 2^22 limit, and all four templates have registered frame-v3 cells on H100 with a separate verifier. The IR3 review request went to red-team-flock-2, with the IR4 tip and covering the RoPE and SiLU·mul cells. Pods are terminated; about $11 of $15 spent

**Option B, as built.**
- A finer cut alone couldn't fit fused RMSNorm. The 16 warps reading a chunk pair are about 6.6M bits against a 4.2M-bit block, at any unit size.
- So v2 splits each chunk's compressions into runs. Every compression's counter, block_len and flags, and every run's chaining input (the key, or the previous run's public output), are verifier-fixed region claims. A chunk's runs therefore chain across blocks, and one circuit serves every block.
- The planner takes the largest run that fits:
  - RoPE and SiLU·mul: whole chunks, as in v1;
  - RMSNorm fused: runs of 4, k_log 22;
  - RMSNorm Triton: runs of 8, k_log 22.
- Cut words are region claims on each unit's cut ports, checked at load against the IR4-pinned tail.
- flock-pure-gpu's limit and parameters are untouched: the CUDA mode-1 cap is k_log ≤ 22, and v2 uses at most 12 of the 16 extra claims.

**Cells.** `verity_numerical.bench.cell`; prover vy-flock-ir-lowering-h100d, verifier vy-flock-ir-lowering-ver2 (both H100, EUR-IS-3). Each verifier staged its own files. Inputs are captured sets. `check` finds no problems on any cell, and all pass the interaction rule.

| cell | input set | plateau | e2e | throughput | open-conn RTT | art |
| --- | --- | --- | --- | --- | --- | --- |
| rope-head/d64/neox-bf16 | art:16825154 | 1024 heads, 1 proof | 0.70 s | 1,470 heads/s | 0.20 ms | art:dd27fdab |
| silu-mul/i8192/bf16 | art:d3e2d9b1 | 128 rows, 4 proofs | 9.73 s | 13.2 rows/s | 0.18 ms | art:8a07b80f |
| rmsnorm-fused-cuda/n2048-eps1e-05/bf16 | art:a261c0c2 | 64 rows, 1 proof | 2.59 s | 24.7 rows/s | 0.22 ms | art:9563d2c8 |
| rmsnorm-triton/n2048-eps1e-05/bf16 | art:9582a734 | 256 rows, 1 proof | 9.65 s | 26.5 rows/s | 0.18 ms | art:63553a6c |

- The v1 RoPE and SiLU·mul cells (art:9d899633, art:3173830b) are superseded by the v2 re-runs; they stay as v1 evidence.
- Fused RMSNorm reached 27.3 rows/s at 256 rows, but that point was flagged contended.
- RMSNorm is host-witness bound: 2.4 s of fused's 2.6 s. A device witness would be the next speedup.

**For red-team-flock-2** (`lanes/red-team-flock-2/20260926T0640Z`):
- It covers the v2 statement at c53d9148, the four v2 cells, and the v1 cells.
- The evidence is 99/99 CPU selftest cases (`lanes/flock-ir-lowering/evidence/20260926T0635Z-frame-v2-selftests.txt`). The negatives include forged flags, a forged chained run input, eps-forged tail words, a forged aggregate, and a unit reading another cut word.
- The IR4/IR5 confirmation (06:02Z, b4e05b48) is still pending.

**PR #54:** ready for merge once red-team-flock-2 confirms IR4 and grants IR3 on v2. `origin/main` is merged in as of 06:00Z.
