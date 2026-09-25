---
kind: kb
topic: the tables the user wants
updated: 2026-09-25T06:30Z (rewrite with the user's decisions of 2026-09-24 evening, published from the Project store's docs/tables-spec-draft.md; replaces the 2026-09-24T20:20Z spec, kept as kb/TABLES-v1-20260924.md)
---

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

