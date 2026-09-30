---
lane: lean-gemm-relation
kind: report
created: 2026-09-30T05:38Z
status: final
---

CHECKPOINT 461f7020 (07:04Z) [final] Hopper + Ampere/Ada GEMM step relation = tc_dot_total, proved in Lean (18 pins, 0 sorry); PR #490 @461f7020; recorded audit r20260930-065514-59bb PASS
CHECKPOINT 461f7020 (07:02Z) [open] boundary+gadgets proved: 18 pins, 0 sorry, recorded audit r20260930-065514-59bb PASS (preserved); commits 41ec25e1,461f7020 local (GitHub token expired), bundle in store artifacts/lean-gemm-relation/; PR #490 remote @5d8ef983
CHECKPOINT 5d8ef983 (06:44Z) [open] Ampere/Ada proved too (ampere_step_sound/_complete/_iff/_hw, unit, ada_eq_ampere); 13 pins, 0 sorry; recorded audit r20260930-064104-5cf0 PASS (preserved); PR #490 @5d8ef983; next: pack_relation (BF16 boundary)
CHECKPOINT 60ebd57e (05:38Z) [open] statement fixed+pinned (Verity.TC.hopper_step_sound/_complete/_iff/_hw, packages/verity/lean); 2 sorry; proving; push blocked (token expired), commit 60ebd57e local

## FINAL

~~~text
tip: cursor/lean-gemm-relation-a815 @ 461f7020 (base main@b82f1dd2, merged)        merge-with: none
known-failures: none    pod: none created (recorded runs on vy-nebius-1, already paid); $0
artifacts: runs r20260930-062851-727b r20260930-064104-5cf0 r20260930-065207-fd65 r20260930-065514-59bb (preserved)
~~~

PR danielreuter/verity#490 (draft): `packages/verity/lean`, a core-only Lake package. `verity.ml.tc.relation`'s k16 step
relation, unit chain, BF16 boundary and chunk gadgets are proved equal to `total.tc_dot_total` / `cvt_rn_bf16_f32` for
the Hopper (H100, sm_120) and Ampere/Ada (A100, RTX 4090) pipelines: 18 pins, 0 sorry, standard axioms only. The two
`_hw` theorems take the named assumptions `gemm-hopper-step` and `gemm-ampere-step`. Before merge: a named statement
reviewer for the 18 new records. Handoffs sent: lanes/coordinator 20260930T0538Z and the proof-closes one; friction note
20260930T0629Z (research run --timeout units).
