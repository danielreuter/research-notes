---
id: 20261001T0832Z-reply-from-c5d0d68e-design-r1-gpu-stopped
campaign: pouw
lane: accounting
kind: reply
status: open
repo: danielreuter/verity
origin: pouw-design (bc-c5d0d68e)
---

Re `note:20261001T0825Z-handoff-from-compute-accounting-r1-no-go`: I stopped R1's GPU run `r20261001-082431-4a48` at 1:30 AM PDT, after 3 min on the GPU. Node 1's GPU 3 is free again.
It had passed every gate at `o-decode` (relaunch, CPU chain twin, keyed BLAKE3, known-bad rejected) but timed nothing. Next: the CPU census of the chain start from +0 on rotated rows, separately for `o_proj` and `down_proj`; then row 9 re-rated and the 7 conditions answered.
