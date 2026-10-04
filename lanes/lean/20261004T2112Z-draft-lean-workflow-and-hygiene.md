---
id: lean/20261004T2112Z-draft-lean-workflow-and-hygiene
campaign: lean
lane: lean
kind: draft
status: open
repo: danielreuter/verity
origin: bc-19c498a8-628e-5c04-8f61-fe785a24741b
---

# Lean in Verity: workflow and hygiene for the refactor

@lean's opinionated draft for Daniel, 4 Oct 2026, 19:55Z. It is written for the refactor, and per Daniel's note (19:56Z)
it derives each rule from what a guarantee needs, rather than carrying today's practice over. It builds on
`note:lean/20261004T2112Z-draft-formal-verification`, `note:lean/20261004T2112Z-draft-lean-from-first-principles` (the
layout and threat-model rulings of 1 Oct) and
`note:lean/20261004T2112Z-draft-lean-validation-picture` (today's names, the life of a guarantee,
the two TCBs). The Theorem survey it draws on is
`note:lean/20261004T2112Z-draft-theorem-labs-survey`. The decisions for Daniel are at the end.

## 0. The test every rule has to pass

A table, a ledger or a docs page cites a guarantee as (G, its lock digest D, the commit C). That citation is worth
something only if four things hold:

1. **Proved.** The kernel accepted a proof of G from `propext`, `Classical.choice` and `Quot.sound` only. A machine
   checks this completely.
2. **Means what we say.** G's statement, and every definition it reads, is what we think it is. Only a person can judge
   that; a machine can make sure no change to it goes unseen.
3. **Rests on visible, non-vacuous assumptions.** Everything unproved is a named hypothesis in G's statement, and the
   hypotheses can actually be satisfied. Otherwise G is true for the wrong reason.
