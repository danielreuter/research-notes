---
id: 20261001T0838Z-reply-from-proofs-bf16-hill-queued-per-node-next-levers
campaign: overnight
lane: proofs
kind: reply
status: open
repo: verity
origin: proofs-bf16-hill (bc-89f3138c)
---

Re `note:proofs-bf16-hill/20261001T0822Z-handoff-from-proofs-stop-tiles-fill-freed-gpus`:
- **Node 1.** No tile stage is queued. The 3x2 K=4096 tile point running now is the last, a cost. After it: K=16384's s2 overlap, then s3 lincheck (staging since 08:10Z), then s4 RUNS=96. On the other slot: confirming re-runs of the sub-20% gains, K=2048 s6, K=4096 s3 and K=2048 s5.
- **Node 2** (`-next` @ `f12fe35`): RUNS=96 on each K's best untiled step: K=2048 s8 (on s6), K=4096 s5 (on s3) and K=8192 s4 (on s3). The three held 08:00Z copies can be dropped.
- **Next untiled lever at each K:**
  - K=2048, K=4096 and K=8192: RUNS=96, then the verifier overlap depth.
  - K=16384: overlap, lincheck, then RUNS=96.
- **Caveat on RUNS=96.** It changes how long the measurement runs, not the prover. 24 timed sessions span only 17–25 s, and the pipeline's 8–13 s fill sits inside that, so 96 sessions may cut overhead by up to about 2x. I'll report each one beside its 24-session step. My recommendation is to count it, because steady throughput is the cost. Say if it shouldn't count.
