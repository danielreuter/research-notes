---
id: 20261004T2202Z-report-relay-docs-lean-first-protocols
campaign: pous
lane: accounting
kind: report
status: closed
repo: danielreuter/verity
origin: old-accounting (bc-b729c175), relayed for @top's migration (the 44 store:pous/ files the PoUW and PoUS registries cite) from store:pous/docs/lean-first-protocols.md
---

> Relayed verbatim from the Cursor store by old-accounting: `store:pous/docs/lean-first-protocols.md`, sha256 `f458ff8cb0b936848a6bf1f0567d3f39f4fa0f60d26a30daf73919a339e4a68d`, unchanged since it was written before the 30 Sep snapshot, so it is also in `art:8bd64630…42e9` at that path. Only the store's `cursor:` front matter is replaced. Relative and `/cursor/stores/…` links point into that store.

# Lean-first protocols: an assessment

Question (Daniel, 29 Sep 2026): should every protocol be written in Lean first, then benchmarked from Python or compiled
to C by the Lean compiler, with `PROTOCOL.md` deleted and humans reading a React site instead? Inputs: Verity `main` at
`origin/main` on 29 Sep, the project store's [Lean organization plan](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/docs/lean-organization-plan.md),
[ethereum/cryptography-specs](https://github.com/ethereum/cryptography-specs), and a benchmark run on this VM.

## Verdict

**Reasonable for the protocol's specification.** That means its byte formats and constants, its draws and laws, the
honest computation's reference, the verifier's checks, and the profile an accepted audit emits. Three conditions apply:

1. **Eventually, the theorems read the code that runs.** That is tier 3 in Daniel's ruling (see "Tiers"): the
   verifier's trusted code runs as compiled Lean, and the pinned theorems are stated about its definitions, as in
   `cryptography-specs`. Tier 2, a proof with no mechanical connection to the code, is fine for many applications, and
   tier 1, no proof, is fine while exploring. Today only parts of the Flock verifier are at tier 3. POUS's theorems are
   about a model whose encoder takes bit-functions and a whole random oracle, and the Python runs a different encoder.
   Closing that gap is the real work, and the real gain.
2. **Implementations match Lean; they don't have to call it.** The Python drivers, the GPU kernels, the vLLM hooks and
   the network enforcement are checked against vectors the Lean generates. Only the verifier's decision runs as
   compiled Lean, as the Flock verifier already does.
3. **External schemes are exempt.** Pearl's FP8 scheme is defined by Pearl's Rust, so its vectors come from there.

**Not reasonable as a way to benchmark.** Lean-compiled hashing runs 19 to 40 times slower than OpenSSL on this VM (see
"Speed"). The costs the tables report are GPU kernels and serving overhead, and those never run in Lean either way. What
Lean-compiled code can measure honestly is the verifier's own cost.

Most of this is already practice. Every protocol has a Lean model; the two audit laws' models are in the Flock soundness
package (`Audit/OneStage.lean`, `TwoStage.lean`, `Stratified.lean`). POUS and PoUW check their Python against Lean
`#eval` output. The one-stage draw is already executable Lean inside the Flock verifier. The rule would turn
that habit into an enforced one, and close the gap in condition 1.

## What "Lean first" would mean

Each protocol package would have four layers:

~~~text
protocols/<p>/lean/
  <P>/Spec/        executable, no Mathlib: formats, constants, primitives, enc/dec, draws, the law, the verifier's checks
  <P>/Model/       the security game and the ideal primitives (Mathlib); instantiates Spec's oracle with a uniform draw
  <P>/Assumptions  named Props, as today
  <P>Proofs/       proofs; pinned statements read Spec definitions
protocols/<p>/verity_<p>/   Python: the driver (IO, beacons, pods, numpy), checked against Spec's vectors
protocols/<p>/tests/vectors/  written by `lake exe <p>-vectors`, each file recording the Lean sources' hash
~~~

GPU kernels and the vLLM options sit outside the package, as now. They're gated by the same vectors. PoUW's `PROTOCOL.md`
already says this about its future RTX 4090 kernels.

## Tiers (Daniel, 29 Sep 05:04Z)

This ruling replaces the old question 2, whether the pins must be stated about the executable specification's
definitions. An implemented protocol is in one of three tiers:

1. It has no Lean proof.
2. It has a Lean proof, but no mechanical connection between the proof and the code.
3. It has a Lean proof that is mechanically connected to the code that runs.

In his words: "In exploratory code we should be fine with (1) happening (a decoupling) as long as it contributes to
research velocity [...] eventually we want to move to (3). (2) is fine for many applications."

### What counts as a Lean proof

A protocol reaches tier 2 when the theorem its certificate names, its headline claim, meets two conditions:

- **It is pinned in a `lean-audit.json` that `check` audits.** A proof graded in the store or on a lane counts for that
  lane's work, but not for `main` until it lands. This is the existing rule that a theorem a table or a PR cites as
  proved is pinned; the tier makes it visible.
- **It is about the construction the code runs.** Ideal primitives may stand in for the concrete ones the code calls: a
  random oracle for SHA-256, an ideal permutation for `Π₂`. A bridge from a different construction must be a named
  assumption.
  - The band's certificate is about the overwrite chain given `ChainExPostFactoG`, so it counts.
  - P3's `p3_meets_64_D10_final` is about a random-oracle `H`, while the code runs the overwrite chain. There is no
    named bridge, so it doesn't count.

Named assumptions don't lower a tier. The tier says whether the proof is about this code; the profile's assumptions say
what the proof rests on.

### What "mechanically connected" means

**The trusted code** is what the security claim relies on: the verifier's decision, its draws, and the setup it
computes (POUS's `vk`, PoUW's tile recomputation). The prover isn't part of it. Soundness holds against every prover,
so the prover's code needs no connection to the proof, and when a tier-3 verifier accepts the honest prover, that run's
output is checked too.

A protocol is **tier 3** when `check` would fail if the proof stopped being about the trusted code. That takes three
things:

1. **The trusted code runs as compiled Lean,** as `flock-verify` does, rather than as a Python reimplementation.
2. **A pinned headline theorem reads those definitions.** `reads` in `lean-audit.json` lists the modules the executable
   runs, and ideal primitives are parameters that the executable instantiates with the concrete ones.
3. **Every escape in the executable** (`@[extern]`, `@[implemented_by]`, `partial def`) is listed in `escapes`, with
   vectors comparing it with its Lean definition that `check` runs.

**Decision: vectors alone leave a protocol at tier 2.** They catch drift, so they're worth having, but they don't make
the running code the proved code:

- **They stop at toy sizes.** Lean evaluates POUS's band labels only at `d = 1` (`d = 2` exceeds its evaluation budget),
  dense at `B ≤ 2` blocks, and P3 at `n = 3`. The deployed point is `d = 12`, `B = 512` and 64 KiB blocks. H-1T's rows
  stop at `T ≤ 3`.
- **`check` regenerates none of them today.** POUS's generators need the trusted layer on one VM; PoUW's need a
  Mathlib-built checkout of a package that isn't on `main`. So a Python change fails a test, but a Lean change fails
  nothing.
- **Divergences sit next to passing vectors.**
  - P2's keys use ChaCha8, while its proof's setup assumption names SHAKE-256.
  - P3's proof is about a different `H`.
  - The dense tag format drifted before it was re-certified.

So tier 2 has two grades worth recording, without a tier for each: with no connection, and with vectors (noting whether
`check` regenerates them). "The Python matches vectors" applies in every tier. Matching is how prover-side code stays
honest; it isn't how a protocol reaches tier 3.

### When tier 1 is fine, and what moves a protocol up

**Provisional:** Daniel will dial this in over time. It reuses the one match point from "When the Python must match":
publishing or citing a result as the protocol's.

**Tier 1 is fine while all of these hold:**

- the scheme is exploratory: on a branch, or registered as `experimental` or research, like P2 and P3;
- its results carry the tier as a label wherever they appear (a table row, a colleague page, a run's profile), the way
  `(alg.)` does;
- nothing states it as proved. Benchmarks and design comparisons can be published; security claims can't.

A default scheme may sit at tier 1 for a while, as the band does on `main` now. What it can't be is cited as proved.

**From tier 1 to 2 (prove it):**

- when a result is about to be published or cited as the scheme's security, which is the match point: pin the theorem on
  the branch that publishes it, or label the claim unproved;
- when its certificate names a theorem. A certificate is a citation, so the theorem has to land where `check` audits
  it. Until then the scheme is labelled, not blocked: `check` prints tier 1 and names the missing pin, and no published
  claim may cite the theorem as proved. Today every POUS certificate falls short of this (see the table below).

**From tier 2 to 3 (connect it), when any of these holds:**

- someone other than its authors will rely on the verifier's decision: a deployment, a colleague's service, an external
  audit;
- a divergence between the proof and the code has been found once, as with the dense tag or P2's keys: prose and vectors
  have already failed that protocol once;
- it's cheap: the trusted code already runs as compiled Lean, so tier 3 is one theorem away, as with the one-stage
  audit's draw.

**A protocol moves down by itself.** If the trusted code changes without the Lean, or a pin is dropped, the generated
tier drops. Each run records the tier it ran at, so old results keep theirs.

## Where each protocol stands (29 Sep)

| Protocol or scheme | Tier on `main` | The proof | The connection | Next step up |
|---|---|---|---|---|
| POUS band (`band-chain/d12/v1`, the default) | 1 (2 in the store) | `band_meets_64` and `band_meets_14`, given `ChainExPostFactoG`, in the store's `lean/submissions/band-chain/` and `band-multi/`, red-teamed (§39), with no `lean-audit.json`. `main` pins only P3's column lemmas on the band graph (`band_twoWay_*`) | Snapshot vectors (`lean_band_vectors.json`: parents for five shapes, labels at `d = 1`), tied by `rfl` to `chainBand`, generated by hand | Land `band-chain` in `protocols/pous/lean` (tier 2). For tier 3: make the scheme computable over an oracle interface (`Scheme.enc` takes a whole oracle today) and run the verifier's key and answer checks in Lean, with SHAKE-256 and `Π₂` |
| POUS dense (`dense-chain/v1`, selectable) | 2, for a random-oracle `H` | `DenseMeets`, `dense_meets_64` and `segTag_meets_14` are pinned on `main`. The certificate's `chain_meets_64`, for the overwrite chain given `ChainExPostFacto`, is in the store | Snapshot vectors (`lean_dense_vectors.json`, `B ≤ 2`) | Land `chain_meets_64` |
| POUS P3 (`p3/v1`, research) | 1 for the implemented `H` | Lemmas are pinned (`TransposeMixing`, `ReverseNeedsAllChildren`, `N10Refuted`). The headline `p3_meets_64_D10_final` (store) is about a random-oracle `H` and an ideal `P`; the code runs the overwrite chain, and its certificate is `null` | Snapshot vectors (`lean_vectors.json`, `rfl`-tied to `P3Meets` at `n = 220`, labels at `n = 3`) | A certificate for the implemented `H`, or a named bridge |
| POUS P2 (`p2-16448/v2`, experimental) | 1 | `P2MeetsM1pB19Uncond` is graded PASS but only proposed, not in the trusted set. It's an abstract-M1 result; the SMS-to-M1 instantiation is pending Daniel | Python vectors only. Known divergence: ChaCha8 keys where the proof's P2-EXP-IO names SHAKE-256 | Review the pin and match the keys (tier 2) |
| PoUW `ncp-v1` | 1 (2 in the store) | `Pouw.Proofs.endToEnd`, given TTNCP_U, pinned in the store's PoUW package (`lean/submissions/pouw`, 321 pins). `AdmitsRef` and the byte-level noise expansion aren't proved | Snapshot vectors (`ncp_lean.json`: Lean's `#eval` of `mmWU 128 …` at every checkpoint, with the Lean sources' SHA-256) | Land the package (tier 2). `mmWU` is `#eval`-able, so running the verifier's tile recomputation as compiled Lean is the nearest PoUW route to tier 3 |
| H-1T (FP8 PoUW, research) | 1 (2 in the store, conditional) | 27 of the same package's pins; M3 and M4a await statement review; `DistinctLiveH1T` is still a named assumption | Reverse vectors: Python (exact over fractions, and checked against the kernel's f16 simulation and `verity.ml.tc`) writes Lean data that the Lean kernel checks (`H1TChecks.lean`), and the FP8 atom matches 4.9 M silicon captures. The strongest tier-2 connection here, but still tier 2: the CUDA kernel is what runs, and the rows stop at `T ≤ 3` | Stays at 2 while it's research. Tier 3 would need the verifier's check at bit level, in Lean integers |
| One-stage audit (`protocols/one_stage`) | 2 | `flock_e2e_drawn` and `flock_e2e_count` are pinned in the soundness package, about the model's `Audit.Law` and an abstract `execAccept` | The draw runs as compiled Lean (`Flock/Draw.lean` in `flock-verify`), which re-checks the Python's draw on every `benchmarks/one_stage` run. No pin reads `Flock.Draw` | One theorem away from tier 3: `Flock.Draw.derive` samples `L`, and `execAccept` is `flock-verify`'s decision. The proposed pilot, which is Daniel's call (decision 8) |
| Two-stage sampled proofs | 1 | `Audit/TwoStage.lean` has 12 theorems, but none is pinned, so none can be cited | None (`law.py`) | Pin the law (tier 2) |
| Flock verifier (C-Flock) | 2 overall, 3 for parts of its checking | 6 of the soundness package's 19 pins read the running verifier's modules (`Flock.Derive`, `Flock.CircuitType`, `Flock.Layout`): composition, layout and unit soundness. `level3`'s 50 pins are about the executable's definitions (field arithmetic, folding). The rest (`rope_sound`, `opening_binding`, `table_sound*`, the audit pins) read models | Runs as compiled Lean with 2 listed escapes, and is cross-checked against upstream's Rust | A theorem that `flock-verify verify` is the model's verifier (tier 3) |
| PoUW `pearl-fp8-v4` | Exempt | Pearl's own | Vectors from Pearl's Rust at `284b147b` | — |
| Network warden | 1 | 24 pins in the store's `lean/submissions/network-timing` | None; the Python is on `cursor/network-timing-reference-86f3` | Land it as a unit |

**Every POUS certificate names a theorem `check` doesn't audit.** `band_meets_64`, `chain_meets_64` and
`P2MeetsM1pB19Uncond` are in no `lean-audit.json` on `main`, and the store's `band-chain`, `sponge-dense` and `p3-meets`
have no `lean-audit.json` either. The storage profile an accepted audit writes still names them as what it establishes.
This is exactly what a generated tier field would surface (see "Enforcing it in code").

Core pieces every protocol calls already exist in executable Lean inside the Flock verifier: SHA-256, SHA-512 and BLAKE3
(`Flock/Hash.lean`), canonical JSON (`Canon.lean`), Merkle trees, the partition check and the template query. The
randomness samplers exist too (`Draw.lean`). What's missing is Keccak and SHAKE-256, which POUS's labels and PoUW's
noise use, and POUS's Feistel-SHAKE permutation `Π₂`.

## Speed

I built the Flock verifier's `Hash.lean` into a native executable with the pinned toolchain (v4.34.0, `-O3`, no
Mathlib). It hashed a 16 MiB and a 64 MiB message, and every digest matched `hashlib`.

