---
cursor:
  subagentId: "bc-289e3cdc-efb4-5313-9d86-6f706fe20b3d"
---

# vLLM programs as Boolean circuits: what we actually know (ground truth, Sep 27)

**For:** Daniel. **Written:** Sun Sep 27, 2026, about 12:15 PM PT. **Scope:** row #101 in depth, all 13 served rows in summary. **Method:** every number below was recomputed on CPU from the Project datasets (`internal/datasets/boolean-circuits/`, `program-graphs/`, `serving-view/`), from `main` at `e40fa730`, and from PR #140's head `b2527cb6`, unless its confidence says otherwise. No pods, no code changes. The scripts and their outputs are in `internal/vllm-circuit-ground-truth/`.

**Confidence scale.** **High:** recomputed here and cross-checked a second way. **Medium:** recomputed here one way, or a lane's record that I spot-checked. **Low:** taken from a lane report or PR description without recomputing it.

## Headline

1. **#101 is one Boolean circuit of $1.568 \times 10^{14}$ ANDs, $1.12 \times 10^{16}$ XORs and $2.57 \times 10^{13}$ NOTs.** It covers one request end to end: 32 engine steps, 46,654 Calls, $1.88 \times 10^{10}$ word gates. GEMM is 94.7% of the ANDs, the sampler 3.6% and attention 1.6%. *High.*
2. **Its inputs are the weights, the prompt, one seed and one split count per step, and its outputs are the 32 sampled tokens.**
   - The KV cache is not an input. It is ordinary interior values that later attention Calls read directly (137.6 M words over 268,832 reads).
   - Temperature, top-p and the per-step Philox positions are circuit constants.
   - One input has no anchor: `splits`, the top-p kernel's split count, is supplied by the prover and checked only by the Match at serving time, never in the circuit. *High.*
