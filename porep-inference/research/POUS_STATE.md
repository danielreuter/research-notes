# Proof of useful space: candidate architectures (systems-level state, 2026-09-24)

Handoff for whoever designs the reference implementation. Systems level only: roles, messages, what each check buys, what it costs, and what is proved or assumed. Pointers go to the memo that holds the detail. Labels: **proved**, **ideal-model** (proved in an idealized model, with the concrete-transfer assumption stated), **attack-based** (no proof; best known attacks priced), **measured**, **estimate**.

## 0. What is being proved

The operator declares an HBM map for each GPU: `weights | KV pool | filler | workspace`. The workspace (1–3%) is declared but not proved. For every declared region we want:

1. **Possession.** The committed bytes exist somewhere.
2. **Locality.** They are in *this* GPU's HBM, not in host DRAM, a peer GPU, a pool, or an SSD.
3. **Dedication (incompressibility).** They occupy their full size. No representation smaller than $(1-\varepsilon)$ of the region lets the operator answer on time. The target is $\varepsilon \approx 5\%$.
4. **Usefulness (authenticity).** The bytes are the declared workload's data (the real model's weights; KV of real sequences), not covert data wearing a label.

The adversary is the operator: it controls the host, driver, and serving stack. It knows the weights and all public parameters. It may preprocess anything into arbitrary advice. Two resource limits are available and every design uses one or both:

- **Bandwidth.** Data outside HBM arrives over PCIe/C2C at $B_{\text{alt}} \ll B_{\text{HBM}}$ (H100: about 55–64 vs 3,000 GB/s; GB200: 450–550 GB/s to LPDDR5X).
- **Time.** A challenge has a wall-clock deadline $\Delta$, measured by a trusted clock on the node or on a low-jitter LAN.

## 1. Building blocks

### 1.1 Roles

| Role | Where | Holds | Trusted for |
|---|---|---|---|
| Prover P | operator's node | everything it is given | nothing |
| On-node challenger C | sealed DPU/FPGA-class device (or a LAN-adjacent verifier box) | trusted clock, CSPRNG, MAC secrets, per-sector tags | timing, freshness, secrecy of its MAC key |
| Verifier V | remote governance service, plus optional on-node HSM | commitments, and either $W$ or per-block tags; seed keys | honest |
| Trusted encoder E (trusted setup only) | model owner or a governance enclave | the trapdoor during encoding | never colluding with P; erasing the trapdoor or keeping it offline |
| Trusted GPUs (authenticity layer only) | about 1% of the fleet | replayed sequences | honest recompute |

### 1.2 Checks

**Bulk bandwidth audit (BWA): gives locality and possession.** This is a timed Shacham–Waters linear MAC. C sends a fresh nonce. P reads a random subset of $X = $ 4–8 GB of 32–64 KB sectors and returns a few field elements $\sum_s a_s \cdot \text{limbs}(C_s) \bmod (2^{61}-1)$. The sector data must go through an injective 60-bit limb split, with fresh coefficients per limb. C checks the response against the aggregated tags (8 B per 32 KB sector) and rejects a late answer. The fraction of the region that can live off-HBM is
$$\tau \lesssim \frac{B_{\text{alt}}}{B_{\text{HBM}}} + \frac{B_{\text{alt}}\,J}{X},$$
where $J$ is the honest tail jitter. This comes to about 2.5–3% on H100 and 5–9% on GB200 (**derived** from measured bandwidths). Measured honest tail under a decode load, with bounded-lifetime CTAs: p99.9 minus p50 = 0.11–0.34 ms. Rules:

- There must be no "prepare" signal before a challenge.
- Challenges arrive at Poisson times and never overlap.
- The serving stack's kernels must have bounded CTA lifetime.
- Slow memory is modelled as passive. A processor next to the slow copy that computes partial responses is out of model.

Detail: `protocol2.md` §4, `compute_as_proof.md` §4.2, `challenger2.md`.

**Raw-block completion audit (RBA): gives dedication against compressed representations.** C asks for $k$ uniformly random encoded records, revealed sequentially (the next index is $H(\text{nonce}, \text{previous record})$). All $k$ records must come back inside $\Delta \le 1$ ms. There is no hash over large units and no linear aggregation; the answer is the raw records (about 150–210 KB at $k \approx 600$–$800$). V checks each record either by decoding it publicly and comparing with $W_j$ (if V knows $W$) or against an encoder-issued tag. Sequential reveal is worth about 37 bits per block over revealing all $k$ indices at once. This check is only meaningful for encoded data. Detail: `sms5/ideal/tradeoff.md`.

