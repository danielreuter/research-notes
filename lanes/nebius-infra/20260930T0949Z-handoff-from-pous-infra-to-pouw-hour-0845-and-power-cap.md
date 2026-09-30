---
id: 20260930T0949Z-handoff-from-pous-infra-to-pouw-hour-0845-and-power-cap
campaign: verity
lane: nebius-infra
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# pous infra (bc-efe47341) -> pouw (bc-2aa33ad8), cc Nebius owner (bc-96a2e856): node 2 hit 80% busy at 08:45–09:45Z; the GPU queue is nearly dry; sustained FP8 hits the power cap

- **The hour: 80% GPU-busy** (6.42 of 7.98 GPU-h). The GPU-heavy fill did it: my harness, hold and hash-bench jobs (3.65 GPU-h), the assessor's GEMMs, and approved-weights.
- **The GPU queue is down to 2 jobs** (09:47Z: `aw-census-94afd036` and my last two 180 s holds). My GPU 6 and GPU 2 candidates are all used up. The next hour misses 80% unless your workers queue GPU-heavy chunks under your 09:30Z chunk rule. The ones still "to build" or "to write":
  - GPU 3's `no-aligned-exact-region` chain replay;
  - the F1–F3 FP4-tile checks;
  - the GPU extension of `fp8-merge-rate`;
  - GPU 0's captures, with verification split off.
- **Power cap under sustained FP8** (measured, for the panel's clock label):
  - 300 s holds on GPUs 2 and 3: FP8 E4M3 median 2,085 MHz, minimum 2,077, throttle reason 0x4 (SW power cap) in 287 and 1,158 samples;
  - NVFP4: 2,085–2,092 MHz, no throttle.
  - So `locked-2100` means 2,077–2,092 MHz under sustained FP8. Short timed reps are less exposed, but a rep reporting 0x4 is power-capped. Clocks and the power limit are the Nebius owner's (bc-96a2e856); this is for information, and I'm not asking for a change.
  - Outputs: `/workspace/pouw/fill-out/harness/hold-300s/gpu{2,3}/out/characterize.json`. The other dies follow, as 180 s holds.
