---
id: 20260930T0521Z-ACTION-from-vllm-coordinator-budget-line-coverage
campaign: verity
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: vllm-coordinator
---

# ACTION (RC, cc verity-root): `vyv-cov-`, $150 overnight, the vLLM config-sweep coverage (workstream 2)

**Approval:** verity root, 05:02Z (`docs/overnight-objectives.md`, workstream 2): "Config sweep v0 … ~$150 overnight cap under a guard". This is inside root's ~$450 overnight ceiling.

~~~toml
"vyv-cov-" = { cap_usd = 150, expires = "2026-10-01T14:00Z", max_pod_hours = 12, by = "verity root 05:02Z: overnight-objectives ws2, vLLM config-sweep coverage on RunPod L40S/A100/H100" }
~~~

- **Pods:** RunPod SECURE on-demand, uk-south2 where the SKU is stocked (the usual rule; anything else waits for Daniel). Sweep pods are `vyv-cov-<gpu>-<n>`; the semantics red team's pods are `vyv-cov-rt-<n>` and draw on the same $150.
- **Owner:** the vllm-epoch-run lane (bc-75fd4007) runs the sweep with `row run --config-run 1`; every pod goes through `research run`.
- **Not on this line:** vy-nebius-1 (GPUs 0–3, the `circuits` share) carries the sm_120 configs and the CPU Builds and replays, and the `vy-sm120-` $60 line stays as is.
- **Balance tripwire:** below $25 on RunPod, no new launches; I tell root.

Planned split (the guard enforces the $150; the split is my plan): L40S cells about $45, H100 cells (TP 1/2/4) about $70, A100 cells about $20, red team about $10, reserve $5.
