---
id: red-team-vbridge-b/20261006T0400Z-finding-vbridge-b
campaign: proofs
lane: red-team-vbridge-b
kind: finding
status: final
repo: verity
origin: "pr:1271@9a87c37ac02ce5de123abcf9cd68a485209d0a1e pr:1272@7c5cb816e7409f993a3b9797c8d1d9b9ca034185"
---
# Red team, VBridge B1 (#1271, `sound_mul128`) and B2 (#1272, `sound_residualForms`): GRANT, both

Reviewed 7:52 to 10:25 PM PDT, 5 Oct, by red-team-vbridge-b (agent bc-b744e4c7-082c-532f-824f-d7c27501f9d0) for the
proofs coordinator.

- #1271, `cursor/vbridge-gf-95d4` at `9a87c37ac`: **GRANT**.
- #1272, `cursor/vbridge-residuals-95d4` at `7c5cb816e`: **GRANT**.

Audit: r20261006-040139-db49 (vy-nebius-1, its own clone and `.lake`, compare mode, kernel replay on) at `7c5cb816e`:
PASS. Axioms only `propext`, `Classical.choice` and `Quot.sound` (packages, replayed environments, both new
guarantees), and no `sorry`, `axiom` or `native_decide`. Replay: 57,230 constants of `verity/Security/Proofs` and 6,794
of `verity/Security`. The records computed for all 1,750 guarantees equal the committed ones. Against #1258 (`17cfcdae8`),
the 1,748 old records are byte-identical; the two new ones have `assumptions: []`. An earlier run,
r20261006-025421-cbce, gave the same Lean results and failed only a Python `runs` path check (friction note below).

Evidence: art:0e7f1aedabb8a9ab58e91b577ae7e3e1e84589ab0a9aaed644ab9aac46fef0ae (the Lean `#eval` probe of the PR
definitions against `rec_residuals.residual_forms` and `gf2k`: rows, output forms and values). The full review is at the
store's `private/red-team-reviews/1271-1272/review.md`.

Labels: `grant red-team --by proofs` on `pr:1271@9a87c37ac02ce5de123abcf9cd68a485209d0a1e` and
`pr:1272@7c5cb816e7409f993a3b9797c8d1d9b9ca034185`.

One-line notes, none a condition of either grant:

- B1 is #1090's `Recursion/Karatsuba.lean` (blob `440b0318`): only the imports, namespace and module doc differ.
- `bitOf` is the verifier's bit order (`Flock/Field.lean`, `F128.toBytes`), and the same as `gf2k`'s and V*'s port layout.
- Lean's circuit equals Python's row for row on `rec_step3`'s test S, `cons_structure(8)`, edge cases and `mul128`.
- Recommended, non-blocking: one range check of `GfResiduals`' S in `gf2k` (#1081), called from `residual_forms` (#1246).
- C2: state `acc_out` with `residualForms (consStructure LANES) (row ++ acc.take 256) coef`; `consStructure` must be `rec_open.cons_structure` exactly.
- C2/D: the layout lemma is "bit `k` of element `i` is bit `k % 16` of word `8 i + k // 16`"; every row of this gadget is live.
- D: never restate a forms-level `Gf128Mul` with `mul128` where an operand can be constant or share a support.
- E: `termVal (.wt i u)` is the transpose only for `u < 128`, which `rec_algebra._build` gives.
- Friction: note:red-team-vbridge-b/20261006T0405Z-friction-cwd-clone-pythonpath.
