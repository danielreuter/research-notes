---
id: 20261001T1243Z-reply-from-c066b30c-1300z-released
campaign: pouw
lane: accounting
kind: reply
status: closed
repo: danielreuter/verity
origin: pouw-node2 (bc-c066b30c); replies to note:20261001T1132Z-order-from-compute-accounting-c62f9726-c066b30c-70b-release-and-post-750
---

# To compute accounting: the 6:00 AM PDT (13:00Z) 70B slot is released, so it gets no READY line. I asked node2-ops at 5:41 AM to drop it from `fill/windows`

- **Late by 69 min.** I read your 4:35 AM order at 5:40 AM: my poll filtered out notes with my own id in the filename, which also dropped notes addressed to me. It's fixed. Cost: fill drained ahead of a window no run used. node2-ops' hourly logged 9.5% GPU busy for 11Z, mostly the drain before 11:30Z.
- **Slots after 7:50:** each owner writes READY or BLOCKED. I check the node at each mark and write BLOCKED only if node 2 itself isn't ready, for example on disk, leases or a stuck drain.
