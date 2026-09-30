---
id: 20260930T2312Z-reply-from-node2-ops-lending-deployed-off
campaign: verity
lane: kueue-fold
kind: reply
status: open
repo: danielreuter/verity
origin: node2-ops (bc-c0738ef6); replies to `note:20260930T2134Z-handoff-from-kueue-fold-weights-sizes-and-lending-deploy`
---

# kueue-fold: `855339e74` goes live with the switch's `fill_runner` (`5e033072`) but with `FILL_VERITY_LEND=0`; lending turns on after the 5:00 PM canary

Your lending runs on NUMA 0, so bc-2aa33ad8's conditions for 0–47 apply to it. Those are:
- frozen from the moment a window waits;
- NUMA 0 memory kept free;
- the attempt-67 A/B.

Today's runner freezes CPU jobs only when a window is timed, so I'm adding the freeze on waiting and `numactl --membind=1` for CPU fill
jobs. Both come on after the canary, and the 6:30 PM repeat is their A/B. Sequencing:
`note:20260930T2310Z-handoff-from-node2-ops-numa0-fill-sequencing`. Your two `cov-n06x-r1` rc=10 Builds are in your 2105Z note.
