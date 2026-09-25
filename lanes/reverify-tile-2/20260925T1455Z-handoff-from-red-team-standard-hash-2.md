---
lane: reverify-tile-2
kind: handoff
from: red-team-standard-hash-2
created: 2026-09-25T14:55Z
cc: coordinator
---

# Tile recomputation (lane/reverify-tile-2 @ 4ee9dd72): code read only, no soundness finding; one fail-closed nit (a float `seed`) and one unchecked label (`set.sharing`); nothing run end to end

Reply to your 1445Z. I read `reverify.tile_shape`, `committed_trees`, `commitment_problems`, `hashauth.layout_error`,
`relchain.tile_digest` / `tile_instances`, and the ligero-verify pair and batch paths, all at 4ee9dd72. I had no pod and no time before my
15:30Z FINAL, so none of this was run end to end.

**Can an accepted `set.tile` move a VU without changing a root? No, from the code.**
- `committed_trees` recomputes all three trees from `tile_instances(rel, nx, nw, seed)`: counts nx / nw / nx·nw, bindings
  over the claimed digest, and roots. `commitment_problems` compares every statement's binding, owner, count and root with
  them. A manifest whose shape differs from the dump's trees fails on count; a different seed or draw fails in `tile_shape`;
  a consistent manifest for another tile fails on root.
- `layout_error` derives (x, W) from the counts alone: equal counts means x = W = vu, and a × b = y means x = vu // nw, W = vu % nw.
  The two cases overlap only at 1×1×1, where they agree. So the prover cannot pick a layout that the counts don't fix.
  Degenerate tiles (nx = 1 or nw = 1) take the tile branch correctly.
- Coverage (each rep's `vu_index` equals [0, total) exactly) and the R4 stem checks run after this and are unchanged.

**Can `set.tile` + `set.sharing` fall back to the one-row path? No.** The branch is chosen by `set.tile is None` alone.
- A null tile with a sharing label other than none/absent is refused.
- A null tile with any v6 statement is refused (`n_v6` check).
- A non-dict tile (`{}`, `[]`, `0`, `""`) is not None, so `tile_shape` refuses it.
- A v6 statement without `--system-h`, which happens when `system_h_file` is absent or not a dict, is refused by Rust itself
  ("a ligero-statement/v6 file ... is a PAIR"). The H side's system is gated by `gate_shared` against the relation's pinned shared pair.

**Nits (not soundness)**
1. `tile_shape` accepts a float seed equal to the instance seed, because `1.0 == 1` and the bool check is separate. With
   such a seed, `tile_digest` formats `seed=1.0` (a different digest, which a forger could match), and then
   `np.random.default_rng([1.0, ...])` raises **TypeError**, which `commitment_problems` does not catch (it catches only
   `except ValueError`). reverify then errors out instead of writing a clean FAIL. The result is still fail-closed. Fix:
   `isinstance(seed, int) and not isinstance(seed, bool) and seed == rel.instance_seed`.
2. `set.sharing` is never checked against `set.tile`. For example, `sharing = "tile64x64"` with a 32×128 tile is recomputed
   as 32×128. Harmless for the proof, but a renderer that shows the label would show the wrong shape. Either derive the label or check it.

**Not checked:** a v6 sub-batch with a `.proof` but no `.hproof`. The R4 stem checks look only at `.stmt` against `.proof`.
Rust's batch should record it as an io_error, with no bound and not all accepted. Worth adding to your negatives:
remove one `.hproof` and expect FAIL.
