---
id: 20260930T1742Z-reply-from-pous-infra-gpu-lease-usage-shipped
campaign: overnight-sep30
lane: nebius-infra
kind: handoff
status: done
repo: danielreuter/verity
origin: pous infra (bc-efe47341), for the one-cluster design (bc-c3ade0aa) and the nebius-infra steward (bc-fd19a2fe)
---

# pous infra -> one-cluster, steward: `gpu-lease`'s per-lease usage report is shipped and live on node 2 (phase 1a)

Replies to `note:20260930T1713Z-handoff-from-pous-one-cluster-to-nebius-infra-steward-gpu-lease-usage`.

- **Commit:** `infra/nebius` `1ebbd156`. It is `tools/research/src/research/pods/sh/gpu_lease.sh`, plus 2 tests in
  `tools/research/tests/test_nebius.py`. Both the `research` and `repository` suites pass.
- **Deployed on node 2 at 17:40Z:** `/workspace/pouw/infra/bin/gpu-lease` (the target of `/usr/local/bin/gpu-lease`), sha256
  `d03c8d155d787f4d…`, the same as the commit. The previous file is kept as `.gpu-lease.prev-f0af4e6f`. Leases taken before
  17:40Z end on the old script.
- **To the spec:**
  - per GPU: `held_s`, and `busy_s` and `sampled_s` from `$GPU_LEASE_UTIL_LOG` (default `/workspace/pouw/infra/util/*.jsonl`,
    10 s readings, busy meaning `util > 0` or `smact >= 0.01`);
  - never NVML;
  - one stderr line per GPU, with the CPU-prep hint under 50% busy of at least 5 sampled minutes;
  - `gpu-lease/usage/v1` records in `$RESEARCH_RUN_DIR/gpu-lease-usage.jsonl` and in `$GPU_LEASE_USAGE_LOG` (default
    `/workspace/research/lease-usage.jsonl`);
  - report-only: CMD's status is `gpu-lease`'s, and nothing is refused or stopped.
- **One mechanism change, needed for the report:** CMD now runs as a child instead of being `exec`'d.
  - stdin is passed through;
  - SIGTERM, SIGINT and SIGHUP to `gpu-lease` are forwarded to CMD;
  - the GPUs are released before the report runs (a 30 s cap);
  - a preemption without a scope signals the lease's children too.
  - Checked on node 2 against a private lock directory: exit status kept (5), stdin, a scope SIGTERM giving 143, and a 25 s
    lease reading 20 s of real samples.
- **On node 1**, set `GPU_LEASE_UTIL_LOG` to its per-GPU series. Without one, a lease records `held_s` alone and prints no
  warning.
