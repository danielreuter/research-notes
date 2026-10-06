---
id: proofs/20261005T1614Z-finding-flock-security-defs
campaign: flock
lane: proofs
kind: finding
status: done
repo: danielreuter/verity
origin: bc-e3b551b5-6835-5a58-ba91-31ab8894f651 (flock-security-defs, for the proofs coordinator bc-8416bc72)
---

# C-Flock's trusted text on Mathlib: the Goldreich–Kahan closure, `Game` on `Verity.Game`, the closure test, and the spec extraction

**Question.** Can C-Flock's Goldreich–Kahan simulator, extractor and model build on Mathlib alone, and can C-Flock's `Game`
become core's `Verity.Game`, without weakening any guarantee? And can a test keep trusted text off ArkLib, VCVio and CompPoly
from here on? Step 2 (23:17Z follow-up): can every module a C-Flock guarantee reads, or that states a C-Flock assumption,
build on Mathlib alone, laid out like PoUW?

## Step 2: yes; the spec is extracted (`cursor/flock-specs-95d4`)

- **Answer.** `security` (Mathlib only) builds every module the 39 guarantees read and every named assumption.
  `test_trusted_text_builds_on_mathlib` passes with no pending set: `ARKLIB_PENDING` goes from 190 to 0, and is removed.
- **Layout.** `Definitions/Flock/` (21 modules read, plus `Game.{Expect,Interleave,Prob}`), `Specs/Flock/Assumptions/Soundness`
  (8 named assumptions; A4 `KeyedStreamsUniform` stays in Proofs, since it reads the verifier's SHA-256 and no guarantee
  takes it), `Specs/Flock/Guarantees/{Audit,Partitioning,Table}` (39 `def G : Prop`), and `Proofs/Flock/{Audit,Table,
  Partitioning}` (`theorem Flock.SecurityProofs.<topic>.G : Flock.Guarantees.<topic>.G`).
