---
id: 20260930T0928Z-note-from-pous-449-exp-test-order-owner
campaign: overnight-sep30
lane: vllm-coordinator
kind: note
status: open
repo: danielreuter/verity
origin: pous
---

# #449's `F32ExpRn` test-order failure: the Pearl-C kernel lane owns the fix

Re the node-2 ops repro (the `exp` test fails only after `test_native_jit_load.py` has run in the same pytest worker process).
The fix goes on [#449](https://github.com/danielreuter/verity/pull/449)'s branch, and bc-9914c188 (the Pearl-C kernel lane)
is making it. It will restore the leaked state or run the native JIT load in a subprocess, and pin the fix with a test that
runs both files in one process. Please don't push a parallel fix to that branch. If a stacked branch of yours needs it
sooner, say so here and we'll order the push.
