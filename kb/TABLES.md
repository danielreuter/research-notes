---
kind: kb
topic: the tables the user wants (standing spec)
updated: 2026-09-25T06:30Z (published from the Project store's docs/tables-spec-draft.md, user-approved; previous version: kb/TABLES-v1-20260924.md)
---
# Draft rewrite of `kb/TABLES.md` (for Daniel's review)

**Status:** approved by Daniel on Thu Sep 24, about 10:55 PM PT, and amended about 11:10 PM PT for his commitment decision: Table 2 commitments use SHA-256 or BLAKE3, never an algebraic hash ([commitment-scheme-decision.md](commitment-scheme-decision.md)). Nothing is published yet and the notes repo is unchanged. **Written:** Thu Sep 24, about 9:15 PM PT, against `kb/TABLES.md` as last updated at 1:20 PM PT (20:20Z) and the 8:48 PM PT render (`main` `b84f11ea`).

**Sources:** the current spec; `architecture-decisions.md` (tonight's decisions); `benchmark-standard-proposal.md` (§2 methodology, the per-unit peak sources, §7 views); `proof-optimization-tables.md` (today's cells); the renderer on `main` (`verity_numerical/bench/tables.py`, `drilldown.py`, `contract.py`, `backends/AGENTS.md`); and the lane notes behind the in-proof hash cells.

**How to read it:** the next section lists what changed. The proposed file follows between two rules; on approval it replaces `kb/TABLES.md` as it stands. After it, for review only: what the renderer, the lanes and today's cells must change, and the three points Daniel resolved.

## What changed vs the current `TABLES.md`

- **Records and tables.** The records are benchmark results, one subcircuit each, and "rows" are gone. Table 1 becomes backend configurations and their security, absorbing D1. Table 2 becomes the end-to-end overhead N ÷ P per subcircuit, hardware class and commitment scheme. Table 3 splits each Table 2 cell into serving overhead (committing) and proving overhead.
- **One relation in Table 2.** A cell must prove the full relation: commitments to the inputs, weights and outputs, computed from the instance set, and a proof that the committed outputs are the subcircuit applied to the committed inputs and weights. Weaker statements stay results and move to the drill-down. The "+ in-proof hash" columns fold into their backend's column.
- **Admissible commitments.** The commitments must use a scheme defined in `verity.commitments` and built only on SHA-256 or BLAKE3. Schemes on Poseidon2 or other algebraic hashes, on linear digests such as Ajtai, or on a proof system's own commitments stay results (new reason S). Two schemes are first-class: frame-v3 and the vLLM application's framing (`vllm-v1`). Each configured backend selects one, and Table 2 compares them line by line.
- **Security leaves results.** It lives only in Table 1's configuration records. 2^-128 becomes the published view's default filter instead of a validity rule, so sub-128-bit results are kept and visible unfiltered, never relabelled. Table 1 also records every hash the soundness argument uses and whether it is algebraic, and whether each proximity bound is proven or conjectured; the published view also filters out algebraic hashes inside proof systems.
- **Native side.** A compute-bound estimate from per-unit datasheet peaks (tensor cores, FP32 and integer cores, special-function units, conversions), each cited, with no memory term. The "measured peak" wording and the measured-native column go.
- **Proving side.** No fixed B = 4096 or K = 1536. Each backend chooses its batching, and the harness sweeps the batch to the plateau: warm, at least five runs, median, independently verified. Nothing is weighted or aggregated across subcircuits.
- **Inputs.** Seeded instance sets generated from the IR; the five existing frozen sets, including the A100 set, stay byte for byte.
- **Computed views.** The headline is the best valid configuration per backend family, `archived` hides a configuration, a computed marker flags provisional cells, and "n/s" comes from the backend's declaration. No hand-kept lists or name-prefix recognisers.
- **Kept:** only solid numbers; preserved proof files; independent verification by a non-producer; red-team review for statement changes, with downgrades standing; the phase-sum and instance-equivalence rules; the same GPU SKU; SP1 naming and whole-proof security; the A-GKR hill-climb; your approval for any change of definition, column or rule.
- **Changed:** B-Ligero's headline hashing is no longer Poseidon2 per row. Algebraic hashes don't qualify for Table 2 (your decision, Sep 24, about 10:45 PM PT), so the Poseidon2 and Ajtai leaves join the shared tiles in the drill-down.
- **Dropped:** the K, B and 2^-128 checks in the validity predicate, reason letter B, the note about Table 2's frozen footnote for SP1 precompile, and the old gaps table (rewritten for the new rules).
- **The switch.** Published numbers change once, in a 6 PM PT digest labelled as a change of method with the old numbers alongside, after parity at 2^-128 and plateau re-sweeps. The Foundation site's first public tables wait for the same point.

**Effect on today's 15 cells.** None stays, so Table 2 starts empty.
- The five B-Ligero + in-proof hash cells prove the full relation's shape, but bind Poseidon2 row digests, so they leave with reason S.
- The five A-GKR cells (operands private and bound to nothing) and the five bare B-Ligero cells (operands public, no commitments) leave with reason R.
- All 15 stay results in drill-down D2. SP1 still has no cell, because its results come from the bare guest.
- The first cells will come from B-Ligero's frame-v3 BLAKE3 row leaves, which are built, gated and accepted by the pinned Rust verifier on the FP8 Ada and BF16 Hopper relations, and from SHA-256 row leaves under frame-v3 and `vllm-v1`, still to be built ([commitment-scheme-decision.md](commitment-scheme-decision.md)).
- The native definition leaves today's ratios unchanged for these five subcircuits.

---

*Proposed file. Everything from here to the next rule replaces `kb/TABLES.md`; its front matter is:*

```yaml
kind: kb
topic: the tables the user wants
updated: {on publication} (rewrite with the user's decisions of 2026-09-24 evening; replaces the 2026-09-24T20:20Z spec)
```

# The tables the user wants (standing spec; do not redesign without the user)

The tables answer three questions about every proof backend: what each configuration guarantees (Table 1), how many times longer proving a subcircuit takes than computing it natively on the same hardware (Table 2), and where that time goes (Table 3). Only solid numbers: every cell traces to an `art:` id and was verified by someone other than its producer. Show the user these renders as they are, never a hand-made or re-scaled table.

## Terms

- **Subcircuit:** the atomic unit. One IR Definition with every static bound, plus its finite domain and its ports (inputs, weights, outputs). For example the BF16 GEMM coordinate at K = 1536 on the Ampere tensor-core step. Another K or another pipeline is another subcircuit.
- **Instance:** one evaluation of a subcircuit, such as one output word of a GEMM coordinate.
- **Instance set:** a subcircuit's seeded inputs and expected outputs, content-addressed (see Inputs).
- **Hardware class:** a GPU SKU and board variant (memory within 12% of the datasheet part). Each result also records the driver, CUDA version and host CPU.
- **Backend family:** A-GKR, B-Ligero, SP1: one Table 2 column each. Adding a family needs the user's approval.
- **Configuration:** a backend with one declared variant and its parameters. Its record holds all its security properties (Table 1). The backend declares it; nothing infers it from names.
- **Commitment scheme:** a way of committing port values defined in `verity.commitments` (leaf encoding and tree rules), with a spec, a reference implementation and conformance vectors. A configuration names the scheme its statements bind.
- **Serving:** the live inference path of an application of Verity, such as the vLLM application serving requests. **Serving overhead** is what committing the values costs there; **proving overhead** is what proving costs (Table 3).
- **Benchmark result:** one measured run of a configuration on a subcircuit, a hardware class and a range of an instance set. It holds performance only, never security. Results are the records; there are no rows.
- **View:** a query over results and configuration records. Tables 1 to 3 and the drill-downs are views, and nothing in them is kept by hand.

## Table 1: backend configurations and their security

One entry per backend family, followed by each of its configurations (today's D1 moves here). For each configuration:

- **statement:** whether it proves the full relation (Table 2 below) or a weaker one, and what the verifier sees of the inputs, weights and outputs (committed, public or private);
- **commitment scheme:** the configured backend's `scheme` parameter: its `verity.commitments` id, its tree and leaf rules, and which part the proof computes. For example: frame-v3 SHA-256 trees over keyed-BLAKE3 row digests, with the digests computed in the proof and the trees checked natively by the verifier;
- **hashes:** every hash the soundness argument relies on. For each one, give:
  - its role: statement commitment, proof-internal commitment, or Fiat–Shamir and coin derivation;
  - the property assumed: collision resistance, or a random oracle;
  - its class: *standard* (SHA-2, SHA-3, BLAKE3) or *algebraic* (Poseidon2 and other arithmetization-oriented designs, and linear digests such as Ajtai).

  For example, SP1's proof-internal Merkle trees and challenger use Poseidon2 over KoalaBear, an algebraic hash;
- **ZK class and verifier model;**
- **soundness:** the per-proof terms, how they combine over sub-proofs or shards, and the accountant that computes them. Table 1 prints the whole-proof bound at the batching of each cell the configuration holds. It also prints the dominant term and how that term grows with the batch, for example n/|F| for a proximity or sumcheck term. The per-proof figure is secondary;
- **proximity bounds:** for each code-based component (Ligero's tests, FRI, a polynomial commitment), give:
  - the decoding regime its terms use: unique decoding, up to the Johnson bound, or beyond it;
  - whether each bound is proven, citing its theorem, or conjectured.

  The whole-proof bound uses proven bounds only. A conjectured figure may be printed beside it, labelled, but never enters a filter. A step whose lemma isn't cited is listed under assumptions until it is;
- **setup, interaction and transferability;**
- **assumptions:** everything else soundness and binding rest on: fields and extension degrees, lattice or LPN assumptions, uncited lemmas;
- **pin:** how the verifier pins the relation (a system or circuit digest; a verifying key plus the fork commit);
- **archived**, which hides it by default, and the cells it holds (computed).

The records come from each backend's capability declaration, reviewed as code. Until those exist they come from today's `tables.CANDIDATES` and `drilldown.VARIANTS`, checked against the sources D1 cites. Every view can filter on any of these properties.

## Table 2: end-to-end overhead per subcircuit, hardware class and commitment scheme

One line per subcircuit, hardware class and commitment scheme, a native column, then one column per backend family.
- A scheme here is a `verity.commitments` scheme together with the hash of its leaves. Today there are three: frame-v3 with SHA-256, frame-v3 with keyed-BLAKE3 row digests, and `vllm-v1` (SHA-256).
- The lines of one subcircuit and hardware class sit together, so each family's column compares the schemes.
- A scheme's lines appear once some configuration declares that scheme.

```text
N(S, H)     native throughput: instances of S per second on H, a compute-bound estimate
              N = 1 / max over execution units u of ( ops_u(S) / peak_u(H, dtype) )
P(S, H, C)  proving throughput of configuration C: instances per second end to end
              (committing the batch's values, then proving), at C's plateau batch,
              median of at least 5 warm runs, counting only independently verified
              proofs of the full relation
cell        N / P: how many times longer proving takes than native computation
```

A cell is a per-subcircuit ratio. What an application such as the vLLM application pays depends on how many units it proves, and on its serving overhead in place, which its end-to-end benchmark measures.

### The full relation

Every Table 2 cell proves the same statement about its instances:

- the statement names commitments to the inputs, the weights and the outputs, computed with the configuration's commitment scheme from the instance set's actual values;
- the proof shows that, for every instance in the range, the committed outputs equal the subcircuit applied to the committed inputs and weights;
- the verifier needs none of those values in the clear, although outputs may also be published;
- the independent verifier recomputes the commitments from the instance set and checks that the proof binds them.

**Admissible commitment schemes.** The configuration names its scheme, and the scheme must meet two conditions:

- **It is defined in `verity.commitments`,** with a spec, a reference implementation and conformance vectors. It must be computable from the values alone, so that serving commits once and any backend or spot-check can open the commitment. A proof system's own commitments (a Ligero column tree, FRI trees) don't qualify, even when they bind the witness.
- **It is built only on standard hashes,** today SHA-256 or BLAKE3. Nothing in it is an algebraic hash (Poseidon2 or another arithmetization-oriented design) or a linear digest (Ajtai).

Two schemes are first-class. A configured backend selects one, for example `BLigero(scheme=FRAME_V3)` or `BLigero(scheme=VLLM_V1)`, through the `CommitmentScheme` interface, with no backend code per scheme:
- **frame-v3:** SHA-256 trees over verifier-derived domains, whose leaves are words, or SHA-256 or keyed-BLAKE3 digests of rows;
- **`vllm-v1`:** the vLLM application's framing (SHA-256), given one spec, a reference implementation and conformance vectors, with positions and domain bound where the spec requires. It qualifies once the core defines it.

When the instance set itself shares a row between instances, as serving-shaped tiles do, that row is one leaf, committed and bound once per timed run. The five frozen sets share none.

Results proving a weaker statement stay results. They appear in D2 and never fill a Table 2 cell. Today these are:

- operands public with no commitment: B-Ligero with `authentication = excluded` (reason R);
- operands private and bound to nothing: A-GKR, and SP1's bare guest (R);
- relation-only guests and clear-text modes (R);
- commitments on an inadmissible scheme: B-Ligero's Poseidon2 (`+hash`) and Ajtai row leaves (reason S).

Publishing the operands for the verifier to re-hash (`authentication = included`) is not the full relation either: a verifier that holds the operands can recompute the outputs itself.

Two paths prove the full relation over an admissible scheme today:
- B-Ligero's frame-v3 BLAKE3 row-leaf mode (`authentication = included-hash`, relation suffix `+blake3`);
- SP1's typed path, whose guest checks frame-v3 openings, though it has no result on the frozen sets.

### Native throughput N

- **Work model:** ops_u(S) is what one instance executes on each execution unit, derived from the subcircuit's Definition. Each primitive's unit and operation count on the target silicon is declared once, in `verity.silicon`. It counts what the GPU executes, not how the reference evaluator computes: SiLU is an exponential and a reciprocal on the GPU even though its evaluator is a table. Example: the BF16 GEMM coordinate at K = 1536 is 96 tensor-core steps × 32 FLOP = 3,072 tensor-core FLOP, plus one conversion.
- **Peaks:** peak_u is the unit's nominal peak for the dtype, from `verity.silicon`'s benchmarked-device table. Each entry names its hardware knowledge-base record and cited source. Until that table exists, the peaks are `Target.native_peak` in `verity.verification.target`, and the table must reproduce them.

| Unit | What is counted | Source, cited per entry |
| --- | --- | --- |
| Tensor cores | Dense multiply-add FLOP per operand dtype, at the relation's accumulate width | Vendor datasheet or architecture whitepaper, dense column (never the sparse one) |
| FP32 cores | FP32 add, multiply and fused multiply-add instructions | Vendor datasheet (its FP32 figure counts an FMA as 2 FLOP), cross-checked with the CUDA Programming Guide's per-SM throughput table × SMs × boost clock |
| Integer cores | 32-bit integer add, compare and logic instructions | CUDA Programming Guide per-SM table × SMs × boost clock |
| Special-function units | Exponential, reciprocal, reciprocal square root, logarithm, sine, cosine | The same |
| Conversions | FP32 to and from BF16, FP16 and FP8 | The same |

- **The estimate:** the busiest unit sets the time, units are assumed to overlap perfectly, and there is no memory term. Every subcircuit gets it, elementwise ones included; their large ratios honestly show proving costing a lot for work that is nearly free natively.
- **Data movement is not a subcircuit.** An embedding lookup is an opening of row `id` of the committed weights, which is commitment-layer work. Reshapes, shard views and KV-cache layout are references in the Program, checked by the integration's linkage check.
- **Nominal peaks stand even where a device beats them.** The RTX 5090 reached 1,880 TFLOP/s against a nominal 1,676, so its NVFP4 ratios can be understated by about 11%; the knowledge base shows both numbers. Measured native and serving throughput belong to the application benchmarks, never to Table 2.
- The native column prints N in instances per second with its busiest unit and peak entry, for example `1.0e11/s · tensor cores, BF16 312 T`. Each cell names the work-model version and peak entry it used.

### Proving throughput P

P is measured by the protocol below. It counts committing the batch's values as well as proving, because work done while committing (such as the row digests an in-proof hash reuses) is part of producing the proof. Table 3 shows the two apart, as serving overhead and proving overhead.

### The cell, the headline and the filters

- **The cell** is the family's best valid configuration for that line: the highest P among independently verified plateau points of non-archived configurations that prove the full relation, fall in the family's declared class and pass the view's filters. Ties go to the lower artifact id. There is no hand-curated list.
- **Declared class,** stated in the family's Table 1 entry: for A-GKR a complete non-ZK proof (`NON_ZK_PROOF_DIAGNOSTIC` or `NON_ZK_PROOF`); for B-Ligero malicious-verifier ZK (`COMPLETE_ZK_BACKEND`), with its HVZK Fiat–Shamir variant in the drill-down; for SP1 any sound class.
- **Diagnostic modes** that produce no verified proof of their statement (`ARITHMETIC_DIAGNOSTIC`, `NO_PROOF`, verdict-byte `0xEE` guests) never enter a proving view.
- **Filters:** any Table 1 property, such as the security bound, ZK class, hashes and their class, proximity regime, assumptions, transferability or setup.
  - The published Table 2 has two filters: a whole-proof bound of 2^-128 or better at the cell's batching, and no algebraic hash anywhere in the soundness argument, including inside the proof system.
  - Where the unfiltered view picks another configuration, the cell's footnote names it, with its bound, its hashes and its ratio.
- **No aggregation.** Nothing is weighted, summed or averaged across subcircuits. A request-level number is a separate end-to-end benchmark, not a view of these results.

### Cell states and footnotes

- **`2.2e7×`**, a value. Its footnote gives the artifact, the configuration and its commitment scheme, P in instances per second, the batching (total, per proof, in flight), the sweep and plateau point, the host CPU and the whole-proof bound. It also gives who verified it and how: a live verifier with its own coins, or a file re-verification replaying the runner's coins, which is not transferable evidence. A re-packed instance set names its instance-equivalence artifact.
- **`2.2e7× (prov.)`**, provisional, computed. The configuration's current statement for this subcircuit (its relation pin, commitment scheme and transcript) has no red-team clearance yet, and the footnote says what awaits review.
- **`—`**, no valid result. The footnote says whether the family has results only for a weaker statement (and which), or only below the filter.
- **`n/s`:** the backend declares it doesn't support this subcircuit, with its reason.

Below Table 2, the render lists every rejected result with its first reason (all reasons are in `--format json`).

## Table 3: where the time goes

One row per Table 2 cell, the same result. Each entry is seconds per instance with its share of the end-to-end time, since batches differ between cells. The row also prints the cell's two overheads, each against the native time 1/N, and they add up to the Table 2 cell:

- **Serving overhead** = commitment time × N. Commitment is computing the commitments the statement names, for inputs, weights and outputs (row digests and trees): what serving pays to commit the values. The harness measures it in isolation on the line's GPU, with the scheme's fastest conforming committer; the vLLM application's own benchmark measures it in place.
- **Proving overhead** = proving time × N. Proving is the buckets witness, encoding + witness commitment, arithmetic, lookup, ZK additional, serialization, other. Other = proving total − Σ buckets − Σ joints, and must be at least −1% of the total. A fused stage `t.joint.a+b` prints once as `a+b: 41 µs (37%)` in the first bucket column it covers, with `↞` in the others.
- **End to end** = commitment + proving: the time Table 2's P divides, so serving overhead + proving overhead = the Table 2 cell.

## Drill-downs

These use the same records and rules, and their layouts are part of this spec.

**D2, results by configuration** (replaces today's D2). For every non-archived configuration and line it shows the fastest independently verified result, else the fastest result, as `P · N/P`. Next comes ✓ if the result fills the Table 2 cell, else the first reason that applies, then `iv` or `nv` (independently verified or not). Weaker-statement results, such as today's A-GKR, bare B-Ligero and Poseidon2-bound B-Ligero, are shown here. The reasons, in the order they are checked:

- R: weaker statement than the full relation;
- Z: not the family's declared class;
- S: commitments on an inadmissible scheme: an algebraic hash (Poseidon2), a linear digest (Ajtai), a proof system's own commitment, or a scheme the core doesn't define;
- L: fails the view's security filter: the bound, or an algebraic hash in the soundness argument;
- U: not independently verified;
- F: proof files not preserved;
- I: another instance set;
- K: prover not on the line's GPU;
- P: phase-sum;
- M: protocol not met (not warm, fewer than five timed runs, contended, or not a plateau point);
- D: capped by a red-team verdict;
- X: other.

**The other drill-downs:**

- **D3, verifier and communication cost per Table 2 cell,** as today but per instance: proof bytes, prover-to-verifier Gbit/s to keep pace, verifier-to-prover bytes (coins), rounds, verifier CPU seconds, verifier cores to keep pace, and the same-datacenter live tax. Sources and the ‡ † ° … markers are unchanged.
- **D4, sweep curves:** throughput against total batch for each configuration that heads a cell, with the plateau point marked.
- **D5, native estimates:** each line's work model per unit, its busiest unit and its peak entries with sources.
- **D6, history:** each cell's past values (the hill-climb view).

## Admissibility

A result counts in any proving view (Tables 2 and 3, and a ✓ in D2) only if all of these hold:

1. **It is schema-conformant**, so the result builder accepted it (`contract.validate` for `bench-result/v1`). Its phase buckets and joints don't exceed its proving total by more than 1%: a result that does stays out, and the fix is to the accounting, never the rule.
2. **It names a registered subcircuit, a hardware class and a declared configuration.**
3. **It ran on the subcircuit's instance set,** by id and index range. A re-packing counts only through an `instance-equiv/v1` artifact showing decoded x, W and y byte-identical, labelled `verified=accepted` by someone who produced neither it nor the result (footnoted).
4. **The prover ran on the line's GPU SKU and board variant** (`tables.normalise_sku`, memory within 12%).
5. **Its proof files were dumped and preserved:** `research data preserved` succeeds.
6. **A non-producer verified it.** That means a `verified=accepted` label (or the back-filled `independently_verified=true`) whose asserter is not a producer: not the producing attempt's campaign, not an asserter of the result's own `candidate` or `label` labels, and not a lane its meta or a `lane` label names. The re-verification works from the store alone: proof hashes against the dump manifest, the statement's commitments and public words recomputed from the instance set, the verifier's build identity, and negatives rejected.
   - The producer's own verification never counts.
   - A proof counts only under a pinned identity. An SP1 verification names the fork commit, and a verifying key must be reproduced from a fresh build before its proofs count.
7. **It was measured under the protocol:** warm, at least five timed runs, uncontended.
8. **The red team has not capped it** below the family's declared class. The latest `red-team-*` audit on its configuration's statement stands, downgrades included, and nothing is upgraded.

**Red-team review of statement changes.** A change to what a configuration proves or how it is checked (the relation's lowering, circuit or compiled system, the commitment scheme, the transcript) makes its results provisional. They stay provisional until a `red-team-*` audit of the new statement grants its declared class. A prover-only change keeps the clearance when its proof bytes equal a cleared version's under fixed coins, and its verification records that comparison.

## Measurement protocol

- **Where:** every measurement is a recorded `research run --tool … --campaign …` on a pod, never a laptop or the control pod.
- **Batching** belongs to the backend and is recorded: instances per timed run, per proof and in flight, plus shape settings such as B-Ligero's columns per proof. The suite fixes no batch size and no K.
- **Sweep:** the harness doubles the total batch from 1,024 instances, at the backend's per-proof settings, until two successive doublings together raise the median throughput by less than 2%, or memory runs out. The plateau point is the sweep point with the highest median throughput.
- **Warm:** one full untimed pass comes first, absorbing compiles, CUDA-graph captures, allocator growth and SP1's first large shard.
  - Cold first-proof time and one-time setup (keys, kernel compiles) are recorded separately and never enter P.
  - Commitments are data, not setup. Each timed run commits its own batch and never reuses trees or digests from another run.
- **Runs:** at least five timed runs per point, reported as the median with minimum and maximum, plus the timing guard's uncontended verdict. When two configurations are compared, alternate them on the same machine, since shared hosts give random slow runs of 0.1 to 6.6 s.
- **Recorded with every result:**
  - throughput and per-run totals; commitment time and the phase buckets;
  - batching, and the sweep id and point;
  - peak device and host memory, and proof bytes;
  - verifier cost: CPU seconds, cores to keep pace, rounds, bytes each way, live-verifier tax;
  - hardware (GPU, board memory, driver, CUDA, host CPU) and software identity;
  - the instance set and range, the runs, the contention verdict, and references to verification verdicts.
- **Never security:** a result names its configuration, and Table 1 says what that configuration guarantees.
- **Hosts:** the host CPU can change proving time by 2.2× on the same GPU, so compare hosts in the drill-down and don't read them across lines.

## Inputs

- **Generated from the IR.** Each subcircuit has one instance set generated from its Definition: uniform over its domain plus its edge families, in the shape serving uses (for GEMM coordinates, tiles that share rows), and exhaustive for unary 16-bit operations.
  - Expected outputs come from the reference evaluator.
  - Seeding uses a label-keyed SHA-256 counter, so instance i is computable directly in any language.
  - Each set is content-addressed (`art:` id) and frozen only after byte-identical regeneration on a second machine and hardware replay on its anchor GPU.
  - There is no calibration to "realistic" value distributions.
- **A stream.** A set is index-addressable: its frozen part is the first n instances, and a batch larger than n continues with the recipe's next instances.
- **The five frozen sets stay exactly as they are:**
  - the A100 set (`bench-instances/v1` `vu-k1536`, manifest `059103cf…`, with its 24 captured coordinates and real weight rows);
  - the FP8 Ada, BF16 Hopper, FP8 Hopper and NVFP4 sm_120 sets, pinned by their recipe digests in `contract.py`.
- **New subcircuits** use the generator.
- **Backends never generate benchmark inputs;** they read sets by id.

## Standing decisions

- **SP1 naming:** SP1 stock is unmodified SP1, and SP1 precompile is the TC_DOT chip fork, everywhere (labels, kb notes, briefs). SP1 precompile beyond the A100 is on hold.
- **SP1 security:** about 2^-94.5 per whole proof (2^-99.0 per shard, union-bounded over its shards), limited by the KoalaBear^4 field. It can't reach 2^-128 without protocol changes: grinding in every FRI commit round, in zerocheck and in the jagged reduction, or a larger extension field. The figure uses proven unique-decoding bounds (soundcalc). SP1's Merkle trees and challenger use Poseidon2 over KoalaBear, an algebraic hash. Table 1 records both facts, the published filter excludes SP1 on either one, and nothing is relabelled.
- **A-GKR:** its column is the family's best configuration, hill-climbed onto every line, and a more promising GKR variant may get its own lane (standing permission). Its Merkle hash is SHA-512. Today its configurations keep operands private and bound to nothing, so it fills no Table 2 cell until one binds them to an admissible scheme.
- **Commitments in Table 2 use standard hashes only** (user decision, 2026-09-24 evening): SHA-256 or BLAKE3, and both are benchmarked. Poseidon2 and other algebraic hashes, and Ajtai digests, never qualify. Their results, and shared tiles, stay in the drill-down. This replaces the earlier headline rule of Poseidon2 per row with no sharing.
- **Two first-class commitment schemes** (user decision, 2026-09-24 late evening): frame-v3, and the vLLM application's framing hardened as `vllm-v1`. Configured backends select one, Table 1 names it, and Table 2 compares them, each with its serving overhead and proving overhead. Whether to converge on one scheme is decided later, from these numbers.
- **Approval:** any change to a definition, column or rule here needs the user's explicit approval first.

## Render

Until the switch, the published tables are today's, rendered as before:

```sh
S=~/projects/verity-main-wt/cli   # sparse worktree at main
PYTHONPATH=$S/backends/numerical/python:$S/tools/research/src:$S \
  ~/projects/verity-main-wt/main/.venv/bin/python -m verity_numerical.bench.tables    --root ~/.research/store --format md
PYTHONPATH=... python -m verity_numerical.bench.drilldown --root ~/.research/store --format md
```

- The steward renders both daily at 13:00Z into `renders/daily/` (`steward.toml`).
- The tables are re-rendered on every verified result and for the user's 6:00 PM PT digest. Big changes are reported right away: a new backend, a gap filled, a headline record broken.
- The new views render beside today's tables as a labelled preview, which is never shown as the published numbers.
- After the switch, the new views' command replaces the two above.

## The switch

The published numbers switch once, in a 6:00 PM PT digest labelled as a change of method. That digest shows each old number beside its replacement, or beside the reason it left Table 2. The switch waits for all of:

1. the user's approval of this spec;
2. **parity:** the new views, rendered with today's parameters, select exactly the cells of a `tables --snapshot` taken for the purpose, with the same artifacts and ratios. Today's parameters are a 2^-128 security filter, a batch of 4,096, K = 1536, today's bare and "+ in-proof hash" columns with Poseidon2 per row and no sharing, and proving time only. The parity render is recorded as an artifact;
3. every configuration that heads a Table 2 cell under this spec swept to its plateau, with each plateau point independently verified.

If no configuration qualifies yet, Table 2 is published empty, with every old number beside the reason it left. Until the switch, this spec's views are previews. The Verity Foundation site publishes no tables before the switch, and its first public tables come from the switch render.

## What "complete" looks like, and the gaps (8:48 PM PT render, 2026-09-24)

| Table 2 column | Lines with a full-relation result | What fills the rest |
| --- | --- | --- |
| B-Ligero | 0 of 15 (five lines, three schemes). Its five full-relation results bind Poseidon2 (S), and its frame-v3 BLAKE3 row leaves are built and Rust-verified on two of the five relations | frame-v3 BLAKE3 and SHA-256 row leaves, then `vllm-v1` leaves, on all five lines; the verifier's `steps` pin (red-team H2); plateau sweeps with commitment inside the timed run; independent verification; then optimization |
| A-GKR | 0 of 15: operands private and bound to nothing | Row digests computed in its circuit and published, checked by the verifier against the scheme's trees (SHA-256 first, then BLAKE3), then hill-climb that configuration |
| SP1 | 0 of 15: bare guest, operands unbound | A committed guest on the frozen sets that computes SHA-256 row digests with SP1's SHA-256 precompile (the typed path covers only the Ampere BF16 subcircuit). Below 2^-128 and Poseidon2 inside, so unfiltered view only |

After these come new subcircuits, other K values first, each with its instance set and at least one backend's support.

---

# For review (not part of the file)

## What must change to comply

### Renderer

Today this is `verity_numerical.bench.tables` and `.drilldown`; the new views go in `benchmarks/` (`verity-bench`).

1. Keep today's tables unchanged until the switch, and render the new views beside them as a labelled preview.
2. Add the parity render (today's parameters as filters) and check it against a `tables --snapshot` taken for the purpose, the benchmark proposal's Phase 0 oracle.
3. Remove three checks from the validity predicate: K = 1536 and B = 4096 (reason B), the `SOUNDNESS_LOG2` gate (it becomes the default filter, computed from Table 1), and the `AUTH_MODES` column split.
4. Add these checks:
   - the full-relation check (reason R), read from the configuration's declared statement and the verdict's statement digest;
   - the commitment-scheme check (reason S), read from the configuration's declared scheme: its core id, and the class of each hash in it;
   - the proof-custody check (reason F), which `reject_codes` doesn't make today (only the verifier's procedure implies it);
   - the protocol check (reason M).

   Report red-team caps as D rather than Z.
5. Build Table 1 from configuration records instead of the literals in `tables.CANDIDATES` and D1's prose, including the new hashes and proximity-bound fields. Compute each cell's whole-proof bound from its configuration's soundness function at the cell's batching, from proven bounds only. The published view's second filter reads the hashes' class.
6. Table 2 changes:
   - one line per subcircuit, hardware class and commitment scheme (the scheme with its leaf hash, read from the configuration record), with a scheme's lines shown once a configuration declares it;
   - one column per backend family;
   - drop the measured-native column (`_native_measured`);
   - print N in instances per second with its busiest unit and peak entry, taking peaks from `verity.silicon` (today `Target.native_peak`, with equal values);
   - print P in the footnotes.
7. Compute the headline from declared configurations. The name-prefix recognisers (`Candidate.backend_names`, the `drilldown.VARIANTS` regular expressions) survive only in the frozen `bench-result/v1` adapter. Honour `archived`, and take "n/s" from capability declarations. Compute the provisional marker from red-team labels on each configuration's statement; today the digest writes "PROVISIONAL" by hand.
8. Table 3 changes: add the commitment column (today `relation.hash.commit_seconds`, outside `t.total`), make the total end to end, print seconds per instance, print the serving overhead and proving overhead (each time × N), and relabel the bucket header "Encoding + witness commitment".
9. D2 gets the new reason letters and shows weaker-statement results. Add D4 (sweep curves), D5 (native estimates) and D6 (history).
10. The steward's render in `tools/research` (`notes.py`) calls the renderer by module path, so moving it to `benchmarks/` changes `notes.py` in the same PR.

### Records, declarations and the harness

1. **One builder for `bench-result/v2`,** performance only, which refuses non-conformant results; `v1` stays readable through a frozen adapter. Each v2 result:
   - carries no `security.*`, `proof_class` or `authentication`;
   - names its configuration id;
   - records batching, sweep id and point, the protocol (warm, runs, statistic, contention), commitment time and phase buckets, and the instance set id and range.
2. **Configuration records** from each backend's capability declaration: statement form and per-port visibility, commitment scheme (core id), hashes (role, property, class), class, interaction and transferability, proximity bounds (regime, proven or conjectured), assumptions, soundness function, pin, `archived`.
3. **The harness** sweeps, runs warm with at least five timed runs, and commits each run's batch inside the timed region.
4. **Instance sets:**
   - Generation moves out of B-Ligero (`relchain._instance`, `fp4/chain.instances_fp4`) into the harness, reproducing the four synthetic sets byte for byte against their pinned digests.
   - The A100 set needs a defined stream beyond 4,096 instances; today larger batches recycle the set.
5. **Independent re-verification** recomputes the statement's commitments from the instance set. verify-po does the frozen-set part by procedure today.
6. **Red-team verdicts** name the configuration statement they clear; today they are labels on single artifacts.

### Lanes

1. **B-Ligero:**
   - Register frame-v3 configurations with BLAKE3 and SHA-256 row leaves on all five lines, after the verifier pins `steps` (red-team H2), then `vllm-v1` configurations once the core defines that scheme.
   - Sweep each to its plateau, committing inside each timed run with no tree cache across runs (`--auth-cache`).
   - Get each plateau point independently verified. The pod time is the research coordinator's call.
   - The Poseidon2 configuration stays a D2 result. The lane plan is in [commitment-scheme-decision.md](commitment-scheme-decision.md).
2. **A-GKR:** to return to Table 2, bind x, W and y to frame-v3 trees over SHA-256 or BLAKE3 row digests computed in its circuit, then hill-climb that configuration. Until then its results are D2 entries.
3. **SP1:** needs a committed guest on the frozen sets, checking frame-v3 SHA-256 row leaves; its typed path covers only the Ampere BF16 subcircuit. It stays below 2^-128 with Poseidon2 inside, so it shows only unfiltered.
4. **Every lane:**
   - Declare configurations instead of relying on name prefixes.
   - Until the switch, keep writing `bench-result/v1` with today's fields, because the published renderer needs them.
   - Preserve proof files, and ask for independent verification of the point meant to fill a cell.
   - Send statement changes to the red team.

### Today's cells

P is in instances per second at today's batch of 4,096.

| Line (N) | A-GKR | B-Ligero, bare | B-Ligero + in-proof hash |
| --- | --- | --- | --- |
| A100 BF16 (1.0e11/s) | 3.4e7×: leaves Table 2 (R) | 5.9e6×: leaves (R) | 2.2e7× (P 4.6e3/s): leaves (S), Poseidon2 |
| H100 BF16 (3.2e11/s) | 6.2e7×: leaves (R) | 8.9e6×: leaves (R) | 4.3e7× (P 7.5e3/s): leaves (S) |
| H100 FP8 (6.4e11/s) | 4.4e7×, provisional at 8:48 PM PT: leaves (R) | 1.1e7×: leaves (R) | 4.6e7× (P 1.4e4/s): leaves (S) |
| RTX 4090 FP8 (1.1e11/s) | 1.3e7×: leaves (R) | 2.2e6×: leaves (R) | 9.1e6× (P 1.2e4/s): leaves (S) |
| RTX 5090 NVFP4 (5.5e11/s) | 1.8e7×: leaves (R) | 4.5e6×: leaves (R) | 1.8e7× (P 3.0e4/s): leaves (S) |

- **No cell remains.** Table 2 is empty at the switch unless admissible results have been swept to their plateau and independently verified by then.
  - The b-sweep lane (Sep 22) found bare, non-ZK B-Ligero on an H100 within 10–18% of its plateau at 4,096. The BLAKE3 row-leaf configuration hasn't been swept.
  - Its commitment time enters the total (decision 19).
- **All fifteen leaving cells** stay results in D2: ten with R and five with S. The B-Ligero Fiat–Shamir lines under today's Table 2 move to D2 with Z.
- **SP1 has no cell before or after the switch.**
- **The measured-native column goes,** and N ÷ P equals today's ratio for all five subcircuits: each is 3,072 tensor-core FLOP per instance at the same datasheet peak.

## Resolved points (Daniel, Sep 24 evening)

1. **Table 2 counts commitment time, end to end** (decision 19). Today the in-proof hash mode builds its trees and row digests before the timed runs, recorded as `relation.hash.commit_seconds` outside `t.total`: 2.3–13 s per 4,096 instances in the Sep 23 lane reports. GPU SHA-256 and BLAKE3 kernels hash at 359–446 GB/s on a 4090, so that time is host overhead, and the committer lane's target is to take it to milliseconds.
2. **The full relation's commitments.** Each configuration names a scheme defined in the core, built only on SHA-256 or BLAKE3. Algebraic hashes (Poseidon2 and the like) and linear digests (Ajtai) don't qualify. Two schemes are first-class, frame-v3 and `vllm-v1`, and Table 2 compares them line by line. Reasoning and the plan are in [commitment-scheme-decision.md](commitment-scheme-decision.md).
3. **The published default filter,** approved as drafted: 2^-128 or better, in the family's declared class, with the unfiltered pick footnoted wherever it differs. For consistency with point 2, it also excludes algebraic hashes inside proof systems. That changes no cell today, because SP1, the only configuration it affects, is already below 2^-128.
