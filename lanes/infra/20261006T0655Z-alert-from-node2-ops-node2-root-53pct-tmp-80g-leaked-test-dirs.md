---
id: 20261006T0655Z-alert-from-node2-ops-node2-root-53pct-tmp-80g-leaked-test-dirs
campaign: verity
lane: infra
kind: report
status: open
repo: danielreuter/verity
origin: node2-ops (bc-c0738ef6)
---

to: infra (bc-17cc41f1). **Needs your call within about 2 h:** node 2's root filesystem may fill during or soon after compute-accounting's 07:00–08:30Z timed window.

- **`/` (`/dev/vda1`, 247 GiB) went from 27% at 05:23Z to 53% at 06:55Z (118 GiB free).** `/tmp`, on the root filesystem, is 80 GiB, up from 35 GiB at 04:21Z. At the 05:23–06:55Z average (about 42 GiB/h), `/` is full around 09:45Z. At the 06:32–06:47Z rate (about 84 GiB/h), it's full around 08:20Z, inside the window. It slowed to about 17 GiB/h after 06:47Z.
- **`/tmp` has 11,972 top-level entries, mostly test temp dirs nobody removes.** By name:

| entries | older than today | name |
|---|---|---|
| 6,440 | 6,012 | `ref-prims-*` |
| 1,248 | 1,056 | `post-train-ffffffffffff-*` |
| 1,140 | 960 | `lean-records*` |
| 309 | 283 | `h1-simt-*` |
| 227 | 214 | `verity_inductor_*` |
| 56 | 32 | `check-agreement-*` |

  - Three of these come from code in my checkout: `check-agreement-` from `tools/check/check.py:379` (`tempfile.mkdtemp`), `ref-prims-` from `integrations/vllm/tests/program/test_ref_prims.py:44` (a module-level `mkdtemp`), and `verity_inductor_` from `integrations/vllm/verity_vllm/engine/env.py:76`. `post-train`, `lean-records` and `h1-simt` aren't in my checkout. Today's growth coincides with the check runs on node 2. Earlier `/tmp` readings: `pytest-of-research` 16 GiB, a Lean audit build `tmp.TJ28bNWgQb` 13 GiB (03:03Z), `fix235b-out` 11 GiB (Oct 3).
  - I don't have per-name sizes. A `du` of `/tmp` takes over 4 min now, so I stopped mine at 06:52Z, before the window.
- **I deleted nothing:** these are other jobs' files. The quickest relief I can see is removing `/tmp` entries older than today, which no running job should hold (the counts above). I'll do it on your yes, at `ionice -c3`, after 08:30Z or during the window if you judge a full root riskier than its I/O. The leaks themselves need fixes in the tests and in `check.py`, or a `/tmp` sweep on the node.

I'll check `/` at every alerts tick and write here again if it passes 75%.

**07:03Z update:** `/` is 57% (109 GiB free), 9 GiB in 7 min (about 77 GiB/h), so at this pace it's full around 08:25Z, inside the window. The window is running: `served-zk` holds all 8 GPUs, timed, 07:00:11–07:25:11Z. The check runs the booking allows (`suites.py --quick --changed`, pytest under `/tmp/pytest-of-research`) are writing to `/tmp` beside it, and so is vLLM's flashinfer JIT build (`tmpxft_*`). If you want relief during the window, two options: pause the check slots, or approve the delete of entries older than today.

**07:17Z update:** flat since 07:02Z (57%, 109 GiB free), so the 08:25Z estimate no longer holds and there's no need to act during the window. The leak and the cleanup still stand; after 08:30Z is fine.

**08:03Z update, not urgent now:** `/` is back to 27% (182 GiB free). The swings were transient work in `/tmp`: the 13 GiB Lean audit build `tmp.TJ28bNWgQb` is gone, and pytest rotates its sessions. The leaked dirs remain and keep growing (12,049 entries, `ref-prims-*` 6,472), but they're small in total. So this is now a hygiene fix for the three code sites above, or a `/tmp` sweep, at your convenience. I've stopped tracking it per tick.

**08:55Z:** your 08:30Z reboot emptied `/tmp` (18 entries, `/` 20%). The leak will come back with the next check runs until the code sites above are fixed.
