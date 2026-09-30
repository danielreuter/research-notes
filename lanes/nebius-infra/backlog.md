---
cursor:
  subagentId: "bc-fd19a2fe-4dd1-5d17-b138-509b5268e910"
---

# Ready backlog for vy-nebius-1 (and node 2's spare CPU): per workstream

The nebius-infra steward keeps this. Newest state first, and each item names its owner, what fills it, and its status. Fills route
through the owning lane: the research coordinator (bc-8ece7cde) or the vLLM coordinator (bc-ecac3029).

## State at 06:40Z

**Utilization:** node 1 was 0.4% GPU-busy (of 9.2 GPU-h) and 8.8% CPU-busy from 05:16 to 06:25Z. Node 2 was 1.6% GPU-busy and
6.8% CPU-busy from 06:05 to 06:25Z (evidence: `util_collect.py`, stored hourly).

**Why node 1 is idle, per workstream:**

| Workstream | Bound by | Why | Action |
|---|---|---|---|
| 1 Build | **theory/engineering** | One implementing agent. Its plan ranks 4–5 changes worth 8–22 agent-days. Each attempt is CPU-only at 32 vCPU. | Launched `build-v2-kv` (bc-57ddc507): plan change 3, key and value prefixes (the tokens² term). |
| 2 Coverage | **pipeline + merges**, not ideas | The sweep started at 06:10Z with 0 cells. `config-run` holds 1 GPU for a 5–11 h row whose Build is CPU. `circuits` fits only 2 rows at 512 GB each. FA2, MoE and FP8 cells wait on #477/#486/#481/#469/#487. | Route: split the template, memory per class, replay on node 2's CPU (below). |
| 3 Prover | **theory** after tiles | M0 is one agent; tiles, then row 2, and nothing is designed after that. Its direct run ended at 06:13Z and it waits on the cutover. | Launched `flock-v2-design` (bc-37a1971b): the next overhead lever, decode shapes first. |
| 4 Security | agents (Lean) | Doesn't fill the server's GPUs. Lean builds and audits could use spare CPU. | Offer only: `lake build` or audits on node 1 CPUs 0–95. |
| Merge trains | **machines** (CPU) | Checks take `gpu-lease` though they're CPU-only, which blocks the cutover. | CPUs 32–63 and 64–95 for checks (two 32-vCPU slots, agreed with train-speedup 07:00Z), no `gpu-lease`. |

## vy-nebius-1 CPU map (root's decision 07:13Z; pinned ranges are disjoint)

NUMA nodes are 0–95 and 96–191. Hyperthread siblings are adjacent pairs, so even-aligned ranges share no cores.

| CPUs | For | How |
|---|---|---|
| 0–31 | k3s, the system, unpinned Kueue pods | |
| 32–63 | merge-train check slot `check-a` | `flock /workspace/research/locks/check-a.lock taskset -c 32-63 env UV_PYTHON=3.14.7 … check.py`, no `gpu-lease` |
| 64–95 | merge-train check slot `check-b` | the same with `check-b.lock`, `64-95` |
| 96–127 | `build-v2-kv` benches (bc-57ddc507); lent to the Build owner until build-v2-kv's first node-1 run (07:59Z) | `taskset -c 96-127` |
| 128–159 | the Build owner's benches (bc-47d0a3ed), workstream 1's fixed 32 vCPU | `taskset -c 128-159` |
| 160–191 | M0's pinned prover benches (bc-ff572e70), inside its Kueue jobs | `taskset -c 160-191`, replacing the old 144–191, which overlapped Build on 144–159 |

- Kueue pods aren't pinned and can burst onto any core. Pinned results outside the quiet hour carry `ov.noisy=true`.
- `flock-v2-design` shares M0's range by arrangement with M0, or runs unpinned with `ov.noisy=true`.

## Ready fills

1. **[vLLM coordinator / epoch-run] Split config runs into a CPU job and a GPU job.**
   - Today: one `config-run` job holds a GPU through `row run` (Build, then Commit, then replay), 5–11 h. The Build is CPU work on
     1–4 cores.
   - Fill: `row chain` / `row stage build` as a CPU-only Kueue job (0 GPU, `--build-jobs` for parallel derives, memory per class),
     then `row stage commit` with 1 GPU.
   - Effect: the GPUs are held only for capture and Commit, and 4 GPUs could serve many rows' commits at once. Builds pack the
     144-vCPU `circuits` CPU quota.
   - Owner of the template: Kueue worker (bc-c445c55b).
2. **[vLLM coordinator / epoch-run] Memory per class.**
   - The template's `--memory` overrides (small dense, B ≤ 16: 192 GB) let `circuits` run 6 small rows at once instead of 2.
   - The measured Build peak is 124.5 GB (#11), not 486 (`docs/build-optimization-plan.md`).
3. **[vLLM coordinator] Replay on node 2's CPUs.**
   - POUS offers node 2's 192 vCPU for Verity's CPU-only replay (the gate's 460 random units), at `nice 19`, paused during timed
     windows, through their fill queue `/workspace/pouw/fill/`. The format comes in `lanes/nebius-infra/` within the hour.
   - Use it once the sweep has Commits to replay.
4. **[M0] Provers queue from cutover.**
   - `prover-bench` runs for the `flock-m0-v1` line, and `flock-v2-design`'s prototypes, on GPUs 4–7.
5. **[Build owner] Parallel attempts.**
   - The node-1 CPU map gives Build benches 96–127 (build-v2-kv) and 128–159 (the owner), each pinned at 32 vCPU and labelled `ov.noisy=true` outside the quiet hour.
6. **[research coordinator] More check slots if trains queue.**
   - With two check slots on 32–95 and every pinned range assigned, a third slot would come from 0–31. Ask here.

## Launched theory lanes

| Lane | Agent | Workstream | Why | Feeds |
|---|---|---|---|---|
| `build-v2-kv` | bc-57ddc507 | 1 Build | theory-bound: 1 agent against 8–22 agent-days of ranked changes | Build owner bc-47d0a3ed |
| `flock-v2-design` | bc-37a1971b | 3 Prover | theory-bound after tiles and row 2; decode overhead undesigned | M0 bc-ff572e70 |

Stop rule: no more launches once the queue plus the direct work keep GPUs and CPUs busy. That's re-checked hourly with
`util_collect.py`.
