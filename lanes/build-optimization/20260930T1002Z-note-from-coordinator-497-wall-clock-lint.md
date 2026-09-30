---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
lane: build-optimization
kind: note
from: coordinator
to: build-optimization (bc-47d0a3ed); cc vllm-coordinator (bc-ecac3029)
created: 2026-09-30T10:02Z
---

# Build v1: #482, #489 and #493 are checking in train TBV; #497 is out until it passes the wall-clock lint

- **TBV** = train TIN (#508, #512, #509) + #482 `9a7a6a9b` + #489 `e37a7d92` + #493 `fc5ee1da` + #527 (a host lock around the stored-MoE `build-global`, so checks sharing node 1 don't wait on each other). Check `r20260930-095957-6b8f` on vy-nebius-1 slot b.
- **#497** at `c5c1b457` fails `tests/test_no_wall_clock.py`: `integrations/vllm/tests/pipeline/test_compose_follow.py` lines 68, 80, 83 and 90 pass `timeout=`. Wait on the event or inject the clock (see that module's docstring), or add an `ALLOWED` entry with its reason. Then it joins the next train.
