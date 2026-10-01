---
id: circuits-bool-switch/20261001T1251Z-friction-replay-workers-exceed-mem-gb
campaign: verity
lane: circuits-bool-switch
kind: friction
status: open
repo: danielreuter/verity
origin: circuits-bool-switch
---

# The Boolean hot-swap replay with `--replay-workers 24` fills a 96 GB `research run` cgroup and dies by SIGTERM with an empty stderr

- **What failed.** The SmolLM2 460-unit replay ran twice with 24 workers under `--mem-gb 96`: `r20261001-105818-4571` and `r20261001-114003-c1ae`.
  - Each time the cgroup hit its cap: `memory_peak_bytes` 103,079,215,104, 25 OOM events, 1 OOM kill.
  - The job then ended with rc 143. Its stderr was empty, so it looked like an outside kill.
- **What it cost.** About 40 minutes of node time and a re-run on the PR 1 deadline.
- **What worked.** 16 workers under 144 GB (`r20261001-115415-9980`), which peaked at about 154 GB without an OOM event, and 12 workers under the default (`0b4b`).
- **Where to look next time.** `resources.jsonl`'s `cgroup` samples show the cap: `memory_events.oom_kill`.
- **The better abstraction.** The replay could size `--replay-workers` from the cgroup's `memory.max`, or report the OOM kill instead of exiting 143 with an empty stderr.
