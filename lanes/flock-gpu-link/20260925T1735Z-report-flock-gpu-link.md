---
lane: flock-gpu-link
kind: report
created: 2026-09-25T17:35Z
status: open
---

CHECKPOINT none (19:10Z) [open] coord 12:07 PT: pure Flock split with flock-backend; handoff 1912Z to lanes/flock-backend (proposes one block-R1CS statement flock-pure-block for CPU+GPU, or B); read their report 81f01ab8. s9 fixed (C8: route (a) 2^-130.19, gap = prime FS). WAIT r20260925-190459-8ed1 check-back 19:45Z agent bc-9209cb00-14e7-59ad-85aa-682c82ad797a
CHECKPOINT none (19:06Z) [open] WAIT vy-flock-gpu-link-h100 r20260925-190459-8ed1 check-back 19:45Z agent bc-9209cb00-14e7-59ad-85aa-682c82ad797a. Done: H100 4096 linked GPU sessions ACCEPTED (prove 0.67 s both reps, 244 rounds, wait 0.22 s loopback, art:fff0c041); head-to-head in docs/flock-gpu-route.md s9 -> recommend pure Flock; handoffs 1816Z+1836Z acted on (sweep+RTT/bytes in run 8ed1)
CHECKPOINT 1c1d8153 (18:18Z) [open] WAIT vy-flock-gpu-link-h100 r20260925-181625-409b check-back 18:45Z agent bc-9209cb00-14e7-59ad-85aa-682c82ad797a; also verifier r20260925-181700-f169 on vy-flock-gpu-link-ver (US-MO-1, 64.247.206.95:18877). PR #30 cursor/flock-gpu-link-797a@1c1d8153: CPU selftest all-pass 8/64. next: GPU selftest + 4096 timing
CHECKPOINT f2e8b1b9 (18:11Z) [open] chunk-block statement CPU selftest ALL PASS 8/64 VUs (25 cases incl L1/L2/L4 negs, both reps); Flock-CUDA chunk prover written, building locally (nvcc sm_90). Code on cursor/flock-gpu-link-797a @ local only: git push 401 (VM token), bundle fallback next
CHECKPOINT b684b12 (17:58Z) [open] revised L4 design: one R1CS block per BLAKE3 CHUNK (k_log 18, block = global chunk idx) so Lambda_B is a coordinate map onto the prime's unpadded Lambda_F (leaf-block was not); Flock patch (prove/verify with extra ring-switch claims) written; coding chunk statement + CPU selftest
CHECKPOINT e57e4c8 (17:48Z) [open] scope written (store docs/flock-gpu-route.md): H100 BF16 route (a) projected ~1.6 s = 1.3e8x vs B-Ligero 2.86e8x at 1.5 ms same-DC RTT (break-even ~10 ms); E4M3 0.87 s vs 1.94 s. Building L2+L4 (leaf-block) on branch cursor/flock-gpu-link-797a from lane/agkr-flock-cell
CHECKPOINT b684b12 (17:44Z) [open] design: GPU L4 as leaf-per-block BlockR1cs (k_log 20, 48 compressions/leaf, chain = copy rows, lincheck = 2^14 fold x eq_hi + sparse delta; no wiring GKR, ~240 coin RTs vs 1070); L2 = N-claim ring-switch batch. Writing scope doc
CHECKPOINT none (17:38Z) [open] read brief/contract/kb/red-team; ref: B-Ligero H100 BF16 keyed-BLAKE3 3.64 s/4096 (2.86e8x); cell A100 prime 2.7 s, Flock 20.7 s of which 16.3 s = 1070 coin RTs @15 ms. Next: Flock-CUDA code read, scope doc
CHECKPOINT f7de4620 (17:35Z) [open] started: scoping GPU route (a) L2/L4/L3 + live-coin model; agent bc-9209cb00-14e7-59ad-85aa-682c82ad797a
