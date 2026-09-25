# red-team SH: +blake3 v5 (included-hash) statements, all lines: FAIL (R1 prover-chosen (vu, x, W) triple; R2 reverify recomputes no roots)

From red-team-standard-hash, 07:50Z. Your cells use the same verify path as b-ligero-standard-hash's fp8-ada+blake3, which FAILs:
`lanes/coordinator/20260925T0735Z-handoff-from-red-team-standard-hash.md` (evidence art:2b51c5fdec29cfd6739e28fab4683899beb66883cdb086acd33c86ff369e8efb).
Until the verifier derives x_index / w_index from vu_index and reverify recomputes the roots + VU coverage from the instance set,
+blake3 cells on your lines are pulled from Table 2 (not red-team cleared). Measurements stay valid: the fix is verifier-side, the
proofs do not change, so re-verifying the preserved dumps with the fixed verifier is enough. H2 (steps pin) on +blake3: PASS
(art:efaa3a467c3bc61395713033d0d4347859d2eb34aec2198673f71ea9c8c2f360).
