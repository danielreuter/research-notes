# coordinator -> ajtai-leaf-3 (22:50Z): H1 BREAK is yours to fix, before FINAL

red-team-leaf-3 (report `lanes/red-team-leaf-3/`, CHECKPOINTs 22:27Z-22:44Z) confirmed end to end: the ajtai-leaf-2 PINNED Rust verifier
(system_pinned=true, sys_id 18d915… = fp8-ada+ajtai-n64) ACCEPTS a proof whose statement has steps=96 > n=64. Nothing in Rust binds
`statement.steps` (K) to the relation: verify.rs's chain test and parse_v5 derive the layout from st.steps, relation.rs has no steps/n
bound, public_pins_hashed skips k_ops; `steps <= n` is only a Python compile-time assert in the ajtai gadget. With steps > n the
negacyclic wrap X^n = -1 gives exact digest collisions (their PoC `leaf3_ajtai_steps.py`), i.e. VU rows != committed rows, same digest.

Fix (Rust AND the Python verifier):
1. Every pinned relation carries its expected steps/K (and anything else the layout is derived from); the verifier refuses a statement
   whose steps differ; unpinned systems (`--allow-any-system`) must at least enforce the leaf's structural bound (Ajtai: steps <= n).
2. The steps>n statement as a must-reject negative (fixture from red-team-leaf-3; ask in their dir if it is not there yet), plus one
   steps<n variant.
3. Re-pin if a digest changes; gates 0 failures; note in your report whether the check lives in shared code (verify.rs/relation.rs,
   inherited by blake3/share-logup at integration) or Ajtai-only.
Priority: this over benches if time is short. FINAL stays 23:45Z.
