---
id: red-team-proofs-806/20261002T1634Z-finding-pr828-statement-review-hpt-hh
campaign: e2e-guarantees
lane: red-team-proofs-806
kind: finding
status: open
repo: verity
origin: red-team-proofs-806 (agent bc-7b6772b1-42d3-5a07-9701-82e182ea5921; started by proofs bc-8416bc72)
---

# Statement review of #828's two record changes (`hs` → `hpt`; `hh` under #757): APPROVE, with scope text to fix

**Named statement reviewer: red-team-proofs-806.** I'm the same agent (bc-7b6772b1) who wrote
`note:red-team-proofs-554/20261002T1412Z-finding-pr828-statement-review` before the coordinator's 7:42 AM PDT rename. The
name red-team-proofs-554 now belongs to bc-d8964c29.

**Heads reviewed**, each in its own worktree, with no Lean build. I worked from the source, the recorded `lean-audit.json`
and the status file's outputs 14 and 15, and diffed every changed record token by token with a script.
- A: `cursor/e2e-integrate-95d4` at `ecc370aa2` (output 14, built at `2911e0aea`), against my earlier head `d5311b9f4`.
- B: `cursor/e2e-integrate-757-d747` at `3e1c2b8d4` (output 15, built at `4daa248b0`), against `ecc370aa2`.
- The merged head `67cd3195d` (PR #828's head since 16:28Z). Its three `lean-audit.json` files are byte-identical to
  `3e1c2b8d4`'s. No `--update` output exists for it yet (see V1).

**Verdict: APPROVE both record changes.** Neither makes a guarantee easier. A strengthens the headline. B narrows ten
acceptance lemmas by a hypothesis they need and changes no conclusion. Three findings remain, none about a record: S1
(scope text, fix before merge), M1 (merge path, for the lander) and V1 (build the merged head).

## A. `hs : I.tags.sharedRows = false` → `hpt : pub.tables = none` (`ecc370aa2`)

- **The records change only by the binder.**
  - `flock_headline_exec`, against `d5311b9f4`, has 5 token hunks:
    - `(hs` → `(hpt`;
    - `I.tags.sharedRows Bool.false)` → `pub.tables Option.none)`;
    - `hs` → `hpt`, three times, in the `rsAt`/`rsAt_computes` arguments.
  - `rsAt_computes` has the same 3 kinds of hunk.
  - Assumptions are unchanged. No other pin moved.
  - `circuit_sharedRows` is gone (481 → 480 pins), and nothing at `67cd3195d` cites it or `hs`.
  - The definition `rsAt` changes the same way (`Headline.lean:47-54`).
- **Stronger, not weaker.** `Layout.loadPublic_tables (h : HmRow.loadPublic tags c file = .ok pop) (hs : tags.sharedRows
  = false) : pop.tables = none` is unchanged. At `hpt := loadPublic_tables hpub hs`, the new statement is the old one,
  since `rsAt` takes `hpt` only as a proof (proof irrelevance). So every instance of the old record is an instance of the
  new one, and the new one also covers tags with shared-row files whose public file loads without tables. This reverses
  the narrowing I flagged as T2 at `d5311b9f4`, and answers bc-d8964c29's NO-GRANT.
- **Not a verifier check moved into an assumption.** `pub` is the verifier's own `loadPublic` of the session's fixed
  input file (`hpub`). `hpt` is a decidable fact about that file, and `sitesAt_bcSite` needs exactly it (BcSite reads
  `b ‖ c` as `n · np` consecutive pieces).
- **Non-vacuous on what the headline covers.** I fetched `art:c3386284` and checked three things:
  - **The eval.** `eval967.lean` runs the verifier's own `HmRow.parse Tags.circuit967b8d06` on `art:425f6860`'s
    `stage/circuit.txt`, then `Layout.scopeOk`, then `HmRow.loadPublic` on `art:12f95e2a`'s `stage/pub-4.bin`.
    `eval967.out` prints `sharedRows true`, `HmRow.parse: ok; ports 2; Layout.scopeOk true` and `HmRow.loadPublic: ok; n 4;
    pub.tables = none: true`.
  - **The file.** `pub-4.bin`'s header is `flock-circuit-inputs` with a `content_digest` and no `shared_rows`.
  - **The session.** `art:12f95e2a`'s `sessions/os` is r20261002-055711-3607's `FC_COINS=os` loopback session, accepted.
  - `withCoins .os` changes only `identity` (`Statement.lean:139-140`), so the tag the eval used is the one the headline
    reads.

## B. `hh : tags.hiddenOutputs = false` under #757 (`3e1c2b8d4`)

- **Ten records move, each by exactly one binder.** Between `ecc370aa2` and `3e1c2b8d4`:
  - 33 pins are new, all `FlockSoundness.CROnly.*` (#806's; see M1), none was removed, and exactly ten records changed;
  - in each of the ten, deleting `(hh : Eq I.tags.hiddenOutputs Bool.false)` from the new signature gives the old one
    exactly (`tags.hiddenOutputs` for `setupTables_retain`), and the assumptions are unchanged;
  - the ten are `accepts_setupH`, `accepts_retained`, `accepts_allRetained`, `accepts_rep_rounds`,
    `accepts_tables_hm96`, `accepts_tables_hm96_of_leaf`, `accepts_verdict_hm96` and `setupTables_retain` (e2e-exec's),
    plus `drawSetup_of_accepts` and `tableAt_of_accepts` (Integrate's);
  - the source change, 6ac5bc55f, passes `hh` on and adds `simp only [… ite_eq_right hn] at h` before the walk.
- **Motivated, not easier.** #757's `Stmt.setupTables` (`HmRow.lean:1415-1417`) dispatches on the outer
  `tags.hiddenOutputs` to `setupHidden`. Without `hh`, each conclusion ("every table is `setupH`'s statement") is false at
  a hidden-output tag. So `hh` narrows coverage to where the lemmas hold, and no conclusion is weakened.
  - It isn't a verifier check moved into an assumption: `I.tags` is the verifier's `--statement`, not prover data.
- **Non-vacuous.** `hiddenOutputs` defaults to `false` and is set `true` only at `Tags.circuit` and `Tags.circuitTypes`
  (`Tags.lean:265,274`). `circuit967b8d06`, `circuitE51e2b86` and `circuitEb90718f` don't set it, so `hh` is `rfl` there,
  OS coins included.
- **The headline doesn't move, and is re-proved against post-#757 flock-verify.**
  - `flock_headline_exec` and `rsAt_computes` have the same records at `ecc370aa2`, `3e1c2b8d4` and `67cd3195d`.
  - All 99 of the headline's `reads` groups have unchanged digests.
  - `meaning` doesn't list `Flock.HmRow`, so `Stmt.setupTables`, `setupH` and `setupHidden` are the executable the
    theorem is about, not definitions it pins.
  - Since the headline takes no `hh`, hidden-output sessions are not excluded by a hypothesis. Its `x₀ : DrawSetup`
    asks `Stmt.setupH` to accept the files, and `hdec` asks setupHidden-accepted sessions to decode into `setupH`'s table.
    So the theorem makes no claim about those sessions, which is conservative and over-claims nothing. The status file's
    "the headline's `hdec` cannot hold there" is stronger than anything shown; "is not claimed there" is accurate.

## Findings

- **S1. Scope text: after #757, no session main's prover writes is in the headline's scope.** Text only, should fix
  before merge, no record moves.
  - Main's `flock-circuit.rs` `identity()` writes `"outputs": "hidden: …"` unconditionally.
  - #757 converted the vLLM serving rows and `one_stage` a0.
  - `Tags.circuit` (`verity/flock-circuit`, the default `--statement`) is now the hidden-output statement, and
    `soundness/` has no theorem about `setupHidden` (verifier `PROTOCOL.md` §16.13, §17.4).
  - So the headline covers M0's public-output sessions only: `@967b8d06` (and `@e51e2b86`/`@eb90718f`) on OS coins, from
    builds before #757, such as r20261002-055711-3607.
  - None of the three texts says so:
    - the docstring's Scope paragraph at `67cd3195d` (`Headline.lean:92-98`) doesn't mention hidden outputs, and says
      "as M0's per-instance public files load";
    - the status file's draft PR body names `hh` but not this consequence;
    - the live GitHub body of #828 is still `d5311b9f4`'s, describing `hs` as the narrower replacement of `hpt`, which
      is now backwards.
  - Fix with one sentence in the docstring's Scope and in the PR body, for example: "Sessions of a hidden-output
    statement (the default `verity/flock-circuit` since #757, which main's prover writes) are outside it until
    `setupHidden` has `setupH`'s lemmas; it covers public-output statements (`@967b8d06`) from builds before #757."
    Also refresh the PR body's `hpt` bullet.
- **M1. Merge path: #828 now carries two open PRs.** Both are OPEN, and main is still `56b7e4f7c`.
  - #806 at `5e5e6d558`, through `3e1c2b8d4`'s train prep `a4bce7200`, and at `c7d626d39`, through `f76d9e0cc`.
  - #793 at `16e549a20`, through `4394c78cf` ("Train prep: merge #793"), which `67cd3195d` merges.
  - Landing #828 lands both. The 513 pins include #806's 33 (on main + #757 alone, #828 would have 480).
  - If that's the intended train, list #806 and #793 in the body's joint-merge paragraph and run `check` on this tree.
    If not, re-apply `6ac5bc55f` on #828 + main `56b7e4f7c` without the train preps.
  - My #806 grant at `c7d626d39` covers #806's 33 pins. #793 changes no pin record in any package.
- **V1. The merged head has no build or audit yet.** `67cd3195d`'s `lean-audit.json` files are unchanged from
  `3e1c2b8d4`'s, but #793 rewrites `Stmt.setupTables`'s `count > 1` return:
  - it adds `let hello ← helloOf …` and `coinTree := CoinTree.ofHello hello`;
  - that is the `do` block `setupTables_ok` and `setupTables_retain` walk (`walk_step`).
  - So the proofs need rebuilding. If `audit.py` passes there with no record change, this review covers `67cd3195d`.
  - The head's `check --record` would establish it.
