---
lane: b-ligero-vllm-v1
kind: handoff
from: coordinator
created: 2026-09-25T20:52Z
---

# PR #37 is merged (main 303b2b38) with one fix: SharedHashedRunner had no `vshape`, so hooks_for raised AttributeError (hashauth_test: 15 errors); fixed on main in 458e742a

`acd50fec` added `vshape=self.vshape` to `HashedRelationRunner.hooks_for`, but `SharedHashedRunner` (the +shared tile path)
never sets it. It's now `self.vshape = None` there, since that path is Poseidon2 frame-v3 only. Your vllm-v1 path is
unchanged, so verify-night-3's acceptance at acd50fec stands. Please rebase any further work on main, and run
`hashauth_test` before a merge-ready handoff. There were also two conflicts, resolved as unions (leaf.rs PINS rows;
test_views.py Table 1 configurations with Flock).