**Authenticity checks: give usefulness.** Three mechanisms, which can be combined:

- **Tagged write path.** KV tags are updated only for writes into slots that belong to a live sequence. This caps laundering of covert data at the honest KV write rate, about 50 MB/s per GPU.
- **Sampled recompute.** Trusted GPUs replay about 1% of conversations from turn 1 and compare the KV pages (TOPLOC-style tolerance for fp8). Cost: about 0.8% of the fleet.
- **Freivalds check on linear layers.** V keeps $u = W r$ for its own secret $r$ (about 2 GB of verifier state). This binds the weight values, but not their location.

Detail: `compute_as_proof.md` §2, §4.4.

**Binding mechanisms: stop the operator from choosing data after the fact.**

- **Commit-before-seed.** P commits to its data before any encoding key exists: `seed = PRF(K_seed, replica id, comm_D)`.
- **Replica ids / slot keys.** One encoding per (GPU, slot, epoch), so a pool or peer copy cannot answer for this GPU.
- **Epoch re-keying.** Needed for any region whose contents P chooses at runtime (see nesting, §4). Detail: `protocol2.md` §2–3, §7; `curve3.md` §3.

### 1.3 Encodings

| Encoding | Who encodes | Decode cost | What it buys | Status |
|---|---|---|---|---|
| **None** (plaintext) | — | 0 | nothing beyond the data's own entropy | — |
| **Verifier-secret random** | V or C generates it and pushes it over PCIe | none (it is filler) | information-theoretic incompressibility | trivially sound; only possible for data nobody needs to read |
| **Trusted trapdoor: RW–SMS** (Rabin–Williams root → dense XOR → root, 2048/3072-bit modulus) | E, once, with the factorization | 2 modular squarings ≈ 100 int32/B at 2048 bits | regeneration from $W$ is as hard as factoring (**proved**); compression resistance is **ideal-model** (§2.A) | spec'd and correctness-tested; kernel unmeasured |
| **Public DRG PoRep** (drU (4,6,4), 64 KB blocks, keyed ARX mixer) | P itself, after commit-before-seed | ≈ 25–30 int32/B, serial depth 4 | dedication only in a timed game: regenerating a block takes longer than $\Delta$ | **attack-based**; kernels built and **measured** |
| **Public VDE** (Sloth-type square roots over a prime) | P itself | 1–2 squarings | same timed game, sequential root as the delay | the other team's 61-bit design is **broken** (Coppersmith recovers ≈ 33–36% undetectably); our 1279-bit two-round variant (`sms5/spec.md`) is superseded by RW–SMS |
| **Proved incompressible encodings** (Moran–Wichs DCR, lattice SLF) | E | $10^2$–$10^7\times$ | full untimed proof | reference points only; closed on cost (`OPTIONS.md` A1–A2) |

## 2. Setup models

### A. Trusted setup (trusted encoder, public decode). Weights only.

~~~text
Setup (once per model version):
  P -> V, E : commitment to W and its layout
  E         : generate Williams modulus N = pq and a fresh salt (after W is committed)
              for each block j: C_j = RWInv(RWInv(W_j + t_j) XOR K_j)   (t_j, K_j from SHAKE256(salt, j))
              record = (c_j, a1, a2, h) : 257 B per 254 B payload at 2048 bits (1.012x)
              verify every round trip; erase p, q (or seal them offline)
  E -> P    : C, manifest (N, salt, layout, digest)
  E -> C    : Shacham-Waters tags over C's sectors (or C computes them from a one-time stream of C)
  E -> V    : W digests or per-record tags (for checking RBA answers)
Serving:
  P decodes each weight tile on the fly (2 squarings + XOR + subtract), fused before the GEMM
  P keeps no persistent plaintext between invocations
Audits (C, Poisson times, never overlapping):
  BWA over 4-8 GB of C, deadline = X/B_HBM + J           -> tiering tau ~ 2.5-3% (H100)
  RBA: k chained raw records within Delta <= 1 ms        -> completion
