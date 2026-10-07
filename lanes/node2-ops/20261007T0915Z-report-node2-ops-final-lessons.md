---
id: 20261007T0915Z-report-node2-ops-final-lessons
campaign: pouw
lane: node2-ops
kind: report
status: closed
repo: danielreuter/verity
origin: node2-ops (bc-c0738ef6), worker of the infra coordinator (bc-17cc41f1); final backups 1 (09:00Z) and 2 (13:30Z)
---

# node2-ops: final GPU-hours and lessons from running node 2 (30 Sep – 7 Oct)

For whoever runs vy-nebius-2 next. The day-by-day record is `note:node2-ops-ops` (`lanes/node2-ops/ops.md`).

## Final GPU-hours

From the GPU sampler (`/workspace/pouw/infra/util/*.jsonl`, `util_report.py`), 30 Sep 06:05Z to 7 Oct 13:46Z, 175.4 h on 8 GPUs.
Busy means active plus timed. Node 2 admits no GPU work after 13:00Z (`drain_s = 7200` before the 15:00Z stop), so these are final.

| Span | GPU-h | Busy GPU-h | Busy % | Leased-idle | Free-idle |
|---|---|---|---|---|---|
| Whole record | 1,403.1 | 388.6 (active 298.7, timed 90.0) | 27.7% | 79.1 | 935.3 |
| Since node2-ops took over (30 Sep 19:00Z) | 1,299.7 | 329.1 | 25.3% | | |
| 30 Sep (18 h) | 143.3 | 96.7 | 67.5% | 15.2 | 31.4 |
| 1 Oct | 190.9 | 37.3 | 19.5% | 19.3 | 134.3 |
| 2 Oct | 192.0 | 22.9 | 11.9% | 12.2 | 157.0 |
| 3 Oct | 192.0 | 86.8 | 45.2% | 10.6 | 94.5 |
| 4 Oct | 192.0 | 75.6 | 39.4% | 6.1 | 110.2 |
| 5 Oct | 192.0 | 22.8 | 11.9% | 4.2 | 165.0 |
| 6 Oct | 190.6 | 35.5 | 18.6% | 9.7 | 145.3 |
| 7 Oct (to 13:46Z) | 110.2 | 11.0 | 10.0% | 1.6 | 97.5 |

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
   At 09:00Z on 7 Oct its dry run listed 65 ended runs held only on node 2 (66 by the time the rounds ran): 39 PoUS,
   18 compiled-commit-overhead, 2 network accounting, 1 circuits TP8 and 6 without a campaign (one of them 7.6 GiB).
   Nothing alerted. The hourly report should carry the
   dry run's count and the age of the last push.
5. **Hold during timed windows, and make that a check inside the script.** `hourly.sh` refuses to run during a timed lease or a booked
   window. A guard file that may disappear (`slot-windows`, deleted 6 Oct) has to be optional without letting the guard fail open.
6. **One runner, checked every tick.** Two threads acting on node 2 at once caused real confusion on 1 Oct
   (`note:20261001T0712Z-friction-two-node2-ops-threads-at-once`); the `ops-owner` check fixed it.
7. **Read the notes inbox on every alerts tick, not just `alerts.jsonl`.** I missed a lane's 25-minute ask once, and an origin filter
   in `inbox.sh` dropped replies that cited my own note ids until 1 Oct evening.
8. **The agent store keeps no exec bits.** `bootstrap.sh` has to `chmod` after the last copy; a chmod before it cost an hourly run.
9. **Correct your own log in the next line, plainly.** From 14:18Z to 17:16Z on 6 Oct my hourly lines named the wrong GPU (1 for 7); the 18:10Z line fixed it.
10. **Look for a unit's retention file inside it too.** At final backup 1 I reported the two 3 Oct `mvp-e2e/passes` as having no
   retention file and no backup, because I looked only for `<dir>.retention.json` beside them. Each has a `.retention.json` inside
   naming a preserved artifact (compute accounting wrote them at 07:37Z and 09:17Z).
11. **A cancelled run's custody misses what it writes while it dies.** Every held run here (7 `check` runs, 1 network accounting run)
   had its attempt and run record on R2, but files written after the record was taken (`lean-audit.log`, suite logs, last outputs)
   made its verify fail. Each such residue is a few KB to a few MB; put it in the store as `evidence/v1` rather than re-pushing GBs.

## Left for the owner (infra, bc-17cc41f1)

- **Backups:** final backup 1 `r20261007-090106-71c9` (842 units, 22.4 GB) and final backup 2 `r20261007-133046-6fdc` (854 units,
  21.8 GB, at 13:32Z), both PRESERVED, none skipped. All 37 large units we keep are backed up as standalone runs and unchanged since
  (`large-units.tsv`; the 13 refreshed at 09:05–09:43Z total 84.6 GB).
- **Custody:** caught up by hand. At final backup 1, 66 ended runs: 61 home on R2 with their run records through node 1, and 5 held.
  At final backup 2, 4 more (`check` runs cancelled 10:51–11:22Z). Their run records were already on R2. Each of the 9 held or
  late runs has its missing files preserved as `evidence/v1` and a `pushed/` marker naming the artifact (ids in `ops.md`, 10:10Z and
  13:50Z). `n2_custody.sh --dry-run` lists 0. `n2-custody.timer` is still inactive: runs that end before the stop wait on it.
- **`mvp-e2e/passes` (compute accounting's):** all three passes carry retention files naming preserved artifacts: the 6 Oct pass
  (`art:1da97484…`, "keep read-only until Daniel answers the upload question") and the two 3 Oct passes inside their directories
  (`art:3fb47adc…`, `art:500bb5d0…`, "G4 FP8 served table", until 7 Nov). I left them out of my backups.
- **Not backed up, by design:** `gpu3-fp8/out` (standing rule), `mvp-e2e/venv312` (a virtual environment) and `mvp-e2e/models`
  (stock Hugging Face weights for Llama-3.1-8B-Instruct and Qwen3-8B).
- `/workspace` is at 73% (about 1.36 TiB free); the large-unit tarballs took about 100 GiB of it.
