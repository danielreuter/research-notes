---
lane: red-team-vbridge-c
kind: report
created: 2026-10-06T03:09Z
status: final
---

CHECKPOINT d5efa0005 (12:37Z) [final] rename re-grant: GRANT #1273 @fd6af1d43, #1274 @ca685b7af, #1283 @91e8bdcb8 (restack reproduces from git objects; sources byte-identical; lock deltas equal; records unchanged); labels on remote; note:red-team-vbridge-c/20261006T1235Z-finding-vbridge-rename-regrant
CHECKPOINT d5efa0005 (07:09Z) [final] GRANT #1283 @3d9977368; replay audit r20261006-044346-2f12 PASS both packages, records equal; recOpen == unit_circuit gate for gate; label on remote; note:red-team-vbridge-c/20261006T0708Z-finding-pr1283-review
CHECKPOINT d5efa0005 (06:44Z) [open] pr1283: still waiting on replay audit r20261006-044346-2f12 (security built; security_proofs building ArkLib/VCVio from source on a loaded vy-nebius-2)
CHECKPOINT 5b96da663 (06:01Z) [open] pr1283: all five checks done and clean; only the replay audit r20261006-044346-2f12 (vy-nebius-2, 77 min so far vs 48 on node 1) remains before the verdict
CHECKPOINT 5b96da663 (04:54Z) [open] pr1283 checks 1-3 pass: recOpen == unit_circuit gate for gate at (8,1),(16,2); open_ref == lean forms == statement RHS; honest witness meets every hypothesis (8,1 idx0/1; 16,2); local kernel replay of 6 VBridge modules ok; art:547fabd7; waiting on replay audit r20261006-044346-2f12
CHECKPOINT 5b96da663 (04:46Z) [open] pr1283: check5 merge clean (remerge-diff: imports only; JSON 3-way none); check4 records: only sound_recOpen + RecOpen reads {consStructure,consTerm,recOpen} new, 0 changed vs 2434949b9/7c5cb816e/17cfcdae8; replay audit r20261006-044346-2f12 running on vy-nebius-2
CHECKPOINT 5b96da663 (04:42Z) [open] reopened for #1283 (sound_recOpen) review at 3d9977368: NOT final
CHECKPOINT 5b96da663 (04:02Z) [final] GRANT #1273 @50bf1c080 and #1274 @2434949b9; replay audit r20261006-030819-703e (Lean clean; Warden runs item pre-existing); labels on remote; note:red-team-vbridge-c/20261006T0402Z-finding-vbridge-c-review
CHECKPOINT 5b96da663 (03:46Z) [open] review done pending audit; replay audit r20261006-030819-703e still running at 38 min; finding drafted
CHECKPOINT 5b96da663 (03:20Z) [open] statements checked (hms rfl both schemes, dirs LSB=level0, Carries order, sizes, vacuity); Lean climbRow == rec_open._climb gate for gate art:8312dab4c8905e0f7bdec4ee90cb9d5f194b43b03274cf66e81219d935eec8cb; replay audit r20261006-030819-703e running
CHECKPOINT 5b96da663 (03:09Z) [open] reviewing #1273 (50bf1c080) and #1274 (2434949b9); replay audit r20261006-030819-703e on vy-nebius-1 running

## FINAL

~~~text
tip: none (review only, no commits; reviewed pr:1273@50bf1c080, pr:1274@2434949b9, pr:1283@3d9977368)        merge-with: none
known-failures: Proofs.Warden.DifftestMain `generate` under `research run --cwd clone` (pre-existing; #1283's audit used --no-runs)
pod: none created (shared vy-nebius-1, then vy-nebius-2); $11.48 + $31.03 est.
artifacts: art:8312dab4c8905e0f7bdec4ee90cb9d5f194b43b03274cf66e81219d935eec8cb art:547fabd7fc224c972ff54610264f4467f2108c233d4eb80b555d3c7c0ff740b0
~~~

GRANT #1273 and GRANT #1274: `note:red-team-vbridge-c/20261006T0402Z-finding-vbridge-c-review`. The replay audit is
`r20261006-030819-703e`. Its `security` package PASSed. In `security_proofs`, every Lean check passed, and the one
failure is the pre-existing Warden `runs` item. Both `grant=red-team` labels are on the remote.

GRANT #1283 at `3d9977368581d925cdd6de708198a2330b6f7f9f`: `note:red-team-vbridge-c/20261006T0708Z-finding-pr1283-review`.
The replay audit `r20261006-044346-2f12` (vy-nebius-2, `--no-runs`) PASSed both packages, and its records equal the
committed ones. Lean `recOpen` is `rec_open.unit_circuit` gate for gate. The `grant=red-team` label (by
red-team-vbridge-c) is on the remote. Inbox: nothing received.
