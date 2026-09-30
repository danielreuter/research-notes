---
id: 20260930T2126Z-handoff-from-infra-hold-rigid-rules
campaign: verity
lane: cluster-build
kind: handoff
status: open
repo: danielreuter/verity
origin: infra coordinator (bc-17cc41f1); rewritten at 2:56 PM PDT (the 2:26 PM PDT write was lost)
---

# cluster-build: HOLD the rigid job rules. Build provenance, honest resources, heartbeat and per-lane accounting; phase rules become paved-road defaults later

Daniel wants a Hayekian design: agents choose how to structure their jobs, and success is made very clear. This amends
`note:20260930T2128Z-handoff-from-infra-job-kinds-registry` until he rules on the lighter design. Your `--queue` build already
matches it: `--kind` defaults to `adhoc`, and nothing is rejected.

**Proceed, valid either way:**
- **Templates resolved from git at a recorded commit.** The kind or template comes from the shipped commit, is recorded in the ledger,
  and has no node-local copy.
- **Honest resource declarations:** recorded and compared with use.
- **A lease heartbeat and expiry.** Your dead-owner fix covers the stale-lock case.
- **Per-lane accounting** of leased against busy GPU-seconds, published daily: `cluster usage --by lane`, `--by kind` and `--by question`.

**Hold (warnings only, never refusals):** one phase per job, the 60-minute GPU chunk cap, refusing a GPU kind that has a CPU step, the
shape menu, and missing declared outputs.

**Keep process-level GPU leases as the model**, as node 2's `gpu-lease` does. A job may release its GPU for a CPU phase and reacquire it,
keeping its data in RAM or on disk.
