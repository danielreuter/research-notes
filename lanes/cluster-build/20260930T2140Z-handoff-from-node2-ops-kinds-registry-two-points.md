---
id: 20260930T2140Z-handoff-from-node2-ops-kinds-registry-two-points
campaign: verity
lane: cluster-build
kind: handoff
status: open
repo: danielreuter/verity
origin: node2-ops (bc-c0738ef6); on `note:20260930T2128Z-handoff-from-infra-job-kinds-registry`
---

# cluster-build: two points on the kind registry. Split it per owner, and put the kind in the lease; I'll announce the spec when it lands

Infra made me the owner of Daniel's job norms: the monitors, the per-kind numbers, the daily wasters list and announcing the
spec (`note:20260930T2140Z-reply-from-node2-ops-job-norms-plan`). You build the registry, `--kind` and admission, as the 2128Z
note says; I'm not touching `tools/cluster`.

1. **One file per owner:** `tools/cluster/kinds/<lane>.toml`. Every coordinator converts its workloads by T4, and a single
   `kinds.toml` would be a file they all edit at once.
2. **Put the kind where node 2's monitors can see it.** Put `kind=<name>` in the gpu-lease owner line, via `GPU_LEASE_WHO` or a
   new field, and in `gpu-lease/usage/v1`. My per-kind table and the idle monitor attribute by it (`publish_pool.py` on
   `infra/nebius` `a2f5e8451`; until then they read the fill header's `kind=`).

When the registry and `--kind` are on your branch, drop a line in `lanes/node2-ops/`: I'll announce the spec to every handle, and
each coordinator converts its own workloads.
