---
cursor:
  subagentId: "bc-866e1acc-6010-57e8-b0f8-ec01aced68dc"
---

# Lean organization: packages, trust boundary, one audit, lane conventions

**For:** Daniel, the research coordinator and the Lean lanes; §5 is also for POUS. **Written:** Sun Sep 27, 2026, about 12:45 AM PT; **updated** 5:30 AM PT (12:30Z), and 11:15 AM PT (18:15Z) for the upstream watch (§3.8, §4.3). **Status:** the low-regret pieces are implemented in [PR #130](https://github.com/danielreuter/verity/pull/130), and POUS's review of it in [PR #149](https://github.com/danielreuter/verity/pull/149) (CPU only, \$0). §8 has where they stand. Everything structural is a proposal in §7, waiting for your review.

**Grounded in:** `main` at `ae5db5d3` (#110, #114), then at `928790af` after train A ([#100](https://github.com/danielreuter/verity/pull/100): `check` and `research merge`) and [#117](https://github.com/danielreuter/verity/pull/117) (knowledge-soundness groundwork) merged during the night; the open PRs [#112](https://github.com/danielreuter/verity/pull/112) (the coordinator's `audit.sh`) and [#122](https://github.com/danielreuter/verity/pull/122) (the audit layer); the coordinator's audits `r20260927-042257-7cee` and `r20260927-053940-45db`; `soundness/ASSUMPTIONS.md` and `DESIGN.md`; [audit protocols](audit-protocols.md) §4; [circuit privacy](circuit-privacy.md) §I.8; and POUS's design (`internal/lanes/verity-root/20260927T0700Z-handoff-from-pous.md`). Timings and counts from the audit were measured on a 4-core, 15 GB cloud VM.

## Headline

1. **Keep three Lake packages, split by what they depend on,** and put new work in namespaced subdirectories of the package whose dependencies it needs. The executable verifier builds with no dependencies, and one workspace would take that away. One toolchain and one Mathlib revision across the three is now a test.
2. **One audit for every package, in `check`** (`tools/lean/audit.py`, PR #130). It checks every declaration, not a hand-kept list:
   - only the standard axioms: no `sorry`, `axiom` or `native_decide`, and assumptions only as named `Prop`s;
   - compiled-code escapes are listed, and no source file is left unbuilt;
   - kernel-bypass options are refused in sources and lakefiles, and import layers are enforced;
   - pinned statements, and the definitions they read, are recorded and compared;
   - every declaration is replayed through the kernel.

   Twelve controls show that each check fires (sixteen with #149, §3.4). One of them is POUS's `debug.skipKernelTC` bypass, which passes an audit of axioms alone and fails the replay. Following POUS, axioms are also computed from the replayed environment, and nothing parses `#print axioms` output.
3. **`main` passes, and the merged audits don't need re-running.** All 5,362 declarations of the three packages on `main` use only `propext`, `Classical.choice` and `Quot.sound`, and a kernel replay accepts all of them (the compiler's own copies of recursive definitions aside, which the kernel never checks). No source at `main` or at any audited head names a bypass, and neither does any pinned dependency a proof imports. The replay was the re-run. #117, merged tonight, leaves every pin unchanged, which confirms mechanically that it changes none of the pinned statements.
4. **The trust boundary is wider than the ledger says.** The nine headline statements read 321 definitions in 31 modules, some of them in proof files: `Statement.LinkLayout` is in `LinkSound.lean`, and `adv₀`, `advR`, `C0star` and `SelfClash` are in `CompiledSound.lean`. The audit now pins all of them, so none can drift silently. Moving them into definition files is the main structural proposal.
5. **An axiom audit can't catch a weakened definition, and tonight the pins caught one** (§2.3). #118 redefined `MerkleScheme.Collision`, which made `merkle_binding` vacuous for unsalted Merkle schemes. Every axiom check and the kernel replay passed it, because a vacuous theorem is still a theorem. Only the pin on the definition flagged it, and a reviewer then saw it was vacuous; #146 fixes the definition. So any change to a pinned statement, or to a definition one reads, needs a named statement reviewer in the merge handoff, and `--update` prints the before and after text for that review.
6. **POUS can use the audit as it is,** by copying `tools/lean/`: standard-library Python and core Lean, on the same toolchain and Mathlib pin. POUS ran it on its package and it passed, after two small edits. Its grader maps onto pins, allowed axioms and the replay. No model code should be shared across Projects until a second consumer imports it.
7. **Pins are for merged statements.** An external, untrusted submission still needs an `isDefEq` check of its theorem against a trusted `Prop` from the trusted commit, in a sandbox, as POUS's grader does (§5.3).
8. **Re-checking Mathlib and core too** (`leanchecker --fresh`, POUS's other proposal) is now an option, `--fresh`. On `main` it passes, but it takes about 21 minutes and 11 GB for the three roots here (§3.3). That is too much for every merge, so run it at every bump and nightly.
9. **Decisions for you** (§7): the definition moves; retiring the old `#print axioms` lists (the three PRs this waited on have landed); POUS's code home; a nightly `--fresh` machine; build caching for `check`; computed status lines and a correspondence ledger for the soundness ledger.
10. **Noticing upstream proofs is now mechanical** (§3.8, [#175](https://github.com/danielreuter/verity/pull/175), after #130). The ArkLib survey found `ASSUMPTIONS.md` calling A1 unproved while our pin had the proof.
    - The audit now scans the pinned dependencies' statements for each named assumption, in about 3 s, and fails on a proved theorem nobody has acknowledged.
    - An exact Lean pass runs at bumps.
    - Four of ArkLib's patterns come with it (§4.3): status computed rather than asserted, a paper-to-Lean correspondence ledger (proposed), freezing a statement before proving it, and one Lake build directory per agent.

## 1. Package layout and dependencies

### 1.1 What there is

| Package | Directory | Requires | Size | From scratch |
|---|---|---|---|---|
| `flock_verifier`: the executable (`Flock`, `Main`, built as `flock-verify`) and `FlockProofs` (facts needing only core) | `backends/flock/verifier/lean/` | nothing | 30 files, 3,902 lines, 1,912 declarations | 10 s |
| `flock_level3`: facts about the executable's definitions (the fields, the folds, every field of `Arith.Correct`) | `…/lean/level3/` | Mathlib `5ed29652`; `flock_verifier` by path | 16 files, 2,857 lines, 832 declarations | 67 s setup + 160 s |
| `FlockSoundness` and `FlockSoundnessTest`: soundness of the protocol | `…/lean/soundness/` | ArkLib `b2e456fc` (and through its manifest VCVio, CompPoly and Mathlib `5ed29652`); `flock_level3` by path | 48 files, 12,292 lines, 2,618 declarations (with #117) | 92 s setup + 206 s |

Setup is elan, the toolchain, cloning the dependencies, and Mathlib's prebuilt cache. The path dependencies form one build graph: building `soundness` builds `level3` and the executable's modules.

### 1.2 One workspace or several: several, along dependency lines

- **The verifier of record builds with no dependencies** (`test_no_dependencies`), which keeps its build and its compiled code small. One workspace would put Mathlib and ArkLib into its manifest and clone them for every build of the binary.
- **Facts that need Mathlib shouldn't need ArkLib:** `level3` builds in half the time, and survives an ArkLib bump untouched.
- **The packages match their owners.** flock-verifier owns the executable and `level3`; flock-soundness owns `soundness`.

The cost is three manifests that must agree, and that is now mechanical: `tests/test_lean_packages.py` fails unless every Lake package has a `lean-audit.json`, the same toolchain and the same Mathlib revision. **Add a package only when the dependency set differs,** never one per lane or per area.

### 1.3 Where new Lean work goes

| Work | Where | Why there |
|---|---|---|
| Audit and protocol theorems: the one-stage profile, two-stage, and the relations | `soundness/FlockSoundness/Audit/` (PR #122, where [audit protocols](audit-protocols.md) §4.1 put it) | It needs `Game` and Mathlib. The abstract modules import nothing Flock-specific, and `Audit/Flock.lean` instantiates them. When a second backend needs them, move `Game/` and `Audit/` to a Mathlib-only package beside the protocol (`protocols/sampled_proofs/lean/`); not before. |
| Knowledge soundness (`table_knowledge_sound`, `registered_weights`) | `soundness/FlockSoundness/Knowledge/`; #117's `CompiledTable.lean` can move there as the area grows | Same dependencies. CompPoly's Guruswami–Sudan decoder is already in the manifest, through ArkLib. |
| Zero knowledge: the Lean reference prover | the executable package, as a library `FlockProver` with an executable | It runs: the differential tests compare the production prover with it byte for byte. So, like the verifier, it must build with no dependencies. |
| Zero knowledge: completeness and the simulator theorem | `soundness/FlockSoundness/ZK/` | They are protocol theorems, stated about the reference prover's definitions. |
| The partition evaluator port (`verity/partition/v1`, PR #111) | the executable package, beside `Flock.Partition` | The verifier runs it. It is checked against `verity.ir.cut` the way `unit_cut_agree.py` checks cuts; any facts about it go in `level3`. |
| The private track's V[B] generator | See the next paragraph. | The verifier of record keeps no dependencies, whatever the generator needs. |

**The V[B] generator.** The verifier's checks become an interface with two interpretations:

- the check interface and its native interpretation stay in the executable package;
- the circuit interpretation joins them if it needs no library; otherwise it goes in a package `lean/vb/` that requires the executable, and Clean or zkLean if one is chosen;
- the equivalence theorem goes in `level3`, or in `vb/` if it needs that library.

Writing the checks once against two interpretations is a refactor of the verifier, so it is a proposal for the flock-verifier lane (§7).

Inside a package, each area owns a subdirectory, a namespace, and one aggregator module that imports its files. The package root imports the aggregator once, when the area is created (§4.2).

### 1.4 Pinning the toolchain, Mathlib and ArkLib

- **One toolchain and one Mathlib.** Every `lean-toolchain` is `leanprover/lean4:v4.34.0`, and every manifest pins Mathlib `5ed29652`; `tests/test_lean_packages.py` enforces both. Mathlib is the revision ArkLib's manifest pins, because ArkLib is the most constraining dependency; `level3` pins that revision explicitly.
- **Revisions are commit hashes,** never branches or tags, both in `lakefile.toml` and in the committed `lake-manifest.json`.
- **A bump is a PR of its own:** the toolchain, Mathlib and ArkLib together, across every package. It runs `audit.py --all --build` and then `--update`, and its pin diff shows every pinned statement that moved. A feature PR never runs `lake update` or edits a `require`.
- **At a bump, the dependency definitions that the assumption reads are reviewed.** `ASSUMPTIONS.md` §5 counts ArkLib's Reed–Solomon codes, `mcaError` and Johnson bounds as part of what the theorems mean. The pins follow in-repo definitions only, so today the bump's reviewer diffs those ArkLib definitions by hand. A proposal: add ArkLib's coding-theory modules to the soundness policy's `meaning`, so that the pins flag them too (§7).
- **POUS** now pins the same toolchain and Mathlib, but nothing forces the two Projects to move together.

## 2. The trust boundary

### 2.1 What a reviewer reads, and what they needn't

Per package, a reviewer reads one file and the definitions it points to:

- **`pins` in `lean-audit.json`:** each cited theorem's full signature as Lean prints it, with its named assumptions.
- **`reads`:** for each module, the definitions the pinned statements depend on, and which pins read them. The audit follows them through definitions, inductive types and constructors inside the package's `meaning` modules.
- **The named assumptions:** the `assumptions` module (`FlockSoundness/Assumptions.lean`, one `Prop`) and the ledger that explains it (`ASSUMPTIONS.md`).
- **The allowed axioms and the listed escapes,** each with its reason.

They needn't read proofs, lemmas that aren't pinned, or definitions no pinned statement reads.

What a statement is *about* stays outside `meaning`, and is pinned by other means:

- the executable's functions, by their own tests (the upstream agreement job, fuzzing, `unit_cut_agree.py`) and by `level3`'s theorems;
- Mathlib and ArkLib, by commit (§1.4).

### 2.2 Today the boundary is wider than the ledger's reviewer list

`ASSUMPTIONS.md` §5 sends the reviewer to §1 of the ledger, `Soundness.lean`, `Model/*` and `Accounting/Bound.lean`. Computed from the elaborated statements, the nine soundness pins read **321 definitions in 31 modules**:

- `Model/*` (153);
- `Accounting/*` (42);
- `Game/*` (26), including the lockstep's 12 in `Game/Lock.lean`;
- `Defs.lean` (7), `Instance.lean` (1) and `Assumptions.lean` (1);
- nine `level3` modules of arithmetic (39), for the executable-instance theorems;
- and proof files.

The proof files are the problem, because a lane editing a proof doesn't expect to change a statement:

| Definitions | Read by | Where they are (a proof file) |
|---|---|---|
| `Statement.LinkLayout`, the hypothesis `hlay` | all nine pins | `LinkSound.lean` (548 lines) |
| `adv₀`, `advR`, `C0star`, `SelfClash`, `Clash`, `Verified`, `opens₀`, `slotOpens` and 7 more | `table_sound_compiled` | `CompiledSound.lean` (642 lines) |
| the lockstep's 25 builders | `table_sound_compiled` | `CompiledLock.lean` (673 lines) |
| `Merkle.Enc`, `Verifies`, `walk`, `up`, `reach` (`Model/Compiled.lean` imports `Merkle.lean`) | `table_sound_compiled` | `Merkle.lean` |
| `levelGood`, `levelsChained` | `table_sound_compiled` | `LigeritoPhase.lean` (482 lines) |
| `Rewinding.ConflictAt` (`Game/Expect.lean` imports `Rewinding.lean`) | `table_sound_compiled` | `Rewinding.lean` |

`Soundness.lean`, conversely, holds no definition any statement reads; it only states theorems. The ledger's list is therefore both too wide and too narrow, which is what a computed boundary fixes.

The pins make each of these changes visible now (§2.3). What would make review cheap is structural, and waits for you: move these definitions into definition modules (`Model/Statement.lean`, `Model/Compiled.lean`, a new `Model/Merkle.lean`), so that `reads` shrinks to `Model/`, `Accounting/`, `Game/`, `Defs.lean`, `Assumptions.lean`, `Instance.lean` and the `level3` arithmetic, and `layers` rules keep proofs out of those modules (§7, item 1).

### 2.3 How pinned statements are kept from drifting

What the audit records:

- **A pin's record:** the signature, the named assumptions, and a hash of the elaborated type.
- **`reads`:** for each module, a digest of the definitions the statements depend on.

`audit.py` recomputes both from the build and fails on any difference, so neither a pinned statement nor a definition it reads can change without a diff of `lean-audit.json` in the same commit:

- **a changed signature** fails with the unified diff of the old and new signatures;
- **a changed definition** fails, naming the module and the pins that read it; a definition entering or leaving a statement's meaning is named too;
- **a closed `Prop` hypothesis** that isn't a constant of the `assumptions` module fails, so an assumption can't be written inline.

`--update` rewrites the records, and that diff is what the reviewer reads. A record holds the statement, not the proof. So a pin can be recorded on a `sorry` stub: the audit fails until a proof with allowed axioms replaces it, which is how a grader pins a target.

What pins don't catch, and what covers it:

- **A statement weaker than intended, but true:** only review, which is why the signatures are in the file.
- **Mathlib's and ArkLib's definitions:** pinned by commit, and reviewed at bumps (§1.4).
- **The executable's behaviour:** the agreement tests and `level3`'s facts.
- **False alarms:** re-proving a proof field inside a definition changes the definition's hash, since the hash covers the value, proofs included. The audit errs toward flagging.

The hashes are Lean's structural expression hashes, combined per module with SHA-256. At 32 bits per expression, a changed definition goes unnoticed with probability about $2^{-32}$. That is enough to catch accidental drift, not adversarial collisions. Two runs here reproduced every record, and the recorded `check` confirms them again in a fresh process.

**An axiom audit can't catch a weakened definition.** Axioms, `sorry`, declared axioms and the kernel replay all ask whether the proofs are valid. A weaker definition leaves every proof valid, so all of them pass. Tonight's case:

- #118 added salts to the Merkle leaves, and changed `Flock.MerkleScheme.Collision`'s leaf disjunct to $\exists\, r, r', y, y' : (r, y) \neq (r', y') \wedge \mathrm{leaf}(r, y) = \mathrm{leaf}(r', y')$.
- For an unsalted scheme, whose leaf ignores $y$, taking $r = r'$ and $y \neq y'$ satisfies this. So `Collision` holds for every such scheme, and `merkle_binding`, which concludes `ms.Collision`, says nothing about it.
- The audit, the replay and the train D audit all passed the new code. The `reads` digest for `FlockProofs.Merkle` was the only signal: it changed, naming the three pins that read the definition. A reviewer then saw that the new definition was vacuous. #146 fixes it.

So definitional weakening is caught only by pins and review.

**Pin diffs need a named reviewer.** A change to a pinned statement, or to a definition one reads, needs a named statement reviewer in the merge handoff: someone who read the before and after and agrees the theorem still says what the ledger claims. `--update` doesn't decide that. It prints each changed pin's signature before and after, and each changed definition's new text and the pins that read it, so the reviewer has the text in front of them (PR #130). The merge handoff carries the reviewer's name and the pins they reviewed.

### 2.4 Alternatives weighed

- **A restated statements file** (`Statements.lean` with `theorem pin : ⟨statement⟩ := @proof`). It catches a changed statement but not a changed definition that the statement reads, and it is kept by hand. The pins record the same text, generated.
- **A file-hash manifest** (POUS's `TRUSTED.sha256`). It is simple, toolchain-independent, and exact when every definition a statement reads sits in a trusted file. Ours don't (§2.2), so the audit computes the boundary rather than trusting a layout. The two compose: a package with a clean layout can keep a manifest as well.
- **`isDefEq` against a pinned `Prop`** (POUS's grader). This is the same as pinning a theorem whose type is a pinned `def target : Prop`. The record is then that constant, and `reads` holds `target`'s definition.

## 3. Mechanical enforcement

### 3.1 The audit

The audit has three parts:

- `tools/lean/audit.py` (standard-library Python) holds the policy.
- `Audit.lean` (core Lean) reports facts from the environment:
  - each audited module's declarations, and the axioms each uses;
  - declared axioms, compiled-code escapes, and imports;
  - for each pin, its signature, its hypotheses and the definitions its statement reads.

  Axioms come from `Lean.collectAxioms`, which reads the sets each module's `.olean` recorded when it was built. This takes 1.1 s, 2.9 s and 6.2 s on the three packages.
- `Replay.lean` sends every declaration to the kernel again (§3.2).

The policy is a `lean-audit.json` beside each lakefile ([`tools/lean/README.md`](https://github.com/danielreuter/verity/blob/cursor/lean-audit-68dc/tools/lean/README.md)). The audit fails a package on:

| Check | Fails on |
|---|---|
| axioms | a declaration using an axiom outside the allowed set (by default `propext`, `Classical.choice`, `Quot.sound`). That covers `sorryAx`, and `native_decide`, which in Lean 4.34 declares an auxiliary axiom `…._native.native_decide.ax_*`. |
| declared | any `axiom` declaration: an assumption is a named `Prop`, taken as a hypothesis |
| escapes | an `opaque` declaration (which a `partial def` is), or an `unsafe`, `@[implemented_by]` or `@[extern]` one, not listed with a reason |
| orphans | a `.lean` file that no root imports and that isn't exempt with a reason |
| unchecked | a source file or lakefile that names `debug.skipKernelTC`, `debug.byAsSorry`, `debug.proofAsSorry`, `debug.terminalTacticsAsSorry`, `bootstrap.*`, `addDeclWithoutChecking` or `addDeclCore` |
| layers | a module under a prefix that imports outside the prefix's allowed imports |
| pins | §2.3 |
| replay | a declaration the kernel rejects |

Because it audits every declaration, no list has to be kept in step with the proofs. The old `#print axioms` lists named 6, 50 and 77 theorems; the audit covers 1,912, 832 and 2,618 declarations.

**The coordinator's audits so far.** `r20260927-042257-7cee` covered #85 and #89, `r20260927-053940-45db` covered #110 and #114, and `r20260927-055525-fb18` covered #117. Each built the packages and ran `#print axioms` over those lists (`audit.sh`, `Check.lean`). They were right as far as they went, but they didn't cover unlisted declarations, and they didn't replay the kernel. `audit.py` supersedes `audit.sh`; PR #130 contains PR #112, and keeps its `setup.sh`.

**One finding on the executable.** `Flock.canon`, a `partial def` (canonical JSON for the statement's objects), is compiled code that no proof sees. `ASSUMPTIONS.md` §5 says "none today" of such code. It is now listed under `escapes`, with its reason.

### 3.2 The kernel replay, and the bypass POUS found

`#print axioms` reports what a declaration's proof uses, as the environment records it. A declaration that never passed the kernel can state something false and use no axiom, and then every axiom check passes it. It could have been added with `debug.skipKernelTC`, with `addDeclWithoutChecking`, or by a metaprogram. There are now two defences:

1. **Refusal in the sources** (the `unchecked` check). It is cheap and catches the plain option, but a name built at run time evades any scan.
2. **The replay.** `Replay.lean` reads every constant the audited modules declare from their `.olean` files, imports once whatever they import from outside, and sends each constant to the kernel (`Kernel.Environment.replay`, the core of `leanchecker`).
   - The toolchain's own `leanchecker` does the same check, but it replays every module under a prefix at once, each on its own copy of the Mathlib environment. On this 15 GB VM the kernel killed it (exit 137) on `level3`.
   - `Replay.lean` loads the dependencies once, and takes 1.7 s on the executable, 201 s on `level3` (whose `decide +kernel` facts the kernel recomputes) and 9.1 s on `soundness`.
   - A replay killed by a signal (the out-of-memory killer, a timeout) is reported as a kill, never as a kernel verdict.

**Axioms from the replayed environment** (POUS's second proposal, now implemented). Nothing parses `#print axioms` output any more; the old lists and `audit.sh` did. `Audit.lean` reads the axiom sets each module's `.olean` recorded when it was built (`Lean.collectAxioms`). After replaying, `Replay.lean` walks the bodies of the environment the kernel just checked, and finds the axioms again independently. The audit fails if the two differ, which is what a tampered or stale `.olean` would show. On `main` they agree on all three packages. This check has no control of its own, since a disagreement needs a hand-edited `.olean`; the clean control shows that the two agree.

**Against a build that tampers** (from PR #112). Elaborating a Lean file runs arbitrary code, and a build could rewrite the audit or the toolchain. So the Lean files run from a copy taken before the first build, and this directory, that copy and the toolchain's `lean`, `lake` and `leanchecker` are hashed, then checked after each package.

**PR #112, reconciled.** The coordinator's #112 grew three things overnight:

- `replay.sh`: per-module `leanchecker`, two at a time, with killed checks retried alone and reported as kills;
- a negative-control package;
- the hashing just described.

POUS's author found two bugs in it that the coordinator had already fixed (by #112's commit messages: a killed check reported as a verdict, and a negative control that didn't parse at v4.34). PR #130 merges #112's head and folds each idea in, as `Replay.lean`, the kill rule, the `kernel` and `kernel_option` controls, and the seals. It then removes `audit.sh`, `replay.sh` and the negative-control package in a commit of its own. Merging #130 therefore lands #112 as well, and #112 can be closed.

**The negative controls.** The `kernel` control adds `theorem Control.bogus : False := True.intro` through `debug.skipKernelTC`, with the option's name built at run time. The controls require that the audit passes it without the replay, which is the gap, and fails it with the replay. A second control, `kernel_option`, uses the plain option, and must fail the source check.

**Do the merged audits need re-running? No.**

- The replay of `main` at `ae5db5d3`, which contains #85, #89, #110 and #114, accepts every declaration of the three packages. That is the re-run, through the kernel. #117, merged since, is covered too: the audit and the replay pass on `928790af`, and `--fresh` accepts its closure (§3.3).
- No source at `main`, or at any audited head (`aaf68b8f`, `6dc1cd07`, `806f719e`, `aeb97971`, `ada69ed9`), names a bypass. The lakefiles' `leanOptions` set only `autoImplicit`.
- Among the pinned dependencies (Mathlib, ArkLib, VCVio, CompPoly and the rest), only doc-gen4's loader sets `debug.skipKernelTC`, for its own documentation loading. No proof imports it.
- Open PRs (#122 and later) get the full audit from `check` once PR #130 lands.

The package replay doesn't re-check the dependencies' own declarations. `--fresh` does (§3.3), and on `main` it accepts all of them. Their sources were also scanned by hand tonight; a build-time scan is a proposal (§7).

### 3.3 Re-checking the dependencies too: `--fresh` (POUS's other proposal)

The package replay (§3.2) re-checks our own declarations. For everything they import, it trusts the `.olean` files as built on the audit machine, and, for Mathlib, as downloaded from Mathlib's prebuilt cache. `leanchecker --fresh ROOT` replays a root's whole import closure into an empty environment, core, Mathlib and ArkLib included, so it trusts neither. `audit.py --fresh` runs it on each root. Measured on this VM:

| Root | Closure | `--fresh` | Peak memory | Package replay alone |
|---|---:|---:|---:|---:|
| `Main` (the executable) | 58 modules | 66 s, accepted | 0.7 GB | 1.7 s |
| `FlockLevel3` | 2,093 modules | 471 s, accepted | 10.1 GB | 201 s |
| `FlockSoundness` | 3,898 modules | 732 s, accepted | 10.7 GB | 9.1 s |

So `main`'s whole closure, Mathlib, ArkLib and core included, passes the kernel from scratch. Each `--fresh` is a single process, so more cores barely help. Running the three roots one at a time takes about 21 minutes and needs about 11 GB; running them side by side would need about 22 GB.

**Recommendation: not on every merge.** Between bumps, the dependency closure is the same bytes at the same pinned commits, so checking it on every merge proves the same thing again, for 21 more minutes of every `check`. Run `audit.py --all --build --fresh` in two places:

- **in every bump PR** (toolchain, Mathlib or ArkLib), as part of its `check`;
- **nightly on `main`,** as a recorded run on a CPU pod with at least 16 GB, which also covers a Mathlib cache that changed between downloads.

A Lean-touching train changes no dependency, so the package replay covers it. The executable's closure is cheap enough (66 s) to add to every `check` if you want core Lean re-checked each time, but it adds little.

### 3.4 Where package code runs, and what stops it (POUS's review of #130, in [#149](https://github.com/danielreuter/verity/pull/149))

POUS's Lean author ran #130 on the POUS package. It passed after two small edits, and the review found that a hostile package could still act in three places. #149, on top of #130, closes each:

- **Initializers in the facts process.** #130 gathered facts with `lake env lean` on a file importing the package. That runs the package's `initialize` code, which can write files, so it could forge every fact except the axioms, which the replay cross-checks. Now `Facts.lean` reads the `.olean` files as data: initializers disabled and no environment extension loaded, with attributes and source ranges read straight from module data.
  - A control's initializer, which writes a forged facts file wherever it runs, runs under `lake env lean` and never under `Facts.lean`.
  - On all three packages the new facts equal the old ones, except that signatures now print without notation (for example `Eq (…) (Option.some sch)` for `… = some sch`). The type hashes and `reads` are unchanged, which the re-record's diff shows.
  - No notation, ours or a hostile package's, can change how a pinned statement reads.
- **Compile-time IO in the build.** A build runs the package's code (`#eval`, `run_cmd`, initializers of imported modules, elaborators), and POUS's red team rewrote a checker input and restored it. Two layers:
  - The build runs in `sandbox.sh` where `unshare` and unprivileged user namespaces are available: new user, mount, network and PID namespaces; everything read-only except the build's `.lake` directories; no network; nothing outlives the build. On this VM it costs nothing measurable.
  - Everywhere, code run while compiling is refused in the audited sources unless its module is listed under `compile_time` with a reason. So is a `lakefile.lean`, which `lake` runs whenever it loads the package, `lake env` included. None of our three packages needs either. Since [#294](https://github.com/danielreuter/verity/pull/294), prompted by the red team's review of the first listing (#291's proof-only `walk_step` tactic), a listing names one module and records the digest of its file as reviewed. Any edit then needs a new review. No listed module may declare a pinned theorem or hold a definition a pinned statement reads, since a term elaborator, notation or macro there could change what a statement means.
  - The exploit is a control: the static check refuses it, and the sandbox blocks its write.
- **Dependency `.olean` files.** Without `--fresh`, the replay trusted the dependencies' `.olean` files as built or downloaded. Now each fetched package's `.olean` files, and the toolchain's, have a digest recorded under `dependencies` and checked on every run. Lean's `.olean` files are reproducible: a rebuilt ArkLib module was bit-identical, and Mathlib's digest is the same in two separate clones. So the record holds on any machine and changes only at a bump. It costs 5 s warm and 23 s cold for 6 GB of Mathlib and ArkLib.
- **Onboarding.** A package without a `lean-audit.json` fails with a template built from its lakefile. The text scans skip comments and docstrings, so prose may name `debug.skipKernelTC`. `--build` accepts relative paths.
- **A machine without Lean.** `--all --build` installs each audited toolchain (`setup.sh`) before the controls build the fixture. Before, the controls needed a toolchain that only a package's own build step installed, which the research coordinator hit. Run with an empty home directory, it installed elan and Lean v4.34.0 and passed. The toolchain's binaries are sealed at the start, or right after the controls install them.

What remains trusted is the toolchain, the pinned dependencies' sources, and the machine. Untrusted submissions still need a grader's `isDefEq` against a trusted `Prop` (§5.3).

### 3.5 The controls

`--all` first builds `tools/lean/tests/fixtures/control` with each audited package's toolchain and runs twelve controls, in 26 s. The clean fixture must pass, and each of eleven violations must fail its check:

- a `sorry`, a declared axiom, and a `native_decide`;
- an unlisted `partial def`, and a file no root imports;
- an inline closed hypothesis, and a changed statement;
- a broken layer, and a changed definition that a pin reads;
- the plain `skipKernelTC` option, and the hidden bypass.

#149 adds four, for sixteen in all. They take 76 s with every build in the sandbox, and pass without one too:

- an initializer that tries to forge facts;
- compile-time IO that rewrites and restores a checker input;
- a docstring naming the option, which must pass;
- a package without a policy.

Because the controls run under the audited toolchain, a bump that changed how Lean records axioms would fail loudly rather than blind the audit.

### 3.6 In `check`, and build caching

`check`'s `lean-audit` step (PR #130) runs `audit.py --all --build`: for every package with a `lean-audit.json`, the setup, `lake build` and the audit, after the controls. Its reports are kept among the run's artifacts.

**What it costs:**

- On a machine that has built before, about 4 minutes, most of it `level3`'s replay.
- From scratch, add about 9 minutes of builds on four cores, less on a 16-core check pod: Mathlib comes from its prebuilt cache, and ArkLib is compiled.
- In [#134](https://github.com/danielreuter/verity/pull/134)'s parallel groups (the fast `check`, which lands first, in train E2), the audit runs in the Lean group after the unit-cut check and before the upstream agreement, so the two never share memory. When the agreement's cache hits, as it does for most PRs, the Lean group finishes beside pytest. When it misses, the audit's minutes add to the agreement's 30.
- The agreement's cache key covers every tracked file of the executable's package, `lean-audit.json` included, though neither its build nor `ci.py` reads that file. So a change to the pins alone would re-run the 30-minute agreement. Once #134 is on `main`, #130 excludes that one path from the key, in a commit of its own. Circuit-checks agreed, after checking that nothing the agreement uses reads the file. #134's test that keeps the agreement's scripts on the standard library now also fails if those scripts or the package's lakefile mention `lean-audit`, so a later dependency on the file fails a test instead of leaving the cache stale.

**Build caching, when it pays** (proposals, §7):

- **A cached pass.** Under fast-check's content-addressed caches, key a passing `lean-audit` on the toolchain and the tracked files of the Lean packages and `tools/lean/`. Most PRs touch no Lean, and would skip it.
- **A stored dependency build.** Store a build of ArkLib's, VCVio's and CompPoly's `.olean` files, keyed by the manifest and pinned by hash (the way fast-check pins the upstream verifier). That saves the ArkLib compile on a cold pod.

### 3.7 Cross-checks between the executable and the model

What holds today:

- **The arithmetic is shared, not copied.** `execArith` is the executable's arithmetic (as `level3` defines it), and `execArith_correct` proves `Arith.Correct` for it, so `table_sound_exec` has BCHKS25 as its only hypothesis.
- **The executable is checked against upstream:** the agreement job (412 of 412 sessions), fuzzing, the forgeries, and `unit_cut_agree.py` against `verity.ir.partition`.
- **The executable's refinement facts** (`fold_get`, `foldB_get`, `foldT_get` and the rest) are pinned in `level3`.

What doesn't hold yet: that the model's protocol flow (which checks, in what order, on which coins) is `Flock.Verify`'s. That is Stage 2, the refinement theorem, still to be written. Until then, two cheap cross-checks, proposed for the flock-verifier and soundness lanes:

- **Seam theorems.** For every constant both sides define (schedules, tags, sizes, coin counts), prove the two equal by `decide` or `rfl` in `level3`, and pin each theorem.
- **A differential test of the model.** The model's games can be interpreted on a recorded transcript, but `execArith` is noncomputable, because the `GF128` and `GF256` field instances are. A computable instance built from the executable's operations would let a test replay recorded sessions through the model and compare its verdict with `Flock.Verify`'s.

### 3.8 Noticing when a dependency proves what we assume: the upstream watch ([#175](https://github.com/danielreuter/verity/pull/175))

**Why.** `ASSUMPTIONS.md` said A1 was unproved in ArkLib while our pin, `b2e456fc`, already had the proof ([ArkLib survey](archive/arklib-survey.md) §5).
- The status line was written by hand.
- The proof arrived as a different theorem with a different constant (`ReedSolomon.mcaError_affineLine_johnson_le`, from DKT26), so watching the name we mirror (`rs_mcaError_le_in_johnson_range`, still admitted) finds nothing.

So the watch list names what a statement is about, and the status comes from the dependency, not from a document.

**The tool.** The survey's two prototypes, folded into `tools/lean/` as `upstream.py` and `Upstream.lean`.
- **The watch list** is the `upstream` section of a package's `lean-audit.json`. It has one entry per named assumption or hand-proved lemma, with the constants its statement mentions and the upstream theorems already looked at (`ack`). Soundness has nine entries:
  - A1's Johnson-range MCA, and the unique-decoding fallback;
  - the list bound, in two forms, and the tensor fold;
  - the novel basis (CompPoly);
  - three forms of collision resistance for A2 (VCVio).
- **The no-build pass** reads the dependency's theorem statements at the pinned revision with `git show`.
  - It matches the constants' last components as words, with comments stripped and each statement bounded.
  - It takes proved or not from ArkLib's own transitive `sorry` baseline (`scripts/axiom_baseline.json`, which ArkLib's `validate.sh --axioms` keeps current).
  - It takes 2.6 s.
- **The audit runs it** for every package with an `upstream` section. A proved hit that its entry doesn't acknowledge fails the audit, so a bump that brings a proof about a watched statement can't pass unseen. The report records the computed status per entry.
- **The exact pass** (`upstream.py PKG --lean`) builds `imports`, then matches the constants in the elaborated types of everything imported (ArkLib, CompPoly, VCVio, Mathlib), with each hit's axioms taken from the proof bodies.
  - It reads modules as data, as #149's facts do.
  - On this machine the first build of all of ArkLib took 11 minutes on four cores; after that the pass takes 36 s. It is for bumps.
- **Replayed on ArkLib's history,** the no-build pass flags `ReedSolomon.mcaError_affineLine_johnson_le` under A1 at `0f01ddf1` (Sep 25, "#907 P7a slice 81"), two days before our pin. The audit's failure message is what a bump author would have seen.
- **At the pin both passes are clean.** The survey's reviewed hits are acknowledged, and so are nine more that the exact pass finds and the text scan misses, all of them in the survey's reviewed output.
- **At ArkLib's head** `7653a901`, 11 commits past the pin, nothing is new; the survey found the same. The check takes 3.5 s with the fetch.

**What it doesn't do.**
- It doesn't judge whether an upstream theorem discharges an assumption. A person does, then acknowledges it.
- It doesn't bump anything. What upstream has proved since the pin is one command, `upstream.py soundness --fetch --rev origin/main`, for a weekly run (§7).
- It adds only the audit's three-second step to `check`.

**One interaction with #149.** The exact pass builds all of ArkLib inside the package's `.lake`. #149's dependency digest hashes every `.olean` file a fetched package has built, so on a machine that ran the exact pass the digest changes. #149 now hashes only the `.olean` files of the modules the package imports; the facts list them. That is also a more precise statement of what the replay trusts. The cost: a PR that changes a package's imports runs `--update`, and the failure message says so.

## 4. Agent conventions

### 4.1 The rule text, now in `AGENTS.md` (PR #130)

```text
## Lean

- The Lean packages are `backends/flock/verifier/lean/` (the executable verifier, no dependencies), its `level3/` (proofs
  about the executable's definitions, Mathlib) and `soundness/` (the protocol's proofs, ArkLib). New Lean goes into the
  package whose dependencies it needs, in a subdirectory and namespace of its own. All packages share one toolchain and
  one Mathlib revision (`tests/test_lean_packages.py`); bump them together, in a PR of their own.
- Every Lake package has a `lean-audit.json`, and `check` audits every declaration (`tools/lean/audit.py`): only `propext`,
  `Classical.choice` and `Quot.sound`; no `sorry`, `axiom`, `native_decide` or kernel bypass; an assumption is a named
  `Prop` in the package's assumptions module, taken as a hypothesis; every `.lean` file is built, and every declaration
  is replayed through the kernel.
- A theorem that a ledger, a table or a PR cites as proved is pinned in `lean-audit.json`. `audit.py --update` records
  it. A changed record means the theorem now says something else (its statement, or a definition the statement reads).
  No axiom check can catch a weakened definition, so a changed record needs a named statement reviewer, who reads what
  `--update` prints (each changed signature before and after, each changed definition as it is now), and the merge
  handoff names them.
- A named assumption, or a hand-proved lemma a dependency could prove, has an entry in the package's `upstream` watch
  list. The audit fails when the pinned dependency proves a theorem about it that nobody has acknowledged
  (`tools/lean/upstream.py`). A document's "status upstream" cites that output; it is never written by hand.
- Two agents never share a writable Lake build directory (`.lake`): parallel Lean work uses separate checkouts.
- How to work on Lean, and how parallel Lean lanes avoid conflicts: `.agents/skills/lean-proofs/SKILL.md`.
```

The last two bullets before the skill pointer come with #175.

The workflow is the `lean-proofs` skill (`.agents/skills/lean-proofs/SKILL.md`, written to the authoring-skills conventions). It covers where work goes, the build and audit commands, assumptions and pins, and the PR checklist. It adds one review step, and only for changed pins: a named statement reviewer, other than the author, reads what `--update` printed. That step exists because nothing mechanical can judge whether a changed definition still means what the ledger says (§2.3).

### 4.2 Parallel Lean lanes

The conflicts so far all came from shared, append-only files:

- the root import file (`FlockSoundness.lean`: #117 adds a line, #122 four);
- the `#print axioms` lists (`Check.lean`: #117 adds six lines, #122 twenty-one);
- the ledger's status table;
- and a test file (`test_lean_verifier.py`, edited by #113, #118 and #122).

The conventions:

- **One area per lane:** a subdirectory, a namespace and an aggregator module. The package root imports the aggregator once, when the area is created.
- **No lists to append to.** The audit covers every declaration, so `Check.lean` needs no more lines (retire it, §7). Pins are one entry per theorem in `lean-audit.json`; since the records are generated, a conflict there is resolved by merging and re-running `--update`.
- **Layers, not bespoke tests.** A rule like #122's `test_audit_layer_is_abstract` is one `layers` entry.
- **The ledger:** each lane edits its own sections and status rows, and conflicts keep both rows.
- **Cross-package edits are named.** A `level3` change to a definition that a soundness statement reads fails soundness's pins too. The lane that makes it runs `--update` on both packages, and says so in the PR.
- **Notes.** Lanes coordinate through the notes repo: checkpoints, handoffs, and a merge-ready handoff to the coordinator carrying the audit's summary line. The repo is public, so nothing sensitive goes in lane notes. A bypass found in unmerged code goes in the Project store's `internal/`, outside `lanes/`, with a one-line pointer in the notes.

### 4.3 Four patterns from ArkLib (the survey's §6)

1. **Status is computed, not asserted.**
   - ArkLib keeps a transitive `sorry` baseline behind a regression gate, and its Grand Challenge witnesses record whether they rest on an admit.
   - Ours: the audit computes axioms and pins, and the upstream watch now computes what upstream proves about each named assumption.
   - What remains is to stop writing status by hand. `ASSUMPTIONS.md`'s "Status upstream" lines and Table 1's assumption column should cite computed output: claim id, Lean declaration, axioms (§7, item 14). The rule is in `AGENTS.md`.
2. **A paper-to-Lean correspondence ledger.**
   - ArkLib's #907 records, for every ported result, the source, the exported Lean type, the relation (equivalent, generalized, specialized or intentionally different) and what is deferred. DKT26 ships the same as `lean-statements/sources.json`.
   - Ours is half there: DESIGN §4's deviation table, and the pins for the Lean side.
   - A machine-readable ledger beside `ASSUMPTIONS.md`, one row per cited paper result and spec clause (source, pinned declaration, relation, what's deferred), would make statement review mechanical where it can be. The audit would check that each row's declaration is pinned (§7, item 15).
   - Not built: it needs the soundness lane's rows first.
3. **Freeze the statement before proving it.**
   - ArkLib's `prove-milestone`: audit the statement against the primary source, freeze it, then prove it, with the `sorry` count only falling.
   - Ours: a pin records the statement, not the proof. A stub pinned in a lane branch and reviewed first shows any later drift.
   - The skill now says so, with `prove-milestone`'s list of ways not to make a theorem easier: strengthening an input relation, weakening an output relation, shrinking the challenge space, adding an unmotivated hypothesis, or moving a verifier check into an assumption. That list is also the statement reviewer's checklist.
4. **One Lake build directory per agent.**
   - #907's owner runs implementers in isolated worktrees, and they never share a writable Lake build directory.
   - Our lanes mostly have VMs of their own, so this held by accident. It is now stated in `AGENTS.md` and the skill: concurrent builds overwrite each other's `.olean` files, and an audit then reads what another agent's build left.

## 5. Cross-Project reuse: POUS

### 5.1 What POUS has

Per its design note:

- **Toolchain and layout:** Lean `v4.34.0` and Mathlib `5ed2965`, the same pin as `level3`, with `autoImplicit` off. The package is split the Flock way, into `Pous/Game`, `Pous/Model` and `Pous/Accounting`.
- **Assumptions and checks:** named-`Prop` hypotheses, no declared axioms, and a `CheckAxioms.lean`. The `sorry` targets live in a `PousTargets` library outside the default build.
- **Shareable pieces:**
  - a parallel oracle machine (`Prog`, about 30 lines);
  - a grader that checks a submission's `solution` against a pinned `Prop` by `isDefEq`, checks its axioms against a registry, and replays the submitted constants through the kernel, with negative controls including the `skipKernelTC` bypass;
  - a `TRUSTED.sha256` manifest, over a trusted boundary of about 400 lines (Game, Model, Params and `Pinned.lean`).

### 5.2 Sharing the audit without coupling

- **The tool is self-contained.** `tools/lean/` needs Python's standard library, `lake`, and the toolchain's `lean`. It imports no Verity package, finds packages under `--root`, and runs its controls under whatever toolchain the audited package pins. POUS copies the directory at a Verity commit and records that commit beside it; nothing in its build requires Verity.
- **It is not a Lake package to `require`.** That would put Verity's repository in POUS's manifest, and tie the two toolchains together.
- **The code home is your call.** One option is POUS's own repository, with the copied `tools/lean/`. The other is inside Verity: `protocols/pous/lean/` would sit beside `sampled_proofs`, and the same `check` and `research merge` gate would cover it. The first keeps the Projects independent; the second shares one gate and one audit run.

### 5.3 POUS's pieces, mapped onto the audit

| POUS | The audit |
|---|---|
| pinned `Prop`s, checked by `isDefEq` | pins: record them on the `sorry` targets, and any proof with allowed axioms passes |
| the axiom registry | `axioms` in `lean-audit.json` |
| the kernel replay of submitted constants | `Replay.lean`, plus `--fresh` for the whole closure (§3.3) |
| axioms from the replayed environment | `Replay.lean`'s walk, compared with the `.olean`'s recorded sets |
| the `skipKernelTC` negative control | the `kernel` and `kernel_option` controls |
| `TRUSTED.sha256` | `reads`, semantic and computed; the manifest can stay as well |
| `CheckAxioms.lean` | superseded: every declaration is audited |
| `sorry` targets in `PousTargets`, outside the default build | not a root, so not audited; pin the solutions |
| the data-only load | `Facts.lean` and `Replay.lean`: initializers disabled, no extension loaded (follow-up PR) |
| `.olean` hashes | `dependencies` in `lean-audit.json`, checked every run (follow-up PR) |
| the grader's sandbox | `sandbox.sh` for builds, where `unshare` allows; the `compile-time` refusal everywhere (follow-up PR) |

**For a grader of untrusted submissions:**

- elaborating a Lean file runs arbitrary code, so build each submission in a sandbox, from a clean tree;
- take the trusted files from the trusted commit, never from the submission's tree;
- never trust `.olean` files a submission ships.

The replay closes environment hacks, and the sandbox closes the rest.

### 5.4 Shared model code

POUS's parallel oracle machine (bounds on rounds and queries) and Verity's interaction model (`FlockSoundness.Game`: live coins, strategies and values) solve different problems, so share none of it yet. If both Projects come to import the same definitions, extract a small Mathlib-only package into its own repository, pinned by commit in both. Until a second consumer imports it, copying 30 lines costs less than a dependency.

## 6. What not to build

- One Lake workspace for all of Verity's Lean, or a package per lane or per area.
- A shared Verity Lean core library, or a cross-Project model library, before a second consumer imports it.
- Per-lane audit scripts, `#print axioms` lists or grep tests: the policy has `layers`, `pins` and `escapes`.
- GitHub Actions or another CI service (you decided against it), or a grading web service for POUS.
- An approval workflow for pin changes: the diff and the PR's note are the control.
- Per-declaration axiom allow-lists: a package-level `axioms` list is enough until someone needs `native_decide`.
- `--fresh` on every merge (§3.3), an independent kernel in every `check`, or a Lean build service.
- A generated ledger: `ASSUMPTIONS.md` stays prose, and cites pins by name.
- A statements file restating every pinned theorem, or a file-hash manifest for Verity's packages (§2.4).
- An R2 build cache, before `check`'s running time calls for one.
- A watcher service, scheduler or dashboard: the audit's step and a weekly `research run` of `upstream.py` suffice.
- Automatic acknowledgement at a bump: `ack` records that a person looked.

## 7. Proposals for your review

These are structural, or change another lane's files, so nothing here has been done.

1. **Move statement-defining definitions out of proof files** (§2.2, soundness lane):
   - `Statement.LinkLayout` to `Model/Statement.lean`;
   - the collision finders and plurality table (`adv₀`, `advR`, `C0star`, `SelfClash`, `Clash`, `Verified`) and the lockstep builders to `Model/Compiled.lean`, or a `Model/Lock.lean`;
   - `Merkle.Enc` and `Verifies` to a new `Model/Merkle.lean`;
   - `levelGood`, `levelsChained` and `Rewinding.ConflictAt` into `Model/`.

   Then add `layers` rules to the soundness policy: `Model`, `Game`, `Accounting` and `Assumptions` import only Mathlib, ArkLib and each other. Today `Model/Compiled.lean` imports `Merkle.lean`, and `Game/Expect.lean` imports `Rewinding.lean`.
2. **Retire the old audit machinery; #113, #118 and #122 have all landed, so it can go once #130 does.** Delete `lean/CheckAxioms.lean`, `level3/CheckAxioms.lean` and `soundness/FlockSoundness/Check.lean`, the `check_axioms` tests in `test_lean_verifier.py`, and their `exempt` entries. Also point `ASSUMPTIONS.md` at `lean-audit.json` instead of `Check.lean`.
3. **#122:** replace `test_audit_layer_is_abstract` with a `layers` entry for `FlockSoundness.Audit` (with `except: ["FlockSoundness.Audit.Flock"]`), and pin the audit theorems it cites.
4. **Follow the assumption's ArkLib definitions** by adding ArkLib's coding-theory modules to the soundness policy's `meaning`, so that a bump flags changes to `mcaError` and `ReedSolomon.code`.
5. **Update `ASSUMPTIONS.md` §5:** the reviewer's list becomes `lean-audit.json`, and the compiled-code line gains `Flock.canon`.
6. **Seam theorems, then a computable `Arith` instance** for a model-against-executable differential test, and then the refinement theorem (§3.7).
7. **Build caching:** a cached `lean-audit` pass under fast-check's caches, and a stored dependency build (§3.6). For the circuit-checks lane, when `check`'s time calls for it.
8. **POUS's code home** (§5.2).
9. **V[B]:** write the verifier's checks against an interface with two interpretations (§1.3), in the flock-verifier lane, when the recursion track resumes.
10. **Name changed pins in the merge commit.** `research merge` would list which pins a merge changes; that is visibility, not an approval.
11. **A build-time scan of the dependencies** for the `unchecked` options. The audit scans only the package's own sources; tonight's scan of the dependencies was by hand.
12. **Now and then, an independent kernel** (lean4lean or nanoda) run on the headline theorems, when a claim needs independence from Lean's own kernel (`ASSUMPTIONS.md` §5 lists this as a mitigation).
13. **`--fresh` at bumps and nightly** (§3.3): add `--fresh` to a bump PR's `check`, and have the steward launch a nightly `audit.py --all --build --fresh` on `main` on a CPU pod with at least 16 GB, recorded like any run. The machine, and its cost of about 30 minutes a night with the builds, are your call.
14. **Computed status lines** (soundness lane): replace `ASSUMPTIONS.md` §3's hand-written "Status upstream" lines with a pointer to the audit's computed `upstream` status, and name each assumption's watch entry. One of them still says A1 is "Unproved in ArkLib", which the pin disproves.
15. **A correspondence ledger** beside `ASSUMPTIONS.md`, with an audit check that each row's declaration is pinned (§4.3).
16. **A weekly look at ArkLib's head:** the steward runs `upstream.py backends/flock/verifier/lean/soundness --fetch --rev origin/main` through `research run` each week, and a nonzero exit means a bump would gain something. This is the survey's recommendation; it costs seconds of CPU.

## 8. Where things stand (Sep 28, 05:20Z)

- **[#130](https://github.com/danielreuter/verity/pull/130) is on `main`,** as train H (`d69ce770`). `check` audits every Lean package.
- **[#175](https://github.com/danielreuter/verity/pull/175), the upstream watch (§3.8), is on `main`,** in train J (`216d7b66`).
- **[#149](https://github.com/danielreuter/verity/pull/149), POUS's hardening (§3.4), is merge-ready at `5653b1fa`:**
  - `main` at `6746f408` (trains K, L and M) is merged in; `check` `r20260928-043329-9cbc` passed; the merge gate accepts it.
  - The re-record changes no statement across the 70 pins: every type hash, named assumption and read is unchanged, and only the printed signatures changed. No named reviewer is needed.
  - The research coordinator's order is #149, then #134 rebased onto it.
- **[#294](https://github.com/danielreuter/verity/pull/294)** ties each `compile_time` listing to its file's digest and keeps listed modules out of what pins read (§3.4). `check` `r20260928-151130-0ead` passed on `269829d8`; `main` has moved since, and the new `main` merges into it cleanly.
- **Still waiting:** the cache-key commit (`cursor/agreement-key-policy-68dc`) for #134's rebase, and the soundness lane's computed status lines (§7 item 14).

What #130 brought, for reference:
- `tools/lean/` (`audit.py`, `Audit.lean`, `Replay.lean`, #112's `setup.sh`, the controls);
- a `lean-audit.json` per package (11, 49 and 9 pins);
- the `lean-audit` step in `check`;
- the `AGENTS.md` "Lean" section and the `lean-proofs` skill.

The train D audit's flag on the pre-#118 Merkle pins is how the vacuous `Collision` came to light (§2.3). The pins were re-recorded on #146's extractor statements, with red-team-flock-3 as statement reviewer and flock-verifier confirming intent.
