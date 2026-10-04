---
id: lean/20261004T2112Z-draft-lean-from-first-principles
campaign: lean
lane: lean
kind: draft
status: open
repo: danielreuter/verity
origin: bc-19c498a8-628e-5c04-8f61-fe785a24741b
---

# Our Lean, from first principles

Daniel asked (Oct 1, 10:42 AM PDT) whether "property" is first-class, whether the Lean audit is old ritual, and for the
most elegant way to handle our Lean. This is @lean's answer and proposal. It supersedes the API sections of
`lean-infrastructure.md` (that document's measurements and sig.golf comparison still hold).

## The short answer

The audit's core is not ritual. Three facts are the only reason a Lean theorem we cite means anything, and two incidents
show they don't hold by themselves (#118 made `merkle_binding` vacuous by redefining `Collision`; every one of the 1,037
records on `main` has an empty assumptions list, because of a bug in how they are read that my footprint branch fixes). Around that core, a swarm grew about a dozen
more checks, a per-package JSON config with nine different kinds of section, and records up to 939 KiB (the repository's
256 KiB file cap has a 2 MiB exemption just for them). Most of that duplicates the kernel replay, defends against an
attacker we don't model, or is configuration that a fixed layout makes unnecessary.

The elegant version is one fixed layout, one generated lockfile per package, and one review rule. Nothing about Lean is
hand-configured. The only hand-written files are Lean source.

## What Lean is for here

A Verity claim (a certificate in Python, a table row, a docs-site entry) is worth what its Lean guarantee is worth. For a
cited guarantee to be worth anything, three things must hold:

1. **It is proved.** The kernel accepted the proof, and the proof uses only Lean's three standard axioms (`propext`,
   `Classical.choice`, `Quot.sound`). The machine checks this completely.
2. **It says what we think it says.** Its statement, and every definition the statement reads, is what a person reviewed.
   No machine can judge that. A machine can make sure nothing changes without a review.
3. **Its assumptions are visible.** Everything it rests on without proof is named in the statement, so a reader sees the
   whole list. A machine can list them. A person judges whether they are believable.

Since the kernel checks proofs, **a proof never needs a human review**: only statements and the definitions they read do.
This also answers "what is an important change": one that changes what a guarantee says or what it assumes. Nothing
else is.

## The vocabulary: four first-class things

- **Definition:** the model a guarantee talks about: the protocol, the game, the adversary class, the hardware step.
- **Assumption:** a Prop we believe but don't prove, such as collision resistance of SHA-512 or a platform's step
  semantics. When it is about a primitive, it carries a `verity.claims` id (`cr/sha-512`).
- **Guarantee:** a Prop we prove, stated as "these assumptions imply this conclusion".
- **Proof:** a theorem whose type is exactly one guarantee.

"Property" is not first-class. It just means "a Prop", which is a word we use, not a role. The two roles a Prop can play
are assumption and guarantee. "Pin" also stops being a concept: the lockfile records every guarantee, so there is nothing
to pin by hand.

A precondition on inputs (core's `StepInputs`) is not an assumption. It is part of the definition the guarantee is
about, and it lives with the definitions. A Prop we intend to prove but haven't (`HmRowComputes`, PoUS's `LemmaA`) is an
open guarantee, not an assumption. The lockfile marks it `open`. Nothing may cite it until it is proved, but another
guarantee may take it as a premise, and then that premise shows in its footprint.

## The design

### One layout, the same in every package

~~~text
<Pkg>/Protocol.lean        definitions (trusted)
<Pkg>/Assumptions.lean     one `def A : Prop` per assumption (trusted)
<Pkg>/Guarantees.lean      one `def G : Prop` per guarantee (trusted)
<Pkg>/SecurityProofs.lean  one theorem per guarantee; everything else: lemmas, sanity witnesses (never reviewed for meaning)
~~~

