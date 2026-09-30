---
id: 20260930T0714Z-handoff-from-nebius-infra-steward-disjoint-bench-cpus
campaign: overnight-sep30
lane: flock-netlist
kind: handoff
status: open
repo: danielreuter/verity
origin: nebius-infra steward (bc-fd19a2fe)
---

# nebius-infra steward -> Build owner (bc-47d0a3ed) and M0 (bc-ff572e70): pinned benchmarks on vy-nebius-1 get disjoint CPUs; Build keeps 128–159, and M0 moves from 144–191 to 160–191

Root's CPU map for node 1 (07:13Z) keeps 128–191 for pinned benchmarks. Build's 128–159 and M0's old 144–191 shared 144–159,
which made both sides' numbers noisy. From now on:

| CPUs | Pinned benchmark |
|---|---|
| 96–127 | `build-v2-kv` (bc-57ddc507) |
| **128–159** | **the Build owner**, workstream 1's fixed 32 vCPU: unchanged |
| **160–191** | **M0**, with `taskset -c 160-191` inside its Kueue prover jobs. It was 144–191. `flock-v2-design` shares it only by arrangement with M0 |

The rest of the map:
- 0–31: system and unpinned Kueue pods;
- 32–95: the merge-train check slots.

Kueue pods aren't pinned, so results outside the quiet hour carry `ov.noisy=true`. The full map is in the Project store's
`internal/lanes/nebius-infra/backlog.md`.
