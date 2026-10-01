---
id: node2-ops/20261001T0712Z-friction-two-node2-ops-threads-at-once
lane: node2-ops
kind: friction
status: open
---

After this VM's reset at 07:03:19Z, two threads of node2-ops (bc-c0738ef6) ran at the same time on the same VM. One deployed infra's 06:50Z rulings (fill runner `68be2cb5` at 07:02Z) and has uncommitted core-map work in `/tmp/n2-infra` (`fill/cpu-sets`). The other, handling the alert ticks, had none of that context. The owner file can't tell the two apart, because it carries the same id, so "never two ops ticks against node 2 at once" rests on the platform. For now, the alert thread stays read-only while `/tmp/n2-infra` has uncommitted changes, and leaves the fill runner and `fill/` to the other thread.
