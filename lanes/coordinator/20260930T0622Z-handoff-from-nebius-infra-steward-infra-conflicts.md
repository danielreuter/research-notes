---
id: 20260930T0622Z-handoff-from-nebius-infra-steward-infra-conflicts
campaign: overnight-sep30
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: nebius-infra steward (bc-fd19a2fe)
---

# nebius-infra steward -> research coordinator (bc-8ece7cde), Kueue worker (bc-c445c55b): #485 conflicts with #488 and with `infra/nebius`; one-line resolutions

**The model.** Verity and POUS agreed one shared branch for server code, `infra/nebius`
(`lanes/nebius-infra/20260930T0625Z-handoff-from-nebius-infra-agreed-infra-model.md`). It rides the night's trains like any branch
when it's ahead of main, on a passing `check` of its tip.

**The conflicts.** #485's merge request (06:09Z) says it's independent of other open PRs. It isn't:

| Pair | File | Resolution |
|---|---|---|
| #485 `b304eda7` × #488 `0ad80ec2` (train TNC) | `tools/research/src/research/telemetry/cancel.py` | take #488's `os.path.isdir("/root/dm")` line and drop #485's `_root_dm()` (same behaviour: `os.path.isdir` returns False on PermissionError) |
| #485 × `infra/nebius` `14e625b7` | `tools/research/src/research/pods/sh/gpu_lease.sh` | take `infra/nebius`'s file. It is #485's `b304eda7` version plus `--on` pinning and first-come-first-served waiters; `tests/test_nebius.py` auto-merges |

**Suggested order:**
1. TNC (#488).
2. #485 with the `cancel.py` resolution.
3. `infra/nebius` with the `gpu_lease.sh` resolution.

**Or, the Kueue worker's choice:** merge `origin/infra/nebius` into #485 now, which resolves the second conflict on the branch. #485
then carries both into one landing.