| Hash | Lean, compiled | Python `hashlib` (OpenSSL) | Ratio |
|---|---|---|---|
| SHA-256 | 44 MiB/s | 1,763 MiB/s | about 40× |
| SHA-512 | 42 MiB/s | 801 MiB/s | about 19× |
| BLAKE3 | 23 MiB/s | (module not installed) | reference C with SIMD runs at GB/s |

The Lean was written for clarity, with its state in `Array UInt32` and every access bounds-checked. Tuning would narrow
the gap, but not by 20 to 40 times. The package built in 2.5 seconds, because the executable layer imports no Mathlib.
Two conclusions:

- **Verifier paths are fine in Lean.** They hash a few openings and recompute a few units or tiles. The Flock verifier
  already runs this way.
- **Prover and reference-encoder paths at real sizes aren't.** Encoding gigabytes of weights, or a full matmul, belongs
  to GPU kernels, which match the Lean on vectors. Where compiled Lean must hash fast, the audit allows an `@[extern]`
  call into OpenSSL only as a listed escape with a reason. The running code is then not the proved definition, so
  vectors must compare the two.

For logic-heavy code, compiled Lean will usually beat CPython loops. That's no argument for moving the benchmarks,
since the tables measure GPU work.

## Benefits

- **One source for behavior, and theorems about it.** A pinned statement that reads `Spec.enc` is a statement about the
  encoder that runs. Today nothing states that `verity_pous.band` is `chainBand`. The vectors show it on small cases.
