---
id: lean/20261004T2112Z-draft-theorem-labs-survey
campaign: lean
lane: lean
kind: draft
status: open
repo: danielreuter/verity
origin: bc-19c498a8-628e-5c04-8f61-fe785a24741b
---

# Theorem (theorem.dev) public GitHub survey: Lean practice and Python↔Lean equivalence

Read-only survey, 4 Oct 2026. Repos were cloned shallowly to `/tmp/th` on the worker VM. Nothing was posted anywhere.

## (a) Hypothesis for Python↔Lean equivalence: not found

None of Theorem's public repos uses Hypothesis to test Python code against a Lean spec. A strict search of every
cloned repo (`from hypothesis`, `import hypothesis`, `@given(`, `hypothesis.strategies`, a Hypothesis dependency pin)
returned zero hits. The only `hypothesis` matches are the English word, plus prose in the upstream tinker-cookbook
skill file.

Hypothesis does appear in exactly one public Theorem artifact, and not as a Lean bridge. The blog post
[Catching bugs with fractional proofs](https://theorem.dev/blog/catching-bugs-with-fractional-proofs/) (Jason Gross,
Oct 2025) recommends Hypothesis ("If you code in Python, I highly recommend the Hypothesis framework") and shows
`@given` tests of JAX `lax.approx_max_k` and vLLM. Its idea is to state a theorem as an end-to-end property-based test,
decompose it into sub-lemmas the way a proof would, and run each sub-lemma as a cheap unit-level PBT. No Lean is
involved, and the Colab notebooks it links were not inspected.

Theorem does keep Python and Lean in agreement in one place, `xv6-lean`, and the direction there is the reverse of a
PBT. Untrusted Python generators compute values and emit them as Lean literals plus `theorem … := by decide` leaves, so
the Lean kernel re-derives every value from the Lean reader (see §1).

