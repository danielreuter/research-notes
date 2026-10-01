---
id: 20261001T0141Z-reply-from-0f3f8a2f-v2hot-fix2-running-custody-done
campaign: pouw
lane: accounting
kind: reply
status: open
repo: danielreuter/verity
origin: GPU 3 (bc-0f3f8a2f); replies to the 0104Z (v2hot-fails) and 0111Z (v2hot-route) orders
---

# GPU 3 (bc-0f3f8a2f): fix (2) is running; custody is done (6:41 PM PDT)

- **0111Z item 1, fix (2):** it has run since 6:35 PM PDT as a `prio=10` fill job. The selftest passed, and the first unit's gates are clean.
  - **The GPU half** is `gpu3-fp8-fix2-gpu.sh` (`gpus=1`, chunks of 8 min or less): 6 families × 4 units at 8,192², chain from H_i (`const`), bitsets for all 256 atoms. Estimated 25 GPU-min.
  - **The families** are drawn exactly as `hot_late_start.py`'s `family()`; the draws were checked equal on all seven. The code is verity `85474991`, shipped by `r20261001-013255-7ab0` with `--custody-r2`.
  - **The seventh family, `cancel-pair@t4`,** reuses Results 20's 4 units: the same draw and salt.
  - **The judging** is `gpu3-fp8-fix2-blocks.sh` (`gpus=0`, `cpus=16`), which the GPU job queues when it finishes. It covers all seven families at starts 0–5, then 6–16, at every row count against `row-floors-staircase.json` (`6f197bc6…`), as Results 22 did. Estimated 2 CPU-h for starts 0–5. The verdict goes here when it lands.
- **0111Z item 2, (a):** it keeps running, frozen in windows. If fix (2) finds a block in any family, I stop it at once by ending my two jobs and withdrawing their files.
- **0104Z item 2:** superseded by 0111Z item 2, so (a) was not dropped.
  - `cancel-pair@t4` as a separate job stays DROPPED. Its starts 0–3 are judged only inside fix (2), because the assessor's spec lists the family.
  - `v2-hot-16384` is on hold: nothing is written or queued for it.
- **Custody (pinned 5:52 PM PDT):** all eight runs are PRESERVED. The local records lost in VM resets were rebuilt from node 2's run directories, then fetched, published and pushed. The verdict lines are in `internal/pouw/rtx-pro/workers/3-fp8-attacker.md` (6:40 PM PDT). Every node-2 run now launches with `--custody-r2 --custody-ttl 8h`.
- **MKL race:** not exposed. None of my CPU code or jobs imports torch.
