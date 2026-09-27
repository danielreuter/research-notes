---
lane: one-stage-e2e
kind: report
created: 2026-09-27T05:15Z
status: open
---

CHECKPOINT d27e6941 (05:54Z) [open] inbox 0545Z from M0 acted on: bindings at e51e2b86 (--partition/--program/--unit-indices, units.classes) make A1's M0 half runnable now (pass partition 8797a174..., program e1e6bf41..., indices 0..1023); full A1 still waits on Lean verify for the eb90718f/e51e2b86 format; awaiting coordinator go for A1-partial (~$0.2, new CPU pod)
CHECKPOINT d27e6941 (05:54Z) [open] A0 DONE: accepted, 12/12 negatives refused (r20260927-054332-8ba7, r20260927-055014-8abd, preserved); stand-in commitment; Lean verify not run (format gap), audit complete=false; wrong-unit bound 254/1024 at delta 0.01, k=16; cursor/one-stage-e2e-6014 @ d27e6941 PR #116; pod vy-one-stage-e2e TERMINATED, ~$0.23; A2 (served roots from vllm-serving-commit) planned in store internal/one-stage-e2e-plan.md; next: A1 on Lean format + M0 binding, A2 on served files
CHECKPOINT 3e6ad7cc (05:45Z) [open] WAITING r20260927-054332-8ba7 on vy-one-stage-e2e, check after 06:05Z; agent bc-c520c11b-172b-5758-a4c3-07b2e7956014; next: fetch A0 audit/negatives, report. Glue on cursor/one-stage-e2e-6014 @ 3e6ad7cc (PR #116); Lean flock-verify built, M0 building
CHECKPOINT 3040ac1f (05:28Z) [open] plan cross-checked by 3 read-only surveys (store internal/one-stage-audit-serving-inventory.md, flock-circuit-m0-e2e-status.md, one-stage-e2e-flock-verifier-readout.md); no change to headline; awaiting coordinator go; no pods, $0
CHECKPOINT 3040ac1f (05:27Z) [open] STEP 1 DONE: plan at store internal/one-stage-e2e-plan.md. Headline: all stages have code except 3 bindings + profile; critical path = Lean verifier parsing M0 eb90718f format; smallest real run = RoPE d64 over 1,024 heads captured from served #101 (art:16825154, M0 staging passed on CPU in 26 s); ~$1-2 on one 16 vCPU pod; awaiting coordinator go before building; no pods, $0 spent
CHECKPOINT 3040ac1f (05:19Z) [open] surveying: #111 partition object + IntegrityProfile read; 3 read-only explorers on vLLM commit/registration, M0 #83 statement, Lean verify/draw #113; plan doc next; no pods, $0
CHECKPOINT 3040ac1f (05:15Z) [open] opened: integration lane for one-stage audit e2e; step 1 (CPU, $0) inventory+gap list -> store internal/one-stage-e2e-plan.md; agent bc-c520c11b-172b-5758-a4c3-07b2e7956014; no pods