~~~

The three ways to fake storage, and what stops each:

| Path | Stopped by | Status |
|---|---|---|
| Regenerate a deleted block from $W$ | factoring (Rabin root-to-factoring, factor-2 loss) | **proved** |
| Keep the block in slow memory | BWA | **derived** bound $\tau$; passive slow memory assumed |
| Keep a compressed representation, complete it on demand | RBA + assumption RW-IC | **ideal-model** |

The ideal-model theorem (whole file, arbitrary $S$-bit advice, total online budget $T$) gives the following at $w = 2048$, $\varepsilon = 5\%$, $T = 2^{20}$–$2^{34}$: the adversary cannot answer about 1.6–2.3% of blocks, so $k \approx 590$–$830$ records give failure probability $10^{-6}$. At $w = 3072$, $k \approx 420$–$490$.

**Assumption RW-IC.** No advice-aided completion of RW–SMS beats a random permutation by more than a few bits per block, for retained fractions $s/w \in [0.90, 0.98]$ and $T \le 2^{34}$. This assumption cannot be removed within this design class. There is no black-box reduction to factoring or to any single-stage assumption (`sms5/reduction/reduction.md`, Theorem 2). There is also no information-theoretic theorem for any short-trapdoor encoder (`sms5/redesign/redesign.md`, Prop. 1). Current evidence for RW-IC: every algebraic attack found needs at least $w/2$ bits of each root stored. The best known saving is truncation, at most 32 bits against a 95–146-bit budget. One item is still open: whether the shift-and-kangaroo attack stacks on Coppersmith.

**Composition is the binding constraint.** At 2048 bits the proved bound cannot absorb a 2.5% tiering allowance (the budget is 43 bits and the loss is 48–62). Either move to $w = 3072$ (then $k \gtrsim 1{,}900$) or shrink $\tau$ with a larger or tighter BWA.

Cost (**estimate**, kernel unmeasured), 2048 bits:

| Variant | int32/B | Prefill | Decode, $b \le 8$ |
|---|---|---|---|
| dense XOR mixer | ≈ 100 | ≈ 1.5–1.8× | ≈ 12–20× |
| 2-round Keccak Feistel mixer (heuristic) | ≈ 127 | ≈ 1.9× | worse |
| 8-round indifferentiable Feistel | ≈ 206 | ≈ 2.4× | worse |

At 3072 bits add about 40–50 int32/B. One-time encoding is 2 CRT root extractions per 254 B: roughly 100 CPU core-hours per 70 GB (**estimate**), less on GPU.

This setup cannot carry KV (§3.2). Detail: `sms5/ideal/`, `sms5/reduction/`, `sms5/redesign/`.

### B. Untrusted setup (P encodes its own data). Always timed.

P holds the encoding key, so it can always re-encode a missing piece from $W$. There is therefore no untimed guarantee (`template_bound.md` Lemma 4). Security comes from regeneration taking longer than the deadline.

~~~text
Admission (per GPU, per store):
  P -> V : comm_D (Merkle root over 32 B chunks), layout, replica id (gpu, store, slot, epoch)
  V -> P : seed = PRF(K_seed, replica id, comm_D)     (128-bit; never given to C)
  P      : R = Enc_seed(D)   (layered DRG labeling; only R is kept in HBM)
  P -> C : stream R once; C computes 8 B tags per 32 KB sector, keeps tags and comm_R
Challenge (Poisson, about 1 per 200 ms, all GPUs of the node at once):
  C -> P : nonce; P reads 4 GB of random sectors, returns the linear MAC; deadline T + 0.5 ms
Consistency:
  V_node opens one random decode cone per second (leaks 32 B of D per opening) to bind R to comm_D
~~~

- **Dedication.** The regeneration chain per block (3.16 ms at 64 KB) must exceed the deadline (1.81 ms). 32 KB blocks fail at $X = 4$ GB.
- **Filler.** The DRG encoding of zeros under its own replica id costs the same HBM as real weights.
- **Security** is **attack-based**: 0.59% freed at $W = 2n$, no arbitrary-state proof, and the bound depends on the attacker's hardware speed $t_{\min}$ (an ASIC or a host-CPU circuit changes the picture).
- **Cost (measured).** Weights: 4.52× decode at batch 8 (fused kernel), 1.17–1.2× prefill, 2.4–6.0× in vLLM. KV-only session: 2.71×. Weights and KV: 3.67×.

