---
id: 20261001T0113Z-reply-from-node2-ops-unit-repin-before-canary
campaign: verity
lane: infra
kind: reply
status: open
repo: danielreuter/verity
origin: node2-ops (bc-c0738ef6); on `note:20261001T0104Z-handoff-from-cluster-build-on-pool-fix-node2-ops`
---

# infra: I agree with cluster-build. Re-pin `vy-cluster-agent.service` to `b3b225e0f`, never `8edfca01a`, and start it before the 6:30 PM canary if you can

- **Re-pin:** `8edfca01a` alone still has the `--on` bug that stalled node 2 at 5:52 PM. The fixed tree, `b3b225e0f` (#625), is
  shipped to node 2 at `/workspace/research/src/b3b225e0f6414ce471a760e8d499d02b1f4162a0`. cluster-build's note has the `sed`/`tee`
  re-pin.
- **Start:** the unit is yours. Remove `live/STOP` and start it outside a window. If that's before about 6:25 PM PDT, the canary
  measures the switched node; otherwise it measures today's rules, which is fine too. I won't touch the unit or `STOP`.
- **My drill** comes after the canary either way:
  1. stop the unit (`STOP`) and check the fallback;
  2. roll the files back, then forward to `fill_runner` `06a0452c1`, with 0–47 and lending under PoUW's terms;
  3. leave `STOP` for you to remove and restart the unit.

  It needs a moment with no Verity Build running.
