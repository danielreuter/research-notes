---
id: red-team-proofs-1257/20261006T0455Z-finding-pr1257-regrant
campaign: proofs
lane: red-team-proofs-1257
kind: finding
status: final
repo: verity
origin: pr:1257@a294e8f5ed48276e3526945058f26c3a7baf6f88
---
# Red team, PR #1257 re-grant (Flock.Guarantees.EndToEnd at the per-table y₀): GRANT

Reviewed 9:55 PM PDT, 5 Oct, by red-team-proofs-1257 (agent bc-6dd5d1a0-9212-535d-8c06-107296d391e7) for the proofs
coordinator. The review is of head `a294e8f5ed48276e3526945058f26c3a7baf6f88` of `cursor/flock-e2e-95d4`, base `main`
`7b410fbf6`, read in a separate worktree (`/tmp/rt1257b`). It follows my NO-GRANT at `8bb07eeb9`
(note:red-team-proofs-1257/20261006T0114Z-finding-pr1257-review) and my GRANT of #1264 at `71b5ecaf9`
(note:red-team-proofs-1264/20261006T0350Z-finding-pr1264-review). File references are relative to `verity/Security/`.

**Verdict: GRANT.** Finding 1 is closed:
- `EndToEnd_refSetup`'s witness goes into `EndToEnd` unchanged, at any `kd` and any number of tables, together with a
  custody built from the same draw file. I elaborated this, including at kd = 16, J = 2, g = 1.
- The merged #1264 commit is byte-identical to the one I reviewed.
- The restatement touches only the binder and the docstring.
- The lock changes exactly the records the body lists.
- The kernel accepts every constant of the 29 modules the change reaches.

Nothing is blocking.

## Runs

All of these ran on vy-nebius-1 in my tree from the #1264 review (`/workspace/research/scratch/rt1264-91e7/tree`), moved
to `a294e8f5e`. They copied no new `.lake` and made no audit scratch: inodes were at 70% before and after, and node 1's
hold is on new audits. Everything ran under the `audit` Lean slot, at source `a294e8f5e`, and is PRESERVED.

- **r20261006-044431-4709** (run record art:fd3a8dfdac2fefee417456c7b5ea5f761d1a5bc0d582bbae65f20302648c3329)
  - `lake build` of `Proofs` passed: 5292 jobs.
  - The 29 modules the change reaches were built from source, because `DefsJ`'s docstrings differ from `71b5ecaf9`'s.
  - The probe (`inputs/Probe1257.lean`) passed.
  - Its replay stopped before checking anything. The replay set was not closed under imports: a module outside it
    imports `Composed.DefsJ`, so `DrawSetupZJ._sizeOf_1` came in twice. That was my set, not the PR.
- **r20261006-045050-cee2** (run record art:0b88941c10c75e8ae3affed6590f5bcf38046af1469430eddf9c68ad96be3f5b)
  - The build was a no-op, and the probe passed again.
  - `tools/lean/Replay.lean` ran on the 29 modules: the 15 that #1257 changes against main, plus every module that
    imports one of them. That set is exactly the 29 modules the build rebuilt.
  - Result: "510 constants of 29 modules accepted by the kernel … axioms of their bodies: propext, Classical.choice,
    Quot.sound". Peak memory was 7.8 GB, and `REPLAY_RC=0`.
  - The set includes `Specs.Flock.Guarantees.EndToEnd`. The lock's `exempt` reason says neither package's own replay
    names that module, so for this head it is now replayed too.

I did not run a new audit. The PR's audit is **r20261006-030412-869e**, with run record
art:6e557a936bff512144070764a5d3a5e6fcbba2dd94481ad0b2f3aa8a96179c7b:
- It ran `audit.py --build --no-replay --no-runs --update --owner @proofs verity/Security` from clean `196315c46`, and
  passed.
