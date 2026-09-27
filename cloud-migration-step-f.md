---
cursor:
  subagentId: "bc-1639584e-b5b8-521b-a290-7304b8abe080"
---

# Cloud migration step (f): run custody on the remote

PR [#11](https://github.com/danielreuter/verity/pull/11), branch `cursor/run-custody-r2-e080`, ready for review 6:27 PM PT Sep 24, not merged.
Complements `internal/cloud-migration-implementation.md` (steps c, h, d, a).

## Live evidence (6:18 PM PT)
- The machine side ran on a cloud VM with the parent key removed from its environment, as on a pod. It used a key minted as the launcher does, with actions only.
- Run `r20260925-011831-5973` (campaign `cloud-migration-f-live-test`): `.custody` preserved, 9 files, logs included. The key was deleted and the workload never saw it.
- A fresh store verified custody from R2 alone. The minted key got 403 on DELETE.
- That run is an R2-only attempt; parity explains it as a pod-side write not yet pulled.

## Switch-over (after current lanes finish; nothing here changes live paths until then)
1. Launch pods' runs with `research run --on M --custody-r2 [--custody-ttl 8h]`. The TTL must outlast the run. The launcher needs the parent key: the Cursor secrets, or on the laptop `set -a; . ~/.config/verity/r2.env; set +a`.
2. Give pods `guard = N` in their machines entry. Otherwise `--custody-r2` drain and reaper can't see the pod's run dirs and refuse (they fail closed).
3. Restart the watcher with `--reap --custody-r2` so reap custody comes from R2 plus the pod guard, not `~/.research/runs`.
4. F2 triage on the laptop, with the parent key sourced: `research data custody --triage --json > /tmp/triage.json`. Then, for each `no-custody` run:
   - `research fetch --all RUN` if its pod is alive;
   - else `research data custody RUN --publish`;
   - or record Daniel's waiver: `research data label RUN custody waived --by daniel`.
5. F1 (not yet run): launch with `--custody-r2` from a cloud VM onto a guarded pod, delete the VM mid-run, then check `research data custody RUN` from another machine and that the guard terminates the pod.
