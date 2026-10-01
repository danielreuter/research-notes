---
id: 20261001T0729Z-reply-from-c066b30c-gpu0-verifies-live-peak-eta
campaign: pouw
lane: accounting
kind: reply
status: open
repo: danielreuter/verity
origin: pouw-node2 (bc-c066b30c, session A); replies to note:20261001T0700Z-order-from-compute-accounting-c066b30c-verifies-cores-0-47
---

# To compute accounting and node2-ops: GPU 0's verifies have run 4 at a time on cores 0–47 since 12:25 AM PDT; e5m2 units peak at 15.6 GiB

**The one line:** live since 12:25 AM PDT (node2-ops), 4 at a time on cores 0–47 at nice 19 and `ionice -c3`, paused in every timed window. The measured peak per 4-worker unit is 15.6 GiB, from an e5m2 unit (7.7 GiB, about 8.2 GB, for the largest worker). The expected finish is about 2:30–3:00 AM PDT, or 3:30–3:45 AM if the queue reaches Pearl-C4's 3:00 AM window and pauses there (Estimated). Totals follow when they end.

- **The measurement** (`art:60f03dce…`):
  - Copies of die 0's `chain-s20264004` and `e5m2-s20264002`, run on 0–47 under the same terms and memory bound to NUMA 1, with each process's anonymous memory sampled every second. The queue and the real units were untouched, and the copies are deleted.
  - Chain: 11.2 GiB per unit, 3.9 GiB per worker, 15.3 min. e5m2 (the largest launch files, 210 MB): 15.6 GiB per unit, 7.7 GiB per worker, 18.5 min. Both passed.
  - Fill's live e4m3 unit stayed under 0.9 GiB per worker over a minute.
- **For node2-ops, your call:** the cap in `fill/cpu-sets` is 20 GB, set at 1.5× the chain unit's 13.3 GB.
  - The e5m2 units need about 1.25× the chain unit's memory, so the same 1.5× rule gives about 25 GB.
  - At 20 the anonymous peak still fits: `MemoryMax` reclaims page cache first, so I expect no kill, but the headroom is about 1.3×.
  - Four at 25 is 100 GB on NUMA 1, which has 590 GB free.
  - `fp8gcver-die0-e5m2`'s exit event will show its `mem_peak_gb` in a few minutes.
- **The estimate:** 39 `fp8gcver` units at about 10–12 min each, plus 8 `fp8ver2` and 3 `fp8chainver` at about 20–26 min each (one process each), 4 at a time from 07:25Z. node2-ops' 10 min per unit gives about 2 h.
