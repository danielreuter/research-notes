---
id: lean/20261006T0009Z-draft-consolidation
campaign: lean
lane: lean
kind: draft
status: open
repo: danielreuter/verity
origin: bc-19c498a8-628e-5c04-8f61-fe785a24741b
---

# Lean tooling consolidation (after the layout move, at fc6d04815)

This covers `tools/lean/`, the parts of `tools/check/` that touch Lean (`lean_changed`, `lean_slot`, check's Lean steps),
`research jobs`' `lean-regen` key, `spec_alert`, `tools/move/lean.py` and `tests/test_lean_packages.py`. A survey agent
read the tree, and I re-checked every item marked **verified**. Each item gives what to change, which copy survives,
value against risk, and whose code it touches.

## Done while writing this note

1. **The `lean-regen` dedupe key missed `proved_in` and any path dependency more than one level down** (bug, verified,
   #1255). `research.jobs.cli.lean_inputs` never read `proved_in`. After the move, `verity/Security` is audited from
   the nested `Proofs` build, which requires the flock verifier. A change to `Proofs` or to the verifier alone left the
   key unchanged, so a second `lean-regen` would be answered with a stale regeneration. The key covered 258 inputs,
   against 1186 for `lean_audit.inputs`. Now the package files are equal for Security, the verifier and PoUS. The PR has
   a test that fails on the old code. Owner: @infra's file, fixed under the 09-30 `tools/research` ruling.
2. **`tests/test_lean_packages.py` defined `_module_roots` and `test_lean_module_roots_are_disjoint` twice**
   (verified: byte-identical, a merge artifact of the move). One copy is deleted in #1254. Owner: @lean.

## Ranked changes still to make

| # | change | value | risk | touches |
|---|---|---|---|---|
| 1 | Pass `runner` and `tool` into `audit.facts_of` and `proved`, instead of `lean_changed.records` swapping `AUDIT.run` and `AUDIT.TOOL` in a try/finally (`audit.main` also rebinds `global TOOL`). Make `audit()` keyword-only after `out`; only `main.one` passes four booleans positionally. | high | low | @lean |
| 2 | Retire the `pins` and 32-bit hash conversion: `OLD`, `as_guarantees`, the `old=` paths of `digest` and `read_groups`, `old_group`, the `REHASHED` and `REGROUPED` review branches, the legacy branches of `listings` and `definitions`, `merge.group`'s width check, `spec_alert`'s fallbacks, `price_twins.py:206`, `move/lean.py`'s conversion, and the tests of these paths. No lock in the tree carries `pins` (verified, all 5). The last one left with the move, and the last 16-hex hash on 09-30. Keep a one-line refusal (`pins: rebase onto main`) for an un-rebased branch. Rename `Facts.lean`'s live `facts["pins"]` key to `guarantees` and drop its 32-bit `hash`/`type_hash` in the same PR: that changes the facts output, so the fast path's records rebuild once. Several hundred lines go. | high | low-medium (an old branch now gets a refusal, not a silent conversion) | @lean (bulk); @infra (`spec_alert`); compute-accounting (`price_twins`); move lead (`move/lean.py`): one PR per owner, @lean's first |
| 3 | One `deps_key`. `lean_audit.deps_key` returns `None` for a package that fetches nothing, while `run_daily.deps_key` (whose docstring says it is the same function) always hashes (verified). A no-dependency package (the verifier) gets different keys on the daily side and the check side. The survivor goes in `cache.py`, which is standalone and deployed beside `run_daily`, and `lean_audit` imports it. | medium | low | @lean |
| 4 | Expose `lean_audit.missed(files, cache)` and drop the copies in `check.lean_audit_misses` and `lean_changed.missed`. | medium | low | @lean, @ci |
| 5 | One sandbox probe. `audit.sandboxed` checks `sandbox.sh` and a read-only tool directory; `lean_changed.sandboxed` only runs `unshare -- true`, so the fast path checks less than the audit. Use one function with `extra_ro` (the fast path mounts `.lake/packages` read-only). | medium | low | @lean |
| 6 | Package discovery has five copies. `lean_audit.packages` (tracked `lean-audit.json`) survives. `cache.packages` stays, because it is standalone on node 1, with a new test that it agrees with `lean_audit.packages`. `audit.packages`, `test_lean_packages.lake_packages` and the `rglob` in the upstream-watch test call the survivor. | medium | low | @lean |
| 7 | Path-dependency parsing and the nested-package filter. `lean_audit.path_deps` and `own_files` survive. `audit.module_files` stops re-parsing manifests, and `check.agreement_closure` and `audit.lean_modules` call `own_files`. `jobs/cli` is the one copy that can't import them, because it reads a commit and not the worktree. #1255 brings it level, so the next change to `own_files` should add a test that the two agree. | medium | low | @lean, @ci, @infra |
| 8 | Failures as `(category, detail)`, not strings matched on their prefix. Sites: `controls.beside` (`dependencies:`), `violations.json`, `lean_changed.records` (`guarantees:`), `lean_audit.transient` (`setup:`/`build:`), `statement_changes` (review suffixes). One question to settle first: whether `build-roots:` should count as transient (it doesn't today). The report also gets an explicit `replayed` field, so `check.lean_fast` stops inferring the replay from a timing key. | medium | medium (every consumer of a report changes together) | @lean, @ci |
| 9 | `spec_alert._entries` re-derives what changed with rules of its own: it pairs any removed and added guarantee of equal `type_hash` as a move, and lists lifts. The audit report should carry the classification and `spec_alert` should only render it. This leaves one source of truth for what a statement reviewer is shown. | medium-high | medium | @infra, @lean |
| 10 | Utilities. `sha256` has four copies (`audit.sha256` reads whole files; `lean_audit._sha` duplicates `COMMON.sha256`, which the same module already uses). `cores` exists twice (only `common`'s has the cgroup-v1 fallback). The elan toolchain spelling has three copies and the elan PATH setup four. `strip_comments` and `STANDARD` are in both `audit` and `upstream`. `tools/check/common` survives for check; `cache.py` for what must stay standalone. | low | low | @lean, @ci |
| 11 | About eight module loaders (`_module` and `sibling`, plus inline ones in `merge`, `run_daily`, `upstream` and `check`) each load their own instance of `audit.py`, so its globals aren't shared. That is what makes item 1's monkeypatching fragile; once item 1 lands, this matters less. | medium | medium (import order) | @lean, @ci |
| 12 | `tools/move/lean.py::merge_locks` writes locks with its own `json.dumps(indent=1)` and `ORDER`; switch it to `A.text`, the writer `audit`, `merge` and `upstream --ack` share. Delete `tools/move/lean_moves.json` (`{}`, no reference, verified). Retire `move/lean.py` and `tests/test_lean.py` once the open layout-move branches have landed (on main it is a no-op: "renamed 0"). | low | low | move lead |
| 13 | `lean_changed` calls the private `WarmDeps._lock`; make it public or a context manager. Small tuple returns (`listings`, `proved`, `assign`, `lean_slot.wait`, `cache.state`) become named tuples. | low | low | @lean, @ci |

## Documents that say what isn't so

- `tools/lean/README.md`:
  - line 49 still mentions "soundness's 3,900 imported dependency modules";
  - the `proved_in` example at lines 217 and 223 has the old `security_proofs/` paths and a guarantee without `owner`,
    which the audit would fail;
  - lines 151-153 and 171-173 document `pins` and 32-bit hashes;
  - the command table omits `--no-replay`, `--fresh`, `--no-runs`, `--no-controls` and `--repo`.

  `audit.py`'s docstring also lists checks that don't match the prefixes it emits. Owner @lean: one docs PR, after item
  2, so the `pins` text goes with the code.
- `tools/check/lean_slot.py` says "`audit.py --build`" calls `hold(pool)`, but `audit.py` never imports `lean_slot`
  (verified). The question is whether the docstring or the wiring is wrong. My recommendation is to wire it: a hand-run
  `--build` on a shared pod is exactly what the `audit` pool is for. Owner @ci, with @lean.
- `.agents/skills/lean-proofs/SKILL.md`:
  - its description still says "level3, soundness" and names `verity/Security` twice;
  - its timings ("~3 min", "three packages, about nine minutes") predate the move;
  - its test command misses `tools/check/tests/test_lean_*.py`.

  Owner @lean. Re-measure the timings from the next `check` record instead of guessing.
- The tests of `tools/lean/lean_audit.py` and `lean_changed.py` live in `tools/check/tests/`, and neither README says so.
  Moving them is cheap, but it changes two suites' inputs. Documenting where they are is enough. Owner @lean, @ci.

## Order

Items 1 and 2 first, as @lean PRs on main after the move and after #1247 (whose instance pass touches `audit.audit`).
Then items 3 through 7 together in one PR, because they share callers. Item 8 needs a quiet window, since every
report consumer changes at once. Item 9 is @infra's to schedule. The doc fixes ride with item 2.

## For Daniel

Nothing here changes what "proved" means or what a gate accepts, with one exception: item 9 changes which component
decides what a statement reviewer is shown. That stays a tooling change only if the classification is unchanged. If
@infra wants `spec_alert` to keep listing lifts that the audit certifies as unchanged, that is a question of what the
reviewer sees, and it goes to Daniel. My recommendation: the audit's classification, with lifts listed as lifts (the
README already says the DM lists them).

## Records dropped from a lock

The condition from 23:12Z is that any pinned record an owner drops from a lock gets listed by name in their
consolidation note. No lock has dropped a record in @lean's work this cycle. The instance-naming run
(r20261005-233335-bff5) checks that every lock is byte-identical before and after.
