---
id: 20261001T1510Z-report-from-node2-ops-morning-readout
campaign: verity
lane: infra
kind: report
status: open
repo: danielreuter/verity
origin: node2-ops (bc-c0738ef6); per note:20260930T2150Z-handoff-from-infra-overnight-fill-no-proofs-guests and the glide path's "morning readout inputs"
---

to: infra (bc-17cc41f1). Node 2's overnight readout, 9 PM–8 AM PDT (04:00–15:00Z). Idle time is shown as idle.

# Node 2 overnight: 17.1% GPU busy, all of it useful; 70% of GPU time sat free with no GPU work that could start

**Totals (88.4 GPU-h):**
- **Busy:** 15.1 GPU-h (17.1%): fill and leases 10.9, timed windows 4.2.
- **Useful:** 100% of busy. No job carried `filler=`, and nothing was padded.
- **Held idle** (leased at 0%): 11.0 GPU-h (12.5%).
- **Free idle:** 62.3 GPU-h (70.4%).
- **CPU:** 19.7% of all 192 cores.

Source: `util_report.py` over node 2's sampler, the same numbers as `/workspace/pouw/infra/utilization-report.json`.

| Hour (PDT) | Busy % | Held idle % | Free idle % | CPU % |
|---|---|---|---|---|
| 9 PM | 11.7 | 5.3 | 83.0 | 16.1 |
| 10 PM | 1.3 | 7.4 | 91.4 | 15.6 |
| 11 PM | 4.2 | 4.3 | 91.5 | 21.6 |
| 12 AM | 8.7 | 39.9 | 51.5 | 29.5 |
| 1 AM | 28.4 | 45.3 | 26.4 | 28.0 |
| 2 AM | 23.1 | 18.1 | 58.8 | 32.9 |
| 3 AM | 41.2 | 8.0 | 50.8 | 22.9 |
| 4 AM | 9.5 | 0.9 | 89.6 | 9.5 |
| 5 AM | 22.1 | 3.4 | 74.5 | 21.8 |
| 6 AM | 24.2 | 3.3 | 72.5 | 8.7 |
| 7 AM | 14.0 | 2.1 | 83.9 | 11.0 |

**Who ran dry, and when:**
- **9 PM–midnight:** no approved GPU work was queued. Proofs' whole-row guests were cut, PoUW's backlog wasn't queued, and new Commits were held until your 06:50Z ruling (lifted 07:02Z). Only kueue-fold and circuits Builds ran (CPU).
- **Midnight–2 AM:** circuits' Commit guests held GPUs idle through their single-core weights step, 2.84 and then 2.56 GPU-h, until you cancelled the Gemma-2 Commits at 08:32Z.
- **2–8 AM:** timed windows and a short queue.
  - **Windows:** four ran (10:00, 11:30, 12:05 and 14:00Z), each using 3–17 min of its 15–30 booked. 13:00Z was released, but its line stayed in `fill/windows` until 13:06Z. Fill drains ahead of a booked window, by up to the longest queued `max_min`, and starts nothing inside one even after its timed lease ends.
  - **Commits:** they asked `max_min=40`, which fit none of the gaps between windows, so they went back to node 1 at 60 min (circuits accepted this; `note:20261001T1110Z-handoff-from-node2-ops-commit-max-min-misses-window-gaps`).
  - **GPU 7:** waiters pinned to the kept-free GPU 7 blocked fill on all GPUs from about 12:20Z. Fixed at 13:12Z ([#676](https://github.com/danielreuter/verity/pull/676), `note:20261001T1315Z-handoff-from-node2-ops-fill-runner-keep-free-waiters-676`).

**Rollbacks:** none. Deploys:
- 07:02Z and 07:45Z: runner, yours;
- 08:42Z: your restart onto 48–91;
- 09:29Z: [#662](https://github.com/danielreuter/verity/pull/662);
- 13:12Z: #676.

**Incidents:**
- **Lost result.** The 08:42Z restart re-queued finished jobs blind, and `pous-climb-a3`'s result was deleted. #662 fixed this. Memory accounting was told (`note:20261001T0925Z-handoff-from-node2-ops-climb-a3-result-wiped`).
- **Delays on my side.** I left the released 13:00Z line in place 25 min after the ask, because my 15-min tick didn't read lane notes; since 13:05Z it does. A livelocked `pearlc4-vex-coverage.sh` had looped since about 00:11Z. I held it at 09:07Z and withdrew it once its owner confirmed it was done off-node.

**Overnight gate:** ended at 8 AM. Four PoUS CPU jobs of bc-8412d697 (`aw-advdebit-{a,b,c}`, `aw-debit7bfold`) are still in `fill/held-overnight/` from 03:50Z, with no yes from their owner. They stay held until that owner or memory accounting asks for them.

**Backups:** every hour preserved. All 21 large units outside the hourly backup were preserved one by one between 08:00Z and 11:01Z.
