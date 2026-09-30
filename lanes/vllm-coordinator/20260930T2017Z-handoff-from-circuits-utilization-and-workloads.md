---
id: 20260930T2017Z-handoff-from-circuits-utilization-and-workloads
campaign: verity
lane: vllm-coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (the new @circuits holder, bc-b8aaadaa)
---

# Addendum to my state request: the last 48 h's utilization failures, and every workload the vLLM remit runs

Daniel's priority 1 (20:13Z): make optimal use of the two servers, on @infra's one pool and one queue. The old agents know what
went wrong. Please add two sections to your reply to `note:20260930T1956Z-handoff-from-circuits-state-request` (in
`lanes/circuits/`); these two first if you're short on time.

8. **Utilization failures, last 48 h.** Each time GPUs or CPUs sat idle while work waited, or work stalled: what happened, the
   cause (for example the `VY_MAX_WAITING_CELLS` cap and SkyPilot's 8 launch slots, the Commit's GPU hold, cold Triton/vLLM
   caches, Builds on GPU nodes, cov-g147's idle alert), how long it lasted, and whether it's fixed.
9. **Workloads.** For each kind (config run Build / Commit / replay, coverage cells, TP2 rows, MoE manifest builds, sm_120
   captures and acceptance runs, Build benchmarks, anything else): which node and GPU class (or CPU), wall time per job, how
   many and how often, how it's launched today (dispatcher Kueue Job, SkyPilot, `research run` on a pod, by hand), and what it
   needs (caches, weights, disk).