3. **It is plain gates except in three places, and none of them is fixed on `main`.**
   - The top-p keep word is one word gate of $1.45 \times 10^{11}$ ANDs, counted piece by piece but never built as a circuit. It computes all six split-count pipelines and discards five, which is about 83% of its ANDs.
   - The embedding gather (587,776 word gates) is a "commitment opening" with 0 gates in the store's export. PR #140 lowers it as a multiplexer, adding an estimated $1.2 \times 10^{12}$ ANDs.
   - The MUFU table reads are counted as gates but have no gate lists (they're "lookup slots").
   - Everything else is AND, XOR and NOT gates, and the XORs are 71× the ANDs because every table read's linear sums are counted as XOR chains. *High.*
4. **The published sizes are badly wrong on 5 of the 13 rows.**
   - On the four MoE rows and #74 (FP8), the export multiplies a per-Call gate count by a per-coordinate instance count. So #67 is $5.8 \times 10^{15}$ ANDs, not $2.84 \times 10^{18}$, and #74 is $4.3 \times 10^{15}$, not $1.91 \times 10^{19}$ (400× to 4,400× too high).
   - On five batched rows, attention assumes every key count T is equally common. That overstates them by 1–10%: #4 is $3.79 \times 10^{14}$, not $4.16 \times 10^{14}$.
   - #101 and the other rows are right. *High that the published values are wrong; Medium on the exact corrected values.*
5. **Circuit ↔ IR rests on test vectors, and on `main` it doesn't reach most of #101.**
   - `circuit-check --all` on `main` compares a whole Definition's Boolean circuit with the IR on 85 of 811 targets, mostly at toy shapes (N = 16, V = 16).
   - On `main`, no piece exists for attention's softmax, the norms' row scalars, the sampler, the argmax or the gathers. PR #140 raises the count to 154, but still has no piece for the keep word or the gathers.
   - In Lean this link is the named hypothesis L1. *High.*
6. **IR ↔ GPU rests on the Match plus sampled replay.**
   - #101's record replays 1,374 of 46,558 Calls (2.95%) bit-exact, and the tensor-core model replays A100, RTX 4090 and H100 captures with 0 mismatches.
   - The weakest links are four:
     - the MUFU tables were measured on an RTX 4090, not the L40S;
     - `MufuEx2Ftz` knowingly differs from the hardware below $|x| = 2^{-63}$;
     - the split top-p reference was partial where the two warp halves disagree about stopping (being made total in #169);
     - `splits` is unanchored. *Medium.*
7. **`Q_word` v1 ($X = 16$, $W = 32$) gives #101 273,995,039 units, and every one of them commits exactly one value.**
   - 84.3% of units are 16-bit and 15.7% are 32-bit.
   - Committed: 209.8 M Call-output words plus 64.2 M interior words, 634 MB per request.
   - Serving already commits all but 349,439 of those words (4 tap classes, 1.4 MB).
   - #101 has 0 invariant violations: core's evaluator (#111) and the vLLM copy agree on every #101 Definition. *High.*
8. **Nothing uses `Q_word` as the record.**
   - The one-stage audits used `Q_template_instances` over synthetic population programs. A4 used 6,771,765 units for layer 0, where `Q_word` has 11,609,150; GEMM coordinates are identical, and RoPE, norms and SiLU are 64× to 8,192× coarser.
   - The regression record replays one unit per Call (46,558).
   - Serving's `vllm-v1` roots bind no partition. The steps to make `Q_word` the record are in §4.4. *High.*
9. **Units spanning Calls could remove up to 42% of #101's committed words.**
   - 116.4 M of its 209.8 M Call-output words are read by exactly one unit: GEMM outputs into the residual add or SiLU, the residual chain, and the logits into the sampler.
   - The remainder fans out to between 2 and 128,256 units and must stay committed under any query. *High for #101; not computed for the other rows.*

## 1. Row #101: inputs, outputs and interior

#101 is Llama-3.2-1B, BF16, L40S, TP1, batch 1, a 256-token prompt, 32 output tokens, temperature 0.8, top-p 0.95, batch-invariant eager. The record Build's request program is `ccc21347…` (SHA-256 `program_digest`).

**The program** (serving view, *High*):
- 46,654 Calls: 46,558 model and sampler Calls, and 96 constant Calls;
- 32 engine steps: prefill, then 31 decode steps;
- $1.8806 \times 10^{10}$ word gates in the Calls, plus 1,244,203,361 Input gates, $2.0050 \times 10^{10}$ in all.

A **word gate** is one IR primitive producing one value, usually 16 or 32 bits. The lowering expands each one into AND, XOR and NOT gates: a tensor-core k-step is 8,260 ANDs, and the top-p keep word $1.45 \times 10^{11}$.

### 1.1 Inputs

| Input | Words | Bits each | Read by | Anchor | Confidence |
|---|---:|---:|---|---|---|
| Weights: 99 tensors | 1,244,203,072 | 16 | every model Call | the declared model's weights root | High |
| `prompt` | 256 | 32 | the embedding at prefill | the client's request | High |
| `seed` | 1 | 64 | each sampler (32 reads), through Philox4x32-10 | the request or randomness source | High |
| `splits` | 32 (one per step) | 32 | each sampler: which of six top-p pipelines to keep | **none in the circuit.** $S_t = \mathrm{SplitsFor}(\lvert\mathrm{live}(t)\rvert, \mathrm{SMs})$ is checked only by the Match (GM-01 G6) | High |

The 99 weight tensors are:
- the embedding table, which is also the LM head (tied): one tensor, read by both the gather and the `logits_processor` GEMM;
- 6 per layer × 16 layers: input norm, qkv, o, post-attention norm, gate_up and down;
- the final norm;
- one `rotary_emb.cos_sin_cache`, filed under layer 0 and shared by all 16 layers. It is a table vLLM derives from RoPE's θ, not a checkpoint tensor.

**Not inputs** (*High*):
- **Constants.** The 96 constant Calls are temperature `0x3f4ccccd` (0.8) × 32, top-p `0x3f733333` (0.95) × 32, and Philox positions 255 to 286. Together with every constant inside the Definitions (34 constant primitive kinds) they are public circuit structure, which makes the circuit specific to the request's sampling settings and shape.
- **The KV cache.** The program spans the whole request, so K and V are the outputs of earlier positions' RoPE-k and qkv Calls, read directly by every later attention Call. These are the serving view's `state` edges: 15,872 edges, 268,832 reads, 137,641,984 words. Each K and V word is committed once, as its producing Call's output.
- **The sampled token.** It feeds back through 31 `token` edges: step $s$'s sampler into step $s+1$'s embedding.

### 1.2 Outputs

The program returns the 32 sampled token ids, 32 bits each. The serving view's `sampler_rule` is `return`: element $s$ of the request program's return is step $s$'s sampler output. The first 31 are also read by the next step's embedding. *High.*

### 1.3 How every other gate is classified

At the word-gate level (`Q_word` v1, *High*):

| Class | Word gates / values | Share | Notes |
|---|---:|---:|---|
| Input gates | 1,244,203,361 | | certified by the input unit (always checked, never drawn) |
| Structure (constants and wiring) | 206,960,187 | 1.10% of Call gates | never committed, never counted. They are `Const32[0]` accumulator seeds (one per GEMM coordinate, 112,254,976), `Bf16ToF32`, and constant-folded `I32Add` lane counters (256,511 per sampler step) |
| Computing gates, in 273,995,039 units | 18,598,672,371 | 98.9% | |
| of which output units (one per Call-output word) | 209,825,824 units | 76.6% of units | 209,825,792 BF16 activations plus the 32 tokens |
| of which committed interior units | 64,169,215 units | 23.4% | attention's S scores 21,159,424, f32 probabilities P 21,257,216, BF16 probabilities 21,159,936, `max_scaled` 242,688, inverse sums 146,944, guarded max 97,280 and row maxima 96,256; the fused norms' rsqrt 9,184; the Triton norm's scale 287 |
| Redundant (computed twice inside one unit) | 32 | | one per sampler step, inside its single unit |
| Dead units | 0 | | |
| **Program-level dead Calls** | 2,040 Calls | about $7.3 \times 10^{12}$ ANDs, 4.7% | *Medium.* No sampled token depends on them (serving view: `needed_by_none` = 2,040). They are layer 15's work after qkv and RoPE-k at the 255 non-final prefill positions, plus the final norm there: 255 × 8 Calls. Every check passes them, because `Q_word` works Call by Call |

At the Boolean level, each word gate's piece is AND, XOR and NOT over its input bits and the constants 0 and 1. A MUFU read (ex2, rcp, rsq or sqrt, over tables of $2^{23}$ or $2^{24}$ words) is one-hot decoding plus one AND per value bit and minterm, then XOR sums: 41,308 or 49,576 ANDs. In the store's export these reads are `lookup-slot` subcircuits whose value bits enter the gate lists as inputs. PR #140 re-presents them as plain gates, with the table as constants.

By template (ANDs, *High*):

| Template | Instances | ANDs | Share of ANDs | XOR / AND |
|---|---:|---:|---:|---:|
| GEMM coordinate (K = 2048 and 8192, LM head included) | 112,254,976 | $1.485 \times 10^{14}$ | 94.70% | 1.9 |
| Gumbel top-p sampler | 32 | $5.61 \times 10^{12}$ | 3.58% | 1,352 |
| Attention head (exact per T) | 146,944 | $2.47 \times 10^{12}$ | 1.58% | 1,331 |
| SiLU·mul, fused RMSNorm, RoPE, Triton RMSNorm | | $2.26 \times 10^{11}$ | 0.14% | |
| Embedding gather | 287 rows | 0 in the store's export | | |

## 2. Is it all plain gates?

| Construct | On #101 | Size | Status | Confidence |
|---|---|---|---|---|
| **The top-p keep word** `TopPMaskWordx128256_v1` (composed Definition, too large to materialize) | 1 word gate per step, 32 in all | $1.449 \times 10^{11}$ ANDs each, $4.64 \times 10^{12}$ in all (3.0% of #101); $2.37 \times 10^{14}$ XORs each | Written once over vectors of words (`topp_word`): six pipelines × seven stages × pieces with instance counts. An engine counts or evaluates it, and no circuit object exists. It computes all six split-count pipelines (about $2.41 \times 10^{10}$ ANDs each) and keeps the one `splits` selects, so about $1.21 \times 10^{11}$ ANDs per step are discarded. Checked against `sampling.topp_keep` on 480 rows at V up to 9,000 and on 12 rows at V = 128,256. On PR #125, open. #169 makes the reference total on rows where the warp halves disagree, and #125's twin still has to follow it | counts High; checks Low |
| **Gathers:** the embedding `GatherBf16x128256` | 587,776 word gates | 0 gates in the store's export (`commitment-opening`); about 2.05 M ANDs each as PR #140's multiplexer (about 16 per candidate: 1,049 ANDs at V = 64, 2,072 at 128), so about $1.2 \times 10^{12}$ in all (+0.8%) | Being lowered: PR #140 (open) makes it a composed Definition of multiplexers. The store's copy of the export predates that | Medium |
| **Constant tables:** MUFU ex2, rcp, rsq, sqrt | about 1.5 M reads per keep word, plus attention and the norms | 41,308 or 49,576 ANDs per read | Counted as gates, but no gate lists (`lookup-slot`). PR #140 re-presents them as plain gates. The tables are pinned by SHA-256 | High |
| **Batch and scan nodes** | 109 Definitions (78 primitives) with 54 batch nodes and 2 scans (`TopPMask` over 128,256 lanes, `GumbelSelectF32` over 128,255) | none: they're compression | `Q_word` flattens each Call, and a separable batch is cut member by member. The cost is verifier memory: the sampler's flat graph is 2.18 M gates (42 s in Python), and a flat `Gemm_v1{K=2048,N=16384}` ran out of memory at 14 GB | High |
| **Dead gates** | IR dead gates are warnings in `circuit-check` (e.g. one unused `Const32` per attention head Definition). At program level, 2,040 Calls (§1.3) | about $7.3 \times 10^{12}$ ANDs | Nothing flags the program-level ones except the serving view's `needed_by_none` | Medium |
| **Free (structure) gates** | 206,960,187 word gates | 0 ANDs by definition | Settled design: hardwired, never committed | High |
| **Redundant gates** | 32 IR gates; Boolean redundant ANDs | on `main`, `circuit-check` warns of 95,249 redundant ANDs over 87 targets | Hash-consing, PR #104 (open), removes the Boolean ones. The export already uses it | High |
| **Constants not propagated** | 384,743 word gates per sampler step lowered with generic pieces | Each lane's `BitAt` reads its own bit of the keep word at a constant index, but is lowered as the generic 128,282-AND multiplexer. That is about $1.65 \times 10^{10}$ ANDs per step (9.4% of the sampler, 0.34% of #101) that are really wiring | Not being fixed yet. A record lowers at most 8 constant-operand variants of one primitive | Medium |
| **Recomputes on the default path** | none on #101 | | §5 (#74, #57) | High |

## 3. How we know it's right

### 3.1 Circuit ↔ IR (test vectors, not proofs)

- **`circuit-check --all` on `main` `e40fa730`**, run here in 11 minutes on 4 CPUs. *High.*
  - 811 targets: 790 Definitions and 21 templates, 64 vectors each (edge vectors first, fewer when the reference is expensive).
  - Whole-Definition Boolean circuits are compared on 85 targets, and 151 more through their template's units.
  - 400 targets have a primitive with no piece: attention's softmax, the norms' scalars, the sampler, the argmax and the gathers.
  - The rest: 109 are constants, 37 are over the lowering budget, and 8 have no IR body.
  - It reports 14 failures, all known: 12 `F32Add` and `F32Mul` NaN-payload mismatches (fixed by #104, open) and 2 `ScaledMmFp8Block` recomputes.
- **The same run on PR #140's head `b2527cb6`**, which includes #104 and #125. *High.*
  - 154 targets are lowered whole, 183 are over budget, and 186 still have no piece: small gathers such as `GatherBf16x16`, `BitAnd`, `Lifted[…]` variants and `AmpereBF16TcDot16_v2`.
  - The keep word (`TopPMaskWordx16`, `x64`) has no piece at any V.
  - The only failures are the 2 known recomputes.
- **The shapes are small.** The targets are toy specializations plus 21 templates (RoPE head at D = 64, GEMM coordinate at K = 64, RMSNorm at N = 2048, SiLU·mul at I = 8192, attention head at T = 1 and 17). No #101 Definition at its served shape is compared with the IR as one Boolean circuit. *High.*
- **At the served shape the evidence is per piece.** From the lane's reports: 20,000 vectors per tail primitive, 6,000 for the others, 60,000 for the BF16 k-step and 1,500 for FP8; the keep word on 492 rows; 0 mismatches. *Low: not rerun here.*
- **The export's self-checks** show the export is consistent with itself, not that it matches the IR:
  - 3,126 gate lists, each evaluated against its circuit on 64 random vectors;
  - 59,817 wiring instances compared;
  - 9,009 cuts equal to the program graphs'.
- **The partition evaluator.** I re-ran core's `verity.ir.cut` (#111) on every distinct #101 Definition: attention at seven key counts, and the sampler. Units and gates equal the program graph's (computed by `verity_vllm.query.word`), and `check_cut` passes the invariant and the width rule. *High.*
- **In Lean** this link is **L1**, "each template's rows compute its gates": a named hypothesis whose evidence is these tests. A verified lowering, RoPE first, is planned.

**Weakest point:** on `main` there is no Boolean circuit at all for most of #101's non-GEMM primitives. Even with #125 and #140, the keep word and the gathers are checked only by their own lane tests, not by `circuit-check`.

### 3.2 IR ↔ what the GPU ran

| Evidence | #101 | Confidence |
|---|---|---|
| Build → program; Match GM-01 G1–G8 folds the capture onto the program | GREEN in the regression record; PASS on the redraw run `r20260926-035624-a133` | High (record read) |
| Sampled replay, bit-exact against committed values | 1,374 of 46,558 replay units (per stratum 2), grade complete | High |
| VU export replay | 1,568 units, 256 per family and all 32 samplers, replayed equal | Medium |
| IR evaluator on recorded served inputs | 48 inputs over #101 and #4, all equal (`validation.json`) | High |
| Silicon semantics | tensor-core models replay A100, RTX 4090 (sm_89) and H100 captures with 0 mismatches (`tests/ml/fixtures`) | High |
| MUFU tables | measured on an RTX 4090 and applied on the L40S (both sm_89) | Medium |

**The weakest links:**
1. **Replay is sampled.** 97% of a run's Calls are never replayed, so the rest rests on the Match's structural fold.
2. **A known divergence from the hardware.** `MufuEx2Ftz` at $\lvert x \rvert$ below $2^{-63}$ returns, for example, 1.0083 where the GPU gives 1.0 (undefined behaviour in the model's shift). The circuit copies the IR.
3. **The split top-p reference** was partial where the warp halves disagree (#169, open).
4. **`splits`** is checked only by the Match.
5. **No L40S capture** of its own. The RTX 4090 stands in.
6. **The 09-22 records' program digests** can't be reproduced by today's tree, because the program id embeds the wrapper's module path (verify-optins finding).

## 4. Partitioning

### 4.1 `Q_word` v1 ($X = 16$, $W = 32$) on #101

*High throughout; checked against the serving view, the program graph and core.*

**It commits one value per unit.** Every #101 unit class has exactly one boundary value, so a unit is one committed word plus its private cone back to other committed words. That follows from $X = 16$ with BF16 activations: two outputs would already be 32 bits in two values, which the width rule refuses.

| Template | Units | Units per Call | ANDs per unit |
|---|---:|---|---|
| GEMM coordinate | 112,254,976 | one per output | 1,057,346 (K = 2048); 4.23 M (K = 8192) |
| Attention | 73,564,160 | 2,144 (T = 1) to 29,920 (T = 287) | 63 to 325,078 (the inverse-sum unit at T = 287) |
| Fused RMSNorm | 37,626,848 | 4,097: two outputs × 2,048 plus the rsqrt | about 2.8 k per output; rsqrt unit 7.96 M |
| SiLU·mul | 37,617,664 | 8,192 | 2,606 |
| RoPE | 11,755,520 | one per element | about 2.9 k |
| Triton RMSNorm | 588,063 | 2,049 | scale unit 9.80 M |
| Embedding | 587,776 | 2,048 | 0 in the store's export (about 2.05 M as a multiplexer) |
| Sampler | 32 | **1** | $1.753 \times 10^{11}$ |

- **Widths:** 230,985,728 units of 16 bits (84.30%) and 43,009,311 of 32 bits (15.70%), nothing else. The 32-bit units are 32 token outputs and 43,009,279 committed f32 interior values.
- **Unit size spread (ANDs):**

  | Size | Units |
  |---|---:|
  | $10^1$ | 21.2 M |
  | $10^2$ | 18.8 M |
  | $10^3$ | 69.0 M |
  | $10^4$ | 48.4 M |
  | $10^5$ | 3.75 M |
  | $10^6$ | 112.3 M (GEMM) |
  | $10^{11}$ | 32 (the sampler) |
  | 0 | 587,776 (the gathers) |

  The sampler unit is about 18,000 times the next largest. A uniform draw almost never touches it, and the stratified law gives it its own stratum.
- **Committed boundary:** 273,995,039 words, 634.0 MB per request (462.0 MB of 16-bit words and 172.0 MB of 32-bit words), plus the inputs. Units and committed words are the same number.
- **What serving must commit, beyond today:**

  | Tap class | Words | Where it comes from |
  |---|---:|---|
  | `max_scaled` | 242,688 | MS plane, labelled in PR #99 |
  | guarded max | 97,280 | ROW word 3, opt-in `GUARDED_MAX_TAP=1` (#95) |
  | fused-norm rsqrt | 9,184 | a new tap in `fused_add_rms_norm_kernel` |
  | Triton-norm scale | 287 | a new tap in `_rms_norm_kernel` |
  | **total** | **349,439** | 1.40 MB, 0.13% of the committed words |

  Everything else is already committed today: the Call outputs (`instance_outputs`) and attention's S, P, BF16 P, row max and inverse sum (`fa2_hidden_m1_stream`).
- **Invariant violations:** 0. `check_cut` passes on every Definition, and the only recomputed pair is the sampler's one, inside its unit.

### 4.2 `Q_template_instance(s)` v0

- **It can't be evaluated on #101's real program.** Every root node must be a `call` or `batch` of a listed template, and the 96 constant Calls are primitives at the root. Attention would also need all 287 specializations listed. Were it applicable, it would give one unit per Call: 46,558, the replay record's granularity. *Medium: from the query's rules; not run on the descriptor.*
- **What the audits used** were synthetic `TemplatePopulations` programs, not #101's program. Each has one batch per template and every instance's inputs as program inputs. *High.*
  - A2: 183,680 RoPE heads (partition `17478e85…`).
  - A4 P6, the partition of record for layer 0 (`631d88f8…`): six templates and 6,771,765 units.

| Layer 0, six templates | A4 (template query) | `Q_word` v1 |
|---|---:|---:|
| GEMM coordinates (K = 2048 and 8192) | 6,759,424 | 6,759,424 |
| RoPE | 11,480 (heads) | 734,720 (elements) |
| RMSNorm, Triton and fused | 574 (rows) | 1,763,902 |
| SiLU·mul | 287 (rows) | 2,351,104 |
| **Total** | **6,771,765** | **11,609,150** |

  Attention, the embedding and the sampler aren't in any audit yet.
- **The committed boundary** under the template query is each instance's inputs and outputs. GEMM rows are shared-row tables under the layout rule `gemm-grid/v0`. The link from the population program back to #101's program is that layout file (`a4_layout.json`), not a relation between digests.

### 4.3 What the record uses

- **Serving's roots of record** are `vllm-v1`, SHA-256. They bind the program, context, geometry and layout digests, **but no partition**.
- **The regression record** partitions #101 into 46,558 replay units, one per non-constant Call. Its strata are spec × request × rank × phase × module × window, and it picks 2 per stratum (1,374).
- **The program graph's `q_word_v1`** is derived data and binds nothing.
- **The opt-in serving commit in M0's format** (#119) binds a partition digest, but it's the population program's.

### 4.4 What's needed to make `Q_word` the partition of record

1. **Serving commits `Q_word`'s whole boundary.**
   - On #101 that's the 4 tap classes above (349,439 words).
   - On the MoE rows it's also the router's interior values: 10.7–15.7% of their interior words.
   - Plus tap exactness and non-interference evidence.
2. **The roots bind `verity/partition/v1`** = {#101's `program_sha512`, `Q_word` {16, 32}}, which comes with the M0-format commit becoming the record (the re-baseline).
3. **The Lean verifier evaluates `Q_word` v1 itself** (#126, #129 and #157, open). Until then the audit must report the partition as taken as stated.
4. **The backend proves `Q_word`'s unit classes.**
   - #101 has about 2,749 classes, against 7 template modules today (`docs/workstreams.md`).
   - It needs the tail pieces on `main` (#104, #125 and #140), a statement per class, and input sets built by lift and slice.
5. **The sampler, as one $1.75 \times 10^{11}$-AND unit.** Either the keep word is restated as a composite so the query can cut it, or the unit gets a statement of its own. Removing the five discarded pipelines, the constant `BitAt`s and the unanchored `splits` (§6.2) shrinks it by about 80% first.
6. **A draw law over 274 M units** (the adopted law stratifies by template).
7. **Zero recomputes on the record's rows**, which means switching on #106 and #109 (§5). A cross-Call recompute check also belongs in core's `verify`, which checks Calls one at a time today, or at least in `check`.

## 5. All 13 rows

The AND column is corrected: attention exact per T from the program graph's histogram, and the MoE and FP8 GEMMs from their own Call records. "Published" is the lowering lane's 13:30Z headline. The unit columns are `Q_word` v1 {16, 32}. *High, except the corrected ANDs on #67–#75, which are Medium.*

| Row | Model, GPU, TP, batch, sampling | Class | Calls | ANDs | Published | `Q_word` units | 16 / 32 / other bits | Dead units | New-tap words | Cut violations |
|---|---|---|---:|---:|---:|---:|---|---:|---:|---:|
| #101 | Llama-3.2-1B, L40S, 1, b1, top-p | GREEN / PASS | 46,654 | 1.57e14 | 1.57e14 | 2.74e8 | 84.3 / 15.7 / 0 | 0 | 3.49e5 | 0 |
| #4 | SmolLM2-135M, L40S, 1, b16, greedy | FAIL, PASS on redraw | 1,712,158 | 3.79e14 | 4.16e14 | 3.29e9 | 69.6 / 30.4 / 0 | 0 | 8.10e6 | 0 |
| #11 | Llama-3.2-1B, L40S, 1, b1, greedy | GREEN | 747,358 | 3.01e15 | 3.01e15 | 1.98e10 | 44.4 / 55.6 / 0 | 0 | 8.50e7 | 0 |
| #23 | Llama-3.2-1B, L40S, 1, b64, greedy | GREEN | 2,855,826 | 9.49e15 | 9.76e15 | 2.05e10 | 75.2 / 24.8 / 0 | 0 | 4.03e7 | 0 |
| #39 | Qwen2.5-1.5B, L40S, 1, b1, greedy | GREEN | 1,429,194 | 3.85e15 | 3.85e15 | 1.66e10 | 55.8 / 44.2 / 0 | 0 | 1.12e8 | 0 |
| #57 | Gemma-2-2B, L40S, 1, b8, greedy | FAIL | 4,400,870 | 4.64e15 | 4.70e15 | 1.10e10 | 61.3 / 38.7 / 0 | 0 | 9.78e6 | 0 per Call; **cross-Call recompute** |
| #60 | Mistral-7B, L40S, 1, b8, greedy | GREEN | 1,211,108 | 1.39e16 | 1.40e16 | 1.47e10 | 78.5 / 21.5 / 0 | 0 | 4.82e7 | 0 |
| #67 | OLMoE-1B-7B, L40S, 1, b32, greedy | GREEN | 5,745,046 | **5.76e15** | 2.84e18 | 1.39e10 | 86.3 / 13.0 / 0.7 | 1.02e7 | 2.86e8 | 0 |
| #68 | OLMoE-1B-7B, L40S, 1, b32 arrivals, greedy | GREEN | 5,830,562 | **5.84e15** | 2.88e18 | 1.40e10 | 86.4 / 12.8 / 0.7 | 1.03e7 | 2.90e8 | 0 |
| #70 | OLMoE-1B-7B, L40S, **2**, b8, greedy | FAIL | 2,689,685 | **1.22e15** | 6.00e17 | 4.49e9 | 88.0 / 11.1 / 0.9 | 4.28e6 | 1.17e8 | 0 |
| #73 | Qwen3-4B, H100, 1, b8, greedy | GREEN | 6,664,748 | 7.00e15 | 7.11e15 | 1.35e10 | 76.4 / 23.6 / 0 | 0 | 3.02e7 | 0 |
| #74 | Qwen3-4B-FP8, H100, 1, b8, greedy | GREEN | 7,853,122 | **4.34e15** | 1.91e19 | 1.63e10 | 77.9 / 22.1 / 0 | 0 | 3.37e7 | **581,040 Calls** |
| #75 | Qwen3-30B-A3B, L40S, **2**, b2, greedy | FAIL | 3,013,185 | **9.34e14** | 3.76e17 | 4.63e9 | 73.1 / 25.3 / 1.5 | 7.13e6 | 2.02e8 | 0 |

Across the 13 rows there are $1.53 \times 10^{11}$ `Q_word` units.

**Inputs.**
- The 12 greedy rows read only weights and `prompt`: no seed and no `splits`.
- The two TP2 rows are one rank's shard, so the peer rank's contributions are **inputs**: 8,448 `peers_*` inputs on #70 and 12,544 on #75, fed by `AllGather2` and `AllReduce2`. This program proves nothing about them; they have to be tied to the other rank's program.
- #39 has a qkv bias, and #74 has `weight_scale_inv` tensors.
- Every row carries a `cos_sin_cache` "weight". *High.*

**Constructs that aren't plain gates, by row:**
- **MoE expert gathers** (#67, #68, #70, #75): not lowered in the store's export. There are $8.0 \times 10^{12}$ of them on #67, not the published $5.46 \times 10^{15}$, and the gate_up experts' gathers are missing from the not-yet-lowered list.
  - As PR #140's multiplexers they'd add $8.4 \times 10^{15}$ ANDs to #67 (×2.46, not the ×3.02 the PR states) and $2.2 \times 10^{15}$ to #75 (×3.33, not ×4.96).
  - The MoE router leaves 64 (or 128) dead `SelectF32` units per router Call. *Medium.*
- **Gemma-2's tanh tables** (#57): the $2^{27}$-word `MufuTanh` and `TanhF32Rn`, with 131,976 and 131,998 ANDs, lowered on PR #140. *Low.*
- **The greedy argmax** (a scan over V): pieces on PR #140. *High.*
- **FP8 k-step** (#74): pieces on PR #140. *High.*
- **FA3** (#73, #74): the default construction has 0 recomputes. The opt-in (#105, open) removes 15.5 M `-inf` guards that the kernel doesn't execute. *Medium.*

**Recomputes on the default path** (*Medium: the verify-optins lane's real-Build numbers; High for the program-graph counts*):
- **#74, the FP8 block-scale product.** 581,040 Calls in the program graph, and 747,936 violations and 146 G recomputed word gates on the real Build. The `SHARED_SCALE` opt-in (#106, merged, off by default) brings both to 0 at +1.15 G committed words.
- **#57, Gemma's norm weight + 1.** 57,855 Calls and 133 M gates. This is a cross-Call recompute, which `Q_word`'s per-Call cut can't see; only the opt-in `query.cross_call` pass finds it. `weight_only_calls = "once"` (#109, merged, off by default) brings it to 0.

## 6. Where this plugs into the workstreams

This maps onto `docs/workstreams.md` (bc-ea1c2c4f's design). I haven't edited it.

### 6.1 Workstream 1's checks before handoff

"The ground-truth audit's items (inputs, outputs, non-gate constructs) once it lands" becomes these concrete checks, each runnable on the program and the export:

| Check | Pass rule | #101 today | Row that fails |
|---|---|---|---|
| Every input has an anchor | each Input is tagged `weights`, `prompt`, `seed` or `peers` with its external anchor; a derived table (`cos_sin_cache`) names its derivation | `splits` has none | every stochastic row (`splits`); every row (`cos_sin_cache`) |
| The outputs are exactly the sampled tokens | the root's return equals the samplers' outputs (serving view's `sampler_rule`) | pass | |
| No program-level dead Calls, or listed | the number of Calls no output depends on (`needed_by_none`) is 0 or listed | 2,040 unlisted | every row with prefill (not computed for the others) |
| Every primitive has gates | no `commitment-opening`, `lookup-slot` or `not-yet-lowered` kind in the export | embedding gather | MoE rows (gathers) |
| The headline equals the sum of the cut's units | Σ (node instances × template ANDs) = Σ (`commitments.json` unit ANDs × count × Calls), per template, within 2% | pass on GEMM and attention; 2× on RMSNorm (methodology) | #67, #68, #70, #75, #74 (×400 to ×4,400) |
| Attention counted by the T histogram | uses the program graph's `varying_calls` | pass | #4, #23, #57, #60, #73 |
| Cross-Call recompute check | `query.cross_call` finds 0 | pass | #57 unless `once` |
| Per-Call recompute check | `Q_word` `verify` finds 0 | pass | #74 unless `SHARED_SCALE` |

### 6.2 Concrete fixes for workstream 1

Owned by the lowering lane (bc-9916bbb1) unless marked "program side".

1. **The export's granularity bug.** For `RoutedGemmCoordinate` and `ScaledMmFp8BlockCoordinate`, a template's count is per Call (a whole `MoeExpertGemmW_v1` or `ScaledMmFp8Block_v1`), but `nodes[].instances` counts coordinates.
   - The template cache key (`[tname, params, T_range]`) also leaves out N, so one N's per-Call count is reused for another N.
   - Fix: make these templates per coordinate, like `GemmCoordinate`, and key the cache on the full spec.
   - Then republish the headlines. #67 is $5.76 \times 10^{15}$, #68 $5.84 \times 10^{15}$, #70 $1.22 \times 10^{15}$, #74 $4.34 \times 10^{15}$ and #75 $9.34 \times 10^{14}$.
2. **Gathers dropped from the not-yet-lowered list.** `MoeExpertGemm_v1` (the gate_up experts) maps to the dense `GemmCoordinate` template, which drops its 2,048 `GatherBf16x64` per coordinate. With it, #67 has $8.0 \times 10^{12}$ gathers. The multiplier PR #140 states (×3.02 and ×4.96) needs recomputing: it's ×2.46 on the OLMoE rows and ×3.33 on #75.
3. **Attention's T weighting.** Weight `per_key_count` by the program graph's `varying_calls`, not uniformly over the range.
4. **The export's cross-check.** Add §6.1's "headline equals the sum of the cut's units" to the export's `index.json` checks, and fail when it doesn't hold. It would have caught fixes 1 and 2.
5. **Constant propagation.** Lower `BitAtx{W}` with a constant index as wiring, and lift the 8-variant cap for index-like operands. On #101 that is about $1.65 \times 10^{10}$ ANDs per step (0.34% of the headline).
6. **One counting convention.** RMSNorm's template count (the hash-consed warp unit) is about half the sum of its `Q_word` units' pieces, and Gemma's scalar ops differ by 1.1–2.9×. Pick one convention for headlines and say which.
7. **Publish the gates-only export to the store.** The store's copy still has `commitment-opening` and `lookup-slot` kinds and the MoE gathers as not lowered, although PR #140 says it was republished. Also register the gather and keep-word pieces where `circuit-check` sees them: on #140's head it still reports "no piece" for `GatherBf16x16` and `TopPMaskWordx16`.
8. **The keep word's twin** should take each lane's own half's stop bit, as #169's total reference does (cross-call-check's follow-up on #125).
9. **Program side** (workstream 1, the vLLM lanes):
   - bind `splits` as a per-step constant, or derive it in the circuit from the committed batch size, so no input is left without an anchor;
   - list or prune the 2,040 program-level dead Calls;
   - anchor `cos_sin_cache` to its derivation;
   - fix `MufuEx2Ftz` below $\lvert x \rvert = 2^{-63}$ to match the hardware (low priority, from the 08:11Z lowering finding);
   - add the four tap classes of §4.1.
10. **The lowering digest** (workstreams gap 1) would pin every one of these fixes. Today `circuit-check` pins only counts.

### 6.3 The fan-out data behind units spanning Calls

Every Call-output word of #101, by how many units read it. Readers per parameter leaf come from core's `CallGraph` and cut; word classes come from the program graph's edges. *High.*

| Readers | Words | What |
|---|---:|---|
| 0 | 1,110,016 | the final norm's unread outputs |
| **1** | **116,369,408** | o_proj → residual add (9.40 M); gate_up → SiLU (75.24 M); down → residual add (9.40 M); logits → the sampler's one unit (4.10 M); each norm's residual output → the next norm (18.22 M) |
| 2 or 3 | 12,343,296 | qkv's q and k → RoPE; embedding → first norm and residual |
| 1 to 1,144, by position | 14,106,624 | RoPE-q → its position's scores (T readers, 1 to 287; position 0's 32,768 words have one); K and V → every later attention Call, 4 GQA heads each (4 to 1,144, mean 576) |
| 2,048 to 128,256 | 65,896,480 | attention → o_proj, SiLU → down, the token → the next embedding (2,048); norm → qkv (3,072), → gate_up (16,384), → LM head (128,256) |

- **The upper bound on the gain.** A cross-Call query could stop committing the single-reader words: 116.4 M words, 233 MB per request. That's 55.5% of Call-output words and 42.5% of all committed words.
- **What it costs.** Units get bigger and fewer (274 M becomes about 158 M):
  - a SiLU unit that absorbs its two GEMM coordinates grows from 2,606 ANDs to about 2.1 M;
  - the logits absorbed into the sampler make one unit of about $3.1 \times 10^{11}$ ANDs per step.
- **What never shrinks.** The 65.9 M high-fan-out words (norm → GEMM, SiLU → down, attention → o_proj) must be committed whatever the query.
- **For the other rows** I haven't computed it. The same four patterns (GEMM into a residual add, gate_up into SiLU, the residual chain, logits into the selector) are architectural, so expect a similar share on the dense rows.

## 7. Things that would confuse Daniel

1. **"Gates" means two things.** `Q_word`'s "gates" and "units" are word gates (IR primitives). A 16-bit unit can hold a million ANDs (a GEMM coordinate), and one word gate can hold $1.45 \times 10^{11}$ (the keep word).
2. **A unit is one committed value.** With $X = 16$ and BF16, `Q_word` never packs two values into a unit, so "units" equals "committed words" on every #101 unit.
3. **The published MoE and FP8 sizes are off by up to 4,400×** (§6.2, fix 1). Rows #67–#75 are about the same size as the dense rows, not 100× bigger.
4. **XORs dwarf ANDs:** $1.12 \times 10^{16}$ against $1.57 \times 10^{14}$ on #101. The XORs come from table reads' linear sums, which are free in Flock's R1CS.
5. **The sampler isn't small:** 3.6% of #101 in 32 units of $1.75 \times 10^{11}$ ANDs. About 83% of the keep word is pipelines thrown away by `splits`, and another 9% of the sampler is constant-index `BitAt`s counted as multiplexers.
6. **"The record" means three different partitions.**
   - Serving binds none.
   - The regression record replays one unit per Call (46,558).
   - The audits prove template instances of a synthetic population program (6.77 M on layer 0).
   - `Q_word` (274 M) is computed everywhere and bound nowhere.
7. **Two `Q_word` implementations:** core's `verity.ir.cut` (#111) and the vLLM integration's `query.word` (`R=no-recompute`, plus the #98 member check). They cut identically on #101, but only the vLLM side has the cross-Call check.
8. **The KV cache isn't state.** It's ordinary values inside one big per-request program, so "each gate in exactly one unit" already covers it.
9. **Request settings are circuit constants.** Temperature, top-p and positions are part of the public circuit, so the circuit changes with them.
10. **TP rows prove one rank.** The other rank's values are inputs.
11. **4.7% of #101 is dead code.** The last layer at the 255 non-final prefill positions affects no token, and it's still proved (or sampled).
12. **Row class labels disagree across files.** #4 is FAIL in its regression record (a v1 record audit) and PASS on its own redraw run. #101 is GREEN in the record and "PASS on run" in the program graph.

## Files

**Created:** `docs/vllm-circuit-ground-truth.md` (this file) and the folder `internal/vllm-circuit-ground-truth/`. The folder holds:
- `scripts/`: the headline, `Q_word`, width, input, fan-out, cross-check and core re-evaluation scripts. They read the store's datasets and run from the verity workspace with `uv run python …`.
- `results/`: the corrected headlines, the per-template cross-check, #101's fan-out classes, core's `Q_word` results, the input roles, and summaries of both `circuit-check --all` runs.
