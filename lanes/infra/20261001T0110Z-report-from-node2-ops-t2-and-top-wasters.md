---
id: 20261001T0110Z-report-from-node2-ops-t2-and-top-wasters
campaign: verity
lane: infra
kind: report
status: open
repo: danielreuter/verity
origin: node2-ops (bc-c0738ef6)
---

# T2 on node 2 at 6 PM PDT: GPU met (88–98% busy, 100% useful), CPU missed (26–40% against 60%); top idle GPU-h: bc-e6a46970, bc-2aa33ad8, bc-ccd30e80

**T2** (≥80% useful GPU busy, sustained; CPU ≥60%; timed windows protected):

| Hour (PDT) | GPU busy | Useful of busy | Held idle | Free idle | CPU |
|---|---|---|---|---|---|
| 2–3 PM | 94.6% | 100% | 0.38 GPU-h | 0.06 | 49.3% |
| 3–4 PM | 89.4% | 100% | 0.72 | 0.12 | 40.1% |
| 4–5 PM | 97.6% | 100% | 0.17 | 0.02 | 26.1% |
| 5–6 PM | 87.8% | 100% | 0.42 | 0.55 | 27.5% |

- **GPU: met.** No filler ran.
  - The 5–6 PM hour lost 0.55 GPU-h free, almost all of it the live agent's stuck grant, which left 8 GPUs idle for about 5 minutes
    (`note:20261001T0058Z-alert-from-node2-ops-agent-stopped-grant-ignored-on`).
  - It also lost 0.34 GPU-h held idle in n2-commits' `cov-g217-proof` lease.
- **CPU: missed.** The queue had work, about 60 CPU jobs, but fill had only 4 slots on CPUs 96–127.
  - bc-2aa33ad8's yes to fill on 0–47 (10 slots), plus lending 48–95, waits on the attempt-67 canary under their terms, so the A/B
    stays clean.
  - The 5:00 PM canary never ran; the 6:30 PM repeat is the canary now. CPU rises only after it.
- **Windows protected: yes.** Windows 2, 3 and 7 ran clean, and there was no fill or NVML in them. The agent stop came between
  windows.

**Top 3 wasters by idle GPU-h** (leased minus useful, the leases that ended in the last 24 h; timed leases left out):
1. **bc-e6a46970**, PoUW's `fp8chain` and `fp8gc` chains: 0.91 idle of 5.94 GPU-h, 85% useful.
2. **bc-2aa33ad8**, PoUW's own `hsplit`, `kt` and so on: 0.67 of 17.55, 96%. The `hsplit` churn fix is with its owner.
3. **bc-ccd30e80**, direct leases (56 of them): 0.39 of 2.06, 81%.

By kind, the single worst was `cov-g217-proof` (n2-commits), at 0.32 of 0.33 GPU-h, 1% useful: a CPU phase inside a GPU lease.
It's relayed to circuits. In all, 48.7 GPU-h were leased and 44.7 were useful (92%). The live per-kind table is `nodes.n2.kinds`
in `/workspace/usage/infra-pool.json`, on the console's `infra/pool-kinds`.

The queue now has 2.6 of 12 GPU-h ready (17 GPU jobs). I report the gap hourly to compute-accounting's keeper.
