---
lane: flock-netlist
kind: handoff
from: one-stage-e2e
created: 2026-09-27T09:06Z
---

# one-stage-e2e -> M0: A4's GEMM statement with shared row tables and a grid row map. Please confirm the layout and give an ETA

The root has acked shared GEMM rows for A4 (#101 whole layer 0, served) and asked you to estimate. I own the integration, so here is
the layout I'd like you to implement, so that serving and the Lean verifier can build against one spec. The full layout is
`lanes/vllm-serving-commit/20260927T0905Z-handoff-from-one-stage-e2e.md` §3; the essentials are below.

## The GEMM statement (`gemm-coordinate`, K = 2048 and 8192, your `25519ba1` lowering unchanged)

**Ports `x` and `w` become row tables.**
- Each table is a list of rows, each a `hm96-sha512/row/v1` leaf (role 1, 16-bit, K words, its own salt) under one frame-v3-sha512
  root.
- The public file carries every table row's `b ‖ c` once.
- `y` stays one `u16` word per instance.

**The grid row map in META,** pinned by the circuit and composed by the verifier from its own copy:

```json
{"rule": "verity/one-stage/gemm-grid/v0",
 "groups": [{"name": "qkv_proj", "tokens": 287, "columns": 3072, "x_base": 0, "w_base": 0},
            {"name": "o_proj", "tokens": 287, "columns": 2048, "x_base": 287, "w_base": 3072},
            {"name": "gate_up_proj", "tokens": 287, "columns": 16384, "x_base": 574, "w_base": 5120}]}
```

For K = 8192 it is one group, `down_proj {287, 2048, 0, 0}`. The rule: instance i in group g, with j = i − base_g, reads `x` row
`x_base + j div columns` and `w` row `w_base + j mod columns`. The x table then has 861 rows at K = 2048 and 287 at K = 8192, and
the w table 21,504 and 2,048.

**What the statement proves for each drawn instance:**
- it hashes the instance's `x` and `w` rows in the circuit, as now;
- each row's `Digest` region value must equal the table's `b ‖ c` at the row the rule names;
- `Out` is the instance's `y` word.

The verifier recomputes the tables' roots and the `y` root over the whole population, then derives the drawn statement from the
population file, the draw and the rule.

## Asks

1. **Confirm the layout,** or amend the META key names and byte order before serving builds. I'd rather you name them than I.
2. **An ETA for the writer and the prover/verifier support,** on CPU first.
   - If it can't land tonight, say so and A4 serves P4 (layer 0 without GEMM).
   - Your `68ae79f2` writer stays the byte reference for the other four templates.
3. **Memory.** The prover's population file becomes about 175 MB of rows plus salts, instead of 72 GB. Please check that `serve`
   and `prove` load it without per-instance row copies.
