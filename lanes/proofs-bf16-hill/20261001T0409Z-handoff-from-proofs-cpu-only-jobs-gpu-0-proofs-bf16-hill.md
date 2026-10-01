---
id: 20261001T0409Z-handoff-from-proofs-cpu-only-jobs-gpu-0-proofs-bf16-hill
campaign: verity
lane: proofs-bf16-hill
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs (bc-8416bc72)
---

# Nothing that runs only on the CPU holds a GPU

to: proofs-flock-fp, proofs-bf16-hill, proofs-tc-defs (the same note in each lane). Proofs committed this to infra at
9:10 PM PDT (Slack thread 1790822262.591279).

- **Infra's measurement, 1 PM to 7:32 PM PDT:** proofs' node-1 pods held 14.3 GPU-h and were busy for 1.5. Of that, 9.1
  GPU-h were held before the first GPU use, and 6.5 GPU-h by pods that never used their GPU. `fp-hill-mxf4-k2048` reported
  `gpu_util 0.054`.
- **The rule, for every job you submit from now on:** staging (statement and circuit builds, the CPU selftest), verifier-only
  runs, sweep counts and capture builds run with `gpu: 0` in `provers`. A GPU job only loads the staged statement and proves.
  This extends `note:20261001T0216Z-handoff-from-proofs-provers-floor-and-slices`.
- **Captures (proofs-tc-defs):** `tcdefs-mxf4-edges-346/347` held 5.6 GPU-h with the other SkyPilot jobs and used 0.3.
  Build in a 0-GPU job first, then take the GPU only for the capture.
- **Coming (proofs-verify-overlap):** the verifier moves to its own 0-GPU pod, so the prover's GPU stops waiting on it.
