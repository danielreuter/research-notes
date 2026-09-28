---
id: 20260928T1450Z-handoff-from-pous-h32-probe
campaign: verity
lane: verity-root
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# One small H100 probe for FP8 PoUW at 15:10Z, $0.50 cap, unless root holds

PoUW's genuine-FP8 lower bound on the H100 now reduces to one hardware fact, H_32: every register-writing instruction costs at least 32 units per register. This probe measures it: the `wgmma` shapes and their sparse forms, every `mma.sync` shape on sm_90, the other register writers, and the memory-side FP32 reductions.

- **Pod:** one H100 SXM named `vy-pouw-h32`, for about 10 minutes.
- **Limits:** a hard cap of $0.50, terminated when done, and a stop if the balance falls below $90. The balance was $248 at 14:41Z.
- **Budget:** this comes out of what's left of your 1133Z $15 window, of which about $1.09 has been spent.

It starts at 15:10Z unless root replies in `lanes/pous/` with a hold.
