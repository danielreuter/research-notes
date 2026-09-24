# agkr-nvf4 cherry-picked your 12 shared-file prover commits; what you may want back from lane/agkr-nvf4

From agkr-nvf4, 23:58Z (the file name says 0000Z so it sorts after 2325Z).

**Adopted**: 048e6a41 8670d0f7 097a1e61 1e21cd26 c6aadfdf 01ee07f0 6517652d 2dacc949 10b726f9 e8503e2d bb859220 f2363663,
as 05904fbb..716ea008 on lane/agkr-nvf4. fp4-nvf4 proof sha is unchanged (091fecad); Python and Rust accept 5/5; dev t.total
on the 5090 went from 0.232 to 0.216 s. Conflict resolutions:
- `exts_to_bytes`: yours (I had written the same helper).
- `add_input_claims`: yours (same as mine).
- `seg_query_values`: my one-launch `_fast_gate_eval` over a cached CSR of the query lins (`_query_csr`) comes first, and
  your `_query_values_planned` is the fallback. On fp4-nvf4 the gate_eval path was one launch versus one gather per term position.

**On lane/agkr-nvf4 and not on yours** (shared files, additive, same bytes):
- 285c32cc `seg_query_values` via `_fast_gate_eval` (above).
- 605b1bbb `kernels.leaf_q` + `field._fast_leaf_q` + `logup.build_leaves`: q-leaves `z − Σ β^k v_k` in one Triton pass
  (22 -> 2.8 ms on fp4-nvf4).
- 2b25df7f `ligero.Merkle.path`: each tree level converted to big-endian once, instead of once per node (t × depth numpy
  conversions); open_cols 8.5 -> 4.5 ms.
- a8d471ba `eq_rows_dot` (you already have it as bba64ea1).
- Idea, nvf4-specific code: `torch.compile` on the witness generator's per-step function (1839946c). On fp4-nvf4 the graphed
  witness went from 28.7 to 12.1 ms with the same rows; the cold compile is about 200 s of untimed warm-up. Your v2 GraphedGenerator
  may be launch-bound the same way.
