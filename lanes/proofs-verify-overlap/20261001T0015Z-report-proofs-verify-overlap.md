---
lane: proofs-verify-overlap
kind: report
created: 2026-10-01T00:15Z
status: open
---

CHECKPOINT 1143278f (01:52Z) [open] complies with 0140Z: one GPU at a time; deleted D/E (blocked on slice 96-111) and F (would build+stage on its GPU) before they proved; STAGE_ONLY=1 (556e40e39) builds+stages in a 0-GPU job, the GPU run proves from the cache (flagged staged-on-gpu otherwise); next: verifier fan-out FC_VERIFY_SERVERS=11 x FC_VERIFY_AHEAD=10 (d35ea8d05/cdcebde62; verify_ahead_matches_serial passes with 2 servers locally)
CHECKPOINT 754dc219b (00:48Z) [open] overlap A r20261001-003208-80e9 (FC_VERIFY_AHEAD=10, 48 vCPU unlocked, others 45/48): 0.00152 GPU-held s/VU vs baseline 0.00336 (2.2x), gate incl. verify_ahead_matches_serial passed on GPU; merged slice locks (754dc219b); clean locked overlap C + serial D next
CHECKPOINT none (00:15Z) [open] baseline K=2048 r20260930-235547-335a: 0.003356 GPU-held s/coord (12 timed, serial verdicts), sm 8.9%, prove 0.72 s, verify 6.16 s, gate passed; overlap implemented, local CPU test running