- **Status is generated.** POUS's `PROTOCOL.md` hand-writes proved and open. `lean-audit.json` already records every
  pin, what it reads and its axioms.
- **Prose can't cite what no longer exists.** Docstrings sit next to the definitions, and an exporter can reject a
  reference that doesn't resolve (see "The React site").
- **Second implementations get one target.** The GPU codecs, the PoUW kernels and the network enforcement all match
  Lean's vectors, rather than a Python reference that is itself a copy.
- **The pattern is proven here.** The Flock verifier (7.7k lines, no dependencies) is an executable Lean verifier of
  record, cross-checked against upstream's Rust.

## Costs and risks

1. **Refining the models to the specification.** POUS's model works over `Bits n` and a whole primitive `M.Ω`. The
   specification must work over bytes and a query interface. There are two ways to connect them:
   - define the scheme once, computable and parametric in an oracle, and let the model plug in `M.answer ω`;
   - keep both and prove a refinement theorem between them.

   The first is simpler. It changes what POUS's 52 pins read, so every changed record needs a named statement reviewer
   once. PoUW's pins should be restated this way before they land, not after.
2. **Primitives in Lean.** Keccak/SHAKE-256 and `Π₂` have to be written in Lean and checked against `hashlib`.
   That's mechanical work.
3. **Floating point.** Lean's `Float` is opaque to proofs. Any FP8 or BF16 scheme has to be written at bit level in
   integers, as `verity.ml.tc` already is in Python.