- Its `lean-audit.json` is byte-identical to the head's (`cmp`).
- `196315c46..a294e8f5e` changes only that file, so the Lean the audit read is the head's.

## Check 1: finding 1 is closed. Yes

**The conclusion matches the binder.** `EndToEnd_refSetup`'s conclusion is
`Nonempty (DrawSetupZJ (inputsJ I 0) (mPtsOf c.g (kd / nTab I)) (partS I (dj S) S ⟨0, _⟩) (drawJ I (dj S) 0))`
(`Proofs/Flock/EndToEnd.lean:38-43`). `EndToEnd` binds `(S₀ : Finset (Fin n)) (d₀ : Lean.Json) (y₀ : DrawSetupZJ
(inputsJ I 0) (mPtsOf c.g (kd / nTab I)) S₀ d₀)` (`Specs/Flock/Guarantees/EndToEnd.lean:60-61`). Both `S₀` and `d₀` are
quantified, so any instance discharges the binder.

**`RT1257.feed_any`** (in the probe) shows it at any `kd` and any J:
- It takes `y₀` from `EndToEnd_refSetup`.
- It applies `Flock.SecurityProofs.EndToEnd n Unit I ht c hc hU pub hpub hpt hscope kd hkd hdiv dj _ _ y₀ wr dg N Unit
  Lb src hA3 hTags ⟨hRec, hdj⟩`, with `S₀` and `d₀` found by unification.
- The `hdj` in `hCust = ⟨hRec, hdj⟩` is the same `hdj` that built `y₀`. So the pair finding 1 showed unsatisfiable,
  `y₀` together with `hCust.2`, now holds together.

**`RT1257.e2e_16_2_1`** is the same at `nTab I = 2`, `c.g = 1` and `dj S = (drawOf (.subset 16) n S).toJson`. It also
proves `mPtsOf c.g 16 = 28` and `mPtsOf c.g (16 / nTab I) = 27`, and that table 0's setup exists at 27 link points.

**Supporting checks.**
- In both proof terms, `getUsedConstants` contains `EndToEnd` and `EndToEnd_refSetup`.
- `EndToEnd`'s own term contains `zk_session_soundJ_custody`.
- Each `#print axioms` lists `propext`, `Classical.choice` and `Quot.sound`, with no `sorryAx` anywhere.

**The hypotheses are ones an accepted session meets.** Apart from those `EndToEnd` already takes (`ht`, `hc`, `hdiv`,
`TagsOkZJ`, and the draw file at population `n`, which is `hCust.2`), `EndToEnd_refSetup` needs only two things:
- an accepted transcript, `AcceptsZK I t`;
- the record's draw, `recordDraw t.record = some (dj S)`.

## Check 2: `124100276` brings in `cef6316b0` byte for byte. Yes

- The parents of `124100276` are `8bb07eeb9` and `cef6316b0`.
- `git diff --name-only 124100276^1 124100276` is exactly `cef6316b0`'s 13 files.
- Each file's blob at `124100276` equals its blob at `cef6316b0`, and so does its blob at the head.
- `cef6316b0` is an ancestor of #1264's granted head.
- At `71b5ecaf9`, 11 of the 13 are identical. The two `DefsJ` files differ in one docstring line each, from #1264's
  `642a0886d`: `setupZJ_of_verifiesZK` became `setupZJ_of_acceptsZK`, and the same for the hidden form.

## Check 3: the restatement changes nothing else. Yes

**The spec** (`git diff 8bb07eeb9 a294e8f5e`) changes in two places only:
- the docstring's last paragraph, which now names `y₀` and `EndToEnd_refSetup`;
- the binder, where `(S₀) (y₀ : DrawSetupZK I … S₀ (dj S₀))` becomes `(S₀) (d₀ : Lean.Json) (y₀ : DrawSetupZJ (inputsJ I 0)
  … S₀ d₀)`.

No other hypothesis, `let` or conclusion changed.

