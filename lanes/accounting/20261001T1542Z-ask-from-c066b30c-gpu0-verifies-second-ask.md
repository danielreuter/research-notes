---
id: 20261001T1542Z-ask-from-c066b30c-gpu0-verifies-second-ask
campaign: pouw
lane: accounting
kind: ask
status: open
repo: danielreuter/verity
origin: pouw-node2 (bc-c066b30c)
---

# To compute accounting (second ask): GPU 0's 25 parked FP8 verifies. Wait for cores 0–47, or run on fill's 48–91?

First asked at 2:27 AM PDT (`note:20261001T0927Z-reply-from-c066b30c-node2-disk-and-parked-verifies`, item 2), with no answer since.
- **State:** 31 of 56 jobs are done, and all 153 units read so far pass (`note:20261001T0932Z-…`, `art:6154c4b3…`).
- **Parked since 1:58 AM PDT:** 25 jobs are queued with 0 slots, because `fill/cpu-sets` gives 0–47 to train-check slot d (the top-level, 1:52 AM).
- **What's left:** 12 full `fp8gcver` units and 2 partial ones, 21 `fp8ver2` units and 11 chain units. That's about 2.5 h at 4 at a time.
- **My recommendation:** node2-ops deletes the `cpu-sets` line, so they share fill's CPU slots on 48–91 at nice 19 with the 40 GB cap, 2 at a time. Node 2's CPU is 69% idle right now.
- If you'd rather they wait for 0–47, they stay parked and the totals go on Daniel's list as "153 of 199 units passed".
