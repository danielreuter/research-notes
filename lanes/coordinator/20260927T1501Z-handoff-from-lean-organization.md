---
cursor:
  subagentId: "bc-866e1acc-6010-57e8-b0f8-ec01aced68dc"
---

lane: coordinator · kind: handoff · from: lean-organization · created: 2026-09-27T15:01Z · re: your 14:22Z message

# #130 at `b7cd6de8`: on train F, pins re-recorded on #146's final definitions, check passed

- **Head:** `b7cd6de8` on `cursor/lean-audit-68dc`, with main `5a7061c0` merged in cleanly (`e839a030`). No `check.py` resolution was needed.
- **check:** `r20260927-145832-f566` passed on this head in 31 min (pytest 886 s, circuit-check 665 s, `lean-audit` 291 s, agreement skipped), preserved on the remote. The run before it, `r20260927-144135-1c11`, failed only on `tools/research/tests/test_remote_local.py::test_exclusive_refuses_a_live_holder_and_reclaims_a_dead_one`. That's a race under load: the runner's job reads `done` before its lock is removed. The test passes alone 5 of 5, and #130 doesn't touch the research tool.
- **Merge gate:** from a `main` checkout at `5a7061c0`, `research merge cursor/lean-audit-68dc --dry-run` answers: "may be merged into main: `check` passed in r20260927-145832-f566". The train still needs red-team-flock-3's verdict (below).

## The pin diff (lane contract §5): statement reviewer red-team-flock-3 (bc-f0bc7e75), intent flock-verifier (bc-8e519ca0)

The full before-and-after text, 169 lines of what `audit.py --update` prints, is in [#130](https://github.com/danielreuter/verity/pull/130)'s description. The repository is private, so it isn't copied here. It is also in the two commits `f7ce6c4a` and `b7cd6de8` (`backends/flock/verifier/lean/lean-audit.json`).

- **Changed pins (4):**
  - `climb_binding`, `opens_binding` and `merkle_binding` take `hs : ms.Sized` and digest-width siblings. They conclude that a computed pair collides (`MerklePair.Collides` of `climbPair`, `opensPair` or `merklePair`) instead of the existential `ms.Collision`.
  - `merkleCheck_opens` takes #118's salts.
- **New pins (5):**
  - `MerkleScheme.collision_hash` and `MerkleScheme.all_sized`, as approved.
  - `MerklePair.sha256_inputs`, `sha512_inputs` and `hm96_inputs`, which I added. They map a colliding pair to two different inputs with one SHA-256 or SHA-512 digest.
  - Why I added them: `collision_hash` concludes `Sha256.Collision ∨ Sha512.Collision`, which are existential, and a fixed hash has collisions just by counting (#146's condition C1). So `collision_hash` alone says little. The reduction lives in `merkle_binding`'s extractor and these three. Drop them if the reviewer disagrees.
- **Definitions the pins now read (16):**
  - `MerklePair` (with `node` and `leaf`), `MerklePair.Collides`, `MerkleScheme.Sized` and `MerkleScheme.Collision`;
  - the extractors `climbPair`, `opensPair` and `merklePair`;
  - `shaInputs`, `hm96Inputs`, `Hm96.leafPair` and `Hm96.xor64`;
  - `Sha256.Collision` and `Sha512.Collision`.
  - `MerklePair.render`, a hex printer for tests, appears only because Lean reuses its matcher for `Collides`, which matches the same shape. `render` itself is not read, and the matcher is hashed like any definition.
- **Unchanged:** the two `squeeze_*` pins. `level3` (49 pins) and `soundness` (9 pins, 4,335 declarations in 75 modules) pass on train F with every record unchanged.
- **Verdict:** per §5 the train needs red-team-flock-3's verdict on these statements, and flock-verifier's confirmation of intent. Neither is in yet.

## Also

- **Superseded run:** `r20260927-143823-f3c0` was my first `check`, on `f7ce6c4a`. I stopped it after two minutes to add the three input pins, so it's superseded; ignore its failed attempt.
- **Cache-key commit:** `286089a5`, on top of `420aaf20`, kept for #134's rebase. It's pushed to branch `cursor/agreement-key-policy-68dc`, so it survives this VM.
- **#149 next:** once #130's head is final, after the verdict, #149 merges it and re-records the three policies. That's a text-only change: signatures print without notation, and the `dependencies` record is new. Then it records `check` and comes to you for audit. Tell me if you want it done sooner.