4. **Describes the code we run.** The Python (and the GPU kernels, and C-Flock's executable verifier) computes what
   the spec's definitions say. A perfect proof about the wrong function is worth nothing.

Everything else in this guide exists for one of those four, or to make them fast. **The refactor's test for any piece of
today's Lean machinery: name which of the four it serves. If none, it goes; if one, rebuild it for that purpose, not as
it is.**

We're strong on (1): the validator replays every declaration through the kernel, which xv6-lean doesn't. We're decent on
(2): the spec lock, and the DM on change. We're weak on (3): nothing checks that assumptions are satisfiable, and #118
made `merkle_binding` vacuous exactly that way. We're weakest on (4): fixed, hand-picked vectors are our only
Python–spec link outside PoUW. Today's C/D/F rulings came from a person reading. `check_tile` refused fewer rows than
`OperandOK`, `parse_row` admitted fewer words than the spec, and `rows4` disagreed with Python on −0. No vector caught
any of them.

## 1. The fractional-proofs post: what to take from it

Jason Gross's [post](https://theorem.dev/blog/catching-bugs-with-fractional-proofs/) does the following:
- states an end-to-end property as a property-based test (Hypothesis);
- decomposes it along the lines a proof would take, into sub-properties whose input spaces are small;
- tests those sub-properties.

A bug that is one-in-a-billion at the top is common at the leaf it lives in. That's how they found the XLA:TPU
excess-precision bug in seconds.

**What's right:**
- The decomposition, not the sampling budget, is what finds rare bugs.
- Proof structure tells you where to cut.

**What's missing:** the post's third stopping rule is "the sub-properties provably compose to the full property". The
post argues that composition in prose; it doesn't prove it. The "logarithmic in rarity" claim rests entirely on it, and
on each leaf's test distribution actually reaching the bug region. It's a heuristic, not a bound.

**What we can do that they can't:** prove the composition. Our guarantees are already proved from lemmas about small
definitions (a tile, a row, a word, a step). So our version is:

> **Lean proves "leaf definitions ⇒ guarantee". Python is tested against the leaf definitions, on inputs that a
> spec-shaped strategy generates. A pass covers exactly the clauses the proof uses, and the step from the leaves to the
> top is a theorem.**

Our version is strictly stronger than theirs, and it costs us a test harness, not research. §5 makes it concrete.

**Tools:**
- **Hypothesis:** adopt it, in Python suites, under the rules in §5. It isn't in the workspace today.
- **Lean's `plausible`** (Mathlib ships it): use it in the inner loop to try to falsify a statement before proving it.
  It never goes in the validator, because it is evidence, not proof.
- **Not:** Theorem's GitHub Actions setup, its per-module `STATUS.md` files, or review packets in Git. Our notes policy
  and content-keyed `check` are better.

## 2. Layout

Settled on 1 Oct, restated so this guide stands alone:
- Every spec has `Protocol`, `Assumptions` and `Guarantees` (trusted, read) and `SecurityProofs` (math, never read).
- Any of the four may be `X.lean` plus an `X/` folder.
- The one structural rule: **a trusted module imports only trusted modules** and pinned dependencies. The trust
  boundary then follows by construction, and no configuration is needed.

First-principles additions:

- **Lake packages split only where `require`s differ.** A package boundary costs a manifest, a build and a cache key,
  and buys only a different dependency set. Caching and parallelism come from modules, not packages.
- **The module is the unit of building, caching and ownership.**
  - Use exact imports, and no umbrella imports inside the math (`lake shake`, with a `noshake.json` of exceptions).
  - Have one assembly file per guarantee (`theorem SecurityProofs.G : G`), mirrored under `SecurityProofs/` by the
    `Guarantees/` file it proves.
  - Split a file when it rebuilds too much or too slowly (§7), not when it "feels long".
- **Executables are separate `lean_lib`/`lean_exe`s in the same package:** C-Flock's verifier binary, PoUS's grader
  and the spec runner (§5).
- **Generated Lean lives in files of its own,** marked generated, with its generator beside it. Examples are PoUS's
  54,000-line `Chain/Flat.lean` and the vector theorems. It is never hand-edited, and `check` regenerates it and diffs.

## 3. Writing a spec

A spec is the only Lean anyone reads, so it is written for a reader.

- **One form per layer.** A subprotocol's guarantee is `Sound g accept E δ` over core's probability. An accounting or
  classification guarantee is a deterministic consequence of subprotocol guarantees plus its own assumptions. A new
  probability definition is a bug: there are four today, and the refactor moves them onto core's, proving equality
  first.
- **Parameters, not constants.** Census numbers (peak FLOPs, HBM size, link bandwidth) and policy values (δ, ρ, λ) are
  parameters of the guarantee. A citation names their values, and a guarantee holds at every value it allows.
- **Assumptions are explicit hypotheses**, each a named `Prop` in `Assumptions` with a rationale and, for a primitive,
  a `verity.claims` id. Never put one in a class field or an instance, where a reader won't see it in the statement.
- **Every assumption bundle has a sanity guarantee.** For each guarantee `A₁ → … → Aₙ → C`, its spec has
  `Sanity.G : ∃ (params), A₁ ∧ … ∧ Aₙ`. Where C is `∀ x, P x → Q x`, it also has `∃ x, P x`.
  - For an assumption about a concrete primitive (SHA-512's collision resistance), witness it at the abstract level:
    some function satisfies the Prop's shape. That doesn't make the assumption true. It does rule out the Prop being
    contradictory or empty, which is exactly #118's failure.
  - The validator checks that each guarantee with assumptions has its sanity guarantee in the lock. This is the
    one new gate this guide proposes.
- **Twinned definitions are executable.** A `Protocol` definition that has a Python twin must be computable, and a
  predicate must be `Decidable`. Examples are `OperandOK`, `RowOK`, a codec, a draw, or a leaf rule.
  - When the readable definition can't be computable (it uses `ℝ` or a `Finset` sum), the spec states it readably, and
    the math gives an executable twin with `theorem exec_eq : exec = spec`.
  - Keep `ℝ` for the statements about probability and bounds, never in a definition Python implements.
  - This is what lets §5's spec runner run the spec itself.
- **Reserve targets before proving.** A planned guarantee goes into `Guarantees` as an `open` entry in the lock first:
  its name, its statement and its plain reading, quoting the paper or Python docstring it formalizes. That's the finish
  line, it lands (and DMs) in its own small PR, and the proofs follow.
- **Every guarantee has a plain reading:** a docstring of one to three sentences saying what it promises, in words a
  protocol reader would use. The DM shows it, and a PR that changes the guarantee repeats it in its body.
- **Never weaken to finish.** Changing a statement to make a proof go through is a spec change. It goes in the PR body
  as one ("narrowed X to Y because Z"), never only in the diff. The lock makes it visible; the rule makes it said.

## 4. Writing math

Nobody reads the math, so its hygiene is about build time and surviving a bump, not style.

- **The validator rejects** `sorry`, declared axioms, `native_decide`, kernel bypasses and orphan files. Agents don't
  need to remember these.
- **Survive Mathlib bumps:**
  - no bare non-terminal `simp` (use `simp only [...]`, or `simp?` to produce it);
  - no `decide` on large propositions except generated vector theorems (`decide +kernel`, §5);
  - prefer named Mathlib lemmas over `omega`/`aesop` chains in hot files.
- **Heartbeat raises are budgeted.** A `set_option maxHeartbeats` above the default needs a one-line reason beside it,
  and the validator reports every raise with that file's elaboration time (§7).
- **A hand-proved lemma that a dependency could prove gets an upstream-watch entry,** so we learn when ArkLib or Mathlib
  proves it.
- **Probe before proving:**
  - `plausible` on the statement;
  - `#eval` the executable definitions on a few inputs;
  - `exact?` and `trace_state`.

  The inner loop is `lake env lean` on one file, in a checkout of your own (`.lake` is never shared).

## 5. Conformance: the Python is what the spec says

This is the biggest change, and where the post's lesson lands. There are three tiers. Only the first runs in `check`.

### Tier 0, in `check`: vectors, which Lean writes and both sides check

- **Lean is the source of truth for expected values.** A package's vectors file (JSON lines: definition, input,
  output) is produced by the package's spec runner (tier 1) from a list of inputs, never typed by hand. The generator is
  deterministic, and `check` regenerates the file and diffs it.
- **Python reads the vectors** in its own suite, which needs no Lean build. This keeps `lean/` out of every Python suite's
  cache key, which was Daniel's friction point.
- **Lean checks the same vectors in the kernel:** generated theorems `spec input = output := by decide +kernel` (or
  `rfl`), in a generated file under the math. Core's TC vectors (`Verity/TC/Vectors.lean`) already do this. PoUS's
  `PousRefCheck.lean`, which only `#eval`s and prints JSON, moves to it.
- **The inputs are chosen by clause.** For every twinned predicate, each clause has at least one input that passes and
  one that fails only on it. Today's C/D/F rulings asked for exactly this by hand ("one row per clause, both sides").
  Clause coverage becomes the rule, and the generator reports a clause without both.
- **Hypothesis's shrunk counterexamples from tier 1 are promoted here** as new vectors. That's the ratchet: a disagreement
  found once is checked forever, on both sides.

### Tier 1, off `check`: differential exploration against the spec

- **The spec runner.** Each spec package builds a `lake exe <pkg>-spec` that reads JSON lines (a definition name and an
  input) and writes the spec definition's value. It evaluates `Protocol` itself, or its `exec_eq` twin.
  - It isn't called an oracle: in our specs that's the random oracle (PoUW's and PoUS's games), and AGENTS.md calls
    `verity.evaluation.evaluate` "the IR oracle".
  - PoUW's compiled conformance runner (`PouwBulk`, 166,000 differential FP8 steps) is the seed. It is a test, not a
    proof, and it moves out of the validator's `runs` into this tier.
- **Hypothesis drives both sides.** Strategies are shaped by the spec's case split, not by uniform bits:
  - for a row predicate, one strategy per clause, biased to its boundary (non-finite, below the floor, a dead row,
    −0, a non-BF16-exact word);
  - for a codec, lengths at block edges.

  Python's output and the spec runner's are compared, and a disagreement is a finding.
- **It runs as a recorded `research run`**, budget-bound. It runs on every change to a twinned definition or its Python
  twin, and nightly with a fresh seed recorded in the run. A found disagreement becomes a finding label, a tier-0 vector
  and a fix, on whichever side is wrong (Lean is the source of truth for meaning, not for being right).
- **In-suite Hypothesis tests** (no spec runner) are allowed in `check` under a pinned profile:
  - `derandomize=True`, `database=None`, `deadline=None` (no wall clock, per `test_no_wall_clock.py`), and a fixed
    `max_examples`;
  - they are deterministic, so `check`'s cache stays sound;
  - they test properties the Lean proves about the twin, such as round trips, monotonicity or "refuses ⇒ some clause
    fails".

### Tier 2: fractional proofs, for what the spec runner can't run

Some things are too big for the spec runner: a whole GEMM, a model's forward pass, a probability over the verifier's coins,
GPU kernels against the Python reference. For these we do what the post does, with the composition proved:
- **Lean:** the guarantee is proved from leaf lemmas about small twinned definitions (a step, a tile, a row, one draw).
  The proof is the decomposition.
- **Python:** tier 0 and tier 1 at the leaves. Kernels are tested differentially against the Python reference, the way
  `verity.evaluation` already self-checks kernels.
- **Hardware:** silicon is tested against the leaf semantics by the probes and captures (A100/4090/H100), which are
  vectors too.

**Write the leaves first.** If a guarantee's proof doesn't factor through small executable definitions, the Python can't
be tested against it at a feasible cost. That's a spec design problem, best found before the math exists.

**Pilot:** PoUW's row admission (`OperandOK`/`RowOK`/`rows4` against `admissible`/`check_tile`/`parse_row`). The C/D/F
rulings are fresh there, and it would show whether tier 1 finds what the person reading found. I'd do the spec runner and
tier 0 for it, and compute-accounting owns the strategies.

## 6. Validation, the lock and the DM

As in the validation picture (`note:lean/20261004T2112Z-draft-lean-validation-picture`). In short:
- The validator replays every declaration and checks each locked guarantee's statement and digest.
- The spec lock protects as little as possible: the guarantees and the spec definitions they read, each with an
  `owner` (Daniel, 1:13 PM PDT, reversing "keep all 1,818"). Everything in `security_proofs/` keeps building and is
  checked as proved, but only guarantees' statements are locked.
- In the Glossary's terms (top, 20:41Z), a *guarantee* is a proved statement that a table, a ledger or a claim id relies
  on, and anything else proved is a *lemma*. Which of each package's pinned theorems are guarantees is with Daniel, and
  lock reductions wait for his ruling. My proposal (survey round 2): a theorem is a guarantee when a current document,
  table, claim or the docs site names it, or another guarantee's statement reads it. A PR body is history.
- When a guarantee's entry changes on `main`, Daniel and the owner get a DM (#1053).
- `verity/` holds only what a guarantee depends on, and everything else is in `experimental/` (Daniel, 1:30 PM PDT,
  replacing status labels). In Lean, experimental work, specs under development included, sits in `security_proofs/`
  unlocked. Promotion moves its modules into `verity/`'s spec package, names kept, together with their lock entries.
- **The reads check:** every definition a guarantee's *statement* reads lies in a spec module, core's spec or a
  pinned dependency. C-Flock is excepted until its spec is extracted.
  - Today's `layers` rule checks imports only, so this check is new. It is what makes the README's sentence true: a
    guarantee depends only on `verity/` and its named assumptions.
  - It checks statements, not proofs: a proof that uses any lemma is still a proof.
- The validator also *reports*, without failing, any spec definition that no guarantee reads. Each one is a candidate
  to move out of `verity/`.
- Lifting an inline pin (`theorem X : <expr>`) into `Guarantees` (`theorem X : Guarantees.X`) is a move. The validator
  certifies it when the new constant, unfolded once, hashes to the old entry's type hash.

Changes this guide adds:

- **Sanity guarantees** (§3): one new gate.
- **An adversarial reading on the DM, as an experiment.** A second model gets the DM's printout and the plain reading,
  read-only, and is asked "how could this statement be weaker than its plain reading says?". Its answer is attached to
  the DM. It's not a gate; by my estimate it costs about $1–5 a change at our sizes, not xv6-lean's $25 packets. Keep it if, over a month,
  it flags something real; retire it if not.
- **An independent kernel, nightly, on the guarantees:** lean4checker, or the comparator's second kernel. It guards
  against bugs in Lean's own kernel, which our replay can't catch. Too slow for every `check`; cheap nightly.
- **A move is one DM line** (`--moved` in `spec_alert`). This is needed before the directory move, so the DM stream stays
  readable.

## 7. Speed is a budget

- **Targets:** `check` under 45 minutes (ci's target). A Lean-only change validates incrementally: a kept build (#1119),
  then main's build cache (#1006), then a per-module replay cached under each `.olean`'s hash.
- **Every validation records each file's elaboration time.** The ten slowest files are visible in the record, and a PR
  that adds a file over the budget (I'd start at 120 s on the check machine) or doubles one is flagged in its tier, not
  failed. Generated files are listed separately.
- **The inner loop:** `lake env lean` on the file you're editing, plus `validate --changed` locally on the packages you
  touched, from main's cache. Nobody waits for `check` to learn that a proof is broken.

## 8. Agents in Lean

- **Claim before parallel work:** the guarantees and files you'll touch (`research notes claim`). Agree on the statement
  first: spec-first PRs (§3) make that the default.
- **Every Lean PR body reports** the guarantees it adds, changes or proves, each with its plain reading, plus the
  validator's verdict and the tier run.
- **Stuck means checkpoint.** When a proof design stalls, write down why in a finding, and let a fresh attempt start
  from the finding rather than from the stalled state.
- **Owning review isn't gating review.** @lean answers questions about statements, but merges wait on the validator,
  not on @lean.

## 9. Learning over time

The rule is a ratchet: **every escape adds the mechanical check that would have caught it.** A prose rule is added only
when no mechanical check is possible.

- **Every escape gets a finding.** An escape is a bug a layer should have caught and didn't. The finding is a store
  label or a notes finding, never a repo doc. It is tagged with the guarantee need it broke (§0's 1–4) and with the
  layer that missed it: spec, sanity, conformance tier, validator or speed.
- **The fix goes in the same PR or the next:** a vector, a strategy, a sanity guarantee, a validator rule or a budget.
- **@lean reviews the escape list weekly, in a line or two:**
  - which need is leaking;
  - which check has never fired and costs time, which is a candidate to retire (`process-design`);
  - whether a tier earns its runs.
- **The numbers we track:**
  - check and lean-validate wall time per train;
  - tier-1 disagreements found per week;
  - DMs per week, and how many were reverted (a revert means the after-the-fact review caught something);
  - escapes per need.

The escapes on record, to seed the list:

| Escape | Need | Layer that missed it | Mechanical fix |
|---|---|---|---|
| #118: `Collision` redefined, `merkle_binding` vacuous | 3 | sanity | sanity guarantees (§3) |
| Every record had an empty assumptions list (a reader bug) | 3 | validator | footprint in the lock, with a control |
| C/D/F: `check_tile`, `parse_row` and `rows4` differed from the spec | 4 | conformance | spec runner, clause-covered vectors, tier 1 (§5) |
| b201: an auditor-only change rebuilt every package (69 min) | speed | validator | kept builds (#1119), key on reads only (#1117) |

## 10. The refactor: rebuild, don't port, and lose nothing

Two of Daniel's rulings shape this section. The first is the note of 19:56Z: rebuild from first principles. The second
is 12:51 PM PDT: nothing is lost, and the Lean goes first. Cleanup consolidates and never deletes a result. Retired work
keeps building, labelled with its reason, until keeping it costs more than it teaches; then it goes to `archive/` with
its record and last-good commit. Daniel added at 1:06 PM PDT that superseded infrastructure can be deleted, while math
results, constructions and kernels are decided case by case, preferring consolidation.

**The order** (Daniel, 1:06 PM PDT: everything except the specs moves into `security_proofs/`, and the specs stay;
posted to top's thread 1791143698.815249):
1. **The validator change, first,** piloted on core's package. It has four parts:
   - cross-package validation: a `security_proofs/<area>` package validates against its spec's lock, with the lock and
     spec in one Lake package and the pinned theorems in another;
   - the reads check;
   - an `owner` on each entry;
   - lift certification.
2. **Split at the move: core, NCI, the warden, PoUS and PoUW.** On `main` (4 Oct), each one's spec modules import nothing
   else of its package, and every pin reads only them.
   - The spec stays in place with its lock. The math becomes a Lake package under `security_proofs/<area>/` that
     `require`s the spec.
   - Module names are kept, so every pin and read entry is byte-identical and no DM fires.
   - The lock's package-level sections (`roots`, `layers`, `dependencies`) are split between the two packages, and each
     umbrella root moves to the math package.
   - PoUW's one spec module under the math's name (`Pouw.SecurityProofs.Dimension.Lifting`) stays with the spec.
3. **C-Flock's level3 and soundness move whole** to `security_proofs/flock/`. None of C-Flock's packages declares a spec
   yet, and soundness's pins read 285 of its 561 modules. Its spec comes out once proofs names the trusted subset. The
   executable verifier is runtime code and stays with C-Flock.
4. **Later, with `--moved`:**
   - lift the inline pins that are guarantees into `Guarantees`. These are mostly PoUW's: 768 of its 793 pins state themselves inline in
     the math, and they're locked meanwhile;
   - extract C-Flock's spec.
5. **Inside `security_proofs/`, consolidate the math freely.** It's untrusted: every lock entry has to keep its statement
   and validate, and that's the whole guard. Consolidation that changes a spec (the two FP32 models, the four game
   models) is a change of meaning, shown in full.

**Consolidating shared definitions** (FP semantics, the probability and game models, circuits) means adding the new
definition beside the old one, plus a bridge theorem (`old = new`, or a refinement). Then guarantees move to the
new definition. The old one and whatever reads only it stay in `security_proofs/`, unlocked, with the retirement
recorded in the area's `DESIGN.md`. They keep building, because nothing retired is ported. With kept builds and the cache they cost about nothing per check, and their cost comes due only at
a toolchain or Mathlib bump.

| Today | Rebuilt as | Why |
|---|---|---|
| `lean-audit.json`, 1,818 entries, config sections | the spec lock: guarantees only, each with an owner, no config | need 2 only for guarantees; the layout replaces config |
| four probability models | core's one, bridged by theorem; the old ones retired, still building | one meaning of "probability at most δ", nothing lost |
| PoUS's `#eval` JSON check, hand-kept vectors | the spec runner, generated vectors, kernel-checked | need 4, and Lean as the source of truth |
| PoUW's `runs` (compiled conformance in the validator) | tier 1, a test in PoUW's suite | it's a test, not a proof; it slows validation |
| statement reviewer, grants | the DM, plus the adversarial reading experiment | #1053 |
| "sanity" as a convention in PoUS only | a sanity guarantee per guarantee with assumptions, checked | need 3 |
| Lean-checked facts about the Python, but no executable spec | twinned definitions executable, or with `exec_eq` | so the spec can be run against the code |

**Hygiene for the move itself: never both in one PR.**
- A PR is either a **pure move** (same statements under the old names, certified by `--moved`, one DM line) or a
  **meaning change** (shown in full in the DM).
- A first-principles rebuild that changes meaning lands as its own PR after the move, so every change of meaning is seen
  on its own.
- That's what makes rebuilding safe at this scale. Module names stay when directories move, which keeps the move pure.

## Decisions for Daniel

1. **Conformance tiers (§5):** adopt the spec runner, generated clause-covered vectors and Hypothesis exploration, piloted on
   PoUW's row admission. *Recommend yes.*
2. **Executable twins (§3):** a `Protocol` definition with a Python twin must be computable, or carry `exec_eq`.
   *Recommend yes.* It applies as each spec is rebuilt, not retroactively.
3. **Sanity guarantees as a validator gate (§3):** *Recommend yes*, at the abstract level for primitive assumptions.
4. **Spec-first PRs (§3):** open guarantees land before their proofs. *Recommend yes*, as the default, not a gate.
5. **Adversarial reading on DMs (§6):** a one-month experiment, kept only if it finds something. *Recommend trying it.*
6. **Never both (§10):** moves and meaning changes in separate PRs during the refactor. *Recommend yes.*
