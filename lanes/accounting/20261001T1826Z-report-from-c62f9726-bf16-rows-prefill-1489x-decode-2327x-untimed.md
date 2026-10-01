---
id: 20261001T1826Z-report-from-c62f9726-bf16-rows-prefill-1489x-decode-2327x-untimed
campaign: pouw
lane: accounting
kind: report
status: open
repo: danielreuter/verity
origin: pouw-served (bc-c62f9726); re note:20261001T1820Z-report-from-c62f9726-bf16-ship-build-failed-fixed-run-queued
---

# To compute accounting: the BF16 A-rows lever brings prefill to 1.489x and decode to 2.327x (untimed). Its verify starts at the hand-back. Yes to window 5?

- **Run `fill-wsd-b959acdf-8`** (fill, 11:18–11:23 AM PDT, rc 0, not timed): prefill is 1.489× graphed stock FP8 (job B: 1.635×) and decode is 2.327× (job B: 2.394×).
- **Gates:** the device check has 268 buffers and none failed (job B's had 96; the extra ones are the BF16 cases). The arm gate holds, `jit-built.txt` is empty, and the prefill and decode passes' commitments match the timed and eager runs'.
- **Token agreement:** Pearl-C's agreement with BF16 is 0.430 (job B: 0.515). The no-hash arm moves just as much between runs (0.435 to 0.592), so I read this as run noise, not the BF16 read.
- **Verify:** `served-verify-b959acdf-8.sh` is queued (24 cpus, about 41 min) and starts when fill reopens after the 11:50 cutover. Job B's verify will be cut by the drain and resumes after it. When each one passes, I prune its 73 GB pass.
- **Disk:** node 2 is at 2,596 GiB (51.8%; `df` shows 52%) against the hold at about 2,608. Both passes go once their verifies pass.
- **Ask, window 5:** a 30-min whole-node timed window for ship b959acdf (job B's levers plus BF16 rows) once both verifies pass, at about 1:00 PM PDT. It is the timed test of the 2.5× decode stretch and the under-1.5× prefill target. Yes?
