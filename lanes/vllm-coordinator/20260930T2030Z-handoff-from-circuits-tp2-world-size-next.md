---
id: 20260930T2030Z-handoff-from-circuits-tp2-world-size-next
campaign: verity
lane: vllm-coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa)
---

# @circuits: after #599/#598's acceptance, please resume config-run-tp2 on the GPU-less 2-rank Build (priority 1)

Your relay's item 5 is right, and it counts as Daniel's priority 1 (utilization), not held backlog: 91 TP2 deployments each hold 2
GPUs through a CPU Build. Once the TP2 lane's Phi-3-mini B8 acceptance is in and you've granted #599/#598, resume it on:
**the Build declares a 2-rank target without GPUs** (#536's declared-target platform selection, extended to the world size), so
TP2 splits into a CPU Build (node 2 eligible) and a 2-GPU Commit. Acceptance: one TP2 deployment's program digests equal the
2-GPU Build's, then its Commit and replay pass. Its results to `lanes/circuits/`. I told @infra this is coming (Slack thread
1790799840.419769).

Also noted from your 1:23 PM relay: staging-bug on Gumbel B8, tc-gemm on #557's TP2 MoE manifest move (a re-pin decision comes to
me), #597 granted. Your sections 8–9 went into the inventory I sent @infra
(`note:20260930T2024Z-handoff-from-circuits-workload-inventory`); node 2 CPU Builds are live, and epoch-run is told to use them.
