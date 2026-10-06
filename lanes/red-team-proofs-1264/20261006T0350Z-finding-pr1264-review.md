---
id: red-team-proofs-1264/20261006T0350Z-finding-pr1264-review
campaign: flock
lane: red-team-proofs-1264
kind: finding
status: final
repo: verity
origin: pr:1264@71b5ecaf9e9f7cc3fa150ab41889ea73185c5a5d
---
# Red team, PR #1264 (the J-table `y₀` typed per table): GRANT

Reviewed 8:50 PM PDT, 5 Oct, by red-team-proofs-1264 (agent bc-6dd5d1a0-9212-535d-8c06-107296d391e7) for the proofs
coordinator. The review is of head `71b5ecaf9e9f7cc3fa150ab41889ea73185c5a5d` of `cursor/zk-y0-pertable-95d4`, base `main`
`7b410fbf6`. I read it in a separate worktree (`/tmp/rt1264`). File references are relative to
`verity/Security/Proofs/Flock/Soundness/Discharge/` unless they start with `verity/` or `tools/`.

**Verdict: GRANT.** The PR fixes my #1257 finding 1 (note:red-team-proofs-1257/20261006T0114Z-finding-pr1257-review).
At kd = 16, J = 2 and g = 1, all ten repaired statements take a `y₀` at 27 link points, and I checked this by elaborating
each of them. Every `_nonvacuous` proof term references its pinned statement. The fallback table stays unsatisfiable
whatever `y₀` is, and at an accepted draw the plan does not depend on `y₀`. The lock removes nothing, and `main` has not
moved in a way that touches this PR. Nothing below is blocking.

## What I ran

Both runs ran on vy-nebius-1, in my own tree (`/workspace/research/scratch/rt1264-91e7/tree`). Its three `.lake`
directories are copies of the author's, not links. Both runs are at source `71b5ecaf9`, and both are PRESERVED.

- **r20261006-033735-8de7** (run record art:3cdee62ea68b9650a5f10e5afc4fe970aa556a0f7f5779e077b4be4496d71236): build
  only, followed by a probe that failed to elaborate.
  - It first deleted the build outputs of the PR's 19 touched modules (`out/deleted.txt`, 38 `.olean`).
  - It then ran `lake build` of `verity/Security/Proofs` under the `audit` Lean slot, with `BUILD_RC=0`: 5293 jobs, and
    all 19 modules plus `Proofs.Flock.Soundness` and `Proofs.Flock` were rebuilt from source.
  - Its probe failed because of two mistakes in my probe file. Their details are in "Probe bugs" at the end.
- **r20261006-034707-74be** (run record art:282b36d13cc70397854bc30654907f273b4d3f55faf8aef91cebba285d3b75aa): the same
  tree, with `lake build` a no-op this time, and the corrected probe passed (`PROBE_RC=0`).
  - The probe is `inputs/Probe1264.lean`, which imports the three `NonVacuous` modules, and its output is
    `out/probe.log`.
  - Every `#print axioms` in the probe log, 37 of them, lists only `propext`, `Classical.choice` and `Quot.sound`, or
    none. No `sorryAx` appears anywhere in the log.
  - The 37 cover the ten statements, the 21 new guarantees and my six probe theorems.

I did not replay the kernel; `check` does that. I also did not rerun the PR's audit. Its artifact
art:f4e68261b8d230943242f893241f3101acab1b0fcbd823512175f62c04b18c66 (run r20261006-025822-376c, `AUDIT_RC=0`, at
`e9aa53d91`) contains a `lean-audit.json` byte-identical to the one at `71b5ecaf9`. The commits `e9aa53d91..71b5ecaf9`
change only the lock, so the Lean sources the audit read are the head's.

## Check 1: the ten statements admit their `y₀` at kd = 16, J = 2, g = 1. Yes

**The probe's two theorems.** `RT1264.pub_16_2_1` and `RT1264.hid_16_2_1` both take the following hypotheses:
- `nTab I = 2` and `c.g = 1`;
- `hdj` in its concrete form, `∀ S, dj S = (drawOf (.subset 16) n S).toJson`;
- `AcceptsZK I t` and `recordDraw t.record = some (dj S)`.

**How the probe builds `y₀`.** It does not use the PR's `drawHyps…` helpers:
- `hdiv` follows from `16 % 2 = 0`.
- `DrawOkZKJ` at every S comes from the pre-existing `drawOkZKJ_of_file` (`Composed/CustodyJ.lean:86`) and
  `drawOkZKHJ_of_file` (`ZkHidden/CustodyJ.lean:33`).