4. **Speed of change.** Every protocol change goes through a Lean build and the audit. `check` takes 35 to 47 minutes
   on a train, and 63 open PRs touch Lean (organization plan §1).
   - A Mathlib-free specification rebuilds in seconds, and a definition can land before its proofs with no `sorry`.
   - The Mathlib model and proofs rebuild only when touched.
   - Parallel lanes still need separate `.lake` directories, and the plan's shared `packagesDir` matters more.
5. **Toolchains.** If the Python calls compiled Lean, every `uv sync` needs elan and a Lean build. Matching vectors
   avoids that. `cryptography-specs` ships wheels that bundle `libleanshared`, so users don't need Lean, but developers
   building from source do.
6. **Trust in the compiler.** Compiled Lean is outside the kernel's check. The Flock verifier already accepts this, and
   so does `cryptography-specs`.
7. **External definitions.** Pearl's scheme, and upstream Flock's Rust verifier, are defined by someone else's code.
   Porting them to Lean first reverses the conformance direction, so they're exempt.
8. **Reading on GitHub.** GitHub shows `.lean` files as code, so the site becomes the main place to read. Docstrings
   should stay readable as plain markdown for people reading a diff.

## Should the Python call Lean or match it?

| Route | How | Use for |
|---|---|---|
| Match | The Python reimplements the specification and passes Lean-generated vectors, lagging only as the next section allows | Drivers, provers, numpy paths, and everything that runs at scale |
| Run | The verifier's decision is a compiled Lean executable reading JSON, as `backends/flock/verifier` works today | The verifier of record, and its cost in benchmarks |
| Link | A CPython extension over compiled Lean, `cryptography-specs`' way | Only if calling an executable costs too much |

