---
id: 20260930T2249Z-handoff-from-old-circuits-and-proofs-relay-tp2-gpuless-build
campaign: overnight-sep30
lane: circuits
kind: handoff
status: open
repo: danielreuter/verity
origin: old-circuits-and-proofs (bc-ecac3029)
---
# Relay: TP2 Builds no longer need GPUs (#609, granted and filed for merge)

- A TP2 Build now runs with 0 GPUs, and its digests equal a 2-GPU Build's (runs r20260930-212809-14a0 and r20260930-220713-8e26). This was the hold on your TP2 fill: once #609 lands, TP2 deployments can take config-run-split (a CPU Build, then a 2-GPU Commit).
- Before the TP2 batch, run one TP2 deployment as a canary: a 2-GPU Commit reading a Build made in another pod hasn't been run yet. Question: does a cross-pod Build plus a 2-GPU Commit pass with the same run root as an in-pod one?
- Only rows with a declared target (`__rtxpro6000__`) Build without a GPU.
- For the steward: at about 22:30Z, `deployments-gpu` had its 5-GPU quota fully held with 32 workloads waiting, while node-1 GPUs 2, 4 and 7 used 0 MiB.
