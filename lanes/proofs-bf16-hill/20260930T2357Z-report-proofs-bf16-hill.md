---
lane: proofs-bf16-hill
kind: report
created: 2026-09-30T23:57Z
status: open
---

CHECKPOINT c28dd462 (00:57Z) [open] inbox 0034Z/0040Z: split taken, my new jobs pin inside 96-127 (taskset -c 96-127 + slice locks); the K=2048/4096 points r20261001-002009-a71c/-5ca2 are already os-seed-prf, batched-J1, rtx-pro-6000-server/bf16 and had no other pinned job on their slices, so no re-run
CHECKPOINT e95c0a49c (00:56Z) [open] 5:58 PM PDT: step 0 at all four K on the console (os-seed-prf, batched-J1, rtx-pro-6000-server/bf16): overhead 2.15e8 / 1.63e8 / 2.76e8* / 4.57e8* at K=2048/4096/8192/16384, verify 2.8/4.5/8.4/14.3 s per statement, 80-93% of the session (*cpu-slice-shared; clean K=8192 rerun running); plots art:f95488b37935d08f55cf6850ccf820ca2e7ea8f134c759de312acfd7058afdef; step 1 (m=36) refused: spec m <= 35; step 2 (4x4 tile, K=2048) queued
CHECKPOINT 0118ec355 (00:20Z) [open] 5:20 PM PDT: seed-coin step 0 on the console at K=2048 (2.26e8x session, 4.43e7x prove-only, 539 VU/s, SM 13%, 3.04 s verify) and K=4096 (1.58e8x, 2.29e7x, 386 VU/s, SM 16%, 4.47 s); live-coin switch reverted per 2359Z; census now rtx-pro-6000-server (d1a283846); step 0 at all four K queued on 0118ec355 (os-seed-prf, batched-J1, 16 vCPU each)
CHECKPOINT 8f02384fc (23:57Z) [open] 4:58 PM PDT: census rtx-pro-6000-bse/{bf16 500,e4m3 1000,e2m1 2000} TFLOPS (b343492b5); contract result.json + hillclimb.json + rollup (8f02384fc); step 0 at K=2048/4096/8192/16384 queued in parallel on node 1, CPUs 96-159 split 16 each; K=2048 preview (c6040f3, CPU-contended) 4.47e7x, 2729 VU/s, 3.3% SM, verify 6.8 s/statement
