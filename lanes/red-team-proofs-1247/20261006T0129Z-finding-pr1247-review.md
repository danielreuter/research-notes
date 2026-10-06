---
id: red-team-proofs-1247/20261006T0129Z-finding-pr1247-review
campaign: proofs
lane: red-team-proofs-1247
kind: finding
status: final
repo: verity
origin: pr:1247@2043597b88ddadd667caf22b82728bc99a5f5730
---
# Red team, PR #1247 (Lean audit: fail on anonymous instances; `--name-instances`): GRANT

Reviewed 6:29 PM PDT, 5 Oct, by red-team-proofs-1247 (agent bc-9212d2ec-44e0-532d-b287-841c80eef616) for the proofs
coordinator. I reviewed head `2043597b88ddadd667caf22b82728bc99a5f5730` of `cursor/lean-name-instances-741b` (base `main`
`7b410fbf6`) in a separate worktree. I ran no Lean build. I ran one Python checker over the diff, preserved with its logs as
`art:6172111c44294f085361bdb0ba5abde66ec5ac9fc7fd573f4accbef7d9de2222`. I also ran the PR's no-Lean unit test (2 passed).

**Verdict: GRANT.** Every changed line under the red-team paths only adds a name after `instance`, and each name is the
one Lean had already given that instance. The author's build and replay audited exactly these files and passed. The audit
tool only gains a failure. Nothing changes what C-Flock proves or what its verifier does.

## 1. Every hunk under the red-team paths is a pure naming

`naming_check.py` pairs each removed and added line of every `-U0` hunk. A pair passes only when the added line is the
removed line with one token inserted right after the first `instance` keyword (or after `instance (priority := …)`). The
token must start with `inst`, and the removed line must have had no name there. The script then deletes the inserted
names from the head file and compares the result with the base file byte for byte.

- Red-team paths (`backends/flock/`, `verity/Security/Proofs/Flock/`, `verity/Security/Proofs/Flock.lean`): 28 `.lean`
  files, 36 hunks, 50 named lines, **0 non-naming hunks**, no non-Lean file. 13 names are in
  `backends/flock/verifier/lean` (6 files) and 37 in `Proofs/Flock` (4 in Level3, 18 in Soundness). 46 lines are plain
  `instance`, 4 are `noncomputable instance`. None has a priority or an attribute, and none is private or local.
- All 42 Lean source files: 84 named lines, 0 non-naming. That is 13 in the verifier, 9 in `verity/Security/Definitions`
  and 62 in `verity/Security/Proofs`, as the PR says. The only other changed `.lean` file is the tool's `tools/lean/Facts.lean`.
- My first pass flagged `Audit/FlockLink.lean:153` and `Discharge/ZkLink/Link.lean:155`, but only because my identifier
  regex rejected `Ω`. With the regex fixed they pass as `instFintypeΩc` and `instFintypeΩcZ`.

## 2. The names are Lean's own, and the run audited an equivalent tree

- **By construction.** The naming pass's report (`name-audit.json`, `named_instances`) lists the 84 full names that
  `Facts.lean` read from the elaborated environment of the build before naming. They equal the PR's names by file, line
  and last component (84 = 84, no difference either way). 37 of the 84 already appear by full name as keys in the base
  `lean-audit.json` files (33 of the 50 Flock names, e.g. `Flock.F128.instAdd`, `Flock.CircuitType.instDecidableWellFormed`,
  `FlockSoundness.Game.instMonad`).
- **Against Lean's scheme.** I read `Lean/Elab/DeclNameGen.lean` in the pinned v4.34.0 toolchain and checked 12 names by
  hand. Each checked name followed the scheme:
  - A constant that is a prefix of the current namespace is pre-seeded as already seen, so it's dropped:
    `Flock.F128.instAdd`, `Flock.HmNets.Lin.instHXor`, `Flock.Program.Ty.instBEq`, and `FlockSoundness.Game.instLawfulMonad`
    (versus `FlockSoundness.Refine.instLawfulMonadGame`).
  - A numeric literal is spelled `OfNatNat`, and `mkUnusedBaseName` adds `_1` to the second one:
    `Flock.F128.instOfNatOfNatNat` and `…_1`, `FlockLevel3.instCharPGF256OfNatNat`.
  - Explicit binders the conclusion depends on are dropped: `Flock.Transcript.instDecidableAnswers`,
    `Flock.CircuitType.instDecidableWellFormed`.
  - Instance-implicit binders the conclusion doesn't use become `Of…`, and a repeated one is omitted:
    `FlockSoundness.ZK.GK.instDecidableConflictOfDecidableEq`.
  - `DecidablePred` spells out its type-former argument: `…Layout.instDecidablePredBitValRowShaped`,
    `…Zero.instDecidablePredNatZeroIn`.
  - A projection keeps its field name: `…Audit.Partition.instFintypeΩc`.
