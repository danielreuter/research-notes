---
id: 20261001T1602Z-handoff-from-proofs-root-yes-and-m0-gates-1a-5-9
campaign: proofs-hillclimb
lane: proofs-bf16-hill
kind: handoff
status: open
repo: verity
origin: proofs (bc-8416bc72-c4cc-5551-93a8-b14a6e5f95d4)
---

# 1a, 5 and 9 no longer wait for M0; build them to M0's gates

to: proofs-bf16-hill. This updates `note:proofs-bf16-hill/20261001T1548Z-handoff-from-proofs-owner-yes-prover-changes-1a-5-9`.

**The yes is final.** Root ruled yes at 8:45 AM PDT, as coordinator of both M0 and the research owner
(`note:proofs/20261001T1545Z-handoff-from-verity-root-c-flock-prover-and-554-yes`). The changes don't wait for M0, so
drop "nothing lands until M0 or Daniel agrees". The owner's conditions still hold: byte-identical proofs and verdicts at
each measured K, and one negative control per change.

**M0's how-to** (`note:proofs/20261001T1546Z-handoff-from-flock-netlist-zerocheck-lincheck-answers` §3). Treat each item
as part of the change's gate:
- **1a:** keep `zerocheck_first_round_cpu_structured<14>` as a same-job control behind a switch, as `FC_RING_GROUPED` and
  `FC_ZLIN_BYTEWISE` are, and take the ALU version only if it measures faster. `mcol` is a fixed per-bit map, uploaded
  once per process (§1), so an ALU version computes the same XORs.
- **5:** persistent buffers come out of the arena, or out of memory the arena already accounts for, never beside it.
  The gate includes `rep_reused` = true for rep 1 at K=2048 and K=8192 in the bench buckets. M0 lists today's
  outside-arena allocations: `d_tape`, `d_hin` and the host-slot index arrays, `Hm96Guard`'s tables and midstates, and
  the `DevBuf` pool.
- **9:** nothing that touches the transcript moves: the challenger's observe/sample order, the hm96 tree nonces
  (`tree_cb`) and the salt key. The candidates are the 5–12 ms tree-boundary gaps (a 6 ms `cudaFree`, `Hm96Guard`'s table
  setup).

Targets, order, node-1 slots and reporting are as in the 1548Z note. Node 1 has all 8 GPUs idle right now, so use your 3
slots.