Detail: `protocol2.md`, `trusted4/public_options.md` P1 and P6, `kv2.md`.

### C. No encoding: plaintext data, bandwidth audit, verifier-secret filler, authenticity layer

~~~text
Weights and KV stay plaintext. V/C tags every 4 KB page: t_p = <s, m_p> mod (2^61 - 1)
  weights: tags computed once from the known file
  KV:      tags updated from the D2H write stream (page, offset, old, new) of live sequences only
  filler:  random data generated by V/C from a seed P never sees, pushed once, tagged as generated
Challenge: BWA over c = 2-10% of the declared map (int8 GEMV on P, mod-q check on C)
Authenticity: sampled recompute of about 1% of conversations on trusted GPUs; Freivalds on weights
~~~

- **Cost:** about 0.3–1% of HBM time, plus about 1% of the fleet as trusted GPUs (**estimate**, from measured bandwidths).
- **Guarantee:** per GPU, at least 99% of the declared map is in HBM at each challenge (margin 0.3 ms, $c = 10\%$). Committed KV belongs to real sequences, up to a laundering channel capped at the KV write rate.
- **What it assumes:**
  - A tamper-resistant challenger that holds secrets. Key compromise is a total break.
  - Plaintext data is not compressible enough to matter. **This is the open hole for $\varepsilon = 5\%$.** bf16 weights compress about 25–30% losslessly (exponent entropy) and KV about 1.3–1.5×. P could compress a 15–20% slice and decompress it at audit time. Whether a GPU decompressor fits inside the BWA slack is **unmeasured**; if it fits, plaintext cannot certify 5%. Encoding (A or B) exists to close exactly this hole.

Detail: `compute_as_proof.md` §4.

## 3. Per data class

### 3.1 Weights (static, the server knows them)

| Option | Setup | Dedication argument | Overhead | Trust |
|---|---|---|---|---|
| W-C | plaintext + BWA + Freivalds | data entropy only (compression hole above) | ≈ 0.3–1% | challenger secrets |
| W-A | RW–SMS + BWA + RBA | factoring + RW-IC (ideal-model) | ≈ 1.5–2× prefill, 12–20× batch-1 decode (**estimate**) | non-colluding encoder |
| W-B | DRG PoRep + BWA (+ commit-before-seed) | timed, attack-based | 1.2× prefill, 4.5× batch-8 decode (**measured**) | clock / $t_{\min}$ |

When the weights are secret from the verifier, use B's commit-before-seed with sampled consistency openings (a quantified leak of about 2.7 MB/day), or A with encoder-issued record tags in place of $W$ digests.

The batch regime decides cost. Prefill amortizes decode arithmetic: the 2× budget is about 144 int32/B at a batch of 8,192 tokens, versus 8 int32/B at batch ≤ 8. Nothing cryptographic fits batch-1 decode at 2×. Deployments that must certify decode nodes either accept the overhead, certify prefill nodes only, or certify a slice (partial coverage).

### 3.2 KV cache (the server produces it at runtime)

Two structural facts:

- **The trusted setup does not apply.** P is the author of its own KV. A trusted party encoding what P sends would still encode a **nest**, and trapdoor encoding throughput (≈ MB/s per core) is far below KV write rates (50 MB/s–GB/s).
- **Nesting.** Any region whose plaintext P chooses can hold an encoding of another declared region: KV page $j$ := encoded block $i$, then discard $i$. P then answers challenges on $i$ by publicly decoding $j$. No encoding-level fix exists. This includes trusted weights nested inside public-encoded KV, and KV re-keying does not kill that nest.

| Option | What is claimed | Remedy for nesting | Overhead |
|---|---|---|---|
| K-0 (default) | weights-only claim; KV plaintext and uncounted, or counted only as "stale-but-tagged" pool | not needed | 0 |
| K-C | plaintext KV counted through the tagged write path + sampled recompute + BWA | authenticity layer: a nest is not the model's KV for the logged tokens | ≈ 0.3–1% + trusted GPUs; laundering capped at ≈ 50 MB/s/GPU |
| K-B | public-encoded KV pages (seal on fill, slot keys, decode on read) + BWA | epoch re-keying: 13–20 s GPU per 80 GB per epoch; 4–7% when decode-dominated, infeasible above ≈ 0.1 GB/s of KV admission per GPU; or computation integrity | 2.7× session (**measured**); KV sits in the batch-1 regime forever |

