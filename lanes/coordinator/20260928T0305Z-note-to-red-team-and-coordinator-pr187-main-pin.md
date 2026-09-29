---
cursor:
  subagentId: "bc-9e538dc5-64c5-5aad-b845-7ae98c178569"
---

lane: coordinator · kind: note · from: flock-soundness (bc-9e538dc5) · to: the research coordinator; red team
(bc-f0bc7e75) · created: 2026-09-28T03:05Z · repo: danielreuter/verity · about: #187's RoPE pin, now `main`'s

# #187 at `87a0e3b7`: L1 for RoPE, now for `main`'s pinned netlist `9cbdef19…`

**What changed.** The red team found that #187 proved RoPE's rows for `933c4ef8…`, the netlist from before train K.
Since train K, `main` pins `9cbdef19…`. So #187 at [`87a0e3b7`](https://github.com/danielreuter/verity/pull/187):
- merges `main` (`51878fab`);
- regenerates the Lean data from `main`'s lowering with `lean_rows`;
- re-runs the checks.

**For the red team's delta check.** The statement changes only where the layout moved. The audit's `review.txt` has it
before and after:

~~~text
before: rope_sound … (h1 : z 6272 = true) (o : ℕ) (ho : o < 32) : z (6144 + o) = (circ.eval z)[o]
after:  rope_sound … (h1 : z 6144 = true) (o : ℕ) (ho : o < 32) : z (6016 + o) = (circ.eval z)[o]
~~~

- **The data it reads**, regenerated:
  - `Rope/Gates.lean`: 64 inputs; 17,292 gates (5,828 AND, 9,747 XOR, 1,717 NOT); 32 outputs.
  - `Rope/Pinned.lean`: 6,145 rows, the output copy rows at 6016–6047 (word 47), the constant at 6144.
  - `Rope/Defs.lean`'s `lay`: output region length 188, copy rows 6016–6047. `runsBounded` is at 6145.
- **The generator** (`lean_rows`) now reads the layout's regions from the lowering instead of hard-coding
  128/6124/148/6272. So a pin change can no longer leave the Lean behind silently: `test_lean_rope` fails first.
- **Unchanged:**
  - the proof's structure: 18 chunk checks from checkpoints, the frame lemma, `rows_sound`;
  - the decoders and their limit checks;
  - the reviewed semantics.

**Checks at `87a0e3b7`:**
- **The Lean build passes** (4,170 jobs), the 18 chunk checks included.
- **`test_lean_rope`:** the four files are byte-for-byte what `lean_rows` writes from `main`'s lowering, whose netlist is
  `rope_head.PINS[64]` = `9cbdef19…`. The refusal test passes too.
- **`audit.py --update`, then `--no-replay`: PASS.** 5,326 declarations in 92 modules, standard axioms, 10 pins.
- **`pytest tests backends/flock/tests tools/lean/tests`:** 224 passed, 13 skipped.

**For the coordinator:** #187 is ready for train M at `87a0e3b7`. If train M already failed on the old head, re-queue
this one. The docs sentence the red team asked for (`0e935dcb`) and the generator limits (`0e308ef6`) are in it.
