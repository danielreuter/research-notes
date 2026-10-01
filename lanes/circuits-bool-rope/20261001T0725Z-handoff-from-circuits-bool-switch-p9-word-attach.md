---
id: 20261001T0725Z-handoff-from-circuits-bool-switch-p9-word-attach
campaign: verity
lane: circuits-bool-rope
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits-bool-switch
---

# @circuits-bool-rope: `cursor/bool-rope-8c79` @ `50156733c` fails vLLM lint P9. Please fix by 4:00 AM PDT so it can go in the integration PR

**The failure.** `tests/lint/test_p09_layering.py` fails on the branch alone:

`verity_vllm/program/registry/boolean_rope.py:73,74 [runtime-patch] <module>: <object>.word`

The rule flags a lambda assigned to an attribute of an object the module did not construct. A `@composite`-decorated
function counts as one.

**The fix.** Silu's fix, in `2b2e176f8`, works here too: build the Definition with `CompositeDefinition(...)` at module level,
then assign `X.word = lambda b: ...`. The allowlists are ratchets, so don't add entries to them.

**The integration branch.** `cursor/bool-switch-8c79` already merges rope, and RoPE_v1 is served there (`RoPE_v2`). I'll merge
your fix when you push it.

**Test interaction you should know about.** `test_boolean_rope.py` imports `verity_vllm.program.kernels.twins`. In the same
process, that turns sampling's strict xfail `test_word_view_at_one_logit` into an XPASS. Sampling has a handoff about it, and
nothing is needed from you.
