---
id: 20261001T1205Z-handoff-from-proofs-packed-frame-yes-gated
campaign: overnight
lane: proofs-flock-fp
kind: handoff
status: open
repo: verity
origin: proofs (bc-8416bc72-c4cc-5551-93a8-b14a6e5f95d4)
---

# The packed frame has the owner's yes, gated on red-team's statement review

Re `note:proofs/20261001T1200Z-handoff-from-proofs-flock-fp-packed-frame`. The research owner said yes at 4:54 AM PDT
(Slack `1790855684.072569`): "after red-team's statement review, node 2 first, the 12 FP cells only".
- Red-team-proofs-554 reviews it now (`note:red-team-proofs-554/20261001T1205Z-…-packed-frame-statement-review`). No packed
  GPU point runs before its GRANT.
- After the GRANT, run the packed points at the 12 FP cells (NVF4, MXF4 and E4M3 × K = 2048–16384) on node 2 first,
  through n2-hill's feed as your step-3 node-2 points went. Nothing is placed 20 min before a booked window (13:00, 14:00,
  15:00, 15:30 and 16:00Z), and node 2 is ours through 17:00Z. Node-1 packed GPU points come after node 2's, and count
  against proofs' 4-in-flight cap.
- Record each point's packed statement digest beside the default one, and report FP4 (and E4M3) at the old and the new frame
  side by side. A packed point keeps `packed-statement-unreviewed` until the GRANT label is on its head.
- The K=16384 stages resume at 12:55Z under `feedn1.py`'s window, as you planned.
If you need n2-hill's agent to place them, tell me in `lanes/proofs/`.
