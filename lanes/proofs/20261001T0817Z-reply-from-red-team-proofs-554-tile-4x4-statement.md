---
id: 20261001T0817Z-reply-from-red-team-proofs-554-tile-4x4-statement
campaign: overnight
lane: proofs
kind: reply
status: open
repo: verity
origin: red-team-proofs-554 (started by proofs bc-8416bc72)
---

from: red-team-proofs-554 (bc-d8964c29), read-only second reviewer · to: proofs (bc-8416bc72) · re:
`note:20261001T0608Z-handoff-from-proofs-review-554-statements`, question 2; question 1 is
`note:20261001T0805Z-reply-from-red-team-proofs-554-nontile-statements`

# #554 question 2, the 4×4 tile: OBJECT. It isn't the untiled claim, though its timing stands as a cost

**Scope.**
- The statement: BF16 `GemmCoordinate_v2{K=2048,DOT=HopperBF16WgmmaDot16_v1}` from `Gemm_v2{K=2048,N=2048}`, staged with
  `FLOCK_GEMM_TILE=4x4`. That means records with `stage.tile == [4, 4]`: the gate point (n = 16) and the m35 point (n = 512).
- The code: 8a0b17250's `stage_tiled`, `tile_lowering` and `_tile_fits`. The tile run, r20261001-005713-0652, ran at
  e95c0a49c5, whose staging differs only by one record field (`domain`).
- The same reading holds for any `GemmCoordinate` class the tile catches. E4M3 K=2048, which has two equal ports, is one.

**OBJECT** to "the tiled statement is the same claim as the untiled one". This isn't an objection to the tile point's timing
as a cost.

Conditions to lift it, one per line:
1. **Bind real pairs.** The C row ports carry activation (port-0) rows of C distinct Calls, and the P ports carry weight
   (port-1) rows. Each unit `(a, b)` is then a pair the untiled stage would stage. For `Gemm_v2` that needs the P weight
   rows shared across the C Calls (or C = 1).
2. **Use the reference outputs.** Those pairs' outputs come from `verity.evaluation` (`want`) and are asserted equal to the
   circuit's, as `stage` does.
3. **Pin it.** Add a test that stages a small tile, pins its `class_sha512` and `circuit_sha512`, and asserts the wiring and
   that the weight ports hold port-1 rows.
4. **Name the grouping.** A real 4×4 tile groups coordinates across Calls, and `q-word`, which META binds, doesn't. That needs
   a query that names the grouping, which is Daniel's call, or the tile stays a cost.

For the flag, until then: keep `tile-statement-unreviewed` on tile points, and don't count their 16 coordinates per
instance as proved program coordinates. Plotting the timing is fine.

## Evidence

**What the tile stages.** I ran the probe: `class_statement.main` at 8a0b17250, with `prove` stubbed so it stages and proves
nothing, `FLOCK_GEMM_TILE=4x4` and `--n 16`. The scripts, definitions and outputs are in
`art:d593b85e9a14c2971408694d110a5d03c5e6ba6ad152418340b0934b40adb660`.

| Program | Port-0 lane rows (distinct) | Distinct rows per tile | Distinct rows over all 16 tiles | Tile rows that are weight rows |
|---|---|---|---|---|
| `Gemm_v2{K=64,N=16}` | 128 (8) | 1 | 8 | 0 |
| `Gemm_v2{K=64,N=2048}`, the hill point's N | 128 (1) | 1 | 1 | 0 |

- **At the hill point.** At K=2048 and N=2048, the gate's 128 lanes all come from one evaluation. Every unit of every tile
  proves x·x for a single activation row x. At m35 (4096 lanes) there are two such rows.
- **Why both sides are x.** `stage_tiled` takes both tile sides, `R0` and `R1`, from `per1["p0"]`. The lanes are distinct,
  but the rows are not: every coordinate of one `Gemm_v2` evaluation reads the same x. The untiled stage shows the same
  thing, with `shared_rows` of `{p0: 1, p1: 2048}` at n = 2048.
- **Outputs aren't cross-checked.** The tile's outputs are `low1.evaluate(pairs)`, the circuit's own, and the tile path never
  reads `want`. So no staged tile instance cross-checks the circuit against `GemmCoordinate_v2`, whereas `stage` raises on a
  mismatch.
- **Rows are deduplicated across tiles.** `FC.write(share_rows=True)` without tables runs `share()`, which dedupes each
  port's rows by value across all instances. At the gate point, every one of the 8 ports commits a single table row. This
  corrects `note:20261001T0806Z-reply-from-red-team-flock-3-554-verdict`, which says there are "no row tables across tiles".
- **META's binding doesn't fit the instances.** META binds the `Gemm_v2` program digest and the `q-word` partition, but the
  instances aren't `q-word` units of that program: no weight row is bound.

**Why the timing is still a fair cost.**
- Each VU hashes its 8 rows in-circuit; the `circuit.rs` header says an instance's digests are its rows' `b || c`.
- The witness is a bit-sliced evaluation over every slot (`unit_ab_into`, `GroupProf::eval`).
- So the prover's work doesn't depend on the row values, and the timing is a fair cost of 16 `GemmCoordinate_v2` units over
  8 hashed rows.
- What the degenerate rows do shrink is host work linear in distinct rows: frame-v3 table trees, salts and the size of the
  instance file. I didn't measure it; I expect it to be small next to a k_log 26 prove.

**Pinned or named.**
- **Existing and checked:**
  - The several-units-per-VU format (`units_per_vu`) is parsed by `circuit.rs` and by the Lean verifier
    (`Flock/HmRow.lean`), and #554 doesn't change it.
  - `Stmt::new` and `identity()` are unchanged.
  - The unit circuit and layout are the class's own (`low1.circuit`, `low1.layout`). Their K=64 instances are circuit-check
    targets, as for the untiled class.
- **New and unpinned:**
  - `tile_lowering`'s leaf maps. Each run's `circuit_sha512` covers them, but no test or vector holds a digest.
  - `stage_tiled`, and `_tile_fits`'s bound of 2^25.
  - The shim's name, `unit-class/<shape>-t4x4`, and its content digest, sha256(form + `/tile4x4`).
  - There's no test, no circuit-check target and no PROTOCOL.md text for any of these. M0's
    `internal/gemm-column-batch-tiles-layout-scope.md` isn't on this VM, so I couldn't check it.
- **The tile run's digests (node 1):**
  - circuit `e50163d6528f72fe`;
  - class `efd8962130f9b9a1`, against the untiled class's `7e998f751bd7ab7d`;
  - statements `8ce84a143442e680` (the gate, m = 30) and `efcb2f949826af5a` (m35, n = 512).

**Against red-team-flock-3's verdict.**
- Where we agree: the tile is a cost and not a claim, it's unpinned, and it isn't cross-checked against the reference.
  Their conditions 1 and 2 are inside my conditions 2 and 3.
- Where we differ: on the verdict word, and on two facts. The rows are one x, and they are deduplicated across tiles.

**Needs Daniel.** Can a tile that groups coordinates across Calls be a unit of a GEMM statement at all? That's a partition
change. Until he rules, the tile is a cost.

**Optional, not submitted.** To see this at the real point, run the probe from the art on a CPU pod, from the 8a0b17250
tree, with `Gemm_v2{K=2048,N=2048,DOT=HopperBF16WgmmaDot16_v1}`, `FLOCK_GEMM_TILE=4x4` and `--n 16`. It needs about 7 GB
and no GPU. I expect `distinct_rows_all_tiles: 1` and `tile_rows_that_are_weight_rows: 0`.

**Labels:** none, since this is an OBJECT.
