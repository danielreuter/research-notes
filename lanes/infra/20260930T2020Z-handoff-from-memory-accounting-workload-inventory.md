---
id: 20260930T2020Z-handoff-from-memory-accounting-workload-inventory
campaign: verity
lane: infra
kind: handoff
status: open
repo: danielreuter/verity
origin: memory-accounting (bc-15ada664-f325-5371-a473-65d408be3cf5; @memory-accounting, PoUS)
---

# memory-accounting -> infra: PoUS workload inventory for the central queue (nothing runs now; one exclusive-GPU need on resume)

For Daniel's 20:13Z priority 1. PoUS has been paused since his 04:51Z objectives, and nothing of it runs on node 1, node 2 or a pod
today. When it resumes, its jobs go on your queue, and I launch no ad hoc pods. This comes from the repo and the notes;
@old-accounting's reply (due 21:30Z) may add node workloads, and I'll send a correction only if it does.

| Workload | Node / resource | How long | How often (when active) |
|---|---|---|---|
| `protocols/pous/tests` and the PoUS Lean package's build and audit (Mathlib) | CPU, inside `check` | minutes (slow variants: one band segment ≈ 25 s, one dense segment ≈ 8 min) | per PR, through `check` as today |
| `benchmarks/pous` harness (#474: `band-gpu`, `p2-v1-gpu`, `vllm-gpu`, `p2-gpu`): decode bandwidth, timed audits with controls | **one whole GPU, exclusive**: the audits time 0.5 ms deadlines, so no co-tenant on that GPU; any of 4090, L40S, H100, RTX PRO 6000 (it needs a `census/hardware.json` id) | ~10–60 min per run | a few a day, per kernel or scheme change |
| CPU reference encode of a whole store (band, 448 segments = 14 GiB) | CPU fill: parallel across cores, ~2 GB RAM per process | ≈ 3.1 core-hours (24.6 s per segment per core) | rare: per parameter change |

**What the queue needs for PoUS:** an exclusive, whole-GPU timed window, the same shape as PoUW's `gpu-lease 8 --wait --timed
--no-sampler`, but for one GPU, with the SM clock readable during the run. Everything else is ordinary CPU fill.

**Stale registry entries:** `machines.d/vy-pous-gpu.toml`, `vy-pous-cpu.toml` and `vy-pous-4090.toml` (RunPod `h1ab1zz6mptu1x`,
`9d4dqa1v95nk55`, `qoyit5h904i2a2`). Their pods were terminated on 27 Sep at 15:12Z, 15:31Z and 15:48Z
(`lanes/pous-gpu/20260927T1431Z-report-pous-gpu.md`, FINAL). They can be deleted.

No action needed beyond recording it; ✅ on the Slack thread when it's in your inventory.
