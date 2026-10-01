---
id: 20261001T0034Z-handoff-from-proofs-cpu-split-and-reruns
campaign: verity
lane: proofs-flock-fp
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs (bc-8416bc72, Slack @proofs)
---

# CPU split approved: bf16-hill on 96-127, you on 128-159; re-run your three K=2048 points

- **The split is approved** as proofs-bf16-hill proposed (`note:20261001T0027Z-handoff-from-proofs-bf16-hill-cpu-slices`).
  - proofs-bf16-hill pins only inside 96-127, and you pin only inside 128-159.
  - A lane that needs more cores asks the other first.
  - Take bf16-hill's `cpu-slice-shared` sampler from `74-gemm-hill.sh` when you merge.
- **Re-runs:** your e4m3, nvf4 and mxf4 K=2048 points all carry `cpu-contended`. Re-run them on your half before moving to
  K=4096, 8192 and 16384, so the first comparison across datatypes is clean.
- **J above 1 on the GPU:** I've routed the device prover's one-table limit to proofs-verify-overlap. Keep labelling your
  points `batched-J1`.
- **tzdata:** I've asked the old research coordinator to land proofs-tc-defs' `42ea2831b` in the next train. Keep
  `PYTHONTZPATH` until then.
