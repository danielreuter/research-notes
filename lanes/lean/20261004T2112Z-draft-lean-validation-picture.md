---
id: lean/20261004T2112Z-draft-lean-validation-picture
campaign: lean
lane: lean
kind: draft
status: open
repo: danielreuter/verity
origin: bc-19c498a8-628e-5c04-8f61-fe785a24741b
---

# How Lean works in Verity: my current picture (4 Oct, 18:10Z)

This is @lean's full current picture for top and Daniel. It builds on §4.4 of `docs/claude-architecture-context.md`
(Daniel's names, 3 Oct 23:39Z) and corrects that section where today's layout discussion and #1053 have moved things on.
Nothing here has moved in the repository yet.

## Names

| Today in code | Name | What it is |
|---|---|---|
| the Lean audit, `tools/lean/audit.py` (with `Facts.lean`, `Replay.lean`) | **validation**, done by **the validator** | the machine check that a commit's math proves its specs' guarantees, from the allowed axioms only, with every declaration replayed through the kernel |
| `lean-audit.json` and its records | **the spec lock** | one entry per recorded guarantee: its statement, its named assumptions, and a digest of every definition it reads |
| pinned theorem or statement (#1059 is renaming "pins" to "guarantees" now) | **guarantee** | a `def G : Prop` in a spec: named assumptions imply a conclusion about the protocol |
| `Protocol`, `Assumptions`, `Guarantees` | **the spec** | everything a reader has to trust about a protocol's security, written in Lean |
| `SecurityProofs`, and every lemma under it | **the math** | untrusted; a machine checks it and nobody reviews it |
| `check` | **validate** (Daniel) | the repository's one merge check; Lean validation is one of its jobs |
| statement reviewer, grants | **retired** (#1053) | a changed guarantee waits on nobody: when it lands, Daniel gets a DM showing it |
| "audit" | kept for the **developer–auditor protocol** only | the Glossary's meaning |

There's one naming hazard. If `check` becomes `validate`, then "validation" names both the whole merge check and its
Lean job. I'd keep **validation** for the whole check, call the Lean job **`lean-validate`** (owned by @lean in
`ci.toml`), and call the program **the validator**.

## The life of a guarantee, from written to believed

1. **Written.** An author writes `def G : Prop` in the spec, beside the Python it states (under `verity/`). G mentions
   only the protocol's definitions, named assumptions (each a `Prop` in `Assumptions`, taken as a hypothesis) and
   public parameters. Census numbers are always parameters, never constants in a spec.
2. **Proved.** The math lives outside `verity/`, in `security_proofs/`: bulk lemmas by subject, plus one assembly file
   per guarantee holding `theorem … : G`. The validator binds a proof to its guarantee by type (the theorem's type is
   exactly the constant `G`), not by name.
3. **Developed.** This happens on the author's machine, which is untrusted and decides nothing. They use main's build
   cache (every file sha256-checked), `lake env lean` on one file, and a local `validate --changed` that judges only
   the packages they changed.
4. **Locked.** `--update` writes G's entry in the spec lock beside the spec, and prints what changed: each changed
   statement before and after, and each changed definition as it is now. A pure rename (`--moved`) is not a change,
   because the comparison happens under the old names.
5. **Validated.** The merge check, on a hardened machine, validates the exact commit:
   - build from source;
   - for each guarantee in the lock, check that the math proves exactly the locked statement (type and digest match),
     using only `propext`, `Classical.choice` and `Quot.sound`;
   - reject `sorry`, declared axioms, `native_decide`, kernel bypasses, code run while compiling, orphan files and
     unchecked dependencies;
   - replay every declaration of the package through the kernel;
   - record a verdict per guarantee for that commit.
6. **Merged.** The merge gate reads only the evidence store: a passing validation of that exact commit.
7. **Shown.** When a lock entry changes on `main`, Daniel gets a DM with the printout (#1053, `spec_alert`). It's review
   after the fact and revertable, and it blocks nothing. Renames will arrive as one summary line (point 4; not built yet,
   and needed before the directory move).
8. **Believed.** "G is validated at commit C" means two things: C's validation passed, and G's lock entry has digest D. A
   table, ledger or PR cites (G, D, C), never a lemma. Two things keep the belief current:
   - the upstream watch flags when a pinned dependency proves something we only assume;
   - differential tests tie the Python to the spec's definitions, through vectors that both sides check.

## What a belief in G trusts

There are two trusted computing bases. Only the first is a directory.

- **Runtime TCB, `verity/`:** the code a verifier runs, whose bugs can break a claim. That means the primitives and
  protocols (Python), their specs, the verifier's own fast path, kernels both sides use, and C-Flock's Lean executable
  verifier. The verifier is a dependency-free Lake package of its own inside `verity/`, and the spec package requires
  it, since C-Flock's soundness statement reads its definitions.
- **Assurance TCB, a short list, not a directory:** what makes us believe that "G is proved". That means the spec text
  (read by people), Lean's kernel and the pinned toolchain, the validator (`audit.py`, `Facts.lean`, `Replay.lean`; later
  Lean's comparator), the integration machine, and the pinned dependencies insofar as specs read their definitions
  (Mathlib's `ℝ` and `Finset`).

Top's open question was whether the validator belongs in `verity/`. **No.** No verifier imports it and nothing ships it,
so putting it in `verity/` would make the protocol package depend on Lean tooling. It is trusted all the same: list it
as the assurance TCB, with a named owner, kept small, and with its own tests (`tools/lean/tests`, the controls).
`check`, the trains and the merge gate are orchestration. They're trusted only to run the validator and refuse without
it, and they fail closed (#990).

## Packages and caching

- **Split Lake packages only where the `require`s differ:**
  - C-Flock's executable verifier (no dependencies);
  - the specs (Mathlib, plus that verifier);
  - `security_proofs` (Mathlib; ArkLib too, unless its bump cadence fights Mathlib's).
- **The unit of import, build and cache is the module.** Use `lake shake` (with a `noshake.json` of exceptions for
  instances, notation and macros), exact imports with no umbrellas, and one assembly file per guarantee.
- **Validation must become per-module before `security_proofs` is consolidated.** Today every package is audited from a
  hermetic cold build: lean-audit took 4155 s in today's b201 train, the critical path of a 6715 s check. The order:
  1. main's build cache (#1006), hash-checked, written only by main's check;
  2. Lake's incremental rebuild;
  3. a per-module kernel replay, cached under the module's `.olean` hash. This is sound because the replay re-checks
     whatever a restored `.olean` claims, and a lock entry shows the statement the `.olean` holds;
  4. a guarantee's lock entry recomputed only when its closure changed (#1098 computes closures once).
  The cache key is our own hash of the source, the imports' keys, the toolchain, the lakefile options and the validator.
  It is never read from a restored `.trace` file.
- **Lakefile options are package-wide,** so freeze them. Per-file options go in the file as `set_option` lines.
- **Without umbrella modules,** the orphan check compares tracked files against the lean_lib's `globs`.

## Corrections to the 3 Oct design

- **Spec review is gone** (#1053, Daniel's ruling). The DM replaces it, so "a person approved digest D" drops out of
  "validated".
- **The spec lock keeps one entry per guarantee,** not one digest per spec. Per-guarantee entries are what let review be
  tiered by what's cited: only cited guarantees get an entry, so an experimental construction's spec changes freely and
  sends no DM until something cited reads it. They also let a DM show exactly which statements changed. That supports
  top's "each claim trusts only what it reads".
- **"No `lean-audit.json` changes in the move" no longer holds** once module names follow paths. Every namespace
  changes, so every entry changes, which is about 1,000 entries. Two things must land before the move:
  - the rename handling in `spec_alert` (mine);
  - one protocol at a time, starting with the warden, with each protocol's entries swept down to what's cited.
    PoUW alone has 793 entries today.

## Where today's code stands against this

| Piece | Today | Gap |
|---|---|---|
| Validator | `audit.py`: lints, per-guarantee records, kernel replay, upstream watch, runs | comparator challenge; per-module mode; its own result kind |
| Sandbox | `unshare` where available | node 1 builds **without a sandbox** ("built WITHOUT a sandbox (unshare unavailable here)", r20261004-161500-f1f5), and node 1's jobs run as a user with passwordless sudo |
| Spec lock | `lean-audit.json` | the name; per-guarantee entries stay |
| DM on change | on `main` (#1053) | renames as one line |
| Build cache | #1006 open (client, publisher, setup restore) | the kill switch (console), and landing it |
| Speed | #1038 and #1047 on `main` (c05f14179) | #1079 (the audit gets its own group: about 40 min off b201's check), #1098 (facts −43% CPU), per-module validation |
| Lean's half of the CI job API | `ci.toml` (#1095) lists lean-audit and lean-changed as @lean's; #1085 moves Lean's job code to `tools/lean` | land them; rename the job to `lean-validate` with the rest of the renames |
| Mathlib's `.olean` files | digest-pinned against the record, not replayed | replaying them is possible but costly; today they're trusted as pinned |
