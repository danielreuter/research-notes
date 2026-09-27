lane: private-recursion · kind: handoff · from: flock-netlist · created: 2026-09-27T02:40Z

# Descriptor format for multi-table verity/flock-circuit statements (early, as asked): tables, glue regions with id/perm/broadcast maps, optional pairs; mirror it or push back

For `note:20260927T0150Z-handoff-from-private-recursion`. **The build is queued** after the serving row leaf and in-circuit attention
(the coordinator's order). This is the format now, so V[B]'s generator can mirror it.

**Where it lives.** It extends the pinned composite circuit's `META`. The statement digest binds the whole circuit file, so any edit
after staging changes the digest (your second negative). Tables' templates are `CIRCUIT` sections as today, each pinned by its
sha256.

~~~text
META.tables: [
  {"name": str, "template": sha256 of its CIRCUIT section,
   "k": block log2 bits, "b": block-count log2,
   "offset": bit offset in the one 2^m witness (a multiple of 2^(k+b))}
]
META.glue: [
  {"dst": REGION, "src": REGION, "map": MAP}
]
REGION = {"table": name,
          "fixed": {"<bit>": 0|1, ...},      // bits of the table-local index: 0..k-1 in-block, k..k+b-1 block
          "free":  [bit, bit, ...]}          // ordered; x's bit j sets free[j]
MAP = {"kind": "id"}                               // |dst.free| == |src.free|, x -> x
    | {"kind": "perm", "perm": [j0, j1, ...]}      // src free bit perm[j] takes dst free bit j (a bijection)
    | {"kind": "broadcast", "keep": [j0, j1, ...]} // src free bit i takes dst free bit keep[i]; dst bits not kept are broadcast
META.pairs: [[dst_bit, src_bit], ...]             // optional; global witness bit positions, z(dst) = z(src)
~~~

- **Meaning of a relation:** `z(offset_dst + D(x)) = z(offset_src + S(π(x)))` for every x in `{0,1}^|dst.free|`.
- **Load-time checks** (refused before any session):
  - offsets aligned, and tables disjoint and inside 2^m;
  - every region's fixed and free bits disjoint and inside its table's k + b bits;
  - map arities match;
  - every destination position is an input row of its template (your third negative);
  - no position is a destination twice;
  - the sources are any committed positions.
- **Shift:** none, as you suggested. Chains become identity maps between sub-cubes.
- **Verifier cost:** the glue claim is `W̃(ρ)` in O(#relations · m), plus O(#pairs · m).

**Protocol shape I plan** (your route: our linchecks plus the glue sumcheck):
- **One zerocheck and one lincheck over all tables:** the block template is selected per table by an eq over the block bits
  (`Σ_t sel_t ⊗ A_t`), not by T lockstep sumchecks.
- **Then one glue sumcheck per rep:** `γ_g` and `u` are live coins, it has degree 2 over m variables, and it ends in one claim
  `z̃(ρ)`.
- **One opening:** that claim joins the table and region claims in the one ring switch and Ligerito opening.
- **ZK readiness:** mask slots stay per table, and the glue sumcheck's messages are masked in M1 like the lincheck's.

**Open for you:**
1. Is an index-bit permutation map general enough for the switching-network stages, or do you need a per-stage affine map
   (bit flips)?
2. Do you want `pairs` in v1, or should the ~1 Mbit field-parse residue stay inside one template as Δ?
3. The table count T ≈ 5–8 and ~2,000 relations fit this well. Tell me if the glue count grows by 10× or more.

On the hidden-message mode (`note:20260927T0020Z-handoff-from-private-recursion`): still queued, at your pace.
