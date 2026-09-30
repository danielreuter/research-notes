---
lane: lean-zk-table
kind: report
created: 2026-09-30T07:29Z
status: open
---

CHECKPOINT 980326ef (09:35Z) [open] PR #519 @980326ef: 9 pins recorded (table_shvzk 36891e19 …); r20260930-090944-bc3a PASS+labelled; r20260930-093147-9dc8 running; merge request filed (grant pending, store coordinator/0934Z); table rows handed to lean-gemm-relation (0932Z)
CHECKPOINT 1aba1da1 (09:10Z) [open] PR #519 @1aba1da1: --update PASS (11873 decls, 163 pins, replay clean), review art:f32bd3b9; recorded audit r20260930-090944-bc3a running on vy-nebius-1; grant asked of red-team-flock-3 (handoff 0910Z), wording of zk-public (0844Z)
CHECKPOINT da7f03c4 (08:56Z) [open] PR #519 draft @da7f03c4: table_shvzk, Lemma A (translate/indep), star, padColumn_honest, inner_complete, padOnto_M1, ideal_leaf_swap (T1 from Hm96Hiding); 8 new pins; audit --update running on vy-nebius-1 (CPUs 0-31); asked zk-public for wording
CHECKPOINT 8346336d (08:27Z) [open] Lemma A instance PROVED (table_prefinal_translate/_indep via card_fiber_eq_of_triShift) + table_shvzk @8346336d; next: completeness vs Model.padColumn + inner check, T1/X_L+kappa named Props, pins, audit on vy-nebius-1
CHECKPOINT bbe4dd0a (08:20Z) [open] table_shvzk PROVED (Lemma B, world W1; axioms propext/choice/Quot.sound only) @bbe4dd0a: reference prover Table.view, S_shvzk Table.sim, rows via card_seq_masked (4-block form); next: Lemma A via card_fiber_eq_of_triShift, completeness, pins+audit
CHECKPOINT cfdc5330 (08:02Z) [open] branch cursor/lean-zk-table-b379 @cfdc5330 (on #245 21b0edb0): ZK/Dist (SameDist calculus) + ZK/Blocks (card_seq_masked, card_fiber_eq_of_triShift for 4 blocks) compile on vy-nebius-1; next: reference prover + S_shvzk + table_shvzk
CHECKPOINT f0da69ad (07:29Z) [open] started: reading brief, ZK stack #227/#239/#245, paper §3–4; agent bc-7bf99d94-2cfe-5639-8b30-4de8d243b379; next: branch off #245 head, design reference prover in FlockSoundness/ZK/