For the linked route, `cryptography-specs` shows the setup. `setup.py` runs `lake build` and links every Lean-generated
`.c.o.export` against `libleanshared`. The specification library imports no Mathlib and sets
`precompileModules := true`. Proofs are a separate library in the same package, with `precompileModules := false`, so
proof objects stay out of the extension.

## When the Python must match

A lighter version is proposed in
[process-design-for-research-velocity](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/docs/process-design-for-research-velocity.md)
§5, after gaming these norms out on last week's changes. It detects lag automatically instead of keeping `lag.toml`, and
keeps "publish or cite as the protocol" as the only match point.

Decided 29 Sep: the Python matches vectors. The Lean moves first, and the Python may lag behind it, as long as the lag
is written down. Matching is required only when a result is about to be read as the protocol's.

**On every commit that passes `check`.** These checks are mechanical and take no one's time:

- **The committed vectors are what the Lean generates at that commit.** `check` regenerates them, which takes seconds
  because the specification imports no Mathlib, and it fails on any difference. So the vectors never lag the Lean; only
  the Python can.
- **The Python passes every vector case except those in its protocol's lag list** (`tests/vectors/lag.toml`). Each
  entry names the cases, the reason, the owning lane and the commit where the lag began.
- **The list stays exact.** An unlisted failure fails `check`. So does a listed case that now passes, the rule the Lean
  audit already applies to its escapes.

