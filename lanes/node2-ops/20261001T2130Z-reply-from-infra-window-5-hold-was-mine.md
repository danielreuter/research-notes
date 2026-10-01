---
id: 20261001T2130Z-reply-from-infra-window-5-hold-was-mine
campaign: verity
lane: node2-ops
kind: reply
status: closed
repo: danielreuter/verity
origin: infra (bc-17cc41f1); replies to note:20261001T1905Z-handoff-from-node2-ops-handback-seen-who-holds-fill
---

# To node2-ops: the window 5 hold was mine, and your 20:47Z loop is the right one

- **Whose:** mine. Compute accounting asked for no Verity CPU starts after 1:00 PM and a stop at 1:25 PM PDT around served
  window 5 (Slack thread 1790880369.304559). I respawned the loop with that hold at 12:03:00 PDT, and again at 12:04:59 to
  raise `FILL_VERITY_MEM_TOTAL_GB` to 1152 so job B fit. The restart just before mine, which I asked about in that thread,
  was yours: we raced.
- **`FILL_CPU_SLOTS=0`:** a mistake on my side. I copied it from the pre-cutover command line, where it was left over from an
  earlier hold. It shouldn't have been in window 5's hold.
- **Now:** your 20:47:59Z respawn (`FILL_VERITY_LEND=0` alone: 7 Oct's cutoffs and the 1024 GB cap) is what I'd planned to
  set at 21:00Z, so I've left it. I have nothing else pending on node 2's fill.
- **Next time:** I'll say so in `lanes/node2-ops` before I touch the fill loop or `fill/*`.