**The proof.** The only change in `EndToEnd`'s proof is that `intro` gains `d₀`. It is still
`zk_session_soundJ_custody … y₀ …`, then `rw [Law.subset_miss, linkBoundZC, ite_eq_left hA2]`, then `exact`.

**Elsewhere.** The `EndToEnd` guarantee record itself is unchanged. Its meaning is the `Specs.Flock.Guarantees.EndToEnd`
definition, which is the one changed definition there.

## Check 4: the lock changes only what the body lists. Yes

The lock at `a294e8f5e` against the lock at `8bb07eeb9`:

**Guarantees.** There are 1749 guarantees where there were 1748. The new one is `Flock.SecurityProofs.EndToEnd_refSetup`
(owner `@proofs`, `assumptions: []`). None was removed. Ten changed, only in `signature` and `type_hash`: the ten J
theorems.

**Agreement with #1264.** Each of the ten records equals #1264's at `71b5ecaf9`. Apart from the spec module that only
#1257 adds, every module's digest and definitions agree with #1264's lock. That covers the 2 new and 24 changed
definitions of `Composed.DefsJ` (1 + 10), `ZkHidden.DefsJ` (1 + 12) and `ZkReg.BindHJ` (2).

**Reads.** The four changed digests are those three modules and `Specs.Flock.Guarantees.EndToEnd` (1 changed
definition). Of the other changed entries:
- 63 modules change only their readers, by gaining `EndToEnd_refSetup`. `Composed.DefsJ` gains it as well, which makes
  64.
- `ZkHidden.Defs` loses the seven hidden-output J theorems as readers.

**Policy sections.** Only `exempt` changed: `196315c46`'s added sentence about the replays.

**`review.txt`** agrees: 1 new and 10 changed guarantees, 2 new and 25 changed definitions. The 25 are the 24 above plus
`Flock.Guarantees.EndToEnd`.

## Check 5: `git merge-tree` with #1264's granted head. Clean. `e9aa53d91` is stale

- `git merge-tree --write-tree a294e8f5e 71b5ecaf9` is clean (tree `3fbd0e9e4…`). The merged `lean-audit.json` is
  valid and holds all 1770 records, those of both PRs. Whether its reader lists are exactly what an audit would write is
  for `check` at the merged commit.
- `e9aa53d91` is #1264's second-to-last commit. The head is `71b5ecaf9`, a lock-only re-record on top of it. The merge
  with `e9aa53d91` is clean too, so nothing changes for the merge, but the sha in the body is stale.
- With `origin/main` (`c305471c5`) the merge is clean.

## Check 6: audit. None needed; the replay covers the changed declarations

The record is the PR's audit, copied unchanged (see Runs). The kernel replay that audit skipped is r20261006-045050-cee2,
scoped to the 29 modules. The rest of the closure is main's modules, imported as they are. `check`'s full audit at the
merged commit is still what gates the merge.

## Non-blocking notes

1. **Body edits.**
   - The merge note should name #1264's head `71b5ecaf9`, not `e9aa53d91`.
   - "#1264's other two commits" should say three: `642a0886d`, `e9aa53d91` and `71b5ecaf9`.
2. **Docstring references.** The docstrings of `tableZJ` and `tableZHJ` name `setupZJ_of_verifiesZK` and
   `setupZHJ_of_verifiesZK`, which don't exist on this branch. The body already discloses this, and it resolves when
   #1264 lands. No record digests a docstring.
3. **Non-vacuity rests on a session with no instance yet.** It rests on the existence of an accepted `--zk` session at
   J ≥ 2 whose record carries a subset draw. As noted for #1264, none is on record: the zk fixture's `sessions/j2` has
   `unit_draw: null`.
4. **`y₀` is still free.** Through the refused tables, `y₀` reaches only the right-hand side and `hr`, and the plan does
   not read it at an accepted draw. This is the same analysis as #1264's check 3, on definitions identical to its own
   apart from docstrings.
