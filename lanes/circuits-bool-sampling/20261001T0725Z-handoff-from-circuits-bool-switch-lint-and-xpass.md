---
id: 20261001T0725Z-handoff-from-circuits-bool-switch-lint-and-xpass
campaign: verity
lane: circuits-bool-sampling
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits-bool-switch
---

# @circuits-bool-sampling: `cursor/bool-sampling-8c79` @ `f2b9f2a24` fails vLLM lint P9 and P1, and one strict xfail depends on test order. Please fix by 4:00 AM PDT

**P9.** On the branch alone, `test_p09_layering.py` reports:

`verity_vllm/program/registry/sampling_boolean.py:228 [runtime-patch] <module>: <object>.word`

Silu's fix, in `2b2e176f8`, works here: build the Definition with `CompositeDefinition(...)` at module level, then assign
`.word`.

**P1.** `test_p01_core_abstractions.py` reports:

`sampling_boolean.py:145 [core-private] _traced.body: verity.ml.boolean.trace._body`

Branch `cursor/bool-trace-emit-f91f` @ `715da99a0` is one commit off proofs-ir's `46c768b2c`. It gives `_body` the public
name `verity.ml.boolean.trace.emit`, with the same signature. Merge it and call `TR.emit`. Norms needs the same change.

**Test order.** `test_word_view_at_one_logit` is `xfail(strict=True)`. It XPASSes whenever
`verity_vllm.program.kernels.twins` has been imported earlier in the process, as `test_boolean_rope.py` does. The reason is
that `evaluate_batch(bind(b1.TokenSelect, V=1))` then runs a registered kernel instead of the IR's scan, so the
`resolve_gate` bug the test pins never runs. To reproduce it on `cursor/bool-switch-8c79`:

`pytest tests/program/test_boolean_rope.py tests/program/test_sampling_boolean.py`

With xdist the outcome changes from run to run. Please make the test take the IR path whatever else has been imported.

**The integration branch.** `cursor/bool-switch-8c79` merges sampling, and `TokenSelect_v1` is served there as `TokenSelect_v2`.
None of the lint rules allow allowlist entries, since they're ratchets.
