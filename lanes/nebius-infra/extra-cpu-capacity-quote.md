---
cursor:
  subagentId: "bc-fd19a2fe-4dd1-5d17-b138-509b5268e910"
---

# Extra CPU and RAM for vLLM deployments' Builds, replay and checks: options and quote

For Daniel's go on spend. By the nebius-infra steward (bc-fd19a2fe), 16:20Z Sep 30. Prices are from Nebius's compute pricing page
(docs.nebius.com/compute/resources/pricing, read 16:17Z) and Runpod's API docs. Nothing has been created or requested.

## What node 1 has now (16:18Z)

- **RAM:** 840 GB of 1,716 in use and 875 GB available. The node's scheduler has 1,731 GB (93%) reserved, and big 4k-context
  Builds (100–127 GiB each) now dominate.
- **CPU:** 188 of 192 vCPU reserved at the node, while actual use is about 20–35%.
- **Freeing it for free:** correcting requests frees most of this. A Commit now reserves 64 GB (it uses about 6 GiB), and
  epoch-run is moving Build requests to measured peaks.
- **Adding capacity:** extra RAM helps whenever several large Builds run at once.

## Options

| Option | Size | $/hour | Time to ready | Blockers |
|---|---|---|---|---|
| **A. POUS's spare node-2 CPUs and RAM** | ~120–150 vCPU idle (34% busy at 16:17Z); ~1,600 GB RAM free (44 GiB used of 1,716) | **$0 extra** (node 2 is already billed) | ~3–4 h of integration after POUS agrees | POUS's yes. Only TCP 22 runs between the servers, so node 2 can't join node 1's cluster: jobs run as processes over SSH (a small runner, or POUS's fill queue), paused in POUS's timed windows. Node 1 needs a key node 2 accepts, restricted to the runner (an access change). Model weights and trees go to node 2 over SSH, and results come back. |
| **B. Nebius CPU-only VM**, AMD EPYC Genoa, 64 vCPU / 256 GiB (the largest preset), joined to node 1's cluster | per VM | **$2.27/h** from Oct 1 ($1.60 today): vCPU $0.015, RAM $0.0045/GiB, a 2 TB weights disk ~$0.15, boot disk ~$0.01 | ~1–2 h after both blockers clear: VM ~10 min, k3s join ~15 min, weights copy 30–60 min | The project had **no CPU-only VM quota** at launch (`launch.sh`), so a quota increase comes first. The security group must also admit k3s traffic between the VMs (TCP 6443 and 10250, UDP 8472). Both are cloud changes. |
| B × 4 | 256 vCPU / 1 TB | **$9.07/h** (~$218/day) | as above | **Trips the $800/day Nebius spend alert** (today ~$710/day). One VM (~$54/day) stays under it. |
| **C. Runpod CPU pods** | at most 32 vCPU and 128 GB per pod (general purpose, 4 GB/vCPU) | ~**$1.28/h** per 32-vCPU pod at the $0.04/vCPU example price in Runpod's API docs (the live catalog price needs our key) | ~30–60 min: `research pods create` plus `research run --on` exist; a pod boots in 5–10 min, and weights download per pod | 128 GB is too small for 4k-context Builds (100–127 GiB, some up to ~486 GiB). Fine for small Builds and replay/checks. Needs a `budgets.toml` line. Not in node 1's cluster; outputs return through R2 custody. |

## Recommendation

1. **Now, free:**
   - Keep correcting requests: Commits at 64 GB, Builds at measured peak plus 25%.
   - Ask POUS for option A. It's the most RAM at no extra cost, and the only cost is integration time.
2. **If A is refused or too slow:** one Nebius CPU VM (B), if the quota comes through. It's $2.27/h and stays under the spend
   alert.
3. **Runpod (C)** only for small Builds and replay/checks that fit in 128 GB.
