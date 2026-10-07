---
id: 20261007T0915Z-report-node2-ops-final-lessons
campaign: pouw
lane: node2-ops
kind: report
status: open
repo: danielreuter/verity
origin: node2-ops (bc-c0738ef6), worker of the infra coordinator (bc-17cc41f1); final backup 1 of 2
---

# node2-ops: final GPU-hours and lessons from running node 2 (30 Sep – 7 Oct)

For whoever runs vy-nebius-2 next. The day-by-day record is `note:node2-ops-ops` (`lanes/node2-ops/ops.md`).

## Final GPU-hours

From the GPU sampler (`/workspace/pouw/infra/util/*.jsonl`, `util_report.py`), 30 Sep 06:05Z to 7 Oct 09:08Z, 170.7 h on 8 GPUs.
Busy means active plus timed.

| Span | GPU-h | Busy GPU-h | Busy % | Leased-idle | Free-idle |
|---|---|---|---|---|---|
| Whole record | 1,365.9 | 385.5 (active 295.6, timed 90.0) | 28.2% | 78.7 | 901.7 |
| Since node2-ops took over (30 Sep 19:00Z) | 1,262.5 | 326.0 | 25.8% | | |
| 30 Sep (18 h) | 143.3 | 96.7 | 67.5% | 15.2 | 31.4 |
| 1 Oct | 190.9 | 37.3 | 19.5% | 19.3 | 134.3 |
| 2 Oct | 192.0 | 22.9 | 11.9% | 12.2 | 157.0 |
| 3 Oct | 192.0 | 86.8 | 45.2% | 10.6 | 94.5 |
| 4 Oct | 192.0 | 75.6 | 39.4% | 6.1 | 110.2 |
| 5 Oct | 192.0 | 22.8 | 11.9% | 4.2 | 165.0 |
| 6 Oct | 190.6 | 35.5 | 18.6% | 9.7 | 145.3 |
| 7 Oct (to 09:08Z) | 73.0 | 7.9 | 10.9% | 1.2 | 63.9 |

Timed windows held the node for 11.2 h in all. The biggest users of busy GPU-h were memory accounting's fill jobs (bc-15ada664,
115.1), `research` runs (58.2), circuits' TP8 (43.3), and the fill jobs of bc-2aa33ad8 (21.0) and pous infra (20.2). From 2 Oct on,
the main reason node 2 sat under the 80% bar was an empty GPU queue, not scheduling: since 6 Oct 09:00Z only one fill job (GPU 7)
ran, 11.1% busy. Infra's steward already reports the idle GPUs, so I stopped relaying it.

## Lessons

1. **Test a reader against a known record before trusting its silence.** For about 4 h on 6 Oct my alerts check keyed on
   `ts`/`time`; `alerts.jsonl` uses `t`, so every tick printed nothing and looked like "no alerts". `~/node2-ops/alerts.sh` now
   holds the one correct reader.
2. **"Preserved" is the store's answer, not a run's exit code.** Until 7 Oct 03:12Z I logged a backup as preserved when its run
   ended rc=0. Ask `research data preserved RUN --mode head` (it takes 30–60 s; give it a 200 s timeout).
3. **Large units need tracking of their own, every hour.** `backup.sh` leaves each unit over 1 GiB to a standalone
   `backup_unit.sh` run. The list grew from 21 units (1 Oct) to 41 (7 Oct), and my `large_backup.sh` skipped any unit that already
   had a row in `large-units.tsv`, changed or not. At the final backup, 13 units had no current copy: `fill-out/fp8-gpucheck/die1`–`die7`
   (four changed after their 1 Oct runs, three never had one), `gpu7-fp4/gc` and `kt`, `fill-out/pous/work`, `fp8-security/llama8b-w0`,
   `pouw-design/captures` and `pouw-lean-dd9ede96/work`. `large_backup.sh` now skips a unit only if nothing in it changed since its
   latest row, and the final backup runs all 13. Better still: have the hourly backup list the large units that changed since their
   row, and launch them itself.
4. **A custody path needs a liveness check.** `n2_custody.sh` sends home the runs that can't keep custody themselves (local-only
   runs on node 2's store). Its stopgap loop ended at 16:00Z on 4 Oct, and `n2-custody.timer` is inactive, so nothing has pushed since.
   At 09:00Z on 7 Oct its dry run listed 65 ended runs held only on node 2: 39 PoUS, 18 compiled-commit-overhead, 2 network
   accounting, 1 circuits TP8 and 5 without a campaign (one of them 7.6 GiB). Nothing alerted. The hourly report should carry the
   dry run's count and the age of the last push.
5. **Hold during timed windows, and make that a check inside the script.** `hourly.sh` refuses to run during a timed lease or a booked
   window. A guard file that may disappear (`slot-windows`, deleted 6 Oct) has to be optional without letting the guard fail open.
6. **One runner, checked every tick.** Two threads acting on node 2 at once caused real confusion on 1 Oct
   (`note:20261001T0712Z-friction-two-node2-ops-threads-at-once`); the `ops-owner` check fixed it.
7. **Read the notes inbox on every alerts tick, not just `alerts.jsonl`.** I missed a lane's 25-minute ask once, and an origin filter
   in `inbox.sh` dropped replies that cited my own note ids until 1 Oct evening.
8. **The agent store keeps no exec bits.** `bootstrap.sh` has to `chmod` after the last copy; a chmod before it cost an hourly run.
9. **Correct your own log in the next line, plainly.** From 14:18Z to 17:16Z on 6 Oct my hourly lines named the wrong GPU (1 for 7); the 18:10Z line fixed it.

## Left for the owner (infra, bc-17cc41f1)

- **Custody:** the final backup runs `n2_custody.sh` rounds by hand on node 2 (tmux `n2c-final`, log
  `/workspace/pouw/infra/lane/node2-ops-custody-final.log`) until nothing is left or 11:50Z, before node 1's 12:10Z hold. Whatever
  remains after that, and the inactive `n2-custody.timer`, are infra's.
- **`mvp-e2e/passes` (compute accounting's):** the 6 Oct pass is preserved (`art:1da97484…`), and its retention file says to keep
  it read-only "until Daniel answers the upload question". The two 3 Oct passes (74 GB and 73 GB) have no retention file and no
  backup. I left them out, since uploading them is that same open question.
- **Not backed up, by design:** `gpu3-fp8/out` (standing rule), `mvp-e2e/venv312` (a virtual environment) and `mvp-e2e/models`
  (stock Hugging Face weights for Llama-3.1-8B-Instruct and Qwen3-8B).
- `/workspace` is at 71% (about 1.5 TiB free) and was losing about 11 GiB/h overnight.
