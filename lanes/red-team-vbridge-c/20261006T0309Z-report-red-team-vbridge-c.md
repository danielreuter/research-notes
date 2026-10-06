---
lane: red-team-vbridge-c
kind: report
created: 2026-10-06T03:09Z
status: open
---

CHECKPOINT 5b96da663 (04:46Z) [open] pr1283: check5 merge clean (remerge-diff: imports only; JSON 3-way none); check4 records: only sound_recOpen + RecOpen reads {consStructure,consTerm,recOpen} new, 0 changed vs 2434949b9/7c5cb816e/17cfcdae8; replay audit r20261006-044346-2f12 running on vy-nebius-2
CHECKPOINT 5b96da663 (04:42Z) [open] reopened for #1283 (sound_recOpen) review at 3d9977368: NOT final
CHECKPOINT 5b96da663 (04:02Z) [final] GRANT #1273 @50bf1c080 and #1274 @2434949b9; replay audit r20261006-030819-703e (Lean clean; Warden runs item pre-existing); labels on remote; note:red-team-vbridge-c/20261006T0402Z-finding-vbridge-c-review
CHECKPOINT 5b96da663 (03:46Z) [open] review done pending audit; replay audit r20261006-030819-703e still running at 38 min; finding drafted
CHECKPOINT 5b96da663 (03:20Z) [open] statements checked (hms rfl both schemes, dirs LSB=level0, Carries order, sizes, vacuity); Lean climbRow == rec_open._climb gate for gate art:8312dab4c8905e0f7bdec4ee90cb9d5f194b43b03274cf66e81219d935eec8cb; replay audit r20261006-030819-703e running
CHECKPOINT 5b96da663 (03:09Z) [open] reviewing #1273 (50bf1c080) and #1274 (2434949b9); replay audit r20261006-030819-703e on vy-nebius-1 running

## FINAL

~~~text
tip: none (review only, no commits; reviewed pr:1273@50bf1c080, pr:1274@2434949b9)        merge-with: none
known-failures: Proofs.Warden.DifftestMain `generate` under `research run --cwd clone` (pre-existing)    pod: none created (shared vy-nebius-1); $11.48 est.
artifacts: art:8312dab4c8905e0f7bdec4ee90cb9d5f194b43b03274cf66e81219d935eec8cb
~~~

GRANT #1273 and GRANT #1274: `note:red-team-vbridge-c/20261006T0402Z-finding-vbridge-c-review`. The replay audit is
`r20261006-030819-703e`. Its `security` package PASSed. In `security_proofs`, every Lean check passed, and the one
failure is the pre-existing Warden `runs` item. Both `grant=red-team` labels are on the remote. Inbox: nothing received.
