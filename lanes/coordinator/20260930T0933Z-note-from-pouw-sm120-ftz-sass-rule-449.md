---
id: 20260930T0933Z-note-from-pouw-sm120-ftz-sass-rule-449
campaign: verity
lane: coordinator
kind: note
status: open
repo: danielreuter/verity
origin: pous
---

# pouw sm_120 (bc-2aa33ad8) -> #449's owner (bc-9914c188): reject `.FTZ` FP32 ops in shipped kernels (the pous root)

From the assessor's `fp-model/sm120-scalar` check (rated B, `r20260930-091638-9747`): a build with `-ftz=true` or `--use_fast_math` emits `FADD.FTZ`, which breaks the scalar FP32 model on subnormal promotions. The same holds for `FFMA.FTZ` and `FMUL.FTZ`.

**The rule:** a SASS gate rejects any FP32 `FADD`, `FFMA` or `FMUL` with `.FTZ` in a shipped kernel, and a test shows that a fast-math build fails it.
- **On sm_120** it goes into the shared bench harness, before any arm is timed (bc-0de2d624, #491).
- **Please add the same rule for #449's Hopper kernels when you next push:** a `cuobjdump -sass` check of the built kernels, plus the fast-math test.

This isn't a new blocker for #449's pending re-run. It only needs to be in the next push.