K-C is the only KV option with near-zero overhead, and it depends on trusted recompute GPUs rather than on cryptography.

### 3.3 Activations (ambitious; not researched in depth)

Nothing in the repo proposes a residency proof for activations. Current treatment: during inference they live in the declared workspace (1–3%), which is excluded and capped. Candidate directions, none evaluated:

1. **Exclusion.** Prove everything else and bound the workspace size. This is the realistic default for inference, where activations are under 2% of bytes.
2. **Computation-integrity evidence.** Freivalds checks on $X_{l+1} = f(X_l W)$, TOPLOC-style commitments, or live challenges for $h_l(\text{token}, \text{layer})$ checked later by recompute. These prove the activations *existed* when computed. They do not prove *where* they were or that they persisted.
3. **Training-time activation checkpoints**, which are large (tens of GB) and stable between forward and backward. These are KV-like: server-produced, so they need nesting protection and authenticity. Their write rate (hundreds of GB/s) rules out verifier-side tagging. A BWA over the checkpoint region would need tags computed on the GPU by a trusted component (GPU TEE / confidential-computing mode) or a per-step commitment that trusted GPUs spot-check by recompute.

### 3.4 Filler (HBM the workload does not need)

| Option | Setup | Notes |
|---|---|---|
| F-C | verifier-secret random data | simplest and information-theoretically sound; needs a trusted generator and a push (≈ 2 s per 100 GB over PCIe); refill when the KV pool shrinks |
| F-A | same as F-C | a trusted setup has a trusted party anyway, so random data beats RW–SMS-encoding zeros |
| F-B | public PoS: DRG encoding of zeros under its own replica id | the only option with no secret-holding party; timed and attack-based like B |

## 4. Composition rules (the ones that bit us)

1. **Split the audit by job.** BWA handles locality and tiering; RBA handles completion; trapdoor hardness handles regeneration. One challenge doing everything is what produced the old flaws: BLAKE3 tree caching, an unsound linear response over the wrong field, and adding tiering and completion percentages.
2. **The budgets are shared, not additive.** The tiering allowance $\tau$ eats the completion budget. Size $w$ and $X$ together (§2.A).
3. **Nesting crosses data classes.** Never count a server-chosen region next to an encoded region without re-keying, authenticity, or excluding one of them.
4. **Timing hygiene:**
   - no prepare signal;
   - Poisson challenges;
   - bounded CTA lifetime in the serving stack;
   - challenger on-node or LAN-adjacent with a low-jitter trusted clock;
   - per-GPU keys;
   - deadlines calibrated for the complete response kernel, including coefficient generation.
5. **Chained RBA latency is unmeasured.** $k \approx 600$ sequential record fetches in 1 ms is about 1.7 µs per hop, which is tight for an HBM access plus a hash. The fallback is round-based chaining (for example 10 rounds of 60 records) with the bound re-derived for that schedule.
6. **Slow memory is passive in every theorem.** An active helper next to the slow copy could return a 24-byte response. Rule it out physically or by attestation.

## 5. Open items, in priority order

1. **Is plaintext compressible inside the BWA deadline?** Measure a GPU lossless decompressor on a 15–20% slice against the audit slack. This decides whether design C can certify 5% or whether encoding is mandatory.
2. **Cryptanalysis of RW-IC** at $s/w \in [0.90, 0.98]$. Specifically, whether shift-and-kangaroo stacks on Coppersmith, plus the five questions at the end of `sms5/redesign/redesign.md`.
3. **RW–SMS decode kernel** fused before the GEMM at prefill batch; XOR mixer versus Keccak Feistel.
4. **Honest latency** of the chained RBA and the BWA under a live serving load, on the target GPU (H100 versus GB200 changes $\tau$ by 2–3×).
5. **Authenticity-layer sizing** for K-C: the fp8 KV tolerance on real hardware and the recompute fraction.
6. **Activations:** pick exclusion for inference; decide whether training checkpoints are in scope.
