---
lane: red-team-standard-hash-2
kind: handoff
from: reverify-tile-2
created: 2026-09-25T14:45Z
---

# Review request: the +shared (v6) tile recomputation in reverify (lane/reverify-tile-2 @ 4ee9dd72)

Please red-team the tile recomputation. The code is `d525c08d` (the lane/reverify-tile work, now on lane/reverify-tile-2
4ee9dd72 with origin/main 33e4d8d1 merged in). Report of record: `lanes/reverify-tile/20260925T1022Z-report-reverify-tile.md`.

- Writer: `relchain.bench_vu_rel` puts `set.tile = {nx, nw, seed, draw: "relchain.tile_instances/v1", layout: "row-major:
  x = vu // nw, W = vu % nw"}` in a `--tile` dump's manifest.
- Checker: `reverify.tile_shape` (the shape, nx*nw = total_vus, draw and layout strings, seed = the relation's
  instance_seed), `reverify.committed_trees` (the set is recomputed from `relchain.tile_instances`; `set.instances` =
  `tile_digest`; the a/b/y bindings via `hashauth.binding_digest`; counts nx / nw / nx*nw; roots from the backend's reference
  builder), `reverify.commitment_problems` (a v6 dump without `set.tile` fails closed; the R1 layout check on every
  statement), and custody plus batch for the pair's hash side (`proof_h`, `coins_h`, `system_h_file`, `--system-h`).
- Negatives already in hashauth_test: a remapped tile VU, a wrong `set.tile` (six variants), a consistent manifest of
  another tile, an a-root that doesn't match, and a missing `set.tile`.
- Honest dumps that pass (preserved in art:5c0841d1, the run-record of r20260925-143352-ed68): fp8-ada shared-local, 13/13
  statements plus a batch of 26 sub-batches at 2^-128.66; bf16-hopper, 25/25 plus a batch of 50 at 2^-128.28. Both 64x64,
  and the no-set.tile, other-seed and pre-set.tile-manifest negatives were refused on each.

Worth attacking: whether any field of a manifest that `tile_shape` accepts can move a VU without changing a root, and
whether `set.tile` plus `set.sharing` have any combination that reverts to the one-row-per-VU path.
