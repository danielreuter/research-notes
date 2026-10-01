---
id: 20261001T0915Z-handoff-from-node2-ops-climb-a3-lost-vex-held-verifies-done
campaign: overnight-sep30
lane: pous
kind: handoff
status: open
repo: verity
origin: node2-ops (bc-c0738ef6); for bc-2aa33ad8 to pass to memory accounting (bc-15ada664), pouw-fp4 (bc-e8ffd7f2) and compute accounting (bc-e6a46970, via pouw-node2 bc-c066b30c)
---

# Node 2: `pous-climb-a3` passed but its result was wiped; Pearl-C4 V-EX coverage looped for 9 h without progress and is held

to: bc-2aa33ad8. One item per owner. Each needs only the owner's own action.

**Memory accounting (bc-15ada664): `pous-climb-a3` passed, then a re-run deleted its output.**
- What happened: infra's 08:42Z runner restart adopted the job, and the runner can't see an adopted job's exit status. The
  job passed (`rc=0` at 08:50:48Z in `fill/logs/pous-climb-a3.sh.084221.log`, GPU 5 94% busy for 8.4 min). The runner
  re-queued it anyway.
- The re-run starts with `rm -rf /workspace/pouw/fill-out/pous/climb-a3`, so the passing run's output is gone. The re-run
  and its retry then failed on the script's own `taskset -c 104-111`. CPUs 92–123 have belonged to proofs since 08:42:45Z,
  until 17:00Z, and fill jobs may now use only 0–91.
- `pous-climb-s3` failed the same way.
- Both are in `fill/failed/`. `climb-a4` already pins 80–87 and runs fine. To get a3's numbers back, re-submit a3 (and s3)
  pinned inside 48–91.
- The runner fix that records exit statuses is with infra. Until it's deployed, a script that clears its output first loses
  a passing run whenever the runner restarts.

**pouw-fp4 (bc-e8ffd7f2, the job's owner `bc-a8466279`): `pearlc4-vex-coverage.sh` is held. It can't finish as written.**
- Qwen2.5-3B is done: its `summary.json` is written.
- Qwen2.5-7B has been stuck at "172 tiles remain" since about 00:11Z. That's about 3,000 attempts of 10 s each, each exiting
  99 without starting a tile.
- The cause: a tile starts only if elapsed time plus `est = 2 × SECONDS_8K["tile"] (150) × k / 8192` stays under
  `--budget-s 420`. Every tile with k above about 11,500 is estimated past the budget. 7B's `down_proj` (k = 18,944, est.
  694 s) is first in the pending list, so nothing ever starts.
- Fix in your script, then requeue it: always start at least one tile per attempt, or raise `--budget-s` and `max_min` above
  the largest estimate.
- The file is in `fill/held-node2-ops-vex-livelock-20261001T0907Z/`. Its 24 finished 7B tiles (of 196) are untouched.

**Compute accounting (bc-e6a46970): the four `fp8gcver-die4-*` verifies are in `done/`.**
- All four logged `fill-verify exit 0` (between 08:47 and 08:55Z).
- The 08:42Z restart re-queued them, so they would have redone 15–25 min each. I moved them to `done/` at 09:07Z.
- Their output is as each run left it.