- **The run.** `r20261005-233335-bff5` (vy-nebius-1, rc 0) ran at source `3b13c61b`, the PR's first commit. `job.json`
  records `source.tree f28b71e7…` (equal to `3b13c61b^{tree}`), not dirty, verified `git-push+tree+file-sha256`. It ran
  `audit.py --build --name-instances --no-replay --no-runs`, then `audit.py --build --no-runs` with replay, which is the
  default.
  - The run's `names.patch` is byte-identical to the naming commit's Lean diff (`207726422..2043597b8`), ignoring the
    `index` lines. The `main` merge between them changed no `.lean` file, no lakefile, manifest or toolchain, and nothing
    under `tools/lean/`.
  - So under the red-team paths, the head is byte for byte the tree the second audit read. The head differs from that tree
    in only two non-Lean files from `main` (see finding 1).
  - The second audit passed all four packages, each with a `replay` time: flock 5.6 s, PoUS 6.8 s, Security 10.2 s and
    Proofs 331.3 s. It read the renamed build: from stale pre-naming `.olean` files, the new check would still have found
    the keyword `instance` at each old position and failed.
  - The run's `locks.sha256` equals the `lean-audit.json` hashes at `3b13c61b` for all four packages. At the head they are
    the same for three; see finding 2 for the fourth.

## 3. The executable verifier's behaviour is unchanged

The verifier's 13 instances are in `CircuitType.lean:218`, `Field.lean:19-21,52,119-122`, `HmNets.lean:68`,
`Layout.lean:375`, `Program.lean:67` and `Transcript.lean:69`.

- Each written name is the full name the instance already had, so no new collision is possible, and the build passing
  rules out an "already declared" error anyway. Their priorities, attributes and line positions are unchanged, so
  resolution order is unchanged too.
- No `open`, `export`, `attribute [-instance]` or `attribute [local instance]` anywhere in the red-team paths names a
  renamed instance. The `attribute [instance]` lines in `Proofs/Flock` name structure fields such as `ValueBinding.finPos`.
- The 4 `deriving instance DecidableEq for …` commands at `HmNets.lean:441-444` were neither flagged nor rewritten.
- The flock lock's 3 `reads` entries for these instances are unchanged, and the head's flock lock equals the base's.

## 4. The audit tool change doesn't weaken the audit

- **`audit.py`.** The only change inside `audit()` is `fails += [instance failures]`. With `name=True` it clears just the
  list of anonymous instances it has written, and none of the existing checks: the axiom allowlist (which catches `sorry`
  as `sorryAx` and `native_decide` as its compiler-trust axioms), declared axioms, escapes (`implemented_by`, `extern`,
  opaque, unsafe), replay, `--fresh`, dependency records, guarantee and reads comparison (`changed`, `read changed`,
  failing), listings, upstream, or runs.
- **`Facts.lean`.** The addition is a self-contained `if let … then` that pushes to a new `instances` array and writes a new
  JSON key. Nothing else in the loop changes.
- **`--name-instances` can't run inside a normal audit.** It is an opt-in flag (`name=False` by default). `check`'s
  lean-audit step calls `audit.py` with fixed `FLAGS = ["--build"]` plus `--repo`/`--out`, on a scratch tree
  (`tools/lean/lean_audit.py:136,634`). The controls call `audit()` without `name`, and no other code in the tree passes it.
  Because `tools/lean/` is in that step's key, the merge's `check` re-audits every package at the head.
- **`lean-audit.json` is written only under `--update`** (`dump`, `audit.py:1333-1349`).

## 5. Anything else in the 48 files

Outside the red-team paths: the 34 other names (Definitions, PoUS, PoUW and warden proofs) pass the same check.

- PoUS's `TRUSTED.sha256` changes only for `Definitions/Pous/Model/{Continuous,Invertible,Scheme}.lean`, and
  `sha256sum -c` passes all 49 entries at the head.
- The tests add a no-Lean unit test (detection skips prose containing `instance :`, and the name is placed after a
  priority) and a real-build round trip. The control violation `anonymous_instance` is added too.
- `tools/lean/README.md` documents the check and the flag.

None of this touches C-Flock.

## Findings

1. **Non-blocking: the evidence was taken at an equivalent tree, not at the head.** The run audited `3b13c61b` plus
   `names.patch`. The head adds two non-Lean files from `main`: two run `generate` paths in
   `verity/Security/Proofs/lean-audit.json` (`../../protocols/…` → `{repo}/verity/protocols/…`), and PoUS's `BandChain.lean`
   hash in `TRUSTED.sha256`. The run used `--no-runs`, so the Proofs package's two runs (PoUW FP8 and warden vectors, not
   Flock) weren't exercised. The merge's `check` covers both, and it can't hit its cache since `tools/lean/` changed. The
   evidence builds were also unsandboxed (`unshare` isn't available on vy-nebius-1), which doesn't matter for a pure-naming
   diff.
2. **Non-blocking (wording): "byte-identical locks" holds by construction.** `audit.py` without `--update` never writes
   `lean-audit.json`, so `locks.sha256` couldn't have differed. The evidence that no record changed is the second audit's
   PASS, which compares every guarantee's record and reads.
3. **Non-blocking (tool ergonomics): a naming pass can report PASS for a package it has just rewritten.** In the run's first
   pass, flock reports `PASS` after its sources were rewritten, and a one-package `--name-instances` run would exit 0. I'd
   accept a failure such as "named N instances; rebuild and audit again" for any package it wrote, so the pass's exit status
   can't be read as a pass of the rewritten tree. Separately, `--all --name-instances` is accepted while `--all --update` is
   refused. No gate passes the flag, so neither affects soundness.
4. **Non-blocking (merge reminder): the PR touches `backends/flock/`.** Its `check` needs `lean-agreement`, so record it
   with `check.py --record --on POD`.
5. **Non-blocking (process): the new `instance` check is a new failure in `check` for every Lean lane.** Open branches that
   add anonymous instances need `audit.py --name-instances` when they rebase. The PR body already orders the rebases of the
   mixed-file splits and `cursor/flock-specs-95d4` onto it.

No blocking findings.
