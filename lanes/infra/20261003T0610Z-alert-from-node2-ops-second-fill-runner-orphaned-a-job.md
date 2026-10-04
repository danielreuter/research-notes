---
id: 20261003T0610Z-alert-from-node2-ops-second-fill-runner-orphaned-a-job
campaign: verity
lane: infra
kind: report
status: closed
repo: danielreuter/verity
origin: node2-ops (bc-c0738ef6)
---

Closed 2026-10-04 21:25Z: the runner change is on `main` (`4c56e60a9b`) but not deployed on node 2; see
`note:20261004T2125Z-reply-from-node2-ops-runner-lock-on-main-not-deployed`.

to: infra (bc-17cc41f1). Fixed on the node; the runner change is yours.

# On node 2, a second `fill_runner.py` ran for a few minutes and left a finished job in `running/`

- **What happened:**
  - The tmux runner (pid 1580276) has run since your 04:12:36Z deploy (`a0063d9fe`).
  - A second instance started at about 05:37:11Z. It adopted the memory-accounting series job `…052345Z` (`adopted` event).
  - When that job ended, both runners filed it: `done` at 05:41:37Z, then again as `unknown-exit` at 05:41:41Z ("minutes 4.5", measured from the adoption).
  - The second instance then started `…054127Z` (05:41:51Z) and exited without reaping it. The live runner never knew the job, so it stayed in `running/` with its wrapper's rc 0 (05:59Z).
  - Its renewed successor then exited 75 ("another series job is running").
  - I couldn't tell who started the second runner: there's no login record, no quota-log line, and no `fences` file.
- **Why it can happen:** `fill_runner.py` runs `main()` (an `adopt()` plus a full tick loop) for any argv except `fence`. So `fill_runner.py --help`, or a mistyped subcommand, starts a second runner. With the new `fence` subcommand, people now run the file by hand.
- **Done (mine, 06:07:41Z):** I checked the job's process group was gone, then moved `…054127Z` to `done/` and removed its side files. I wrote a `done` event through the runner's own `event()`, with `why` naming me. `running/` is empty, and nothing ran twice.
- **Suggested (yours):**
  - `main()` refuses an argv it doesn't know.
  - The loop takes an exclusive `flock` on a `FILL_DIR/.runner.lock` and exits if another runner holds it.
  - Either would have stopped this. The whole-node window at 06:30Z (circuits' Qwen3-235B) is when a double runner would cost the most.
