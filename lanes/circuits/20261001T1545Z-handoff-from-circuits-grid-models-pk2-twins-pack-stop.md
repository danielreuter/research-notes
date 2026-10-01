---
id: 20261001T1545Z-handoff-from-circuits-grid-models-pk2-twins-pack-stop
campaign: overnight-sep30
lane: circuits
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits-grid-models
---

8:45 AM PDT, item 3 of your 7:55 follow-up: all 9 `-pk2` twins have ended. The 7 that packed match their bases on run
root, binding map and verdict (note:20261001T1540Z-finding-pk2-twins-packed-match). Three things for you:
- **qwen3-06b is pack-stopped (15:36:59Z), but not because of packing.** gm001-pk2 hit the same SiluMul_v1 edge as its
  unpacked base (`layers.27.mlp.act_fn`, gate -97.0). I recommend `dispatch.py pack-lift qwen3-06b`. The stop costs
  only 2 packable items, and another hit on the same edge would stop the model again.
- **For infra:** `n2_build.sh` submits node-2 Builds' Commits with `dispatch.py submit … --task 1`. That bypasses
  `route()`, so those Commits never pack; that is why gm005-pk2 and gm008-pk2 ran unpacked.
- **Should I submit `-pk3` twins** for gm005 (r1-distill-qwen-15b) and gm008 (qwen25-3b) to get them a packed
  comparison? Each is one more pair of the same row; I'll wait for your yes.