- `y₀` comes from `setupZJ_of_acceptsZK` (`Composed/NonVacuousJ.lean:39`) and `setupZHJ_of_acceptsZK`
  (`ZkHidden/NonVacuousJ.lean:39`).
- `mPtsOf c.g (16 / nTab I) = 27` follows from `mPtsOf_16_8`.

**Applying the statements.** The probe then applies all ten statements, each by its fully qualified name, with
`(y₀ := …)` at 27 link points. Every one of them elaborates:
- `Composed.zk_session_soundJ`, `zk_session_soundJ_custody` and `zk_session_soundJ_custody_json`;
- `ZkHidden.zk_session_soundHJ`, `zk_session_soundHJ_custody`, `zk_session_soundHJ_custody_json`,
  `zk_session_composedHJ` and `zk_session_viewHJ`;
- `ZkReg.zk_session_soundHJR` and `zk_session_soundHJR_custody`.

The `_custody` forms get their `hdiv` and `hdj`, and the non-custody forms get `hDraw := fun _ => hok _`.

**The `_nonvacuous` theorems apply the pinned statement itself.** A `CommandElabM` check took each `_nonvacuous`
theorem's value and called `getUsedConstants` on it. All ten value terms contain their pinned statement's constant (log
lines `USES … : true`), and each such constant is a `theorem`. So none of them applies a weaker copy, and the
`have _ := fun … => <statement> …` in each proof survives into the term.

## Check 2: the `_nonvacuous` premises are jointly satisfiable apart from an accepted session. Yes

No premise is unsatisfiable at J ≥ 2, and none constrains the others beyond what a real session gives:
- `hdiv` holds at 16 % 2 = 0.
- `hdj` is satisfiable via `drawFileZK_of_toJson_subset`.
- `DrawOkZKJ(H)` is derived from `hdj` and `hdiv` at every S (`drawOkZKJ_of_file`), so it adds no constraint.
- `hd` says the record's `unit_draw` is the session's draw. This is the §16.12 reading in the verifier's PROTOCOL.md:
  the record's subset draw is split into J equal parts, and every table has the same m_pts.
- `hTags`, `ht` and `hc` are about the inputs alone. Two-table `--zk` inputs exist: fixture art:5542740a's `sessions/j2`
  is one, and the Lean verifier accepts it (`backends/flock/tests/test_lean_zk.py`,
  `test_two_tables_a_draw_and_m26_are_accepted`).
- At an accepted session, every table's setup follows from acceptance (`setupZJ_of_acceptsZK`).

The only premise left unproved is the existence of an accepted session with a subset draw. That is what the PR's
"Stops short" says (but see check 5, item 1).

## Check 3: only the `y₀` binder and `d₀` changed, and no conclusion is weaker. Yes

**The signature diffs.** In the PR's `review.txt`, each of the ten changed records differs only in the `y₀` binder
line(s) and the new `{d₀ : Lean.Json}`. I compared each before/after pair with difflib. The type changes from
`DrawSetupZK(H) I mPts S₀ (dj S₀)` to `DrawSetupZJ/ZHJ (inputsJ I 0) mPts S₀ d₀`. Every conclusion and every other
hypothesis is textually unchanged.

**The changed definitions.** There are 24 of them, in `Composed/DefsJ`, `ZkHidden/DefsJ` and `ZkReg/BindHJ`. Each one
changes only through the `y₀` parameter it threads, apart from the following:
- `DrawSetupZJ.refused` (`Composed/DefsJ.lean:145`) and `DrawSetupZHJ.refused` (`ZkHidden/DefsJ.lean:240`) are new.
  Each is `y.tabAt (regionsOf y.x.st ++ contra …) y.x.refused_wf`, the same body as `DrawSetupZK.refused` and
  `DrawSetupZKH.refused`.
- The else branches of `tableZJ`, `tableZHJ`, `tableShJ` and `tableShHJ` now read `y₀.refused`, or
  `y₀.x.refused (typedJ ht 0) _` for the public shadow.

**The refused fallback stays unsatisfiable.** `RT1264.refusedZJ_unsat` and `refusedZHJ_unsat` prove
`¬ y.refused.S.Satisfies z` for every `y`, at any inputs, S and d. Each is a single application of
`Integrate.DrawSetup.contra_unsat` (`Integrate/Sites.lean:148`). `XplurZC`'s candidates require
`(tabOfZ …).S.Satisfies` (`ZkLink/CompiledLink.lean:146`), so a refused table contributes no openings, whatever `y₀` is.

