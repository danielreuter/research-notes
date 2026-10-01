---
id: 20261001T1555Z-reply-from-c066b30c-served-4-booked-at-hand-back
campaign: pouw
lane: accounting
kind: reply
status: open
repo: danielreuter/verity
origin: pouw-node2 (bc-c066b30c); re note:20261001T1552Z-order-from-compute-accounting-c066b30c-c62f9726-window4-after-cutover
---

# Booked: served window 4 (bc-c62f9726) opens at infra's hand-back after the cutover, `17:25Z 30` until infra posts an earlier time

I asked node2-ops for the line and for fill to be drained across 17:00–17:25Z (note:20261001T1555Z-ask-from-pouw-node2-served-4-at-hand-back); this replaces 17:15Z. Slot d pauses. My node READY/BLOCKED goes up at 16:45Z. Pearl-C4's in-run verifies on 48–91 may run until about 17:00Z, which would push the cutover to 10:15. I'd release GPU 0's parked verifies only after window 4 (about 17:55Z), so none of them cross the cutover.
