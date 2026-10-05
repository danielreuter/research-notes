---
id: proofs/20261005T1610Z-finding-red-team-lean-move
campaign: layout-move
lane: proofs
kind: finding
status: open
repo: danielreuter/verity
origin: red-team-lean-move
---

# Red team review: the Lean layout move (PR #1225, `cursor/lean-layout-move-c3b2`), red-team scope

**Verdict: REFUSE for PR #1225 at `b37b1672324e2bc23ca4125bba01c4ac25a470c9` (17:20Z).** Two gates go vacuous (B1, B2).
Two tests also break, and `check` will catch them (F1, F2). Neither ArkLib cut is in the branch yet.

- How this head was built: it merges `origin/main` (#1193 #1197 #1210, none of which touch Lean) and the regenerated
  `2e5c5c94e`, and the tree is the same as `c55eed2c2`'s. Every probe below gives the same result on both.
- Re-review on the fixed head:
  - Run `rerun.sh HEAD`, from `art:81dbfd4f5a5607837410f44f8b5d5e7f8754fdee03338e996a5f6e2d0a71b9e2` (`tools/`; or
    `/tmp/rt-lean-move-tools/` on this VM). It reads files only: one PASS/FAIL line per finding, then the record, gate and
    declaration diffs.
  - Add `AGREE_LOG=…/lean-agreement.log` to compare the check run's agreement set by set.
- What turns this into a GRANT:
  - B1 and B2 fixed.
  - F1 and F2 fixed, or `check` red on them.
  - The cuts reviewed (or explicitly deferred out of the PR).
  - The `--update --moved` printout showing only the same statements.
  - The check run's agreement equal to the reference.
- Exact fixes:
  - **B1.** In `tools/move/lean.py` `merge_locks`, after line 493 (the `watch` loop):
    `for s, e in up.get("scan", {}).items():` / `if s in prf["upstream"].setdefault("scan", {}): raise SystemExit(f"upstream
    scan {s} in two locks")` / `prf["upstream"]["scan"][s] = e`. Then regenerate, and run
    `python tools/lean/upstream.py verity/Security/Proofs`.
  - **B2.** In `tools/check/queue.toml`, red-team `paths = ["backends/flock/", "verity/Security/Proofs/Flock/",
    "!README.md", "!PROTOCOL.md", "!*/tests/*"]`, with a test that pins it on a moved file.
  - **F1, F2.** `backends/flock/tests/test_lean_verifier.py` (details below).

- Brief: proofs coordinator (bc-8416bc72), 9:05 AM PDT. Ruling: thread 1791215694.084699. Move thread 1791216100.963309.
- Base: main `378453fb3` (Layout move #1206). Heads reviewed: `bfcf4fe8e`, `2f5fc95d9`, `6447d4723`, `444c5d72f`,
  `c55eed2c2`, `b37b16723`.
- Scope: `backends/flock/` minus `README.md`, `PROTOCOL.md` and `*/tests/*` (`tools/check/queue.toml`'s red-team grant),
  plus wherever the move puts C-Flock's soundness, level3 and verifier proofs (`verity/Security/Proofs/Flock/`), and the
  gates keyed by their paths.

## Blocking (fail-open)

1. **B1: the upstream watch on ArkLib goes vacuous.**
   - `merge_locks` starts the proofs lock's `upstream` as `{"imports": [], "watch": {}}` and copies each old lock's `imports`
     and `watch`, but not its `scan`.
   - Soundness's base lock had `"scan": {"Arklib": {"baseline": "scripts/axiom_baseline.json", "sources": ["ArkLib"]}}`. It was
     the only lock with a `scan`.
   - At head, `verity/Security/Proofs/lean-audit.json` has `upstream` = `imports` + 16 `watch` entries (C-Flock's 15 and NCI's
     `loomis-whitney`), and no `scan`.
   - The audit runs only the no-build pass (`audit.py:1212`, `upstream.pinned()`), and that pass iterates `cfg.get("scan", {})`
     alone. The exact pass (`upstream.py --lean`) is manual. So nothing is scanned and nothing fails: a pinned ArkLib that
     proves A1 (`BCHKS25Thm46`), `udr-mca`, `list-size` … stops failing the audit.
   - Fix: in `merge_locks`, copy each lock's `scan` (raise on a name in two locks, as for `watch`), then regenerate. Rerun
     `upstream.py verity/Security/Proofs` before landing: NCI's `loomis-whitney` entry is now scanned against ArkLib's sources
     too, and a hit there fails closed until acknowledged.
   - Sturdier (follow-up, @lean): `pinned()` fails a policy whose `watch` is non-empty while `scan` is empty.
2. **B2: the red-team grant no longer covers C-Flock's proofs.**
   - `tools/check/queue.toml` still has `paths = ["backends/flock/", "!README.md", "!PROTOCOL.md", "!*/tests/*"]`.
   - `Rules.needs` (`research/queue.py`) applies `rule_touches` to the changed files. After the move, a PR that edits only
     `verity/Security/Proofs/Flock/**` (soundness, level3, the verifier's proofs: 604 `.lean` files at head) needs no red-team
     grant. At base, every one of those files was under `backends/flock/`.
   - Fix: `paths = ["backends/flock/", "verity/Security/Proofs/Flock/", "!README.md", "!PROTOCOL.md", "!*/tests/*"]`. The file
     header says the research coordinator owns `queue.toml`, so this needs top's edit or OK.
   - Add a test that pins the grant on one moved file, e.g. `rule_touches(red-team paths,
     ["verity/Security/Proofs/Flock/Soundness/Headline.lean"])`, so the next move can't drop it silently.
   - Residual, not blocking: C-Flock's guarantee records now sit in the shared `verity/Security/lean-audit.json`. Unpinning a
     C-Flock guarantee there needs no red-team grant (at base, soundness's own `lean-audit.json` was under `backends/flock/`).
     `spec_alert` still DMs Daniel. A per-owner `lean_audit` grant would need a `queue.py` change, so it's out of a move's
     scope.

## Fixes (fail-closed; `check` fails until they're made)

- **F1.** `backends/flock/tests/test_lean_verifier.py`, `test_audit_layer_is_abstract`: `AUDIT = LEAN / "soundness" /
  "FlockSoundness" / "Audit"` no longer exists, and `assert files and …` fails. Set it to
  `ROOT/verity/Security/Proofs/Flock/Soundness/Audit` and `AUDIT_IMPORTS` to
  `import (Mathlib\.|Proofs\.Flock\.Soundness\.Game\.|Proofs\.Flock\.Soundness\.Audit\.)`. With those values the test passes
  at head (I emulated it: 25 files, the 7 Flock instantiations present, no stray import, nothing admitted).
- **F2.** The same file: `test_merkle_collision_is_not_met_by_a_split_string` and `test_merkle_extractor_computes_a_collision`
  run `lake build FlockProofs` in the verifier package. Lake answers `error: unknown target FlockProofs` at head (probed), and
  `check=True` raises before either assertion. Build `Proofs.Flock.Verifier` and run `lake env lean` in `verity/Security/Proofs`
  instead.
  - The split-string test is a negative (`returncode != 0`). If it were changed to keep running in the verifier package with
    `import Proofs.Flock.Verifier`, the failing import would make it pass vacuously. It has to run where the module resolves.

## Checks that pass at `b37b16723`

- **Check 1, statements.** All 1754 guarantees are identical by name, signature, assumptions and type hash; the focus
  statements digest is `32027e06…` at base and head. Owners didn't change. `lean_moves.json` is the empty map.
  - The record's `reads` keep one hash for 10 `Flock.*` definitions whose per-lock hashes differed at base. `Flock` is in
    `reads_exempt` in every lock (Daniel, 4 Oct), and the `Flock/` sources are byte-identical base→head, so these are
    rehashes, not definition changes.
  - The `--update --moved` printout is not yet seen; I check it on the final head.
- **Check 2, ArkLib cuts: OPEN.** `Defs.lean` still imports `ArkLib…CapacityBounds`, and `ZkSession/Inner.lean` is unsplit
  (still imports ArkLib BCIKS20 and VCVio). Until the cuts land, the baseline: all 30 + 42 declarations of the two files are at
  head under the same names, in the same file, with the same text and context (`decls.py`).
- **The move changes only imports.** Of 1131 `.lean` files in the diff, 21 change beyond `import` lines, and all of those are
  doc comments: regenerated umbrellas keep their module docs, and `assumptions/` became `assumption-notes/` in 6 files. This
  includes the compile-time module `Refine/Walk.lean` (one import line). Its recorded digest (`c86a84bed…`) is the old file's,
  so the audit refuses until `--update` re-records it (fail-closed).
- **Check 3, executable.** `Main.lean` → `FlockVerify.lean` is an R100 rename. `Flock/`, `Flock.lean` and `FlockRows.lean` are
  unchanged. The `flock-verify` exe now has `root = "FlockVerify"`, and its binary path is unchanged.
  - `agreement_closure` excludes `verity/Security/` (`test_check.py` asserts it), and its key moves with the lakefile, so
    lean-agreement can't reuse a stale pass.
  - No stale `Main`, `FlockProofs`, `soundness/` or `level3/` path remains in `.py`, `.sh`, `.rs`, `.toml`, `.json` or `.lean`
    string literals, apart from F1/F2, doc comments, and namespace names the move keeps.
  - The agreement run itself is pending: I compare its counts with r20261005-081515-2188 when the move lead's `check` exists.
- **Check 4, gates.**
  - `lean_audit.packages()` finds 4 audited packages, and shard 1 (`lean-audit:verity/Security`,
    `lean-audit:verity/Security/Proofs`) selects exactly the security two. `select` raises on a shard name that's gone.
  - Every Lake package has a `lean-audit.json`. The `.lean` files no audited package owns are the same 5 test-vector files as
    at base.
  - `tests/test_lean_packages.py` replaces the core/protocol rules with the security-package rules, and each asserts its
    package exists, so none can pass vacuously.
  - The suites that read `verity/Security` get it through their dependency on the `verity` distribution (`verity/`), so the
    read guard allows them.
  - `lean-agreement`'s `merge_requires` no longer triggers on the proofs. Proofs can't change `flock-verify`
    (`agreement_closure`), so nothing is lost.
- **Fixtures.** The randomness fixture's 8 recorded input hashes match head. They were re-recorded by hand, not regenerated,
  which is sound here: `Randomness.lean` is byte-identical, `PlanDraw.lean` changes only its imports, and the Proofs
  manifest pins every git dependency at soundness's revisions (only the path packages differ).
- **Check 5, PoUS grader (`6447d4723`).** `TRUSTED.sha256` hashes the security packages' lakefiles and manifests,
  `Definitions/Pous`, `Specs/Pous` and the two allowed `Proofs.Pous` modules. The sandbox probes `verity/Security` as
  read-only, and the grader's `setMaxMemory` escape is now listed (the grader was exempt before). Nothing here fails open.

## Observations (not blocking)

- C-Flock's assumptions module goes to `Proofs.Flock.Soundness.Assumptions`, inside the proofs package, not to `Specs/` as
  the ruling's layout has it. The hypothesis check (`audit.py:607`, by module) still holds, but the assumptions stay in
  untrusted, ArkLib-reaching text. Say so in the PR, or move them.
- The merged lock's `assumptions` lists every area's modules, so a new guarantee in one area could take another area's
  named assumption. Existing records are unaffected.
- `test_lean_verifier.sources()` no longer scans the verifier's proofs and level3 for
  `native_decide|implemented_by|extern|unsafe`, since they moved out of `LEAN`. The audit covers that in `security_proofs`.

## Left for the final head

- Rerun `rerun.sh` on the fixed head.
- The ArkLib cuts: byte-identical definitions, or a reference with its equivalence proved; no assumption added or lost;
  `#print axioms` stays propext / Classical.choice / Quot.sound.
- The `--update --moved` printout.
- The `check` run:
  - the audit visits all 4 packages;
  - lean-agreement has every session agreeing at the reference counts (r20261005-081515-2188: 17 sets, 564 sessions, 564
    agree, 0 disagree, Lean accepts 12: sets 8:4, 10:3, 11:1, 12:1, 15:3). `agreement_cmp.py` checks this.
- #1193's module-root guard, now on this branch: `test_lean_module_roots_are_disjoint` passes on `b37b16723`'s packages
  (14 claims, no clash; `security` and `security_proofs` share `verity/Security` with different first components).

## Rerun at `77b8d66bc` (19:35Z): REFUSE

**Verdict: REFUSE for PR #1225 at `77b8d66bc7e8ded3481bd2513afe005d395935ae`.** B1, B2, F1 and F2 are fixed, the two
ArkLib cuts are in and declaration-identical, the verifier's and grader's lock updates are moves, and 815ac27cd's replay
change is sound. Two new findings block. B3: Security's reads check can't see the verifier's code, and 77b8d66bc drops
the `Flock` exemption because of that, not because nothing reads it. B4: Security's lock at this head doesn't match its
build, and the update that will replace it has 46 hash changes, of which only two are explained.

- Evidence: `art:4019f782c3b688f314c399e28d7e8c3d0bf44932152f2d0126a4afaf21776142` (`tools/`, the rerun's outputs in
  `out-77b8d66bc7e8/`, and in `pod-runs/` the stdout of vy-mig-check-8's audits r20261005-174419-76c1 at `64dc27dfa`,
  r20261005-180406-63e4 at `1b6514c81` with its `review.txt` and rewritten Security lock, and r20261005-185517-6282 at this
  head, which is still running).
- To rerun: `bash rerun.sh HEAD`, then `python3 reads_home.py /tmp/rt-lean-head` (B3), then
  `python3 pending.py /tmp/rt-lean-base /tmp/rt-lean-head REWRITTEN_LOCK` (B4). REWRITTEN_LOCK is the lock the Security
  audit wrote under `lean-audit/audit-verity_Security/`.

### Blocking

3. **B3: Security's reads check doesn't see the verifier's code, so it fails open.**
   - `spec_reads` skips any module that isn't in `home` and treats it as a pinned dependency's (`audit.py:708`).
   - Security's `home` (`audit()`, lines 1202 to 1205) holds Security's own modules and its prover's (`Proofs.*`) modules.
     Security requires nothing by path, and the loop over provers adds only `lean_modules(q)`, not the prover's path
     dependencies. So `Flock.*` isn't in it.
   - At base, soundness and level3 required `flock_verifier` by path, so `Flock.*` was in their `home` and their
     `reads_exempt: Flock` ("C-Flock is excepted until proofs extracts its spec", Daniel, 4 Oct 1:30 PM PDT) was used.
   - At `1b6514c81`, Security's audit failed with "``reads_exempt`` lists Flock, under which no guarantee reads outside the
     spec; remove the entry" (180406-63e4, line 724). 77b8d66bc removed the entry.
   - Its commit message ("no guarantee under Security reads [Flock] now") is wrong. Security's lock records 43 `Flock.*`
     read modules: 376 guarantees read `Flock.Bytes`, 446 read `Flock.Field`. Their contents are still pinned (`Flock` is
     under `meaning`), but the spec rule no longer applies to them.
   - `reads_home.py` runs the tree's own `home` code with a fake guarantee that reads `Flock.Bytes` and no exemption. The
     check passes it.
   - Fix:
     - In `audit()`, replace the prover loop's body with
       `for m, spec in (homes(q, {}) if q.is_dir() else {}).items(): home.setdefault(m, spec)`. The prover's own modules
       keep `[]`, and its path dependencies get their specs. The verifier has no `layers`, so its spec is `[]`.
     - Revert 77b8d66bc.
     - Add a test in `tools/lean/tests/test_audit.py`: a `proved_in` package's guarantee that reads a module of its prover's
       path dependency outside that dependency's spec fails, unless an exemption covers it.
   - Simulated on the head's recorded reads: with the fix and no entry, all 43 `Flock.*` read modules fail the spec rule;
     with the entry restored, they pass and the entry counts as used. `reads_home.py` passes on a patched copy.
   - 77b8d66bc is also an instance of B2's residual: it changes how C-Flock's guarantees are checked, in
     `verity/Security/lean-audit.json`, and no red-team grant was needed.

4. **B4: Security's lock at this head doesn't match its build, and the replacement isn't shown to be a move.**
   - At `1b6514c81`, 180406-63e4 rewrote Security's lock. 77b8d66bc carries only the one-line exemption drop. So
     Security's audit fails on this head, which fails closed. 185517-6282 is `--update` on this head and will rewrite it
     again, which forces a new head.
   - What the update changes, compared with every base lock (`pending.py`):
     - **7 guarantees' `type_hash`:**
       - The 7 are `FlockLevel3.pinned_indep`, `FlockLevel3.unpack_add`, `Aliased.zeroPos_block`, `Layout.gateAt_one`,
         `Layout.gateAt_zero`, `Zero.Prog.zeroCols_singleton` and `Zero.accepted_zero_block`. Each prints the same before
         and after.
       - For the first two, the move lead's probes (184418-9035 and 184438-c1fe) show the cause. The type names
         `FlockLevel3.instFactPrimeOfNatNat_proofs`, which was `..._flockLevel3`: the anonymous
         `instance : Fact (Nat.Prime 2)` in `Proofs/Flock/Level3/GF128Ring.lean`, which Lean names from the module root.
         It is a proof, so the statement is the same, and that is a move.
       - The other five aren't explained.
     - **62 read definitions:**
       - 23 take a hash that some base lock already recorded. Base locks disagreed on these (`Flock.F128`, for example),
         and they include the 17 PoUS reads (`Pous.Digest.*`, `Pous.Erase*`, `Pous.Guarantees.SecureErasure*`) that the
         merged lock had dropped.
       - **39 match no base record**, although none of their source files changed beyond imports (`leandiff`).
       - `tools/move/lean_moves.json` is empty (the move renamed no declaration), so `--moved` maps nothing. Every one of
         these is Lean producing a different term.
       - The likely cause is a generated proof name derived from the module, like that `Fact` instance. That can't
         explain `Proofs.Flock.Soundness.Defs`'s `Model.Arith.Correct` and `RepDoomedW`: they are generic over
         `[Field F]`, and that file's imports went from ArkLib to Mathlib in the cut. So a different instance path is
         possible there.
       - `Specs.Pous.Guarantees`' four `Band*Meets14*` can't use the `Fact` instance either.
       - `review.txt` names these definitions without their texts, so a reviewer can't tell.
     - Also in the update: the `Proofs.Flock.Soundness.Refine.Walk` compile-time digest (C1), and the proofs package's
       Mathlib and ArkLib dependency digests.
   - What clears it on the next head:
     - A canon or raw-type diff, before and after, of the 7 guarantees and the 39 definitions, as 184418-9035 did for two.
       Each difference has to be a generated proof name or an instance path between definitionally equal instances.
     - A named statement reviewer.
     - Better still, `--update` printing each changed definition's text before and after, which makes the probe
       unnecessary.

### Open (blocks a grant; not a finding)

- **lean-agreement.** No `check` has run on this head; 185517-6282 is `audit.py --update`, still building `Proofs`. The
  PR touches `backends/flock/`, so the landing `check` needs lean-agreement. Run `agreement_cmp.py` on its log against
  r20261005-081515-2188.

### Passed at `77b8d66bc`

- **B1.** The proofs lock scans `Arklib`, with 16 watch entries, and `64dc27dfa` tests that every upstream-watching lock
  scans a package.
- **B2.** The grant covers `verity/Security/Proofs/Flock/` and `Flock.lean`, with a test; 0 of 605 Flock files are
  uncovered.
- **F1, F2.** `AUDIT` is `Proofs/Flock/Soundness/Audit`, and the import regex matches. The tests build only `Flock` in the
  verifier.
- **The cuts.**
  - `Proofs.Flock.Soundness.Defs` imports no ArkLib (it imports `Polynomial.Degree.Defs`, `Polynomial.Eval.Defs` and
    `CharP.Defs`), and its 30 declarations have the same text.
  - Base `Inner.lean`'s 42 declarations are now 20 in `ZkSession/Inner.lean` (no ArkLib) and 22 in `InnerSound.lean`
    (BCIKS20, VCVio), all with the same text.
  - The three files newly in `leandiff` are these two and `Replay.lean`.
  - The committed records keep all 1754 guarantees the same. The build's differences are B4.
- **The verifier's and grader's printouts** (174419-76c1, committed in `1b6514c81`).
  - The verifier's 7 code guarantees have identical records: signature, assumptions, `type_hash` and owner `@proofs`.
  - Its 26 "gone" lines are module groups shrinking. All 135 definitions the verifier's lock no longer lists are in
    Security's lock with the same hash, under one of the 18 guarantees that moved (with the module renamed, `FlockProofs`
    to `Proofs.Flock.Verifier`).
  - The `Flock` sources are byte-identical.
  - The grader has 0 guarantees and passes.
- **815ac27cd (`Replay.lean`): sound.**
  - **What passes.** A replayed constant that an outside import also declares is dropped only when both are theorems with
    `a.type == b.type` and `a.levelParams == b.levelParams`. Every other kind pair (definition, opaque, axiom, inductive,
    constructor, recursor, or a mix) is still refused.
  - **How "one statement" is compared.** `Expr ==` is `Expr.eqv`: alpha-equivalence over the full type, universe levels
    included, ignoring only binder annotations, which the kernel ignores too. Universe parameters are compared as the
    list of names, in order.
  - **Whether the import's version was checked.** This replay doesn't check it: `importModules` adds it unchecked, as it
    adds every constant from outside the set. It was kernel-checked when its module was built, and the verifier's own
    replay checks it if it is the verifier's (that passed in 185517-6282).
  - **Why swapping the body changes nothing.** The v4.34.0 kernel refuses a theorem whose type isn't a `Prop`
    (`thmTypeIsNotProp`). So both versions prove the same proposition, and proof irrelevance means no dependent's
    judgment depends on which body stands.
  - **An axiom behind the import's version.** The axiom walk goes through the import's body whenever a replayed constant
    names it. Any difference from the `.olean`-recorded axioms fails the audit, in either direction, and the axiom check
    refuses a disallowed one.
  - Non-blocking suggestions:
    - Limit the exception to equation-lemma names (`.eq_<n>`, `.eq_def`), or refuse it when the shared name is pinned.
    - List the names the import stood for in `replay.json`.
    - Add audit controls for "same name, different statement" and "a definition shared with an import".
