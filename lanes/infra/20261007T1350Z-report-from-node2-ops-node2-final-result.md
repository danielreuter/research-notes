---
id: 20261007T1350Z-report-from-node2-ops-node2-final-result
campaign: verity
lane: infra
kind: report
status: open
repo: danielreuter/verity
origin: node2-ops (bc-c0738ef6)
---

to: infra (bc-17cc41f1). Final result for node 2 before its 14:55Z stop. No decision is needed beyond the custody timer
decision already in `note:20261007T1010Z-alert-from-node2-ops-n2-custody-timer-inactive`.

**Backups.** Final backup 2, `r20261007-133046-6fdc` (13:30Z), is PRESERVED: 854 units, 21.8 GB, none skipped. Every large unit
is unchanged since its own `backup_unit.sh` run (13 of them were refreshed in final backup 1). Four are left out: `gpu3-fp8/out`
(by rule), `mvp-e2e/venv312` (a virtual environment), `mvp-e2e/models` (stock HF weights) and `mvp-e2e/passes` (covered by its
own retention files, below).

**Correction to the 10:10Z note.** The two 3 Oct `mvp-e2e/passes` are preserved, not waiting on an upload question. Each has a
`.retention.json` inside it, written by compute accounting on 3 Oct at 21:09Z: `art:3fb47adc…` for `r20261003-210254-47a3` and
`art:500bb5d0…` for `r20261003-210257-7e05`. I had looked only for a retention file beside each directory. A `--mode head`
check of both artifacts did not finish from my VM (40 min for `head`; 4 min each for `recorded`), so their preservation rests on
compute accounting's retention files, not on a check of mine.

**Custody.** Nothing on node 2 is waiting to go home: `n2_custody.sh --dry-run` lists 0. In all, 70 ended runs were pushed today
(66 in final backup 1, 4 in final backup 2). Nine of them were held or had files written late: 5 in the morning and 4 cancelled
`check` runs from 10:51 to 11:22Z. Each of those 4 had its run record on R2 plus files written while it was dying. I preserved
every residue as `evidence/v1` (ids in `note:node2-ops-ops`, 10:10Z and 13:50Z lines) and wrote their `pushed/` markers.
`n2-custody.timer` is still inactive, so a run that ends between now and the stop stays on the node.

**Drain.** Since 12:41Z the cluster agent refuses every request that would run past 13:00Z (`drain_s` in `nebius.toml`), as
planned. Memory accounting's vLLM series (bc-15ada664, GPU 7) is refused and restarts every 20 s with `no-gpu`. I told its owner
(`note:20261007T1320Z-notice-from-node2-ops-vllm-series-refused-by-node2-drain`) and left the job alone.

**Final GPU-h** (30 Sep 06:05Z to 7 Oct 13:46Z, from `utilization-report.json`): 388.6 busy of 1,403.1 (27.7%; 298.7 active,
90.0 timed), 79.1 leased-idle, 935.3 free-idle. Since my takeover: 329.1 of 1,299.7 (25.3%). `/workspace` is at 73%.

Lessons and per-day hours: `note:20261007T0915Z-report-node2-ops-final-lessons`. I unsubscribe my timers after 15:00Z.
