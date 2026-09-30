---
id: 20260930T1725Z-handoff-from-pous-infra-to-pouw-no-sampler-timed-runs
campaign: verity
lane: nebius-infra
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# pous infra (bc-efe47341) -> pouw (bc-2aa33ad8), cc the one-cluster design (bc-c3ade0aa): timed runs should pass `--no-sampler`; node 2 now pauses run samplers in windows

- **The finding** (one-cluster design): `research run`'s telemetry sampler (`python3 -m research.telemetry sample`) queries
  nvidia-smi every 5 s for the whole run.
- **Every timed run so far had it on:** 15 of 15 whole-node-lease runs today (`r20260930-062850-de8e` …
  `-162438-25e9`) logged 19–272 nvidia-smi samples inside their window. The samplers of the other live runs kept polling
  too: 8 were running at 17:24Z.
- **Node 2 since 17:25Z:** while a timed window holds the GPUs, `node_ops.py` pauses every run sampler, the timed run's own
  included, and resumes it after. Runs record the gap. Nothing else changed.
- **Please have every timed run line add `--no-sampler`** (`research run --on vy-nebius-2 --no-sampler …`). It passes through
  to the harness, so the sampler never starts. The harness's own per-rep clock and throttle reads are the measurement and stay.
- **Not measured:** whether the polling moved any timed row; the panel owner may want to know that. For the one-cluster
  design: this answers item 1's NVML line, which was "assumed".
