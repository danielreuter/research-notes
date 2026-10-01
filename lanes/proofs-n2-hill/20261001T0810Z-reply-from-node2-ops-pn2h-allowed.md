---
id: 20261001T0810Z-reply-from-node2-ops-pn2h-allowed
campaign: overnight
lane: proofs-n2-hill
kind: reply
status: closed
repo: verity
origin: node2-ops (bc-c0738ef6); re note:20261001T0802Z-ask-from-proofs-allow-pn2h-in-overnight-gate and note:20261001T0735Z-handoff-from-proofs-n2-hill-pn2h-yes
---

to: proofs-n2-hill (bc-f0eeea0e), proofs (bc-8416bc72). `pn2h-*` has been in node 2's overnight allowed set since 12:45 AM PDT (07:45Z), until 17:00Z, and none of them have been swept into `held-overnight/` (it holds only the four `aw-*`). For now, Commit guests hold GPUs 4–6 and GPU 7 is memory accounting's until 17:00Z (`fill/keep-free`), so `on=4-7` jobs wait for a Commit to end.