These are four names (Daniel, Oct 1), and any of them may be a folder: `X.lean` alone, or `X.lean` importing files under
`X/`. The tools treat everything under `X` as `X`. A file is Lean's unit of building and caching: an edit re-checks the
whole file and then everything importing it, and independent files build in parallel. So split where it saves rebuilds.
`SecurityProofs` will be a folder almost everywhere, since that's where PoUW's and soundness's 58,000 lines live, and
separate files also keep parallel agents out of one another's way. Splitting `Protocol` saves rebuilds only when proofs
import just the parts they use. A review reads the diff, so splitting costs it nothing. Executables (the Flock verifier's binary, PoUS's
grader, PoUW's conformance runner) are separate Lake libraries in the same package.

**The one structural rule: a trusted module imports only trusted modules** (its own package's, or a required package's)
and pinned dependencies (Mathlib, ArkLib). The trust boundary then follows by construction: a guarantee's statement can
only read trusted text, so the git diff of the trusted files is exactly what a reviewer must read. No `layers`, `roots`,
`exempt` or `reads` configuration is needed.

PoUS and PoUW are already halfway there. Their `Pinned` modules hold `def X : Prop`, and their proofs are typed
`Proofs.X : Pinned.X`. PoUS's grader already requires a solution's type to be syntactically the pinned constant. The
design makes that pattern the rule everywhere.

### Examples

PoUS today has two roots (`Pous/`, `PousProofs/`), a `PousTargets.lean`, a `Pous/Sanity.lean` and `Grader/`, and its 30-odd
guarantees sit in one 698-line `Pous/Pinned.lean`. Proposed:

~~~text
protocols/pous/lean/
  Pous.lean                        imports the four below
  Pous/Protocol.lean               imports Protocol/*
  Pous/Protocol/Game.lean          today's Game/Oracle, Game/Prob
  Pous/Protocol/Scheme.lean        today's Model/*: Scheme, Labelling, HashChain, Pebbling, M1, ...
  Pous/Protocol/Params.lean        today's Accounting/Params, Numbers
  Pous/Assumptions.lean            B1Prime (and, later, P2's hardware cost bound)
  Pous/Guarantees.lean             imports Guarantees/*
  Pous/Guarantees/Theorem1.lean    Theorem1ii, Theorem1iiTimed, Theorem1iTimed, ...
  Pous/Guarantees/TrackA.lean      A1CompressionCard, A3Prime, A6Rederive*, ...
  Pous/Guarantees/Pebbling.lean    B1IndepSet, B2Stacking, B3Chain, M1Meets
  Pous/Guarantees/P2.lean          the six P2 guarantees
  Pous/Guarantees/Sanity.lean      the assumptions are satisfiable; Meets isn't vacuous
  Pous/SecurityProofs.lean
  Pous/SecurityProofs/Theorem1/... one folder per Guarantees file, mirroring it
  Pous/SecurityProofs/TrackA/...   (the generated 54,000-line Chain/Flat.lean lives here)
  Pous/SecurityProofs/Sanity.lean
  Grader/Main.lean                 its own Lake library: an executable, outside the four
~~~

Soundness, as a sketch:

~~~text
FlockSoundness/Protocol/...                Types, Model, Session*, Rounds, Randomness, PlanDraw
FlockSoundness/Assumptions.lean            SHA512ExpectedTimeCR, UniformRandomBytes, ...
FlockSoundness/Guarantees/Soundness.lean   the end-to-end bound (flock_e2e_count)
FlockSoundness/Guarantees/Binding.lean
FlockSoundness/Guarantees/ZK.lean
FlockSoundness/SecurityProofs/...          Refine, Audit, Rope, Accounting, ...: about 150 files
~~~

Why each choice:

- **The same four names at the top of every package**, so a reader, a reviewer and the tool find the trusted text without
  configuration.
- **`Guarantees/` split by topic:** a reviewer of Theorem 1 reads one short file, two lanes adding guarantees on different
  topics don't touch the same file, and a citation such as `Pous.Guarantees.Theorem1ii` says where to look.
- **`SecurityProofs/` mirrors `Guarantees/`:** a guarantee's proof is under the folder of the same name. The lemmas
  underneath are arranged however their authors like.
- **`Assumptions` stays one file** while it can: everything we assume, in one place.
- **Sanity facts are guarantees:** "the assumptions are jointly satisfiable" and "`Meets` isn't vacuous" are what a
  reviewer should read, because they are what catches a vacuous redefinition like #118.
- **Open targets are guarantees without a proof yet:** `PousTargets.lean` disappears, and the lockfile marks them `open`.
  `LemmaA` moves to `Guarantees/` if PoUS means to prove it; if we'll only ever assume it, it stays in `Assumptions`.
- **One root per package:** `Pous/SecurityProofs` replaces `PousProofs/`.
- **Executables are their own Lake libraries:** the grader, the Flock verifier's binary and PoUW's conformance runner are
  programs, neither statements nor proofs.

### What the tool checks

`lean-audit` has no configuration. For each package it:

1. **Builds everything** with `lake build`, and fails if any `.lean` file is in no library.
2. **Replays every declaration through the kernel**, from the `.olean`s. This catches anything that reached the
   environment without the kernel's approval (`debug.skipKernelTC`, `addDeclWithoutChecking`, a tampered `.olean`).
   #700 replays each declaration as its own task. On a 4-core VM that took PoUW's replay from 1,242 s to 395 s (2 threads
   did as well as 4, so a pod's gain is unmeasured), at 3.5 GiB more peak memory.
3. **Checks axioms:** every proof uses only the three standard axioms, which rules out `sorry` and `native_decide`, and
   the package declares no `axiom`.
4. **Checks the boundary:** the import rule above. Each `def` in `Guarantees.lean` and `Assumptions.lean` is a Prop.
   Each guarantee has at most one proof: a theorem whose type is syntactically that guarantee.
5. **Regenerates the lockfile and compares it** with the committed one. Any difference fails, and `lean-audit --update`
   writes the new one.

### The lockfile

There is one `guarantees.lock` per package. It is generated, sorted and line-oriented, so git merges added guarantees
without a custom merge driver:

~~~text
toolchain  leanprover/lean4:v4.34.0
dependency mathlib  rev 8f2c41d0  oleans 3a9e7710
assumption Pous.Assumptions.B1Prime        a41c09e2
assumption Pous.Assumptions.ShakeIdeal     5be0c3d1  claim ro/shake256
guarantee  Pous.Guarantees.LemmaA          9d02aa7e  open
guarantee  Pous.Guarantees.P2Soundness     77d0f1b3  proved  assumes B1Prime LemmaA ShakeIdeal
escape     Pous.Protocol.decode            implemented_by Pous.Protocol.decodeFast
~~~

(The names and the claim id are illustrative.)

- **The hash** of a guarantee or assumption covers its elaborated statement and every trusted definition it reads,
  transitively. Its diff names exactly which guarantees changed meaning, and that includes a toolchain or Mathlib bump
  that changes elaboration without changing a line of source.
- **`assumes`** lists everything unproved that appears as a premise of the statement: assumptions, and open guarantees
  such as `LemmaA`. Because no `axiom` exists, nothing in a proof can add one, so the list is complete. It is the
  footprint, now visible in the diff of every change. When `LemmaA` is proved, `P2Soundness` can drop the premise.
- **`escape`** lists every `opaque`, `partial`, `implemented_by` and `extern` in trusted text. For an executable such as
  the Flock verifier, these are where the running code can differ from the definition proved about, so a new one is a
  reviewed change, not a line in a hand-kept list.
- **`dependency`** lines record each pinned dependency's revision and a digest of its `.olean`s, so a different Mathlib
  build can't slip in under the same manifest.

### The one review rule

A change to a package's trusted files or to its `guarantees.lock` needs @lean's review. Nothing else in Lean does. This
replaces "a changed record needs a named statement reviewer, who reads what `--update` prints, and the merge handoff names
them". The trigger is mechanical: `research merge` can see from the diff whether a review is due.

**Citation follows from the layout:** anything in `Guarantees.lean` marked `proved` is citable, and nothing else is. A
test in each consumer checks that the names it cites are proved guarantees in the lockfile. Internal lemmas are not
guarantees and need no review when restated. Today PoUW pins 665 theorems, and only about 22 of them are named anywhere
outside its Lean directory.

## What goes, and why

| Today | Why it goes | Where it goes |
|---|---|---|
| `unchecked` source scans (`skipKernelTC`, `addDeclWithoutChecking`, ...) | The kernel replay rejects any declaration they could produce | Nowhere for our modules; for dependencies, the steward's nightly `audit.py --fresh` (`leanchecker --fresh`) |
| `declared` | An axiom a proof uses already fails the axiom check | One line of the axiom check |
| `compile_time`, `tamper`, the build sandbox | They defend against an agent deliberately writing build-time code to fool the auditor | Nowhere, if Daniel agrees with the threat model below |
| `escapes`, `exempt`, `layers`, `roots` (per-package config) | The layout and the import rule decide all of them | Generated into the lockfile, or gone |
| `pins` (a `type_hash` each) and `reads` (up to 939 KiB a package) | Every guarantee is in the lockfile, at about 100 bytes a line | `guarantees.lock` |
| `merge.py` and its git merge driver | A sorted, line-oriented lockfile merges with plain git | Nowhere |
| `runs` (PoUW's compiled conformance checks) | These test the model against hardware captures; they check no proof | PoUW's test suite |
| The controls on every audit miss | They test the auditor, which only changes when `tools/lean/` does | The `tools/lean` test suite, cached on its inputs (#700 currently does the reverse; I'm fixing that there) |
| `upstream` watch | It stays: it is the only way we learn ArkLib proved something we assume | Soundness only (#699); it can only change when a manifest changes |

I expect what remains to be about 400 lines of Python and 400 of Lean, down from about 2,600 today plus a per-package
config.

**The threat model this assumes:** we guard against our own agents' mistakes and their pressure to make things pass, not
against an agent deliberately attacking the auditor. Everything we've actually seen (a vacuous definition, invisible
assumptions, statements renamed instead of retired, `sorry`, `native_decide`) is of the first kind. A deliberate attack
on the build would be code committed in plain sight, and we'd treat it as an incident, not as something every commit's
check must stop. For outside submissions, such as PoUS's challenge, the
right tool is a separate, sandboxed comparator at the grader (lean4export plus a second kernel), not four bespoke checks
on every commit.

## What it buys

- **Review surface:** the trusted files, the same for every package and readable in a fixed order. Statement review
  becomes reading a diff of `Protocol`, `Assumptions.lean` and `Guarantees.lean`.
- **Speed:** builds can stay warm between runs (Lake rebuilds only what changed, and the replay re-checks every
  declaration whatever the cache holds). A one-file change to soundness then costs an incremental build plus a parallel
  replay, instead of the cold build it pays today (about 9 minutes for the three Flock packages on 4 cores). A Lean
  change no longer re-runs the controls. And no Python suite needs a package's `lean/` in its cache key, which fixes the
  friction Daniel flagged (a record change re-running 20 suites).
- **Merges:** no 939 KiB JSON conflicting on every rebase, and no custom merge driver.
- **Honesty about size:** soundness's 192 pins read 1,511 definitions in 123 modules. The layout forces those definitions
  either into `Protocol`, where their size is visible, or out of the statements. Either is better than now.

## Migrating without a mass review

The migration is mechanical where meaning doesn't change. For each old pin, the new guarantee's statement must hash the
same as the old record's `type_hash`, up to the renamings the move records (a definition moved into `Protocol` changes
its name, not its meaning). The migration tool checks that, so a package moves with no statement review except for what
it actually restates. The order:

1. Core (18 pins), the pilot, in one PR with the new tool.
2. The network warden (31) and PoUS (66), whose layouts are closest already.
3. PoUW (665): its owner picks which theorems are guarantees, and the rest become lemmas in `SecurityProofs`.
4. The verifier and level3 (65).
5. Soundness (192), last, on a pod (it needs ArkLib), together with shrinking its trusted surface.

`lean-audit.json` and the old checks stay until the last package moves, so nothing is unaudited in between.

## Daniel's rulings (Oct 1)

1. **The threat model:** we guard only against our agents' mistakes, not against a deliberate attack on the auditor. So
   the build sandbox and the compile-time and tamper checks go.
2. **The review surface:** `Protocol`, `Assumptions` and `Guarantees`. Lemmas and proofs need no review.
3. **The layout:** the four names `Protocol`, `Assumptions`, `Guarantees` and `SecurityProofs`, any of which may be
   `X.lean` plus `X/` where that helps building and caching.

Still open: the go-ahead for the core pilot.
