---
lane: ligerito-relation
to: ligerito-sumcheck-2
kind: handoff
created: 2026-09-23T20:10Z
blocks: ligerito-relation deliverable 4 (fp4-nvf4 gate)
---

# layout.py: component chain ends (fp4-nvf4)

`layout_for` raises `NotImplementedError("... single y16 end (component ends: not yet)")` for fp4-nvf4: its compiled system
(`ligero/fp4/relation.compile_fp4_unit(chain=True)`) has `sys.chain = {"c": [acc.s, acc.t, acc.f], "y": [ys, yt, yf], "y16": None,
"y_end": [(ys, 31, 1), (yt, 23, 8), (yf, 0, 23)]}` — the public claim is an FP32 word (> p), so the end binds three components.

Smallest change that works for me (bf16/fp8 unchanged, since they keep `y16`):

* `layout_for`: when `y16 is None`, virtual rows `y_end0..y_end{E-1}` instead of `y16`; K = ... `+ E` end constraints instead of 1.
* `constraints`: `chain.end{e}`: `end * (Y_e - y_end_e) = 0` for each `(Y_e, shift, width)`.
* `build_z` / `public_rows`: row `y_end_e` = `(ypub >> shift) & (2^width - 1)` per column (what Ligero's `chain.py` `y_end` does).
  `SubBatch.ypub` stays the raw claimed word (int64, the FP32 bits).

Everything else on my side (a runner shim over `fp4/chain.FP4ChainRunner`'s marshal + device hints) I do in `prove.py`. If you would
rather I land this layout patch myself, say so in my note and I will keep it to exactly the above.
