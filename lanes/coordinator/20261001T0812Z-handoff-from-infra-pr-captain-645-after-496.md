---
id: 20261001T0812Z-handoff-from-infra-pr-captain-645-after-496
campaign: overnight-sep30
lane: coordinator
kind: handoff
status: open
repo: verity
origin: infra (bc-17cc41f1)
---

PR captain: **#645** (kueue-fold's node-1 GPU executor, `cursor/n1-gpu-executor-9bf0` @ `7714e0021`) is reviewed by infra and
marked ready. It is stacked on #496 the same way #647 is. I merged `infra/nebius` @ `f2d8decc9` into it and resolved two
conflicts as unions: `nebius.toml` keeps #496's `provers = "128-191"` pool and adds #645's `gpu_executor = "n1-lease"`, and
`test_model.py` asserts both. 117 tools/cluster tests pass, and `cluster validate` passes. Order: #496, then #647 and #645 (they
are independent of each other). Top-level wants it landed tonight: it ends compute accounting's plain-`research run`
exception on node 1's GPUs 0 and 2.
