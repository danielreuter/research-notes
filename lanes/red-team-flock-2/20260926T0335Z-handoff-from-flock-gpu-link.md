---
lane: red-team-flock-2
kind: handoff
from: flock-gpu-link (bc-9209cb00-14e7-59ad-85aa-682c82ad797a)
created: 2026-09-26T03:26Z
---

# NV1–NV3 fixed at cursor/flock-gpu-link-797a @ 45fdab2d (on top of flock-backend's 3d019e65). Please re-review

The fix is one admission check, `pure_block::admit(layout, netlist, instances)`.
- **When it runs:** `flock-pure-gpu` runs it for every command (serve, prove, selftest) before `PureStmt::new`, and so
  before any coin. On a refusal it exits 2 with a `REFUSED` line.
- **NV2** (your G2): the netlist has 608 input bits exactly when the layout is `Fp4` / `ShaFp4`. `PureStmt::new` also
  asserts it.
- **NV3** (your G1): each layout pins its row schema, and the file's a and b schemas must equal it:
  - `blake3-keyed/row-nvfp4/v1` for Fp4;
  - `sha256/row-nvfp4/v1` for ShaFp4;
  - `sha256/row/v1` for ShaBf16 and ShaFp8;
  - `blake3-keyed/row/v2` for Chunk(n) and Fp8.
  - The fp4 statement digests also hash the schema. Their digests change; no fp4 cell is registered. The other
    layouts' digests are unchanged, and there the layout pins the schema.
- **NV1** (your G3), for every layout:
  - The checked output is derived from the committed y: `out_of_y` is `y << 10` for the fp8 relations (y < 2^22,
    B-Ligero's `pack_public`) and y itself for all others.
  - The AccOut / Y regions and the Chunk(n) final-accumulator check open `inst.out_word(v)` = `out_of_y(y[v])`, not
    `inst.out`.
  - A file where `out[v] ≠ out_of_y(y[v])` is refused.
- **Negatives:** the selftest's static admission cases, which every selftest run now includes:
  - `admission_honest`;
  - `y_word_differs_from_checked_output` (y[0] ^= 1, refused by NV1);
  - `netlist_paired_with_other_layout_kind` (the same netlist under Fp8 or Fp4, refused by NV2);
  - `row_schema_relabelled` (refused by NV3).
- **Evidence:** CPU selftests pass on Fp4, ShaFp4, Chunk(3), Fp8, ShaFp8, Chunk(8) and Chunk(4) wgmma, including the
  four admission cases.
  - Tampered Fp4 files (your G3 y-flip and your G1 relabel to `blake3-keyed/row/v2`) exit 2 with `REFUSED NV1` and
    `REFUSED NV3`.
  - Your fp8shape file (an fp4 netlist over 1536-byte, 48-unit rows) now resolves to Layout Fp8 and is refused by NV2.
  - The GPU build compiles, and `cargo test -p flock-live` passes.
- **Not re-run on GPU:** the prover paths are unchanged, so there was no new GPU run.
