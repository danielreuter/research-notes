---
id: 20260930T2020Z-handoff-from-node2-ops-first-guest-build-rc2
campaign: verity
lane: kueue-fold
kind: handoff
status: open
repo: danielreuter/verity
origin: node2-ops (bc-c0738ef6)
---

# node2-ops -> kueue-fold: `verity-build-n2proof-g188.sh` built fine (rc 0) and then failed rc=2 on `/home/research/uv.toml: Permission denied`; the Build's attempt is local only

- **Try 1 (20:13:05Z, 2.7 min):**
  - Bootstrap was OK.
  - The Build ran `r20260930-201323-2275`, rc 0, `result=valid`.
  - The script's next step then printed `error: failed to open file /home/research/uv.toml: Permission denied (os error 13)`
    and exited 2.
- **Try 2** hit the same error at once, so the job is in `/workspace/pouw/fill/failed/`. Logs:
  `/workspace/pouw/fill/logs/verity-build-n2proof-g188.sh.2013*.log` and `.2015*.log`.
- **The cause is in the job, not the pool.**
  - `/home/research` is mode 750, and the file doesn't exist. So whatever runs that `uv` command can't read `/home/research`,
    which suggests a different uid, a sandbox, or a mount namespace. uv's config discovery then fails instead of skipping.
  - A likely fix is `UV_NO_CONFIG=1`, or a `cwd` and `HOME` under `/workspace/jobs` for that step.
- **Custody:** the Build's attempt was published "local only (no remote configured)". Its outputs sit only on node 2's disk,
  under `/workspace/jobs/runs/r20260930-201323-2275`, until your rsync moves them to node 1 or a `research data push` preserves them.
- **The pool itself worked:** the job started in the Verity pool, on its CPUs and scope.
- **To retry:** move the fixed script back into `queue/`. The failed copy stays in `failed/`.
