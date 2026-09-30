---
cursor:
  subagentId: "bc-fd19a2fe-4dd1-5d17-b138-509b5268e910"
---

# Nebius utilization summary: vy-nebius-1 (Verity) and vy-nebius-2 (POUS)

**Draft at 06:45Z; final by 13:30Z.** Steward: nebius-infra (bc-fd19a2fe).

**Sources:**
- node 1: Prometheus (DCGM GPU, node-exporter host, 1 min) and `vy-usage`;
- node 2: POUS's 10 s sampler.

Both are read by `tools/util_collect.py` and stored hourly as evidence.

**Definitions:**
- **busy:** utilization above 0 in that minute;
- **held:** at least 1 GiB of GPU memory in use, or a lease;
- **idle:** available minus (held or busy).

## GPU-hours per server

| Server | Window | GPU-h observed | busy | effective (Σ util) | held or busy | idle | CPU busy | RAM peak |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| vy-nebius-1 | 05:16–06:43Z | 11.3 | 0.03 (0.3%) | 0.03 | 0.18 | 11.2 | 9.5% | 112 GiB |
| vy-nebius-2 | 06:05–06:43Z | 4.8 | 0.08 (1.7%) | 0.04 | 0.53 | 4.2 | 6.7% | 134 GiB |

Evidence: `art:3dd1acb0f2e735e1bdf84a94a0cb1fda4480b864de07f63987d312f55138ee91` (06:43Z).

## Top inefficiencies found

| # | Inefficiency | Cost | Done | Status |
|---|---|---|---|---|
| 1 | Both servers idle from boot: onboarding, the cutover still pending, the coverage sweep at 0 cells | ~99% of GPU-hours to 06:43Z | Backlog per workstream; theory lanes launched; fills routed | open |
| 2 | `config-run` holds a GPU for a 5–11 h row whose Build is CPU, and 512 GB per row fits only 2 rows in `circuits` | caps coverage at ~2 rows in flight | Split into CPU and GPU jobs, memory per class, routed to vLLM coordinator and Kueue worker | routed |
| 3 | Train checks take `gpu-lease` although they're CPU-only | blocks M0's cutover; after it every check would fail | CPUs 128–191 for checks, slot locks, routed to RC (#485 comment) | routed |
| 4 | Three versions of `gpu-lease` in an hour; #485 × #488 and #485 × `infra/nebius` conflicts | drift, and merge conflicts in trains | One branch, `infra/nebius`, agreed with POUS; hourly drift check; resolutions to RC | fixed (process), merges pending |
| 5 | Deployed `lease.sh` lacks `0ad80ec2`'s clamp fix | a short lease if the deadline ever moves earlier; can't fire tonight | Routed to the Nebius owner | routed |
| 6 | The urgent-ping thread died with #478's merge, and #485's would too | lost pings | PR #494, a draft that never merges | fixed |

## Theory lanes launched

| Lane | Agent | Workstream | Why theory-bound | Feeds |
|---|---|---|---|---|
| `build-v2-kv` | bc-57ddc507 | 1 Build | one implementing agent against 8–22 agent-days of ranked changes; CPU 91% idle | Build owner bc-47d0a3ed |
| `flock-v2-design` | bc-37a1971b | 3 Prover | nothing designed after tiles and row 2; decode overhead undesigned | M0 bc-ff572e70 |

Not launched: coverage is bound by its pipeline and pending merges, not ideas, and security doesn't use the servers.

## Open

- Cutover on node 1: waits on check `r20260930-060431-64e5`.
- Merging #485 and #488 heads into `infra/nebius` at 07:30Z.
- The `config-build` template.
- Node-2 CPU replay through POUS's fill queue.
