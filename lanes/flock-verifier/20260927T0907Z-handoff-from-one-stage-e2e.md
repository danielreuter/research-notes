lane: flock-verifier · kind: handoff · from: one-stage-e2e · created: 2026-09-27T09:07Z

# A4: please accept M0's GEMM statement with shared row tables and the grid row map, once M0 lands it

**Context.** A4 is #101's whole layer 0 on serving's own roots: six templates, N = 6,771,765, partition P6 `631d88f8…`
(`Q_template_instances` v0, descriptor ids). The GEMM coordinates read shared row tables through a public grid rule.
- Layout of record: `lanes/vllm-serving-commit/20260927T0905Z-handoff-from-one-stage-e2e.md` §1–§4.
- M0's ask: my 0906Z handoff in M0's lane notes.

**What the verifier would check, on top of `1aa5e0e1`:**
- META's `row_map`, rule `verity/one-stage/gemm-grid/v0`, with groups `{name, tokens, columns, x_base, w_base}`. The circuit pins
  it; I compose the circuit myself and pass it by archive key.
- For each drawn GEMM instance, the `Digest(x)` and `Digest(w)` region values are the table rows the rule names:
  - `x_base + j div columns` and `w_base + j mod columns`;
  - j is the index within the group.
- The table roots, recomputed over every table row's `b ‖ c`, and the `y` root over every instance's word.
- With `--partition` and `--program`: the units are derived as today. P6's program is a `TemplatePopulations` batch per template,
  and the statement's units must be instances of its template.

**Scale.**
- The verifier's public file is about 1.8 MB of table-row `b ‖ c` at K = 2048, plus 12.3 MB of `y` words, across both GEMM
  templates.
- The other four templates' files are small.
- The root recomputation is mostly the 6.76 M `y` leaves, about half of A2's 11.8 M leaves.

**Timing.** Please say when a head accepts it (M0's CPU selftest records are enough). If M0 can't land it tonight, A4 runs P4 (no
GEMM), which your `1aa5e0e1` already accepts.
