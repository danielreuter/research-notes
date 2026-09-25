---
lane: agkr-fp8
kind: handoff
from: agkr-nvf4
created: 2026-09-25T01:10Z
---

# agkr-nvf4 took your 5034767f and 3be6a35f; nine shared-file prover commits on lane/agkr-nvf4 you may want (all same-bytes)

**Adopted**: 5034767f (the key → row map in multiplicities) and 3be6a35f (your keep rule), as 90e1fe97 and 6d13c3e4. In the
keep-rule conflict I took your rule over my c3982dd5, which was "≥ 30 GB and 16·size ≤ free + allocator cache". There is now
one rule on both lanes, and on the 5090 both keep.

**On lane/agkr-nvf4 and not on yours** (shared files, same proof bytes; the times are dev, fp4-nvf4 at 4096 VUs on the 5090):
- e1bcf472 `gkr_packed._inputs`: the phase-1 round operands in one pinned non-blocking H2D, and `sumcheck_packed.to_dev` pinned.
  t_arith 54.5 → 51.8 ms.
- 0b7dbb3a `logup.build_leaves(..., out=)` + `logup_packed.leaf_buffers`: the leaves are built straight into the ext-table
  graph's static buffers, and `prove_fs_ext` skips the copy when the data_ptr matches. t_lookup −1.3 ms.
- c7bfa957 `kernels.combine_level_kernel` DEINT/T4OUT + `combine_leaves_into`: the LogUp tree's leaf level in one kernel.
  t_lookup 44.7 → 42.0 ms.
- 9c29e9de `build_leaves`: `torch.empty`, and only the padding is initialised. t_lookup −1.5 ms.
- 9a17b5b7 `add_lookup_claim`: the pad term in closed form, λ(1 − Σ_used eq). open_acc −0.8 ms.
- 19bda30a `scatter_terms` grid (ncols, unit blocks), columns fastest for L2 reuse. open_acc 21.7 → 19.2 ms.
- 024f1cfc `gate_eval` grid (g_n, copy blocks), gates fastest (the GFAST constexpr; the old order is kept past 65535 blocks).
  t_mults 10.0 → 7.2 ms.
- 95343488 `field._h2d`: `t_ext` / `t_exts` / eq_table's point via pinned non-blocking H2D. ~1.5 ms.
- da4d2b44 `ligero.Opening.raw`: w / qc are serialized once from one D2H numpy array and reused by `Proof.to_bytes` and the
  transcript; `exts_to_bytes` gets an ndarray fast path, and the opened columns come back through pinned memory.
  open_cols 5.9 → 2.4 ms, to_bytes 5.5 → 3.8 ms.
- 79f00fd3 `gkr_packed` phase 1: `_inputs_static` (e_lo limbs, e_hi, eq_x for round i+1) is queued behind round i's message
  D2H, which is event-synced. t_arith −1.3 ms.

Tried and not worth it: rank1_add columns-fastest (open_acc +1.8 ms), and a logup_ext_ip BLOCK_K / num_warps sweep (128 / 4 is
best; the other settings spill).

**nvf4-only** (not shared): b7cec878 is a statement change, BOOL_QUADRATIC (bits as b·b = b) plus PAIRED range queries. It is
held for red-team-lk per the coordinator's 0050Z note.
