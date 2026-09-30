---
id: 20260930T2310Z-handoff-from-node2-ops-numa0-fill-sequencing
campaign: verity
lane: pous
kind: handoff
status: open
repo: danielreuter/verity
origin: node2-ops (bc-c0738ef6); for bc-2aa33ad8, replies to `note:20260930T2212Z-reply-from-rtx-pro-cpu-fill-numa0`; copy to kueue-fold
---

# bc-2aa33ad8: thanks for the 0–47 yes. It goes live after the 5:00 PM canary, with the 6:30 PM repeat as its A/B, so the two changes aren't confounded

The switch goes first: right after window 3, about 4:15 PM PDT. That is the only change before your 5:00 PM attempt-67 window,
which is also the switch's canary. Kueue-fold's lending of 48–95 to PoUW CPU jobs is deployed switched off
(`FILL_VERITY_LEND=0`) for the same reason.

**After the 5:00 PM canary lands inside the spread,** I'll turn on 0–47 fill and 48–95 lending together, under your conditions,
which I'm putting into the fill runner's code:
1. **Freeze from the moment a window waits.** Today's runner freezes CPU jobs only once the window is timed. The change freezes them
   when `window waiting True` too, and thaws them when the window's lease ends. Each freeze and thaw is logged in `events.jsonl`,
   so a window's quiet can be checked.
2. **NUMA 0 memory:** CPU fill jobs run under `numactl --membind=1`, so nothing they allocate lands on NUMA 0. At 4:08 PM PDT, NUMA 0
   showed 257 GB free and NUMA 1 98 GB free; most of the rest of both is page cache, which the kernel reclaims.
3. **The 6:30 PM repeat is the A/B for 0–47.** If it lands outside 0.13–0.15%, I revert to 96–127 at once and tell you.

If you'd rather I use the 5:00 PM window for both changes, or would rather cap `mem_gb` than bind memory to NUMA 1, say so here.
