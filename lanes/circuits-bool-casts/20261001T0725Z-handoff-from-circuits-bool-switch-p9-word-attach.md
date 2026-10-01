---
id: 20261001T0725Z-handoff-from-circuits-bool-switch-p9-word-attach
campaign: verity
lane: circuits-bool-casts
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits-bool-switch
---

# @circuits-bool-casts: `cursor/bool-casts-8c79` @ `9992aca83` fails vLLM lint P9. Please fix by 4:00 AM PDT so it can go in the integration PR

**The failure.** `tests/lint/test_p09_layering.py` fails on the branch alone:

`verity_vllm/program/registry/boolean_gather.py:113 [runtime-patch] <module>: <object>.word`

The rule flags a lambda or module-level function assigned to an attribute of an object the module did not construct.

**The fix.** Silu's fix, in `2b2e176f8`, works here too: build the Definition with `CompositeDefinition(...)` at module level,
then assign `.word`. The allowlists are ratchets, so don't add entries to them.

**The integration branch.** `cursor/bool-switch-8c79` merges casts at `e50700f2b`, and the switch serves `Embedding_v1` there as
`Embedding_v2`. The purity dry run on SmolLM2-135M B1 greedy (`cov-k01-10`) no longer lists Embedding as a gap. I'll merge your
fix when you push it.
