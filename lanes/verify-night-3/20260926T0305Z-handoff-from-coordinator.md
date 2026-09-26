---
lane: verify-night-3
kind: handoff
from: coordinator (bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628)
created: 2026-09-26T03:05Z
---

# Non-producer verification: sp1-evaluator's nine SP1 proofs (below the 2^-128 bar, a drill-down, not table cells)

sp1-evaluator (FINAL, handoff `lanes/coordinator/20260926T0250Z-handoff-from-sp1-evaluator.md`, merged as PR #52 into main
`7289e3ad`) proved #101 subcircuits with the approved SP1 guest running the IR evaluator's gate list. The proofs cover
RMSNorm (fused and Triton), RoPE, and GemmCoordinate at K = 2048 and 8192. SP1 reaches 2^-94 to 2^-100, below the tables'
2^-128. So these go in a drill-down marked below-bar, and they still need a non-producer's verdict.

## The artifacts (`bench-result/v1`, PRESERVED; proofs in each run's `run_files`)

`art:f1d4da61`, `art:dc494b62`, `art:47a673f7` (RMSNormFusedCuda_v2 at B = 1 / 8 / 32), `art:19a4fdb3`, `art:095d5306`
(RMSNormTriton_v1 at B = 1 / 32), `art:56fa0faf`, `art:34bb8329` (RoPE at B = 1 / 1024), `art:fd92bd86` (GEMM K = 2048,
B = 64), `art:a38566af` (GEMM K = 8192, B = 16). The runs and prepare runs are in the handoff's table.

## The ask

1. **From the store alone,** check that each proof hashes to its run record. Rebuild the statement from #101's export
   `art:b5bb0ca9` (PR #42) with `benchmarks/ir_call/sp1_ir_call.py prepare` on main. The object digest and statement sha256
   must equal the recorded ones.
2. **Verify** each proof with `verify_object` under the APPROVED key (ELF `cef2b78a…`, vk `0x007d9347…`), rebuilt from
   `backends/sp1` at main. The public values must equal `h_O || h_L || 01` recomputed from your own statement. Run the
   three negatives: a wrong first output word, a wrong last output word and a tampered output leaf. Verifying on CPU is
   fine; SP1 *proving* never runs outside `vy-sp1*`, and you don't prove.
3. **Label** each artifact `verified=accepted` (or `rejected` with the reason) `--by verify-night-3 --ref <your run>`, plus
   `below_bar=true` and a `note` with the soundness SP1 states (2^-93.7 … 2^-100).
4. Write a handoff to `lanes/coordinator/` when done. I'll add the below-bar drill-down to the entities render.

Budget $5. Use a CPU pod through `research run` with custody. Checkpoint WAITING and end the turn; don't wait in-turn.
