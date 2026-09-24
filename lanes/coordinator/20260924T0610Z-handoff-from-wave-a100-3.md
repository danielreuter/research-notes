---
lane: wave-a100-3
kind: handoff
to: coordinator
created: 2026-09-24T06:10Z
---
# wave-a100-3 -> coordinator: frozen tables.py rejects every fused bf16-ampere-v3/v3x4 row (off the frozen instance set); A100 bare has no valid live cell

CORRECTION 06:19Z (after your 06:15Z handoff): the two "valid" v1 cells below are NOT valid either -- v1 predates the phase-sum
fix (P) and the stored metas lack run_id (reg.sh). Every A100 cell is drill-down only; no decision needed from this note.

`reject_reasons` @ 24f252b1 on all 37 wave-a100 results (target `first-campaign-target/2026-09-21`, B-Ligero):
- v3 / v3x4 fused rows carry `instances` = `bench-instances-bf16-ampere/v1`, tier `vu-k1536-bf16-ampere` (manifest 7c12c281...
  v3x4, b30130e0... v3); FIRST's frozen ref is `bench-instances/v1` / `vu-k1536` / 059103cf.... So "instances differ from the
  frozen set" on every fused row, live or local. Only v1 `bf16-ampere` (bare and `--auth included-hash`) is on the frozen set.
- wave-a100-2 ran no v1 live, so the bare column's valid cell is local coins only: bare-v1p8-r3 t.total 0.3191 art:644d2eec
  (Rust re-verified by me, verdict art:8e402b61). Column 2 is valid live: +hash v1 p8 live t.total 0.9713 / live 0.9766
  art:875be1cc (verdict art:525cb68f).
- Fastest fused live (drill-down under the frozen rule): v3x4 p4 r1 0.3230 / 0.3249; v3 p8 r3 0.3347 / 0.3416.
Decision needed only if the fused relations should count: either their instance sets join FROZEN_INSTANCES, or a v1 live
bare cell is measured (~2 min of prover time; my budget said no new benches, both pods are being terminated).
Details: `lanes/wave-a100-3/*-report-wave-a100-3.md`.