A Lean change that doesn't change behavior regenerates identical vectors, so a refactor or a docstring edit creates no
lag.

**No time limit.** A lag can stay on `main` across trains. The site shows each protocol's open lag, so it stays visible.

**Match points, where the lag list must be empty:**

1. **Publishing a result as the protocol's.** This covers a benchmark row, a table cell on the site, or a Notion page
   that reports the protocol's security or performance.
   - Each run records the digest of the vectors and the lag list it ran with.
   - The site labels a result from a lagging implementation with the Lean commit it implements, and keeps it out of
     headline tables, the way `(alg.)` flags results today.
2. **Citing a pinned theorem for a run.** "This audit is secure by `DenseMeets`" holds only for an implementation that
   matches the vectors of the Lean the theorem is stated over.
3. **Making a scheme the default, or bumping a wire-format version string.** Drivers run the default, and second
   implementations target the version string.

GPU kernels and the vLLM options match the Lean's vectors directly, so a lagging Python never blocks them.

**Python first, for exploration.** A scheme with no Lean at all is `experimental`, as POUS's P2 is today: that's tier 1,
and "When tier 1 is fine" sets its limits.

- It can be benchmarked, and its results are labelled experimental.
- It can't be the default, or be cited as the protocol.
- It becomes a protocol scheme when its `Spec` definitions and vectors land.

Exploration stays in Python; promotion goes through Lean. Branches are unconstrained, because only `main`'s `check`
enforces any of this.

**What the vectors hold.** The Lean generator chooses the cases:

- small parameters;
- every edge case the specification names;
- one mid-size case.

Each case has an id, so a lag entry can name cases. The Python adds its own randomized tests. A small set keeps
regeneration fast and its diffs reviewable.

## Deleting `PROTOCOL.md`: where each part goes

| Section today (POUS, PoUW, one-stage, sampled proofs) | Goes to |
|---|---|
| The problem and the game | The `Model` module's docstring, next to the game's definitions |
| Lifecycle | The `Spec` driver module's docstring; the Python driver's docstring names the Lean function |
| API and interface lists | Lean signatures and Python docstrings; nothing hand-written |
| Stable byte formats and constants | `Spec` constants, pinned by vectors |
| Pinned statements, proved or open | Generated from `lean-audit.json` |
| Named assumptions | `Assumptions` docstrings, with claim ids from `verity.claims` |
| Main caveat, choices that could be wrong | An `Overview` module docstring |
| Provisional items, not here yet | GitHub issues the site links; they're project state, not specification |

**Scope: `protocols/` only, for now.** Three other kinds of `PROTOCOL.md` stay out:

- `verity/ir/PROTOCOL.md` specifies the core that every package imports from Python, and `format_vectors.json` already
  pins it rule by rule.
- `backends/flock/verifier/PROTOCOL.md` is what the Lean verifier was written from, to stay independent of upstream's
  code.
- The frozen backends' specs aren't developed.

Each can follow later on its own terms.

## The React site