The adjacent paper [FVSpec](https://arxiv.org/html/2606.01008) (Hypothesis PBTs translated into Lean specs) is by
Galois and Forall R&D, not Theorem. Its authors say the translation is lossy and not equivalence-checked.

## (b) Org identification and repos

- **The org is [github.com/theorem-labs](https://github.com/theorem-labs) (display name "Theorem", blog field
  `https://theorem.dev/`).** It is confirmed in both directions: the theorem.dev home page and blog header link to
  `https://github.com/theorem-labs`, and the org's profile links back to theorem.dev.
- The YC listing ([ycombinator.com/companies/theorem-2](https://www.ycombinator.com/companies/theorem-2), S25, SF,
  "program equivalence driven development") and VentureBeat's $6M seed article match. The only public member is
  `JasonGross` (Jason Gross, fiat-crypto), and the xv6-lean commits are by `Jason Gross <jason@theorem.dev>`.
- `theoremdev` and `theorem-dev` are empty orgs described as "Alias for @theorem-labs". `theoremlabs` is an unrelated
  "Web3 social" org with no repos.
- There are 25 public repos. Most are forks with no commits ahead of upstream on their default branch (lean-zip,
  lean-zip-common, nanoda_lib, rocq-lean-import, VST, …).

The repos with original or Theorem-branch work:

| Repo | What it is |
| --- | --- |
| [xv6-lean](https://github.com/theorem-labs/xv6-lean) | The main Lean project: a port of MachCSL and the xv6 verification. Iris-lean, no Mathlib, Lean 4.32.2, 44 commits. Written by OpenAI Codex agents on Jason's behalf (README footer). |
| [lean-sail](https://github.com/theorem-labs/lean-sail) | Fork of rems-project/lean-sail. Theorem's work is on branches: `xv6-free-v1` is 3 commits ahead and `free-v1-generator-prototype` 7. |
| [lf-lean](https://github.com/theorem-labs/lf-lean) | The Rocq→Lean verified-translation benchmark: Lean translations, round trip via lean4export and rocq-lean-import, and Rocq isomorphism proofs. |
| [rocq-structured-output-print-assumptions](https://github.com/theorem-labs/rocq-structured-output-print-assumptions) | A Rocq plugin: `Print Assumptions JSON` for graders. |
| [lean-zip](https://github.com/theorem-labs/lean-zip) | Mirror of **kim-em/lean-zip** (Kim Morrison's). Its 947 branches, including the `agent/*` ones, all exist upstream too, so it is not Theorem's practice; it is cited below as upstream inspiration only. |

There is no public `rocq-dove` (the spec generator and grader from the lf-lean post) and no Python↔Lean product code.
The YC launch's "Python to Rust while proving no functional change" is product work with no public repo.

## (c) Findings

### 1. Python↔Lean (and cross-system) conformance

- **The xv6-lean pattern: untrusted Python computes, Lean checks with kernel `decide`.**
  [`tools/inode_certificates.py`](https://github.com/theorem-labs/xv6-lean/blob/main/tools/inode_certificates.py) and
  its siblings (`bitmap_`, `directory_`, `symbol_certificates.py`, `user_files.py`, `images.py`) work like this:
  - Each tool checks the source repo's git revision and blob against `upstream.lock.json`, plus a SHA-256 and size of
    the raw image.
  - It computes values in Python and also runs a host-side validity check, labelled "diagnostic only; all Lean leaf
    proofs mandatory".
  - It writes `Xv6/Generated/*.lean`. Each file has a provenance header ("Literal inputs are untrusted until the
    accompanying Lean reader equalities check"), and a `provenanceJSON` string embeds the manifest.
  - For each value it emits leaf theorems of the form `theorem recordNN_eq : dinode blockView superblock i = recordNN
    := by … decide`. These use kernel `decide`, never `native_decide`, with raised `maxRecDepth`/`maxHeartbeats`.
- **Regeneration is checked byte for byte.** Each tool's `--check` mode regenerates and compares; CI runs it
  ([`.github/workflows/ci.yml`](https://github.com/theorem-labs/xv6-lean/blob/main/.github/workflows/ci.yml), step
  "Verify reference provenance and generated files").
  [`tools/check_model.py`](https://github.com/theorem-labs/xv6-lean/blob/main/tools/check_model.py) hashes every
  generated Sail model file against `models/riscv/provenance.json` and the lock.
- **Generators are mutation-tested.** `--self-test` runs negative mutations on the Python side: rejected fields,
  truncated images, the wrong source revision or blob, and a modified generated output.
  [`tests/test_tools.py`](https://github.com/theorem-labs/xv6-lean/blob/main/tests/test_tools.py) covers the
  importer the same way ("fail-closed tests").
- **Executable checks are labelled as such.** [`tests/Images.lean`](https://github.com/theorem-labs/xv6-lean/blob/main/tests/Images.lean)
  is an `#eval` regression test of the decoders, carrying the comment "Executable checks, not theorem evidence".
- **lf-lean checks cross-system equivalence by proof, not by testing.** The Lean translation is exported with
  lean4export, imported into Rocq with rocq-lean-import, and proved typewise isomorphic to the source. The checker ends
  with `Print Assumptions DoesItCheck` (`theories/Checker.v`), and `scripts/verify.sh` re-runs the export and compares
  it with the reference `lean.out`.
- **Upstream lean-zip (not Theorem) does differential testing.** The pure-Lean codec is tested against the C zlib FFI
  (`ZipTest/NativeIntegration.lean`: archives built with FFI, extracted natively). It also has a seeded randomized
  fuzz executable (`scripts/fuzz-inflate.sh`) and sanitizer runs of the FFI path.

### 2. Lean layout and tooling (xv6-lean)

- **Lakefile.** [`lakefile.toml`](https://github.com/theorem-labs/xv6-lean/blob/main/lakefile.toml) has two
  `lean_lib`s (`MachCSL`, `Xv6`) and a path dependency for the generated model (`models/riscv`). Git dependencies
  (iris-lean, lean-sail) are pinned by SHA, and `weakLeanArgs = ["-j2"]`.
- **Upstream pins.** [`upstream.lock.json`](https://github.com/theorem-labs/xv6-lean/blob/main/upstream.lock.json) pins
  the paper, xv6iris, xv6-riscv, sail-riscv, iris-lean, lean-sail and the Sail compiler, each with a `role` note. No
  Mathlib is used, so there is no `lake exe cache get` and no bump process is visible.
- **Thread cap.** [`tools/lake.py`](https://github.com/theorem-labs/xv6-lean/blob/main/tools/lake.py) builds a
  per-thread-count wrapper sysroot (symlinks plus a `lean -jN` shim, created once under `flock`, with
  `LAKE_OVERRIDE_LEAN`) and runs Lake itself under `lean -jN --run tools/LakeMain.lean`. This caps threads without
  touching the toolchain.
- **CI.** One GitHub Actions job with a 120-minute timeout: `leanprover/lean-action` with build, test and Mathlib cache
  turned off, then explicit steps. There is no `.lake` caching. (Upstream lean-zip caches `.lake` keyed on
  `hashFiles(...)` and runs `rm -rf .lake` on a fallback-key restore, because Lake caches `run_io` results.)
- **Audit.** [`Audit.lean`](https://github.com/theorem-labs/xv6-lean/blob/main/Audit.lean) does the following:
  - Assigns "project", "reviewed" or "unreviewed" by each module's physical build directory, not by name prefix. A
    dependency can't gain review by declaring into `Iris.`, and a fixture tests exactly that.
  - Allows only the three standard axioms for every project declaration.
  - Walks two cones. The statement cone expands definitions but not theorem proofs; the implementation cone expands
    proofs too. Both reject `partial`, `unsafe`, `implemented_by`, `extern`, and opaque non-Prop data unless the
    declaration is listed in `reviewedOpaque`.
  - Has a `closedRoots` manifest, currently empty, which makes the audit print "INCOMPLETE: … no whole-system theorem
    is certified".
  - Fails if it finds zero theorems ("empty audit is not success").
- **Audit tests.** [`tests/test_audit.py`](https://github.com/theorem-labs/xv6-lean/blob/main/tests/test_audit.py)
  compiles 12 positive and negative fixtures (private axiom, axiom outside the namespace, a foreign-package hook spoofing
  `Iris`'s namespace, a missing closed root, …) into a temporary overlay `LEAN_PATH`, each in a fresh Lean process.
- **Import coverage.** [`tools/check_imports.py`](https://github.com/theorem-labs/xv6-lean/blob/main/tools/check_imports.py)
  fails if any module is unreachable from the audited umbrella imports.
- **Model audit.** [`models/riscv/Tests/ModelAudit.lean`](https://github.com/theorem-labs/xv6-lean/blob/main/models/riscv/Tests/ModelAudit.lean)
  rejects unbound hooks by name and rejects a `FakeReal` import in the generated model.
- **Comparison with Verity.** Verity's `tools/lean/audit.py` already covers escapes, orphans, kernel replay, pins with
  statement and definition digests, dependency `.olean` records, layers and compile-time code, with control fixtures.
  It is stronger than xv6-lean's audit on replay and on pinning. xv6-lean has no `lean-audit.json`-style statement
  pins, no kernel replay, and no independent-kernel check (Theorem forked `nanoda_lib` but has no commits on it, so any
  use of it is inferred, not seen).

### 3. Spec-writing patterns

- **Role-separated files.** [`docs/CONVENTIONS.md`](https://github.com/theorem-labs/xv6-lean/blob/main/docs/CONVENTIONS.md)
  sets out `Defs`, `CodeF` (generated, never hand-edited), `SpecF` (a named Prop-valued record of obligations), `ProofF`
  (takes explicit callee contract records and imports only callee specs) and `LinkF` (applies the proofs). Callee
  contracts are passed as explicit parameters, not instances, "so a missing proof should appear as an unfilled linking
  dependency". Import restrictions are meant to be checked transitively.
- **Reserved theorem targets.** [`docs/THEOREM_TARGETS.md`](https://github.com/theorem-labs/xv6-lean/blob/main/docs/THEOREM_TARGETS.md)
  reserves Lean names for the six end theorems before any exist, and quotes the Rocq statements verbatim from the pinned
  commit. It classifies each target as "conditional interface" or "closed root" and states what does not count as
  completion: `phi = True`, or a function contract left as a hypothesis.
- **Non-vacuity witnesses.** Conditional theorems are paired with concrete instantiations, for example
  `concrete_positive_execution` in [`MachCSL/Logic/JalMachineSafetyLink.lean`](https://github.com/theorem-labs/xv6-lean/blob/main/MachCSL/Logic/JalMachineSafetyLink.lean)
  ("fully concrete nonvacuity witness … with no remaining premise"), `MachCSL/Machine/ColdBoot.lean` and
  `Xv6/Kernel/PtTreeExamples.lean`.
- **Assumption naming.** Source hypotheses are mirrored as named Props (`PhiExcl`, `PhiFrac`, `ViewShed` in
  `MachCSL/Logic/FsViewSTATUS.md`) and taken as explicit hypotheses, "not new global camera axioms". This is the same
  convention as Verity's.
- **`decide` and `#eval`.** Kernel `decide` is used heavily in generated leaves. There is no `native_decide` and no
  `plausible`/`slim_check` anywhere (searched). `#eval` is used only for regression checks, and those are labelled
  non-evidence.

### 4. Agent-heavy practice

- **AGENTS.md.** [xv6-lean `AGENTS.md`](https://github.com/theorem-labs/xv6-lean/blob/main/AGENTS.md) contains the
  rules "do not silently weaken hypotheses, strengthen preconditions, change the kernel, or alter the model to finish a
  proof"; "audit transitive axioms … text search alone is insufficient"; agree on owned files and theorem signatures
  before parallel work, using separate worktrees; every task reports changed files, exact theorem names, commands,
  results, obligations and the next bounded task; and "if a design stalls, checkpoint its failure and use a fresh
  agent". There is also an authorship footer on every outward post.
- **Cross-model review with recorded custody.** Codex writes; Claude (`claude-fable-5-1`, effort `max`) reviews with
  read-only tools (`--tools Read,Glob,Grep`, `--permission-mode dontAsk`). `docs/reviews/` holds 371 files (176
  `*-peer-review.md`, 41 `fable-*`). Each Claude review records:
  - `*-inputs.json`: the hashed prompt and the primary and full packets, with the repo HEAD;
  - `*-invocation.json`: the exact CLI command, model, turn count and cost (about $25 per review);
  - `*-read-coverage.json`: every file the reviewer actually read, with line ranges and hashes, and stated limits
    ("tool records establish returned text, not … comprehension");
  - `*-result.json`;
  - `*-disposition.md`: the author's response, which "does not strengthen [the reviewer's] verdict or represent later
    evidence as reviewed".

  See for example [`fable-kpt-invocation.json`](https://github.com/theorem-labs/xv6-lean/blob/main/docs/reviews/fable-kpt-invocation.json)
  and [`fable-kpt-disposition.md`](https://github.com/theorem-labs/xv6-lean/blob/main/docs/reviews/fable-kpt-disposition.md).
- **Status in the repo.** There are 299 `*STATUS.md` files beside the modules, plus `docs/PLAN.md` and `docs/STATUS.md`.
  This is the opposite of Verity's rule (status lives in the notes repo, not in Git).
- **lf-lean / rocq-dove ([blog](https://theorem.dev/blog/lf-lean/)).**
  - A task-level spec generator: one reviewed generator produces the correctness theorem for every instance.
  - Compositional work: dependencies that are already verified are given to the agent as trusted interfaces, because
    monolithic attempts failed beyond 9 dependencies.
  - Grader checks: the proof is valid, it adheres to the generated statement, it uses no extra assumptions, and the
    translation does not inconsistently fill in parts the source holds abstract (for example, defining the reals as
    empty).
  - Difficulty is scored by inference compute (best-of-k).
- **Upstream lean-zip (Kim Morrison).** Agents claim issues, work in worktrees and open PRs; a PR can't merge unless the
  round-trip theorem still builds ("the proof is the ratchet"). It keeps a `PLAN.md` and `progress/` "paired-review"
  notes, and CI fails if a committed generated artifact is stale.

## (d) Ideas worth adopting, ranked

1. **Non-vacuity witnesses for assumption bundles.** For each pinned theorem that takes named-Prop assumptions, pin
   one theorem that instantiates them concretely (or proves the hypothesis bundle is satisfiable). Verity's audit stops
   a hypothesis from being an `axiom`, but not from being unsatisfiable, and this check closes that gap.
2. **Cross-model statement review with read-coverage records.** When `audit.py --update` changes a pin, have a
   different model review the printed diff read-only. Store the prompt hash, the files read (from the transcript) and
   the verdict in the evidence store, plus an author disposition that cannot upgrade the verdict. This makes Verity's
   "named statement reviewer" rule auditable cheaply.
3. **Reserved targets with verbatim source statements.** Before proving, record a "completion contract": target names,
   the source statement quoted verbatim from the paper or Rocq, and what does not count as completion. The audit can
   then print INCOMPLETE until those names are pinned. This gives agents a precise finish line and stops quiet
   weakening.
4. **Hypothesis on the Python side, shaped like the Lean proof (fractional proofs).** Write Hypothesis properties for
   the Python reference that mirror the Lean lemma decomposition (one PBT per lemma), and stop the vectors from being
   the only cross-check. This is cheap and catches Python-side bugs the fixed vectors miss. Inferred: Theorem does not
   do this against Lean publicly. A true differential harness (Hypothesis generating inputs, a `lake exe` JSON-lines
   oracle comparing outputs) is my extrapolation, not something they have.
5. **Extend kernel-checked vectors to where Lean still only evaluates.** Verity already has xv6-lean's certificate
   pattern in `packages/verity/lean/Verity/TC/Vectors.lean` (one `decide +kernel` theorem per vector, with
   `test_lean_vectors.py` checking the same vectors against Python). POUS goes the other way:
   `protocols/pous/tests/lean/PousRefCheck.lean` uses `#eval` and prints JSON. Generating `decide`/`rfl` leaves from a
   vectors file, with regenerate-and-diff and a `--self-test` mutation pass on the generator, would make every
   package's agreement a kernel fact.
6. **Grader-style "no inconsistent instantiation" check.** As in rocq-dove's fourth check: wherever a Verity spec
   leaves something abstract (an assumption Prop, a parameter), check that downstream code doesn't instantiate it in a
   way that makes the assumption trivially false or true.
7. **Positive and negative audit fixtures that spoof namespaces.** Add a control where a fetched package declares into
   a project namespace, if Verity's controls don't cover it (Verity scopes by module, which likely already defeats
   this). Low cost; confirms that origin is decided by module rather than name.
8. **An independent-kernel cross-check** (nanoda via `leanprover/comparator`, or lean4checker) on the pinned roots.
   This defends against bugs in Lean's own kernel, which `Replay.lean` can't. Theorem forked nanoda_lib, but whether
   they use it is unknown.

Not worth adopting: per-module `STATUS.md` in Git (conflicts with Verity's notes policy); xv6-lean's GitHub Actions
setup (Verity's content-keyed `check` is stronger); the `tools/lake.py` thread wrapper (Verity already has
thread-affinity work in flight on `cursor/lean-threads-affinity-741b`).
