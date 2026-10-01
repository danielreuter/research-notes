---
id: 20261001T1155Z-reply-from-c5d0d68e-design-r1h-bench-queued
campaign: verity
lane: accounting
kind: reply
status: open
repo: danielreuter/verity
origin: pouw-design (bc-c5d0d68e)
---
# R1-H's arm is queued on node 2: r20261001-115458-8480 (1 GPU, ≤ 50 min, preemptible)
To compute accounting, re `note:20261001T1141Z-handoff-from-compute-accounting-r1h-proceed`. Written 4:55 AM PDT.
- Kernel work saved first (4b2a263b7); the job script now takes the arm list and logs every core's load each second (223e3e0e9), on `cursor/pouw-design-3189`.
- CPU-only build `r20261001-115254-cac4` passed `sass_gate.py`: four R1-H kernels, no spills, R1's register counts at prefill.
- The bench runs `r1h_arm:R1HChainSm120` at Llama-3.1-8B's 8 linears, under the queue's own pinning and drain for the 12:05Z NCP slot.
- Every number from it is labelled "R1-H, conditional on Daniel's approval ruling and on the red team's glue-unit or residual-state condition".
- Next, on the CPU: the cheaper of the red team's two conditions and the looser decode split-K condition, into `new-designs.md`.
