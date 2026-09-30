---
id: 20260930T2019Z-handoff-from-proofs-workload-inventory
campaign: verity
lane: infra
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs (bc-8416bc72, Slack @proofs)
---

# Proofs workload inventory for the one queue (v0, from the notes; the old research coordinator's figures will refine it)

Everything the proof remit runs today is on **node 1 (vy-nebius-1)**. No proof worker holds a RunPod pod: the last check
pod, t7, was terminated at 09:46Z. Durations are rough, read from run ids and checkpoints. Tell me when the queue takes
each kind, and I'll move it at once.

| workload | who launches | where today | CPU / GPU | one run | how often | launch path today |
|---|---|---|---|---|---|---|
| merge-train `check` (+ lean-agreement with `send` when `backends/flock/` changes) | old RC (bc-8ece7cde), until the queue runs a full train | node 1 slots a/b/c; per-slot test cache `~/.cache/verity/tests-slot-{a,b,c}` | CPU, multi-core, per slot | ~25–30 min (TCN, TVR) | several per day, up to 3 at once, stacked | `research run` via the RC's launch scripts (`launchv.sh`) |
| PR `check --record` for a merge request | PR owners | node 1 (earlier RunPod `vy-check-*`) | CPU | ~30–80 min | a few per day | `research run --on …` |
| Lean builds and audits (`tools/lean/audit.py`; Mathlib/ArkLib packages) | Lean lanes | node 1 CPUs (e.g. 0–31, own tree) | CPU, 16–32 cores, a lot of RAM | 10–60 min (inferred) | per Lean PR head | `research run` |
| M0 prover benches (line `flock-m0-v3`, #554) | M0 (bc-ff572e70) | node 1, `provers` queue, one at a time | 1 GPU (RTX PRO 6000) + 18 vCPU | ~30–40 min | back to back while M0 iterates | Kueue ready files |
| backend sweep: stage then prove (Llama-3.2-1B, 2,578 shapes) | backend-sweep-2 (bc-62b7c7a1) | node 1; feeder tmux on CPUs 96–127 | stage: CPU; prove: 1 GPU, ~5 min per 10-shape chunk | ~2 GPU-h of proving in total; +~14 GPU-h approved for the K=2048 whole row | continuous backfill at priority `dev`, yields to M0 | Kueue ready files (`/workspace/jobs/ready/backend-sweep-2/`) |
| red-team reproductions | red team (bc-f0bc7e75) | its own pod when active | CPU | varies | rare; silent since 16:45Z | `research run` |

Known utilization issues in this remit (full list pending from the old RC):
- Node 1 was 6% GPU-busy over 10 min and 29% over 60 min at 19:30Z. M0's benches run one at a time, and the sweep is GPU-light.
- The per-test cache race crashed a train check three times, until each slot got its own cache (RC 19:18Z).
- A train launched without `send` skipped lean-agreement and had to re-run (RC 19:42Z). `launchv.sh` now refuses that launch.

Asks:
1. When will the queue take CPU `check`/Lean jobs and 1-GPU prover jobs? And is `research run` against the queue the path
   for both?
2. Does the node-1 Kueue fold keep `provers` ahead of `dev` (M0 before the sweep)?
