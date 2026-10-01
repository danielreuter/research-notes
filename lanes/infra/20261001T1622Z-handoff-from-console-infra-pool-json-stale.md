---
id: 20261001T1622Z-handoff-from-console-infra-pool-json-stale
campaign: overnight
lane: infra
kind: handoff
status: open
repo: verity
origin: console cloud successor (bc-ccd62491)
---

# `/workspace/usage/infra-pool.json` on node 1 stopped updating at 9:00 AM PDT

From console's cloud successor, 9:22 AM PDT. Node 1's publisher has reported `pool: /workspace/usage/infra-pool.json is N s old` since its 9:16 AM PDT run. At 9:21 AM PDT the file was last written at 16:00:01Z, 21 minutes earlier, so the `infra/pool-*` panels are stale. It's the second gap tonight: the file was 1,152 s old at 3:19 AM PDT, then recovered at 3:20.

Also noted: node 1's publisher now runs main d784c58ee plus your `cursor/held-idle-panel-558b`, installed at 9:18 AM PDT (39 panels). When console's verity #684 lands, the publisher on node 1 needs both, so console will install main only once your branch is in it too, or merge the two.
