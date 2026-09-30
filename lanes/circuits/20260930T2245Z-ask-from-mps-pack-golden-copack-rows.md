---
id: 20260930T2245Z-ask-from-mps-pack-golden-copack-rows
campaign: one-pool
lane: circuits
kind: handoff
status: open
repo: danielreuter/verity
origin: mps-pack (bc-1c69147a), worker of infra (bc-17cc41f1); Daniel approved node-1 MPS packing at 3:22 PM PDT
---

# mps-pack → circuits: name the two rows packed with cov-g217 for the MPS golden check

Plan: `note:20260930T2220Z-draft-node1-mps-commit-packing-cutover` §4.1. One `commit-pack` pod (1 GPU, its own MPS daemon) runs
`cov-g217` and two other Llama-3.2-1B or SmolLM2 Commits at once (`CUDA_MPS_PINNED_DEVICE_MEM_LIMIT=0=28G`,
`gpu_memory_utilization=0.28`, `REPLAY_DEFERRED=1`). Pass = g217's run root and committed record are byte-identical to
`r20260930-175445-077e` (root `4ed9a783…`), and all three validate. On a mismatch I stop and write it up in `lanes/infra/`.

**My proposal, so no new Build is needed and all three rows become goldens** (each rerun in a scratch copy of its row dir;
the reference dirs under `/workspace/jobs/cov/` are not touched):
- `cov-g230-2` SmolLM2-135M B8 stoch (node-1 root `e0d0a9f6dc39d045`);
- `cov-g218-3` Llama-3.2-1B B8 stoch (node-1 root `f03568e5f56bb81d`).

Tree: `/workspace/research/trees/cursor-coverage-v1-2622` (it has the deferred replay; g217's reference tree `cfb12962…` doesn't).
If a root differs, a tree change can't be told apart from packing without an unpacked control on the same tree; I'd stop and ask.

**Unless you name other rows or another tree here by 4:30 PM PDT, I use these.**
