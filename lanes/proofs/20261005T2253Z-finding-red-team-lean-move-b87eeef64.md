---
id: proofs/20261005T2253Z-finding-red-team-lean-move-b87eeef64
campaign: layout-move
lane: proofs
kind: finding
status: final
repo: danielreuter/verity
origin: red-team-lean-move
---

# Red team, round 3: the Lean layout move at `b87eeef64` (PR #1225, `cursor/lean-layout-move-2-c3b2`): GRANT

Head `b87eeef64ce6c6dc9e6758e1839e42590c828c4a` (main `88f5cc533` merged in, with no Lean changes). Rounds 1 and 2 are in
`note:proofs/20261005T1610Z-finding-red-team-lean-move` (REFUSE at `b37b16723`, REFUSE at `77b8d66bc` for B3 and B4).
Label `grant=red-team` by `proofs` on `pr:1225@b87eeef64ce6c6dc9e6758e1839e42590c828c4a`, on the remote at 22:52:01Z.
Evidence: `art:44887ad703b8037594078a5b2fbe7dae53d07f27735e49ab39e4bf8184f05ae1` (probe outputs, records comparison, Lean
diff, the probe scripts).

## B3 (reads check failed open on `Flock.*`): fixed

`703997b5f` adds `reads_home(pkg, policy)`: `homes(pkg)`, then `homes(q, {})` of each `proved_in` prover, so the
prover's own modules are no spec and its path dependencies (the verifier's `Flock.*`) keep theirs. `audit()` passes
`spec_reads(current, facts, reads_home(pkg, current))`. `b3a7cdad7` restores the `Flock` entry of `reads_exempt`. The
probe calls `audit.reads_home` on head's Security policy: `Flock.Bytes` is in the home, and a guarantee reading it with
`reads_exempt = {}` is refused. `test_a_guarantee_reading_its_prover_s_path_dependency_outside_its_spec_fails` pins it.

## B4 (Security's lock did not match its build): fixed

- Both committed locks are byte-identical to the ones `audit.py --build --update` wrote in `r20261005-220205-9ef9`
  (vy-mig-check-16, at `9bdbea234`). Every `.lean`, Lake file and `tools/lean/` file is the same at `9bdbea234` and
  `b87eeef64`. The run exited 0, and both reports list no failures and no escapes.
- Replay: Security replayed 6794 constants over its 217 modules, and Proofs 56872 over 875 of its 880. The other 5 are
  the lock's `exempt` list (two `CheckAxioms`, `Targets`, `Bulk`, `DifftestMain`), which is unchanged since `77b8d66bc`.
  Both replays used only `propext`, `Classical.choice` and `Quot.sound`.
- Records against main `88f5cc533`'s eight locks: all 1754 guarantees keep their records (Security 1747, the verifier
  7). Of the reads, the 7 `Flock.*` modules hold hashes on which main's own locks disagree; head takes soundness's,
  which main's check verifies against the same unchanged source. Two definitions in `Proofs/Flock/Soundness/Defs.lean`
  (`FlockSoundness.Model.Arith.Correct`, `FlockSoundness.RepDoomedW`) have new hashes. Their text is unchanged except
  the ArkLib import that the cut replaced with `Mathlib.Algebra.Polynomial.Degree.Defs`. Both are `Prop`s over instance
  arguments, so a different instance path gives a defeq term with the same meaning. This is a statement-review item for
  @lean (`art:2e8915d1e6975a1f324145ec0e90c72e1fa0a5f94f64e5796f4ff57e88222a46` prints both), not a fail-open path.
- The 12 renamed anonymous instances now carry explicit names. I checked the 11 that changed beyond imports (in
  BandChain, Union, GF128Ring, Refine/Exec, Chain/Flat and Warden/Sanity): each is only `instance :` → `instance <name> :`.
- C1: the `compile_time` digest for `Refine.Walk` is recorded, and it matches the file.

## What changed since `77b8d66bc`: no new fail-open path

- `tools/lean/`: only `audit.py`'s `reads_home` (tightening) and its test. `Replay.lean` is byte-identical to the
  `815ac27cd` fix judged in round 2.
- Locks, section by section:
  - `reads_exempt` gains only `Flock`, the restoration.
  - `compile_time` has the Walk digest.
  - `dependencies` digests are re-recorded for the import set main's PoUS modules widened. Toolchain and manifests are
    unchanged, and the judge requires exact equality.
  - `guarantees` and `reads` changes are main's Pearl-C and PoUS entries.
  - No `exempt`, `layers`, `assumptions`, `escapes`, `upstream` or `meaning` entry loosened.
- `tools/check/`: only `pod_setup.sh`'s CPU-slots file, which schedules and judges nothing.
- `backends/flock/`:
  - `test_lean_verifier.py` serializes `lake build Proofs.Flock.Verifier` under a file lock, with `check=True` kept.
  - main's `ba394c6b9` makes `_source_digest` skip names with a dot. Python imports nothing from those, and no tracked
    `.py` under the hashed package roots has one.
  - main's PoUW-rows tests.
  - The verifier's sources, Lake files and lock are unchanged since `77b8d66bc`.

## lean-agreement

Not rerun. The executable's sources are byte-identical to main `88f5cc533`: `Flock/`, `Flock.lean`, `FlockRows.lean`,
and `Main.lean` → `FlockVerify.lean` (R100). The only changes are to the build files: `lakefile.toml` drops the moved
`FlockProofs` library and renames the exe root, with the same options, and the manifest change is whitespace.

The earlier reference `r20261005-081515-2188` does not carry. It ran at branch commit `e30302586`, whose `HmRow`, `Zk`,
`ProvedScope` and `Main` differ from main's.

The binding run is the landing check on `b87eeef64`. Every tracked file under `backends/flock/verifier/` goes into
`agreement_key`, and the move deletes `level3/` and `soundness/` there, so no earlier pass can be reused. `research
merge` requires `lean-agreement` to be `passed`, not skipped, on that commit for any change under `backends/flock/`
(`merge_requires`, `--no-renames`).

## Residual (known, not blocking)

`verity/Security/lean-audit.json` holds C-Flock's records and lies outside the red-team grant paths
(`backends/flock/`, `verity/Security/Proofs/Flock/`, `verity/Security/Proofs/Flock.lean`), so a later change to only
that lock does not ask for a red-team grant.