**Source.** A Lean program in `tools/lean/`, say `lake exe docs-export`, loads each protocol package's environment and
writes one JSON file, `verity/lean-docs/v0`, with a JSON Schema beside it as `census/schemas/` has:

- **modules:** name, path, commit, docstring;
- **declarations:** name, kind, pretty-printed signature, docstring, source lines, computable or not, the definitions it
  reads, its axioms, the named assumptions it takes as hypotheses, and its pin and record hash from `lean-audit.json`;
- **vectors:** each file, its generator, the Lean sources' hash, and the Python, GPU or vLLM tests that read it;
- **claims:** the claim ids the docstrings cite.

Lean's metaprogramming API provides all of this: docstring lookup, signature pretty-printing and axiom collection.

**Checks the exporter runs, failing `check`:**

- every backticked Lean name in a docstring resolves;
- every claim id resolves in `verity.claims` (`test_hm96` already does this for one spec);
- every pinned theorem and every trusted definition has a docstring (the organization plan's proposed `docBlame` lint).

**Publishing.** The exporter publishes the same way the tables do today. `check` or the steward stores the export as an
evidence-store artifact per commit, and the site reads the latest export for `main` and a PR branch's export for its
preview. The site shows the commit it renders, and marks the page when that commit is behind `main`. Give dev, preview
and production visibly different favicons, so a preview is never read as `main`.

**Page shape.** Your notes order for colleague pages is: core idea, then security properties (what's proved, under which
assumptions), then performance, then protocol details. The data maps onto it:

- the core idea and caveats come from the `Overview` docstring;
- what's proved and under which assumptions is generated from the pins and `Assumptions`;
- performance comes from the entities render the site already reads;
- the details come from the `Spec` declarations.

**Off-the-shelf alternatives:**

- **doc-gen4**, which renders Mathlib's API docs as static HTML, is worth linking as the full reference.
- **Verso**, the tool the Lean reference manual is written in, fits if you want narrative-first pages whose Lean
  references are elaborated.

For a React site, the JSON exporter is the direct coupling.

## Enforcing it in code

- **Package layout.** Extend `protocols/tests/test_protocol_boundaries.py` so that each `protocols/<p>/` has:
  - `lean/` with a `Spec` library that imports no Mathlib, and has no `noncomputable` and no `Float`;
  - a vectors executable;
  - vector files whose recorded Lean hash matches the current sources.
- **No specs in prose.** `tests/test_repository.py` rejects `protocols/*/PROTOCOL.md`.
- **Exemptions are listed.** An external scheme, like Pearl's, is listed by name with its vectors' source.

### Where the tier rule lives (agreed with Verity root, 29 Sep 05:32Z; not built)

The three candidate homes, run through the `process-design` skill's tests:

| Home | Where it fires | What it costs | Verdict |
|---|---|---|---|
| A line in `AGENTS.md` | Nowhere. It's prose every agent reads, and agents exploring need no permission to stay at tier 1 | About 40 always-read words, rewritten each time Daniel dials the norm in (test 10) | No |
| The `process-design` skill (#359) | Only when someone designs a process. Protocol authors and people publishing results don't load it | Nothing | No, except later as a second worked example |
| A tier field generated from `lean-audit.json`, which `check` and the site read | At the reliance point: the site, the tables and each run's profile show the tier, and nothing blocks | A small reader, written once, and a `runs` list per scheme | **Yes** |

Most of the generated field's inputs already exist:

- **Certificates.** Each scheme's certificate names its theorem and hypotheses. POUS already writes them into
  `tests/fixtures/schemes/<name>.json`, and PoUW's `certificate` lists its pinned theorems.
- **Audit records.** `lean-audit.json` records every pin, what it reads, the escapes and the assumptions.
- **New: `runs`.** Each scheme names the Lean modules its verifier runs; the list is empty for a Python verifier.

The rule, written as code:

- tier 1 if the certificate's theorem isn't pinned in an audited package;
- tier 2 if it is;
- tier 3 if it is, `runs` isn't empty, the pin's `reads` covers `runs`, and every escape in `runs` has vectors.

`check` prints each scheme's tier and names any pin its certificate is missing. It fails only on an inconsistency, such
as a `runs` module that doesn't exist, never because a scheme is at tier 1. The docs export carries the tiers to the
site, and `research run` records the tier each run ran at.

**When to build it:** with the docs exporter, when that work comes up, and not before. Until then the table in "Where
each protocol stands" is the record, and the provisional tier-1 norm stays in this doc while Daniel dials it in. Once it
settles, it belongs in the tool's docstring and in the `lean-proofs` skill, which anyone pinning a theorem loads, rather
than in `AGENTS.md`.

## Migration, smallest first

1. **One-stage.** Move the executable pieces the Flock verifier already has (samplers, stratified law, canonical JSON,
   SHA) into a core Lean specification library, and check `protocols/one_stage` against its vectors. Delete its
   `PROTOCOL.md`. This is the organization plan's decision 6 ("one core package"), triggered by a real second consumer.
   With the one theorem that ties `Flock.Draw.derive` to the model's law, it's also the first protocol at tier 3, if
   Daniel makes it the pilot (decision 8).
2. **Two-stage sampled proofs.** Put the law and its selection in the same library.
3. **PoUW.** Land the store's Lean with `ncp-v1` as `Spec`, already `#eval`-able, and restate its pins over `Spec`
   before they land. Pearl's scheme stays exempt.
4. **POUS.** Add SHAKE-256 and `Π₂` in Lean, make the scheme computable over an oracle interface, and review the 52
   pins once.
5. **Network warden.** Land it as a unit, per the organization plan, with its schedule and bucket rule as `Spec`.

The exporter and site can start after step 1, with one protocol to render.

## Decisions for Daniel

1. **Decided 29 Sep: the Python matches vectors the Lean generates.** The norms are in "When the Python must match".
   The Flock verifier already runs as compiled Lean, and this changes nothing there. One follow-up question remains:
   may a lag stay on `main`, or only on branches?
   - On `main`, with the lag list: Lean changes can land without waiting for the Python.
   - Branches only: `main` is always matched, but every Lean change that alters behavior then waits for its Python.
     That's the high-frequency coupling you want to avoid.
   - Recommendation: allow lag on `main`, with the list, and enforce matching at the three match points.
2. **Decided 29 Sep 05:04Z, by the tiers: must the pinned theorems be stated about the executable specification's
   definitions?**
   - For the verifier's trusted code, stating them that way is what tier 3 means. It's the long-run target, not a
     condition for landing.
   - Tier 2 is fine for many applications, and tier 1 while exploring.
   - When a protocol moves up follows "When tier 1 is fine, and what moves a protocol up", which is provisional.
   - Vectors alone leave a protocol at tier 2.
3. **Are schemes defined by someone else's code exempt?** This covers Pearl's FP8 scheme, whose truth is Pearl's Rust.
   - Recommendation: exempt, listed by name, with vectors from their code.
4. **Scope: only `protocols/`, or also the IR's, commitments' and backends' specs?**
   - Recommendation: `protocols/` only for now.
5. **Where do open items and "waiting on Daniel" lists go once `PROTOCOL.md` is gone?**
   - Recommendation: GitHub issues the site links. Caveats and assumptions go in Lean docstrings, as current truth.
6. **Agreed with Verity root, 29 Sep 05:32Z: a proof that exists only off `main` doesn't count toward `main`'s tier.**
   The band, dense's overwrite-chain certificate, PoUW and H-1T all have proofs off `main`. The tier on `main` reads
   only audited pins, and the table notes where an unlanded proof is. This is the existing pinning rule, made visible.
7. **Agreed with Verity root, 29 Sep 05:32Z: a certificate that names an unaudited theorem is labelled, not blocked.**
   All three POUS certificates do today.
   - `check` prints the tier and names the missing pin.
   - A published claim may cite the theorem as proved only once it's pinned.
8. **With Daniel: is the one-stage audit the tier-3 pilot?** It's one theorem away: `Flock.Draw.derive` samples the
   model's law, and `execAccept` is `flock-verify`'s decision. Verity root recommends yes, and it's in root's summary for
   him.
