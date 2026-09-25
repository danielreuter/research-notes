---
lane: flock-link
kind: report
created: 2026-09-25T14:30Z
status: open
---

CHECKPOINT e2cf612b (15:06Z) [open] L1+L2+L4 selftest all-pass at 8/64 VUs (r20260925-145411-c083); F2 pinned union+GPU-unit verifiers all-pass; L3 one-session two-table all-pass (lane/flock-link e2cf612b). 4096-VU timed sessions: prover vy-flock-link-prover, verifier on vy-flock-link-ver (F1), runs r20260925-150605-e857 / -150543-6536
CHECKPOINT a52fcf2d (14:54Z) [open] L1 exchange + L2 both-rep link claims + L4 BLAKE3 chunk-chain circuit implemented (lane/flock-link a52fcf2d, Flock patch in backends/flock); honest accepted, 23 negatives reject at 8 VUs; recorded run r20260925-145411-c083 (selftest 8/64, 4096-VU timing) on vy-flock-link-cpu
CHECKPOINT 33e4d8d1 (14:36Z) [open] plan: Flock patch (eq-weighted link claims appended to union-circuit merged opening, both reps), flock-live Commit(root_F,root_B)->points->Link(y) exchange, BLAKE3 chain circuit (wired CVs/params/endpoints), pinned verifiers; CPU pod next
CHECKPOINT 33e4d8d1 (14:30Z) [open] started 14:35Z; env set, inbox empty; reading re-audit conditions + backends/flock/live; branch lane/flock-link from origin/main
