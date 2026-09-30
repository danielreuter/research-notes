---
id: 20260930T2024Z-handoff-from-circuits-workload-inventory
campaign: verity
lane: infra
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa)
---

# Circuits workload inventory for the one queue: 8 workload kinds, all on node 1's Kueue; Build CPU is our limit

For Daniel's priority 1. Everything circuits runs is already on vy-nebius-1's Kueue (`circuits` share), GPU target RTX PRO 6000
(sm_120). Nothing runs on RunPod. Sources: the old vLLM coordinator's handoff (`note:20260930T2014Z-handoff-from-vllm-coordinator-state-for-circuits`)
and a notes scan; numbers are as of about 1:15 PM PDT; "unknown" means the notes don't say.

| workload | resources | wall per job | volume | launched today | needs |
|---|---|---|---|---|---|
| **Build** (config run step 1) | CPU; 4 vCPU request; RAM class 64–256 GB (4k-context B1 ~486 GiB) | 3 min small; ~40 min 1k; 3 h OLMoE B32; 4k B1 hits the 2 h timeout | **the bottleneck**: the rest of the ~740-deployment grid, incl. ~124 Builds for the formerly held stochastic set; 13 running / 4 waiting at 12:45 PM | dispatcher Kueue Job (`dispatch.py submit config-run`), 8 kept pending in `deployments-cpu` | weights `/workspace/hf`; Program and unit-rule caches; `BUILD_RAM_BUDGET_GB` |
| **Commit** (step 2) | 1 GPU; 64 GB (< B8) / 170 GB (≥ B8) | 5–15 min GPU hold warm; +~6 min cold Triton; plus the replay while it's on the GPU (Phi-3-mini B8 ~16 min) | keep ≥ 8 Commit-ready; 8 waited at 1:12 PM | dispatcher Kueue Job in `deployments-gpu`, engine-key order | persistent Triton/vLLM caches; weights |
| **Replay** (step 3, after PR A/B) | CPU; ~8 vCPU / 64 GB (estimate) | minutes | one per config run | three-task template (`infra/nebius` `900ff195`), off until PR A/B merge | replay bundle |
| **TP2 config run** | 2 GPUs on one host; 8 vCPU; 160–384 GB | unknown (first, p002, submitted) | 91 | plain Kueue Job, `config-run-row` in `deployments-gpu` (root's call, 1:13 PM) | TP2 weights |
| **FP8 deployments** | as Commit | as Commit | 7 now, ~84 after the #582 stack | as Build + Commit | FP8 checkpoints |
| **sm_120 captures** (`port-capture`) | 1 GPU; 16 vCPU; 192 GB | ~1 min warm; ~15 min cold bootstrap | ad hoc, a few a day | `submit.sh port-capture` | HF pins |
| **Build benchmarks** (build-optimization) | CPU on pinned cores (e.g. 96–127) | 25–50 min | a few a day | `research run` / `build_bench.py` on the host | a quiet host for timings; private TMPDIR |
| **MoE manifest rebuilds** | CPU; 256 GB class | unknown | when Definitions change (#557 moves pins) | train checks, local Build | — |

**Utilization failures still open in circuits jobs:**
1. **GPUs held at 0% through CPU phases:** the replay runs inside the Commit on the GPU (alerts for cov-g246, cov-g074, cov-m005/6,
   cov-g208). Fix in flight: PR A/B + the three-task template (lane vllm-config-run-tp2).
2. **The cohort's CPU quota blocks GPU backfill:** GPUs under 5% busy while Commit-ready jobs wait, because Builds fill the CPU
   share; the alerts recur up to 1:07 PM (`lanes/node1-dispatcher/`).
3. **Stale Build jobs requesting 16 vCPU** (they use ~2.5): resubmit at 4.
4. **Node 1 GPUs ~1–2% busy with all 8 reserved** at 12:35 PM (`lanes/kueue-fold/` report): the sum of 1–3.

Fixed in the last 48 h: the GPU held through Build (two-task split), the host-wide bootstrap lock, the SkyPilot waiting cap
(`VY_MAX_WAITING_CELLS`; now the dispatcher route), uid-1000 tree writes, CPU over-request (Build 16 → 4 vCPU).

**Asks:**
- **CPU for Builds** is what limits circuits: node 2's spare CPU for Builds (the old coordinator's 12:09 PM ask), and Build admission
  by measured RSS (build-optimization is measuring; I send you the per-class numbers when they land).
- **Persistent Triton/vLLM caches** per host, so Commits start warm.
- **Keep the 2-GPU-on-one-host shape** TP2 uses in the one queue.
- Tell me when the queue takes `port-capture` and Build benchmarks as plain jobs, and they move.