- **Exactly the reads closure** (top's constraint, 4 Oct 6:20 PM PDT). 282 definitions in 24 modules: 243 in 21
  `Definitions.Flock` modules and 39 statements in 3 `Specs.Flock.Guarantees` modules. flock-spec's model had about 1,800 in
  142. The guarantees are #1170's, 39 of its 41: `audit_profile` and `flock_verify_sound` come with #1179.
  `unread_spec` (r20261006-020536-d4e5) lists 22 C-Flock definitions: the 8 assumptions, `Game.expect` (which
  `SHA512CRExpected` reads), and 13 `deriving`-generated instances of `Stmt`, `Level` and `Schedule`. The other 18 went
  back to their proofs (f971cf900).
- **Import edges reversed.** At 6a98075fd, the 39 read 256 definitions in 23 modules, all under `Proofs.Flock.Soundness`. Now no
  trusted C-Flock module imports a Proofs module, and the lock's `layers` rules for `Definitions.Flock` and
  `Specs.Flock.*` enforce it. C-Flock's `reads_exempt` entries are gone.
- **Records** (review art:664f694137238d9231e4a88bc9e4d67f00c80603c2a2b1eb8ded943a613c1416). Of the 39 guarantees, 37 are the
  same statement under their old names: 24 certified lifts and 13 Partitioning renames. Two
  (`Table.SoundFast100`, `SoundFast100_34_35`) need the named statement reviewer: their `by omega` arguments make the hashes
  differ in a proof term only, and the kernel accepts the old lemmas as their proofs. One reads group (`Accounting.Schedule`)
  printed "changed" from a stale digest that the lock reduction kept; the members are the same
  (art:2bb76e46e7485da62eeed36ab401b9902bbfb459ee421c132a766b428ae890d9).
- **Runs** (vy-nebius-1, all `--no-replay`):
  - r20261006-002501-eba5: build FAIL, fixed by 189132951.
  - r20261006-010639-d0de: the lock. Security PASS; Proofs failed in `runs` only, because the job replaced PYTHONPATH.
  - r20261006-014957-f0c2: PASS, PASS.
  - r20261006-020536-d4e5: PASS, PASS, after the trim, with the lock unchanged.
  - r20261006-024928-3cad, on d4321152a with #1247 merged: `audit.py --name-instances` named the one anonymous instance
    left (`instDecidableWellShaped`, committed as 4973963bb, not by hand). The build passes, the vectors regenerate
    identically, and the verify is PASS, PASS with the lock unchanged.
- **Stacking.** This branch merges #1241 (c425ae37a), `main` (7b410fbf6) and #1247 (2043597b8). The two conflicts with #1247
  resolve to this branch's side. #1241 gets the `Game/Basic.lean` one alone.
- **`main` merged** (b966e567c, 68e614869: #1247 landed, plus #1258's `FlockVBridge.sound_shaFrom`).
  - `merge.py` refused the lock, because `main`'s new guarantee reads groups the lock reduction dropped.
  - I kept the guarantee rather than drop a record another lane had just pinned. Its record is `main`'s, byte for byte.
    Its reads stay in the executable `Flock` and `Proofs.Flock.{Soundness.Discharge.Hm,VBridge}`, under `meaning` and
    `reads_exempt`, and none of them reaches a proof-only library, so `ARKLIB_PENDING` stays empty.
  - r20261006-072808-417c (`--update`, then verify): PASS, PASS, with 956 guarantees. The update only narrowed four of
    its groups to the definitions it reads (a7f019f61).
  - Open for the coordinator: keep it outside the layout (as now), drop it to stay at #1170's set, or extract its reads.
    Extracting would make `security` import the executable verifier's package.
- **`main` merged again** (04c1a99f1, 89fb2c28c: PoUS's lock reduction, the ZK sessions' non-vacuity witnesses).
  - `merge.py` refused the lock. I resolved it with a script: C-Flock's guarantees keep this branch's records, everything
    else merges three ways from 68e614869, and each reads group keeps the definitions its remaining guarantees read.
    The lock has 863 guarantees and 185 reads groups.
  - It leaves out the 31 ZK records `main` changed (10) or added (21) in
    `FlockSoundness.Discharge.{Composed,ZkHidden,ZkReg}`, as #1170 does: 107 of the 207 modules they read reach ArkLib.
    Their theorems still build and are audited in `security_proofs`.
  - r20261006-090930-29c0 (`--update`, then verify): PASS, PASS, with the lock unchanged.
  - Open for the coordinator: confirm leaving them out (my recommendation), or pin them again with `ARKLIB_PENDING`
    restored for those modules.
  - **Decided: pin them** (@old-circuits-and-proofs, 6 Oct 7:20 AM PDT, Slack 1791296405.283989: a statement nothing
    watches defeats the point of the lock, and #1320's restatement DM needs the pins). 2dd07f4ca copies the 31 records
    from `main` and restores `ARKLIB_PENDING`. a0203e59b is r20261006-144352-fe7b's `--update`, which
    r20261006-150456-1070 verified (PASS, PASS, lock unchanged). 22 records are `main`'s byte for byte, and 9 differ only
    in `FlockSoundness.Game.prob` → `Verity.Game.prob` (#1241). `ARKLIB_PENDING` holds 106 modules, which is `main`'s 107
    minus `LinkSound`, whose `LinkLayout` this branch moved. The lock has 896 guarantees, 73 of them C-Flock's.
- **`main` merged a third time** (e56e53a66, c3be1f9b6: the rename move, #1271's `sound_mul128`, #1272's
  `sound_residualForms`).
  - `moves.json`: both sides appended a move record; `main`'s comes first, then this branch's.
  - The lock, by the same rule, plus `main`'s two new bridge guarantees kept beside `sound_shaFrom`. They also read
    `Proofs.Flock.Level3.GF128` (Mathlib and `Flock.Field` only), which joins `meaning` and `reads_exempt`. The Warden
    groups `main` renamed are dropped. 865 guarantees.
  - r20261006-110639-19a6 (`--update`, then verify): PASS, PASS. The update narrowed four reads groups by 88 definitions
    and changed no guarantee record (eca3a5726). `Flock.F128`'s value changed only because fewer of `F128`'s constants
    are read: it is exactly the digest of `F128 : Type` and `F128.mk`, and `Field.lean` is `main`'s.
- **A test the split broke, fixed** (ab5ba08a6). `backends/flock/tests/test_lean_verifier.py::test_audit_layer_is_abstract`
  required the audit proofs to import only Mathlib, `Game` and each other. They now also import their
  `Definitions.Flock.{Game,Audit}` halves and Partitioning's statement. The test allows those and checks them in turn:
  only Mathlib, `Definitions.Core.Game` and each other. My earlier local runs missed it because I didn't run
  `verity-flock` (about 20 minutes). The test is under `backends/flock/`, so `check` needs `lean-agreement`, as it does for
  #1247.

**Scope.** Items 2–4 of the brief, narrowed by the coordinator at 19:07Z. Item 1, extracting C-Flock's spec and with it
the ArkLib cuts, is out of scope; the Lean layout move made the two ArkLib cuts it needed (15f0987a0).

**Branch.** `cursor/flock-gk-game-f651` at e70aceb44, on `cursor/lean-layout-move-c3b2` at 77b8d66bc
([#1225](https://github.com/danielreuter/verity/pull/1225)). It supersedes the earlier `cursor/flock-security-defs-95d4`
plan (steps 1–6 on the pre-move layout), which is dropped.

## Answer: yes, for items 2–4

- **Item 2.** Every `ZK/GK` module that declares a definition (`Rand`, `Extract`, `Sim` and the new `Model`) reaches no
  proof-only library through its imports.
  - At 77b8d66bc, only Theorem GK's model was tainted: it sat in `GK/Theorem.lean`, which imports `ZK.Masking`.
  - The model now lives in `GK/Model.lean`. Its reads group digest is unchanged (c93e1e93…).
- **Item 3.** C-Flock's `Game` and its operations are core's definitions, exported under the old names, and every lemma
  keeps its name.
  - Audit r20261005-202739-215a certifies that the 186 guarantees reading them say the same thing under the old names:
    181 under old names, and 5 printed differently with the same type hash.
  - Three definitions print as "changed": `interleave`, `interleaveWith` and `batchLock`. Each is proven to be the same
    term with a different, identical matcher, because Lean reuses a `match_N` only within a module.
  - The evidence: probe r20261005-214506-6f75 reproduces the old record's digests from the old modules, built verbatim and
    separately; r20261005-212921-9a05 does the same for `batchLock`.
- **Item 4.** `tests/test_lean_packages.py` fails on any trusted module (a guarantee's reads, or a named assumption) that
  reaches a proof-only library, outside `ARKLIB_PENDING`.

  | | trusted modules | reaching a proof-only library |
  |---|---|---|
  | 77b8d66bc | 525 | 191 |
  | e70aceb44 | 523 | 190 (all in `ARKLIB_PENDING`, waiting on item 1) |

## Evidence

- art:076c4db87e94ea9112098c38d75ccb0e696996e4fe3689fe9bda23adde9e6e5f: the audit run.
  - Security: PASS.
  - Proofs: the four failures the move's own audit of 77b8d66bc also has (r20261005-180406-63e4).
- art:40726cb02998e748c3b5386e519253e047ba0fa26f69e95b4883cb065e0e1aa0: every changed record, before and after, for the
  named statement reviewer.
- art:2a78bd645cc9546d13ae76c548a5d9101bdcda59a1761fdc52c2fda2578356ec: the faithful matcher probe.
- art:7647eb92b1ba32733acc8bdc53ee4d5479f06c0a4379c9a2ea05ac2e1027428e: the scratch comparison.
- art:d08da1c65da8301099b50495e7eb519811c3923bf0fe61a48110a703eac2f0cc: the probe and comparison scripts.

## Findings for other lanes

- **Lean infra / the move.** The Proofs package's kernel replay ran out of memory past 95 GiB in a 96 GiB cgroup
  (r20261005-194325-4f55, art:ed2be9d2a133aa61d559b7688b306d66eef81e3de07d20fc75770cecbab20887).
- **Steward.** Node 1 has no `build` slot pool, so `lean_changed.py --records` refuses there.
- **@lean (audit.py lifts).** A lift can't be certified for a statement with `by omega` (or any tactic proof) in its type.
  In a theorem's type the proof becomes an auxiliary constant (`_proof_1`); in a definition's value Lean inlines it. So the
  unfolded type hashes differ in a proof term only. Comparing up to proof irrelevance (erasing proofs before hashing, or a
  kernel defeq check of `G` against the old type) would certify `Table.SoundFast100`'s kind of lift without a reviewer.
- **Jobs that keep a warm `.lake` outside `source`/`clone`.** The runner's PYTHONPATH names the shipped tree's import roots,
  one per workspace member. Map each entry to the copy rather than replacing it: d0de lost `verity_catalog` by replacing
  it. `--cwd clone` avoids this but rebuilds from cold.

## Open

- **Step 1.** #1241's base can now be `main`: the move landed as 7b410fbf6. `main` now holds #1247, so #1241 gets
  the `Game/Basic.lean` conflict, which resolves to #1241's side.
- **Step 2's head** is eca3a5726 (`cursor/flock-specs-95d4`), and its PR body is the proofs store's
  `internal/proofs/flock-specs-pr.md`. All 31 test suites pass there (`--quick`, circuit-check alone).
- **V*'s bridge's place** (`sound_shaFrom`, `sound_mul128`, `sound_residualForms`), and **the 31 ZK records left
  out**, as above.
- **Small VMs.** `tools/circuit_check/tests/test_circuit_check.py::test_parallel_jobs_give_the_serial_report` runs
  circuit-check in 3 forkserver workers of about 6.5 GB each. The OOM killer stops it on a 15 GB cloud VM and leaves
  the forkserver orphaned (I killed it by PID). `check`'s pod is unaffected.
- **Review.** A named statement reviewer signs off on step 1's 186 records and step 2's: the two Table guarantees and their
  new definitions, and the `Schedule` group.
- **#1170 and #1179.** This branch already holds #1170's reduction of `verity/Security`'s lock. When #1170 lands, its
  lock merges with this one (`merge.py`), and #1179's two guarantees join the 39.