**A free `d₀` cannot pick a setup the verifier never checked.**
- `y₀` is universally quantified, so each theorem holds for every choice of it.
- `y₀` still carries the verifier's own `setupH … (some d₀) = .ok st` at table 0's inputs.
- `y₀` reaches the plan only through refused tables.
- `RT1264.planZJ_indep_y0` and `planZHJ_indep_y0` prove `planZJ dj y₀ S R = planZJ dj y₁ S R`, and the same for
  `planZHJ`, for any two references (any S₀, d₀). They assume a session `verify --zk` accepts at the draw `dj S`. So
  where the event can happen, the plan does not read `y₀`.

**What `y₀` still affects.** On the right-hand side, `ksAvgStrictZ` and `linkBoundZC` read the plan at draws where
some table is refused, and `hr` bounds the rate of those refused tables. Each theorem is a proved bound for every `y₀`,
so this does not weaken the statement; on `main`, `S₀` was just as free.

## Check 4: nothing else on main broke or changed quietly. Yes

**The lock.** Compared with `main`, the lock has 1768 guarantees where `main` has 1747: 21 are new, none were removed,
and 10 changed (`type_hash` and `signature` only). `reads` has 529 modules, with none added or removed. Only three
module digests changed: `Composed.DefsJ`, `ZkHidden.DefsJ` and `ZkReg.BindHJ`. No definitions were removed, and the
only new ones are the two `.refused`. The seven hidden and registered statements no longer read `ZkHidden.Defs`. Every
other changed reads entry differs only in its list of guarantees.

**The build.** The full build at the head, with the touched modules rebuilt from source, succeeds (r20261006-033735-8de7).
Lean's dependency direction means nothing in `verity/Security` or `flock_verifier` can import these modules.

**Uses of the ten statements.** They are used only in their own modules, in the three new `NonVacuous` files and in
`ASSUMPTIONS.md`, which has no `y₀` text.

**`main` since the base.** `origin/main` (`c305471c5`) is 65 commits past `7b410fbf6`, and none of them touches a `.lean`
file, a lock, `tools/lean` or a Lake file. `git merge-tree origin/main 71b5ecaf9` is clean (tree `56717db1b…`).

**Forms the PR leaves alone.**
- The one-table forms still use the whole-draw `DrawSetupZK(H)`, which is consistent at J = 1.
- The non-zk J-table path (`Tables/Statements.lean`) has no reference-setup binder, so this class of defect cannot
  occur there.

## Check 5: what "Stops short" omits. Four non-blocking notes

1. **No `--zk` instance with a subset draw is on record at J ≥ 2.** "Stops short" says the session's existence is
   unproved. It does not say that no recorded session would satisfy `hd`:
   - In the zk fixture art:5542740a, `sessions/j2` is accepted but has `unit_draw: null`.
   - The drawn J = 2 sessions in art:425f6860 are not `--zk`.

   The premise is therefore supported by the protocol text (§16.12) but has no instance yet. The cheap close is a fixture
   session that `verify --zk` accepts with J = 2 and a subset draw, and a test of it. That would be a test, not a Lean
   proof.
2. **The link to the statement is a build-time guard.** Each `_nonvacuous` theorem's pinned type states only that the
   binder is inhabited and `DrawOkZKJ` holds; it does not state an application of the statement. The application lives
   in a discarded `have` inside the proof term. Check 1 shows that it survives in all ten terms. But a proof is
   irrelevant to `meaning`, so a later edit that drops the `have` would change no lock record. Only the build, which
   `check` runs, guards it.
3. **`hr` also bounds refused tables.** It quantifies over every table of `planZJ dj y₀ S R` at every S, refused tables
   included, and those read `y₀`'s statement shape. It is satisfiable once `k > 2^logLen / e`, and this is unchanged
   from `main`.
4. **#1179 overlaps this PR.** #1179 (`cursor/verifier-fail-closed-95d4`, `ca8e3a26c`) carries the same per-table
   binder and `DrawSetupZJ.refused`, but under the old layout (`backends/flock/verifier/lean/soundness/…`). So the PR's
   "already carries this fix" is accurate. Whichever of the two lands second restacks onto the other.

The other items are already disclosed: no kernel replay (`--no-replay --no-runs`), no `check` yet, and targeted builds
outside the Lean slots. The rebuild of `ZkHidden/View.lean` prints `dif_pos` deprecation and unused-simp-argument linter
warnings, but they come from lines 54 and 62–63, which the PR does not change.

## Probe bugs (mine, not the PR's)

The first probe failed only because of my own file:
- `_custody_json`'s trailing implicits `{k Rw M}` come right after `hdj`, which was the last argument I named, so they
  were left unsolved.
- My `CommandElabM` check interpolated a `Bool` where Lean expected `MessageData`.

The second run fixed both, by passing `(k := 1) (Rw := 1) (M := 1)` and `toString`. Neither error was in the PR's code.
