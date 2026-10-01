---
id: circuits-bool-elementwise/20261001T2010Z-friction-boolean-replay-workers-exceed-mem-gb-gemma
campaign: verity
lane: circuits-bool-elementwise
kind: friction
status: open
severity: incident
recurs: note:circuits-bool-switch/20261001T1251Z-friction-replay-workers-exceed-mem-gb
repo: danielreuter/verity
origin: circuits-bool-elementwise
---

# Gemma-2-2B's `boolean-replay` with 30 workers filled a 400 GB `research run` cgroup and died by SIGTERM with an empty stderr

`r20261001-183627-ffcb` failed at 12:40 PM PDT, after a 58-minute prewarm. The parent held the compiled Boolean versions of the
picked specs at 328 GB RSS; 90 s after it forked 30 workers, the scope was at 414 GB of 400 GiB. One OOM kill followed, then SIGTERM
(rc 143), with nothing on stderr. This missed the 11:20 deadline and cost about an hour of node time. The rerun is
`r20261001-200753-63d1` (12 workers, 1,100 GB). The fix proposed in the earlier note still applies: size `--replay-workers` from
the parent's RSS after the prewarm and the cgroup's `memory.max`, and name the OOM kill instead of exiting 143.

**Update, 4:40 PM PDT.** `main` now has 1b656985b, which names a worker's OOM kill and caps `--replay-workers` at
`--worker-peak-gb` peaks per the cgroup's free memory. For Gemma it would not have capped this run. The cap is computed in
`cpu_replay.replay` before `C2.run`, so before the driver's prewarm, while the scope still held a few GiB. The prewarm then grew it to
301 GiB. The default peak, 9.6 GiB, is SmolLM2's. In `r20261001-200753-63d1` (run record `art:e0b6c08c…`, `resources.jsonl`), 12 Gemma
workers took the scope from 301.3 to 664.6 GiB, about 30 GiB each at peak. Under 400 GiB, 30 requested workers would pass the cap
uncapped. The cap should read the cgroup after the prewarm, as this note proposed. Until then, pass `--worker-peak-gb 30` for Gemma-2-2B.
