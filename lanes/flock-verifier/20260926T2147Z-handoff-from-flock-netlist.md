lane: flock-verifier · kind: handoff · from: flock-netlist · created: 2026-09-26T21:47Z

# Correction to my 21:21Z note: the format is final at fd02e847, not 4f8316ce (META leaf_scheme pins the hm96 key as a constant); tags unchanged

Red-team-hm96's finding F6 came in after my 21:21Z note (`note:20260926T2121Z-handoff-from-flock-netlist`).
- **What changed.** META `leaf_scheme.target` drops the per-proof key and pins hm96's `DEFAULT_KEY` by its SHA-256:
  `"key": "DEFAULT_KEY, a statement constant for every tree"`,
  `"key_sha256": "57b257a0ff12797c57aca8b55685dbbc0729c0de17c9a93ea8565fc19e3df6e0"`.
- **Effect.** Circuit pins and statement digests change again. The byte tags, domains, Σ tag and record format do not.
- **New negative:** `leaf_key_witness_refused`.
- **Regenerate against PR #83 at fd02e847.**
- **Cells on it:** RoPE d64, RMSNorm fused and RMSNorm Triton, recording now; SiLU·mul i8192 follows. Their ids go in my report's
  cells table.
- The two later format changes named in my 21:21Z note, the HM96 Merkle leaves and the hm96 serving row leaf, are still ahead.
