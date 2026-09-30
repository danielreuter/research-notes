---
id: assumption-sweeps-20260930T1935Z-first-8-die-pass
campaign: overnight-sep30
lane: assumption-sweeps
kind: handoff
status: open
repo: danielreuter/verity
origin: cursor/assumption-sweeps-95d4 (uncommitted job scripts; nothing to merge)
cursor:
  subagentId: "bc-5be66fb3-9d32-5d36-9f25-3511718395d4"
to: coordinator
created: 2026-09-30T19:35Z
---

# First 8-die invariance pass done on vy-nebius-1: every die gives identical results

Action 2 of the GPU-utilization postmortem. All runs are recorded Attempts in campaign `overnight-sep30`, labelled
`assumption-sweep=<edges|digest|tc-probe>` and `die=<uuid>` by `assumption-sweeps`.

## Results

- **`rt-redteam/edges_job.sh` passed once on each of the 8 dies, with identical measurement sets** on all 8. This
  covers the mma floor −133 (0 mismatches), the RoPE, SiLU and block128 counts, and MUFU `ex2`/`rcp` over all 2^32
  inputs (0 mismatches; sha256 `fb25d530…` and `e5c9fc6a…`). One run per die:

  | die | run |
  |---|---|
  | 0 | r20260930-163202-5bca |
  | 1 | r20260930-161129-3ba0 |
  | 2 | r20260930-164644-5fb0 |
  | 3 | r20260930-170413-d329 |
  | 4 | r20260930-191715-b6b0 |
  | 5 | r20260930-155630-c99c |
  | 6 | r20260930-162916-c1a2 |
  | 7 | r20260930-155726-7b34 |

  Later repeat runs on dies 0, 1, 2, 3 and 6 also passed.
- **Digest sweep: one digest per check across all 8 dies.** It is GPU-only and needs 1 vCPU. The script is
  `as_digest.py` (copy in `internal/lanes/assumption-sweeps/tools/`). It hashes 8 MUFU approx ops (`ex2`, `rcp`,
  `lg2`, `rsqrt`, `sqrt`, `sin`, `cos`, `tanh`) over all 2^32 inputs, and bf16 mma at seeds 1–4 with 2^18 tiles.
  Within each run, every digest is stable across repeats on the default stream and across a concurrent second stream.
  Runs: r20260930-170547-cc9d, -162939-dd7e, -161129-3fb4, -164625-6e47, -162700-6a77, -170926-b241, -155954-84bf,
  -162003-4ad7 (dies 0–7).
- **`tc_probe` `sm120.mma.m16n8k16.bf16` sweep with new seeds:** seeds 1–5 passed (r20260930-183310-185c,
  -190318-6f33, -190617-df61, -190927-4a4d, -192041-73cd). Seed 6 is running, and seeds 7 and 8 are staged.
- **Findings sent to the red team** (note `20260930T1756Z-handoff-from-assumption-sweeps-first-die-results`):
  - block128 mismatches almost every coordinate under layout `a_scales_mn_major`, identically on every die.
  - The router harness reports `errors: 1` on the renormalize check while `outputs_equal` and `words_equal` are true.

## How it runs

- Jobs go through node1-dispatcher ready files in `/workspace/jobs/ready/assumption-sweeps/`.
- Digest jobs run in `backfill` with 1 vCPU.
- Backfill preemption kept killing the 10–20 min edges and `tc_probe` jobs. Those now run in `provers`/`dev` with
  8 vCPU and 64 GB, and a gate keeps at most 2 of my jobs there, so an M0 bench still fits.
- Nine `tc_probe` runs killed by backfill preemption still show `running`. They are labelled
  `run-outcome=preempted-backfill-dead`.
- CPU pinning is the dispatcher's (`taskset 96-127`). There were no clock or power changes and no quota changes.

## Next

- Queue whatever the red team names next: cuBLAS workspace, streams and split-k at new seeds.
- Blocked on its job list. Nothing is needed from you.
