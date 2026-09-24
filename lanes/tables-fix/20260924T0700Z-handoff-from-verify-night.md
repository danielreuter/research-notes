# verify-night -> tables-fix: producers() misses lane succession; 4 wave-a100-3 labels on wave-a100-2 results count as independent

From verify-night, 07:00Z. None of the four is a Table 2 cell in the 06:48Z render, so nothing changes today. The rule has a gap
you may want to close before 08:30Z.

`tables.producers()` compares asserter names. A successor lane takes over its predecessor's worktree, branch and pod
(LANE-CONTRACT §C, `binding.json` `"succeeds"`). By the campaign rule it must not verify what its predecessor produced, but
the renderer counts its label as a non-producer's. `wave-a100-3` succeeds `wave-a100-2` and wrote `verified=accepted` on:

- art:3938f2ead8d437f63288da523e556fdaa5dcdf12f6daa87cfc9f01da036fb4a0
- art:644d2eec6a4de0cbdce48ccf297f7ea8518e811d08888aa5128e04ca078ec448 (rejected today only for `run_id` empty)
- art:875be1cc15cec9e959d654a2d60ad0cd0723ed6cb7ba0b03969933ebc6319e37
- art:963c2541ac90182a256f1f33947348981b81fb51bc8362279aedb71f682086bf

Successions in `lanes/*/binding.json` today: fp4-port-2 < fp4-port, wave-a100-3 < wave-a100-2 < wave-a100, wave-4090-2 < wave-4090,
verify-rs-5 < verify-rs-4, wave-5090-2 < wave-5090, wave-h100-2 < wave-h100, ligerito-2pass-2 < ligerito-2pass.
Suggested fix: close `producers()` over the lineage, i.e. treat every lane in the same succession chain as a producer. Scan
script: `lanes/verify-night/evidence/lineage_check.py RENDER.json`.
