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
