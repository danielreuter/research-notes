---
id: 20261001T1158Z-handoff-from-circuits-bool-norms-pr2-head
campaign: verity
lane: circuits
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits-bool-norms (bc-14d6ca5c) @a009c1cbc
---

# circuits-bool-norms (4:58 AM PDT): the PR 2 norms head is `cursor/bool-norms-8c79` @ `a009c1cbc`, handed to circuits-bool-switch

The details are in note:20261001T1158Z-handoff-from-circuits-bool-norms-gemma2-head (`lanes/circuits-bool-switch/`).

## Your four items

1. **Done.** `boolean_dense_norm` keeps only `MeanTriton_v2` and its stages, `NarrowF32ToBf16_v2` and its leaf, and `RsqrtF32_v2`. The
   chain now runs on `boolean_dense`'s eight. Its AND counts at H are unchanged except for `RsqrtApprox_v2`'s 1,134.
2. **Done.** I merged `origin/cursor/bool-switch-8c79` twice: once at your instruction, and again at `443538fed` after the switch moved
   (no force-push). `boolean_norms.py` keeps my fixes. `targets.py` and `pins.json` are the union.
3. **Done.** The switch binds `RsqrtF32_v2`'s RSQRT to proofs' `RsqrtApprox_v2` through `word_statics`, so the chain is Boolean
   throughout. B1's norms on proofs' MUFU are tested and pinned.
4. **Done, with two failures in circuit-check.**
   - The vLLM lints all pass (43).
   - circuit-check on my 12 targets: 10 ok and 2 `partition/gate-recomputed`, one gate each. Both are on the switch's Boolean-MUFU norm
     roots: `RMSNormFusedCuda_v3` with `RSQRT=RsqrtApprox_v2`, and `RMSNormTriton_v2` with proofs' three MUFU.
   - Both are recomputes across an opaque Boolean MUFU Call. Under your ruling (#667, Q_word v2) they are allowed, with no `known.py`
     entries.
   - **Your call:** `circuit-check --all` exits 1 on them until it applies Q_word v2. Should PR 2 cite #667 and accept that, or hold
     those two roots?

## The gemm question

**The `verity.ml.boolean.gemm` breakage does not appear on the merged tree.** The switch's `49e59afd1` resolves a bare op name only to
a word Definition, so `ops["AmpereBF16TcDot16"]` is `_v2` even with gemm imported.

## Evidence

- **Chain at H on `boolean_dense`'s rows:** passes with 43 rows for each RSQRT binding.
- **30k rows of the Boolean chain at H:** running now, groups 0–2 of the 80k test. I'll append the result here.
- **The other 50k rows:** a pod run.
