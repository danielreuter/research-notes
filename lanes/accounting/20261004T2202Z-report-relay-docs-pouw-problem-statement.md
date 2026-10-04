---
id: 20261004T2202Z-report-relay-docs-pouw-problem-statement
campaign: pouw
lane: accounting
kind: report
status: closed
repo: danielreuter/verity
origin: old-accounting (bc-b729c175), relayed for @top's migration (the 44 store:pous/ files the PoUW and PoUS registries cite) from store:pous/docs/pouw/problem-statement.md
---

> Relayed verbatim from the Cursor store by old-accounting: `store:pous/docs/pouw/problem-statement.md`, sha256 `42ac14a12b62407dac14b84d1d385b831d5b231beef310000079c12efad3fffe`, unchanged since it was written before the 30 Sep snapshot, so it is also in `art:8bd64630…42e9` at that path. Only the store's `cursor:` front matter is replaced. Relative and `/cursor/stores/…` links point into that store.

# PoUW problem statement: a 1% work gap for int8 matmul

Draft 3, 27 Sep 2026, applying the campaign's results of that evening; the hashing wording (In brief, §1.4, §3.1, §3.2) was amended on 29 Sep per [hashing accounting](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/docs/pouw/hashing-accounting.md). It replaces draft 2 (19:37), records Daniel's decisions of 27 and 28 Sep (§1.4, §9), and follows the [POUS problem statement](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/docs/problem-statement.md) in style. It consolidates the compute-transparency note [N], the FASR work test [F], and the campaign's reports, cited by finding id (Sources). Status tags follow [N]: **Proved** (a proof here or in [N], or a named Lean theorem that passes the audit), **Derived** (a calculation under stated assumptions), **Assumed** (a modelling choice), **Unverified** (to re-check).

**In brief.**

- **Core definition: the γ-gap game** (§3.3). Work is priced in M_4090 under the accounting W1: instructions at measured RTX 4090 prices, oblivious online data moves free, data-dependent accesses priced like an instruction, pre-salt bytes priced at first fetch, hash calls free, though every checked value must go through them. Give the operator one budget T of online work, free unbounded preprocessing whose hash calls are counted, and its own choice of weights and activations. Then the honest work of the units it gets right is at most T/(1 − γ), except with probability η. Composed with work-weighted sampling, this is resource exhaustion (Theorem 1, proved in Lean).
- **No route from standard assumptions** (§4.1, §4.2).
  - With hashing excluded (decision 1), the random-oracle model certifies no work, and unconditional bounds are about 3n² against n³.
  - A 1% gap needs a hardware-priced cost model (in operation-count models Winograd, Strassen and lookups refute it), a concrete constant, a joint form, and hardness for structured instances (Lemma 1). In M_4090 at checked depth 16, every INT32 or tensor-core instruction costs at least 16 units per output word, exactly what the honest reference pays per checked value.
- **The one assumption: TT(0.5%), the tight noised transcript** (§4.4; decided). It extends [KW]'s Assumption 6.4 from zero inputs to adversarial ones, concrete, joint and integer. At depth 16 it says: no adversary obtains correct checked words for less than 16 units each on average, up to γ_0. It is falsifiable by one fast kernel. Lean proves the rest, including the milestone instance with §3.2's noise. The package passes the audit, and the red team granted it and signed all 55 pins as statement reviewer.
- **The protocol and its limit** (§3.2, §5, §6). Rank-16 noise with inner ±1 factors and E_R shared by groups of 16 units; the checked values are the running sums after every 16-deep step. On degenerate inputs the adversary skips the decode, about (2r + 20)/n + (6r + c)/k of the work, and the hardware forces r ≥ 16. So milestone 1 at (m, k, n) = (2^12, 2^16, 2^16) reaches γ ≈ 0.85% with 131× hashing, while LLM shapes give 2.5–7% and cannot reach 1% at any hashing overhead. A floor for the whole class of additive-noise schemes keeps worst-case γ at 1.89% or more at k = n = 4,096, and 1% needs k ≳ 17,800. The best design found, D4-s, comes close to that floor at about 2.0%, and reaches 1% for k ≳ 18,700; the TT attacker found it safe at checked depth 16 with one fix (§6). Approving the weights roughly halves γ; only activations that the approved model computes from inputs the prover doesn't choose reach γ ≈ 0.5% (§6, question 8).
- **Decisions and questions.** Daniel's six decisions of 27 Sep are recorded (§1.4, §9). On 28 Sep he decided the four questions raised by the campaigns, each at its default (§9, questions 7–10):
  - the accounting W1 is adopted;
  - milestone 1 keeps worst-case inputs, and transformer shapes are research;
  - the checked depth is 16.

  - NCP (D7) is adopted as the full-rank-noise construction for transformer shapes, with TT_NCP(0.5%), about 400× hashing and about 3× arithmetic for its first build.

  Corrections to draft 2 are in §8.

## 1. Setting

### 1.1 Verifiable compute exhaustion

The context is [F]'s verifiable compute exhaustion (VCX): datacenters continuously demonstrate that nearly all of their compute is occupied by an approved workload, such as inference, so that it cannot be used for training. Operators run a declared workload and commit to its inputs and outputs as they go. The commitments, and the datacenters' compute capacities, are verified retroactively, possibly months later.

[F] assumes "a secure proof-of-useful-work (PoUW) protocol for matrix multiplications: every matmul of shape n × m × k at a given datatype comes with a certificate that computing it required at least n·m·k operations at that datatype." This document asks for that certificate with the constant made explicit: the best adversary's work must be within γ ≤ 1% of the honest reference's.

### 1.2 Parties

- **Operator (prover).** Runs the declared workload and commits at run time. It is the adversary. It chooses the inputs, weights and activations alike, including degenerate ones. It may fake upstream values, preprocess without limit before the salt, and wants to free compute for other uses.
- **Auditor (verifier).** After the fact, samples units and recomputes them. Its cost is out of scope (decision 4).
- **Beacon.** Emits salts s, uniform on λ = 128 bits and independent of the oracle and of any preprocessing, each unpredictable before its epoch; an example is a block-header hash modelled as uniform.

### 1.3 Scope

- **In scope:** a declared sequence of integer matmuls on the int8 datapath, with int7 useful operands (decision 3; §3.2).
- **Out of scope:**
  - verification cost (decision 4);
  - hardware capacity and occupancy, the conversion from work to "compute denied to training" (decision 3);
  - the non-matmul glue (its fraction f of the work is zero here);
  - attribution, meaning which machine did the work ([F]'s reviewers flag it);
  - whether the approved workload itself advances training ([N] §'Training security');
  - confidentiality, ASICs, mining and lotteries.

### 1.4 Daniel's decisions (27 Sep) and where each lands

| # | Decision | Where |
|---|---|---|
| 1 | Security must not come from hashing. Hashes may derive noise or bind inputs, but the work must be the useful matmul | Hash calls are free in the γ-gap game (§3.1, §3.3), and every slowdown includes them (§3.1) |
| 2 | Unit of work: RTX 4090 time; ASICs out of scope | M_4090 (§3.1) |
| 3 | No mining. Resource exhaustion on every matmul of a workload, for now a standard sequence of integer matmuls. Hit an assumed or verified lower bound on work; no assumption about hardware capacity | §2, §3.3 |
| 4 | Verification is out of scope: sampled, essentially free | No verification-cost property; sampling composes by §3.5 |
| 5 | Honest reference: plain int8 tensor-core GEMM without Strassen, plus what the protocol adds | H_ref (§3.2) |
| 6 | int8 inputs, int32 outputs, SHAKE256 ideal where needed; revisable | §3.2; revised to int7 useful operands (9.3) |
| 7 | Probability accounting undecided | Decided: a tail bound at every budget (§3.4, 9.1) |
| 8 | γ ≤ 1% between honest and best-adversary work, jointly across many instances, with shared weights and unbounded preprocessing on fixed weights | The game (§3.3) |

Later on 27 Sep Daniel accepted all six defaults of draft 2's §9 (questions 9.1–9.6): the tail-bound accounting; worst-case inputs, degenerate ones included; int7 useful operands; about 130× hashing overhead, for milestone 1 only; TT(0.5%) as the single named hypothesis; RTX 4090 adversaries only. Three new questions arose from the campaign (§9, questions 7–9). On 28 Sep Daniel accepted all three at their defaults:
- the accounting W1 is the cost model;
- milestone 1 keeps worst-case inputs, and transformer shapes are treated as research;
- the checked depth is d = r = 16.

Daniel's standing preferences also apply: working end to end at high overhead first, Lean proofs, and the safest reduction possible.

## 2. Objective: resource exhaustion

The property VCX needs from this layer is:

~~~text
for every T and every operator strategy with online cost at most T:
    Pr[ audit accepts ∧ T < (1 − ε)·W ] ≤ δ,        where W = ∑_{u in U} W_ref(u).
~~~

- T is the operator's M_4090 work budget for the audited window, from the salt to the commitment deadline. The same bound holds for the realized cost (§3.5).
- W is the honest reference's work for the declared workload.
- The PoUW supplies γ: every correct unit costs at least `L(u) = (1 − γ)·W_ref(u)`, jointly over the workload (§3.3).
- Sampling supplies ε_s and δ_s (§3.5). Then `ε = 1 − (1 − γ)(1 − ε_s) ≈ γ + ε_s`, plus the uncertified non-matmul fraction f, which is zero here.
- Sampling is essentially free (decision 4), so γ is the binding term. The target is γ ≤ 1%.

L is a lower bound on work in Daniel's sense: *verified* if the game is proved as a theorem, *assumed* if the proof uses a named conjecture. §4 shows that for γ ≤ 1% it must be assumed, or verified only against a restricted adversary. Turning T into occupied capacity, and so into compute denied to training, needs a capacity model, which decision 3 defers (§3.1).

## 3. Definitions

### 3.1 Work model M_4090

The cost of an online algorithm is the sum of the prices of the instructions it executes and of the pre-salt bytes it fetches. Costs add over time, cores, functional units and devices: parallelism and concurrency never reduce cost.

- **Unit.** 1 unit is one dense int8 tensor-core multiply-accumulate (MAC) on an RTX 4090 at peak rate, 1,024 per SM per clock (measured): 3.03 fs at the whitepaper's 2,520 MHz [Ada], and about 2.72 fs at the 2.8 GHz the measured board runs `mma.sync` at. Large GEMMs are power-capped at about 2.3 GHz (302 T MAC/s at the milestone shape). Prices are ratios per SM per clock, so they do not depend on the clock.
- **The accounting W1** (Assumed as the cost model; decided by Daniel on 28 Sep, question 7 in §9).
  - *Instructions* are priced per instruction, by class, at the measured rates below, per 32-bit lane result. Every opcode class has a price. Texture filtering and b1 `mma` are the exceptions, and excluding them is a named assumption of M_4090 until they are measured and priced (red-team W1-4). A tensor-core instruction is priced by its full shape, however much of it is used. Atomics, reductions and warp reductions are INT32 instructions per lane operation. A move from an immediate is an instruction of its class. A load address is one register plus an immediate; any further addition is an INT32 instruction.
  - *Online data moves are free*: whole 32-bit words moved by loads, stores, register moves and shuffles, at any memory level, when they are oblivious.
  - *Sub-word extraction is priced like PRMT* (Daniel, 28 Sep 03:35Z). Any instruction or access that extracts, inserts or rearranges fields narrower than a 32-bit word costs 16 units per word it produces, on both sides. That covers byte and nibble loads, stores and shuffles, and packing several values into one register. It closes the packed-FFMA route (two products per FP32 instruction) and prices the honest reference's byte-level operand forming.
  - *Data-dependent accesses are priced* (tt-attacks H5; wording tightened by red-team phase E). Every instruction whose address, guard predicate or enclosing branch depends on data costs one INT32 instruction (16) per lane per 32-bit word it moves or produces. This covers every memory space: global, shared, local, constant bank, texture, surface, `ldmatrix`, `cp.async`, atomics and shuffles. Data means the salt, the noise, the inputs, anything computed from them, and anything computed under control that depends on data (implicit flows). This is the taint discipline of constant-time code, so it can be checked on a concrete kernel. Without this rule, byte stores and reloads concatenate values for free, and a load keyed by the result evaluates any function from an online table (the "mov is Turing-complete" construction): all arithmetic would cost 0, and TT would be false for every Π. H_ref's GEMM and the dense noise of §3.2 are oblivious, so the rule costs them nothing.
  - *Pre-salt and supplied data.* Pre-salt data is the preprocessing state σ, the declared weights, and the online program's text, including immediates and constant banks. Supplied data is a unit's activations A_u. The first fetch of each such byte costs 345 units, the DRAM rate; after that the byte is online data. One exception: a unit's operands A_u and B_w(u) are free on first fetch if the unit is correct (red-team W1-1 and W1-3). Activations computed online are priced by the instructions that compute them.
  - *Why.* Additive memory pricing gives γ ≥ 6–29% at milestone 1, because the zero-input adversary generates its H-derived operands on chip while the honest reference reads and stages real ones (red-team A1). Free memory fails the other way: unbounded preprocessing tabulates the zero-input transcript for every value of the noise factors, in σ, the program text, dummy weights or dummy units' activations, and looks it up online (coordinator, 20:35Z and 21:35Z; tt-attacks V1; red-team W1-1 and W1-3; §5 item 11).
- **Prices** (measured on one RTX 4090, `internal/pouw/gpu-constants.md`; run ids drop the prefix `r20260927-`):

| Operation class | Measured per SM per clock | Price (units) | Run |
|---|---|---|---|
| int8 `mma` m16n8k32 / m16n8k16, int32 accumulate | 1,024.0 / 1,023.3 MAC | 1 per MAC (4,096 / 2,048 per instruction) | 202355-71cd, 205223-d716 |
| int4 `mma` m16n8k64 | 2,048 MAC | 1/2 per MAC | 202355-71cd |
| FP8 `mma`, FP16 / FP32 accumulate | 1,024 / 512 MAC | 1 / 2 per MAC | 202355-71cd |
| FP16 `mma`, FP16 / FP32 accumulate | 512 / 256 MAC | 2 / 4 per MAC | 202355-71cd, 205223-d716 |
| FP32 FADD, FFMA | 128 | 8 | 202727-28ca |
| INT32: IADD3, LOP3, SHF, PRMT, IMAD, I2F | 64 | 16 | 202727-28ca, 205223-d716 |
| IDP4A (4 exact int8 MACs) | 64 instructions | 16 per instruction, 4 per MAC | 202727-28ca |
| F2I | 16 | 64 | 205223-d716 |
| Pre-salt byte, first fetch (DRAM read, 958 GB/s) | — | ≈ 345 | 202355-71cd |
| Shared-memory byte; L2 byte (reference only: free under W1) | 122–126 B; 11.4–11.7 B | ≈ 8; ≈ 80–88 | 202355-71cd |

- **FP32 adds are integer adds on small bit patterns** (tt-attacks §2). With flush-to-zero off, FADD on floats whose bit patterns are integers below 2^24 (subnormals and the first normal binade) adds them exactly while the sum stays in [0, 2^24), and the result's bit pattern is the int32 sum (checked on a CPU). So an FP32 instruction outputs an integer word for 8 units, half the INT32 price. Full-rate subnormal FADD on the 4090 is Unverified.
- **Sparsity.** The 2:4-sparse tensor-core mode is priced per nonzero product, so it is never cheaper than dense.
- **Hash calls are free to the adversary and excluded from W_ref** (decision 1). Calls to the ideal primitive H (SHAKE256, §3.2) cost 0 in the γ-gap game, and W_ref counts none.
  - So γ bounds the share of the honest reference's non-hash work that an adversary can skip, and L(u) certifies non-hash work.
  - This is conservative: an adversary that pays for its hashing can do no better. A bound that charged hash calls would certify hashing, and it would hold only as long as nobody hashed faster than the reference.
  - It does not make hashing optional. Π feeds every checked value to H, and the bound holds only for a Π that does. A kernel that folds or drops checked values implements a different protocol.
  - The number of calls q is bounded separately and enters the error term η (§3.3).
  - *Hashing is a real cost of the honest prover.* Every reported slowdown includes it, at the cheapest hash measured on the device, with the arithmetic-only figure beside it. SHAKE256 costs about 2,100 units per int32 value hashed (2,084 with the message in L2, 2,190 streamed from DRAM), or 521–548 units per absorbed byte. A Keccak-f[1600] permutation is 4,312 instructions, about 69,000 units (runs 202355-71cd, 201908-1942).
- **Admissible hardware.** Any number of RTX 4090s (decided, 9.6); ASICs are out of scope (decision 2).
- **Peak prices, not wall-clock time.** The honest reference is priced like the adversary, so the honest kernel's distance from peak is not part of γ. Reading every accumulator after each 16-deep step slows the tensor cores to 77% of peak, 1.30× the bare time (1.01–1.04× at depth 32; run 205223-d716). Under W1 that read feeds a free hash call, so it is real-time overhead, reported beside the hashing, not part of W_ref.
- **What the model does not say: capacity.** Costs add across functional units, so CUDA cores running beside the tensor cores add throughput without lowering cost. Measured, the best mix reaches 1,078 int8 MACs per SM per clock, 5.3% above the tensor cores alone, so an adversary finishes at most about 5% sooner (run 205223-d716). That is the capacity question, which decision 3 defers, not part of γ.

Why a hardware-priced model rather than an operation count: in operation-count models a 1% gap for int8 matmul is false (§4.2). The 4090's prices are what stop the known speedups from paying.

### 3.2 Domain, units and the honest reference

- **Useful computation.** C = A·B over the integers, returned bit-exact as int32. A ∈ Z_7^(m×k) are activations and B ∈ Z_7^(k×n) are weights, where Z_7 = {−64, …, 63} (int7, decided in 9.3). The useful product is exact for k ≤ 2^19 − 1 (Proved: Lean `Int32Decode`).
- **Headroom.** Noised operands must stay on the int8 datapath. Operands in [−127, 126] give an int32-exact noised product for k ≤ 133,144, a tight bound (Proved: Lean `NoisedKBound`, `Int32Transcript`); the noise below keeps them in [−112, 111]. Full-range int8 useful operands would need 9-bit noised operands, two int8 products per block against one for a zero-input adversary, so γ ≥ 1/2 (Derived; the reason for 9.3).
- **Domain D.** D is part of Π. It constrains each unit's shape and the declared layout, and γ is computed from `Ω* = sup over D of Ω` (red-team A2, C1). The verifier rejects any declaration outside D. So what the adversary declares cannot move γ. Milestone D: k = n = 2^16, and m a multiple of 16 with 2^12 ≤ m ≤ 2^17. The upper bound is m·G ≤ 2^21, for the noise groups below (tt-attacks §3). The layout condition: each unit's group (16 consecutive indices) must serve at least 2^16 rows on the unit's weight. Full groups of 16 units at m = 2^12 are the tight case (Lean `m1Domain`, `Sanity.fullGroups_inDomain`; red-team B3, C1). A group never has more than 16·2^17 = 2^21 rows, so the shared-table margin of §5 item 12 holds. Without the layout condition, one unit per weight at m = 2^12 makes the reduction's γ about 2.0%. Other domains give other γ (§5 item 1, §6).
- **Primitive.** H is SHAKE256 modelled as a random oracle (decision 6), as in POUS. It derives noise and hashes commitments.
- **Workload.** A declared finite set U of units. Unit u has a shape in D, a weight id w(u) and an index, a 64-bit field. So a workload has at most 2^64 units, and the noise queries are injective in the index (red-team B1: without the bound, two units get the same noise and one computation counts twice).
  - The weights B_w are fixed before the salt and shared by many units. The operator declares them, so they may be anything, including degenerate.
  - The activations A_u are chosen by the operator at run time: adaptively, possibly after seeing the salt, and possibly degenerate (zero or low rank). This is the permissionless setting of [KW] §5 and of [N] §'PoUW protocol conditions', where upstream values may be faked.
- **The protocol Π** fixes the domain D, the noise, the checked values, the commitment format and the honest reference H_ref.
  - *Noise* (Assumed: tt-attacks §4, adopted by the coordinator at 21:18Z). Rank r = 16 on both operands, E_u = E_L,u·E_R,g(u) and F_w = F_L,w·F_R,w, all entries i.i.d. uniform:

~~~text
E_L,u ∈ {−3, …, 3}^(m×16)   per unit:                            H(s, index, com(A_u), w)
E_R,g ∈ {±1}^(16×k)         per (epoch, weight, group g = ⌊index/16⌋):  H(s, w, g)
F_L,w ∈ {±1}^(k×16)         per (epoch, weight):                 H(s, w)
F_R,w ∈ {−3, …, 3}^(16×n)   per (epoch, weight):                 H(s, w)
|E|, |F| ≤ 16·3·1 = 48, so A + E and B + F lie in [−112, 111]
~~~

  - The ±1 factors must be the inner ones, which touch k: an outer ±1 factor makes 37% of the transcript's columns equal (§5 item 13). E_R is shared by a group of G = 16 consecutive indices, not by the whole epoch, because wider sharing admits a table attack worth up to 44% (§5 item 12).
  - *Checked values* Y: the running partial sums after every depth-d step, `C'^(ℓ) = C'^(ℓ−1) + (A + E)[:, S_ℓ]·(B + F)[S_ℓ, :]` ([KW] Alg. 6.1), with d = r = 16 (red-team A7). The accumulator produces them for free, while standalone slice products would cost H_ref 16/r more per MAC. d ≥ 16 because int8 `mma` has k ≥ 16. d ≤ r is required: at d = 32 with r = 16 the zero-input adversary's step core fits int8 in 91% of rows, one k16 instruction replaces two, and it saves about 40% (tt-attacks §4).
  - *Commitment format*: a Merkle tree under H, ideal in the game (§3.3).
- **Correct unit.** Unit u is correct in a committed transcript if two things hold: its committed checked values equal Y(s, u, A_u, B_w(u)), and its committed useful output equals A_u·B_w(u). The useful output is part of correctness because the workload consumes it.
- **Honest reference (decision 5).** H_ref is one program, fixed with Π, that reads each unit's operands as inputs, fetched free under W1 (red-team B3; `AdmitsRef` is `∃ prog ∀ act`). It runs a plain int8 tensor-core GEMM without Strassen on the noised operands, reads the running sums from the accumulator, and does everything the protocol adds: noise expansion, packing and noising, and the decode (§5 item 1). It is complete: for every input it outputs correct checked values and the correct useful output (Proved: Lean `D1Complete`, `HonestComplete`).
  - `W_ref(u)` is H_ref's M_4090 cost on unit u, excluding hash calls. It depends only on the declared layout (shapes and weight ids), not on input values. Per-epoch work on a weight is apportioned to the units that use it (red-team B3; Lean correction 2). The milestone domain requires each (group, weight) to serve at least 2^16 rows (above); full groups of 16 units at m = 2^12 are the tight case. A unit alone in its group at m = 2^12 would pay the whole E_R product, r/m per MAC, which is why D excludes it (red-team A4; Lean `Sanity.lone_unit_over_budget`).
  - `W_mm(u) = m_u·k_u·n_u` is the plain GEMM.
  - `Ω(u) = W_ref(u)/W_mm(u)` is the arithmetic overhead.
  - Hashing cost, at the reference price of §3.1, is overhead, not part of γ, and it is included in every reported slowdown.

### 3.3 The γ-gap game

The game G_γ(Π, 𝒜, T, q). Probabilities are over H, the salt s and 𝒜's coins.

~~~text
1. Workload.    𝒜 declares the units U (shapes in D, weight ids, 64-bit indices) and the
                weights B_w, before H is sampled or independently of it.
2. Oracle.      H is sampled.
3. Preprocess.  𝒜 runs an oracle program: any computation that does not depend on the salt,
                with no bound on time or memory. It is free, but its calls to H count
                towards q. It keeps a state σ.
4. Salt.        The beacon reveals s, uniform on {0,1}^λ with λ = 128, independent of (H, σ).
5. Online.      𝒜(σ, s) runs a program with M_4090 cost at most T (surely; pre-salt bytes
                are priced as in §3.1) and at most q calls to H in total, counting step 3.
                It chooses each A_u adaptively. Before the deadline it outputs, for every
                u in U, the committed values (A_u, checked values, useful output).
6. Score.       K = the set of correct units (§3.2). 𝒜 wins if
                    ∑_{u in K} W_ref(u) > T / (1 − γ).
~~~

**Requirement, with its quantifier order.**

~~~text
∃ Π  (shape domain D, H_ref complete, W_ref read from the layout only)
  ∀ declared workloads in D (shapes and layout) with |U| ≤ 2^64  (any weights)
    ∀ T ≥ 0,  ∀ q ≤ 2^64,
      ∀ 𝒜 with online cost ≤ T surely and at most q calls to H in total:
          Pr[𝒜 wins] ≤ η,

with γ = 1 − (1 − γ_0)/Ω* ≤ 0.01,  Ω* = sup over D of Ω,  and η = ε_TT(q).
~~~

- *Commitments* are ideal in the game: 𝒜 outputs the committed values themselves. η is then TT's error term ε_TT(q) (§4.4), with no random-oracle term (red-team A10; Lean correction 7). A Merkle tree adds its binding error, `ε_bind(q) ≤ q²·2^-256 + q·2^-λ` (collisions and salt guessing).
- *γ* is fixed by Π and D before the workload exists, and the verifier rejects declarations outside D, so nothing the adversary controls can move it.
- *Side conditions* (red-team A15; each is explicit in the Lean): γ_0 < 1 and γ < 1; m, k, n ≥ 1, so W_mm > 0 and Ω is defined; r ≥ 1 and d ≥ 1, with the last step capped at k when d does not divide k; q ∈ ℕ and T ≥ 0; the salt has full support; the noise distribution is fixed and has the entry bounds of §3.2.

How to read it:

- **Jointly.** One budget T is set against all units of the workload. Amortization across units, shared weights, shared per-epoch noise, batching and preprocessing are all inside the game (decision 8).
- **Adversarial inputs.** 𝒜 picks the weights and every activation, including zero and low-rank ones (decided, 9.2). Because W_ref is input-independent, anything H_ref spends that degenerate inputs make unnecessary counts against γ (§5, item 1).
- **The certified lower bound.** `L(u) = (1 − γ)·W_ref(u)` is the work each correct unit costs, amortized over the workload. It is Daniel's "assumed or verified lower bound on work": verified if the game is proved as a theorem, assumed if the proof rests on a named conjecture.
- **Relation to [N].** This is [N]'s (H_γ, η) property ([N] §'Required property': the number of correct units is at most T/((1 − γ)·W_V)). Here each unit is weighted by W_ref(u), so units may differ in size, and cost is priced in M_4090 rather than in operation counts.
- **Relation to [F].** [F] assumes that every n×m×k matmul comes with a certificate that it required n·m·k operations. The game certifies `(1 − γ)·Ω(u)·W_mm(u)` units per correct unit, which is at least n·m·k whenever Ω ≥ 1/(1 − γ). Under the §4.4 reduction, `(1 − γ)·Ω* = 1 − γ_0`, so it certifies (1 − γ_0)·m·k·n per correct unit: 0.5% short of [F]'s n·m·k (red-team A13).
- **Why γ is measured against W_ref, not m·n·k.** An operator that pays overhead Ω but is certified only m·n·k keeps a fraction (Ω − 1)/Ω of its hardware free.
- **No mining.** There are no tickets and no reward rate (decision 3). Every unit of the workload is in U, and the verifier samples units afterwards (§3.5).

### 3.4 Probability accounting (decided)

Decision 7 left this open; Daniel accepted the accounting built into §3.3 on 27 Sep (9.1).

- **A tail bound, not an expectation.** Resource exhaustion is a statement about one audit: "accepted, and the operator did too little work" must be rare. Bounding expected rewards, as the first draft did, bounds the probability of beating the budget by a factor 1 + x only by 1/(1 + x) (Markov). The tail form bounds the event directly and composes with sampling (§3.5).
- **A budget, not realized cost.** 𝒜's online cost is at most T surely, and T is quantified universally, so the bound holds at every budget.
- **Online work only.** Cost counts from the salt to the commitment deadline.
  - Work before the salt that does not depend on it is preprocessing: free and unbounded (decision 8). Its results are pre-salt data, priced at first fetch (§3.1).
  - Work after the deadline, such as replays for the verifier, is verification, which is out of scope (decision 4).
  - Work fixed for a whole epoch, a weight or a group (forming F and B + F, and the per-group E_R product) is done online once and apportioned to the units that use it (§3.2).
- **Oracle calls are free but bounded.** At most q calls, preprocessing included. Grinding, meaning choosing the best of q noise draws by varying A_u or dropping units whose noise is unfavourable, is inside ε_TT(q) and γ_0, because TT is stated in the same game with the same q (red-team A10). Collisions and salt guessing go into ε_bind(q).
- **Concrete numbers.** γ and η are numbers, with no o(·) and no unspecified constant. That is exactly what [KW] Def. 5.1 (a constant C) and Assumption 6.4 (an o(·) bound) do not give.

### 3.5 Composition with sampling

**Theorem 1** (Proved: Lean `Theorem1`; the work-weighted form of [N] Theorem 3.1). Write `W = ∑_{u in U} W_ref(u)`. Suppose G_γ holds with error η, and the sampling protocol satisfies

~~~text
Pr[ accept ∧ ∑_{u not in K} W_ref(u) > ε_s·W ] ≤ δ_s.
~~~

Then for every T and every operator strategy with online cost at most T surely,

~~~text
Pr[ accept ∧ T < (1 − γ)(1 − ε_s)·W ] ≤ δ_s + η.
~~~

*Proof.* Suppose T < (1 − γ)(1 − ε_s)·W. Outside the η event, `∑_{u in K} W_ref(u) ≤ T/(1 − γ) < (1 − ε_s)·W`. So the incorrect units carry more than ε_s·W of honest work, and such transcripts are accepted with probability at most δ_s. ∎

The same holds with T the realized online cost: run the strategy until its cost would exceed (1 − γ)(1 − ε_s)·W, then commit a default transcript. This needs cost monitoring and default commitments to be free; it is not formalized (red-team A9).

What this gives and needs:

- The audit certifies work at least (1 − ε)·W with `ε = 1 − (1 − γ)(1 − ε_s) ≈ γ + ε_s`. Declared work that is not matmul (a fraction f) is not certified, so in general ε ≈ γ + ε_s + f ([N] §'Theorem 3.1'). For the pure matmul workload of decision 3, f = 0.
- Sampling as in [N]:
  - one proof per replay, so an accepted transcript has an incorrect fraction below Λ/(p·N_R) however the errors are arranged ([N] Theorem 4.2);
  - streaming coins are fine ([N] Lemma 4.4);
  - the verifier chooses the sample; a self-selected lottery needs about 4.7/ε times as many proofs ([N] Theorem 7.1).
- [N] assumes equal-work units. Here sampling is work-weighted: t samples with probability proportional to W_ref(u) give `δ_s = (1 − ε_s)^t` (Proved: Lean `WorkWeightedSampling`). Lean `EndToEnd` composes TT, the reduction of §4.4 and this sampler: `Pr[accept ∧ T < (1 − γ)(1 − ε_s)·W] ≤ (1 − ε_s)^t + ε_TT(q)`.
- Verification is essentially free (decision 4), so ε_s can be made as small as wanted. γ is the binding term, and sampling cannot shrink it.

## 4. Assumption landscape

### 4.1 What standard assumptions prove

"Standard" here means SHAKE256 as a random oracle, collision resistance of a named hash, and the beacon's min-entropy, with no complexity assumption about arithmetic.

- **Binding and freshness** (Proved, in the random-oracle model).
  - Merkle commitments fix the committed values.
  - Noise derived by H from (s, index, commitment) is fresh: distributed as Π specifies, and unknown before the query that fixes it.
  - The index in the noise stops one product from counting twice, provided indices are bounded and the queries injective in them (§3.2; red-team B1).
  - A fresh salt stops stale products from counting.
  - These are the sufficiency conditions of [N] §'PoUW protocol conditions'. Each is also necessary: dropping any one gives a cheap attack there.
- **Sampling and composition** (Proved, unconditionally): Theorem 1 and work-weighted sampling (Lean `Theorem1`, `WorkWeightedSampling`, `EndToEnd`), [N] Theorem 4.2 and [N] Lemma 4.4.
- **Usefulness** (Proved, unconditionally): H_ref's integer arithmetic, decode included, equals A·B. Lean `Usefulness` proves the identity over ℤ, and `Int32Decode` the int32 decode with wraparound for int7 operands and k ≤ 2^19 − 1.
- **Work: nothing.**
  - Hash calls are free (decision 1), so the random-oracle model certifies no work.
  - Unconditional arithmetic lower bounds are far too weak. The bilinear rank of n×n×n matmul is at least 3n² − o(n²) (Landsberg 2014). Bounded-coefficient arithmetic circuits need Ω(n² log n) (Raz 2002). The product costs n³. For general Boolean circuits or RAMs nothing is known beyond the output size.
  - Fine-grained assumptions are asymptotic, with polylogarithmic slack (Ball–Rosen–Sabin–Vasudevan 2018, proofs of work from worst-case assumptions).

So standard assumptions cannot give γ ≤ 1% when the work lives in the matmul. §4.2 says what has to be added.

### 4.2 What a 1% gap needs, and why each ingredient is unavoidable

Four ingredients are needed. Each is forced by an argument or a counterexample.

**(a) A hardware-priced cost model.** In the standard abstract models the 1% claim is false, so no proof can exist there.

- *Commutative multiplication count.* Winograd's inner-product trick (1968) multiplies sums of an A entry and a B entry, and computes A·B with m·k·n/2 + O(mk + kn) multiplications: half the count.
- *Bilinear multiplication count.* Strassen saves 1/8 of the multiplications per level. It applies inside any checked block of size at least 2, because a transcript fixes only the order of the blocks, not how each block is computed.
- *Unit-cost RAM.* Table lookup over the small operand alphabet saves a factor t with tables of 256^t rows: the Four-Russians idea (Arlazarov et al. 1970). Preprocessing one operand turns this into a growing factor (Williams 2007; Larsen–Williams 2017, for Boolean matrices), and decision 8 grants unbounded preprocessing on the weights.

In M_4090 under W1, at d = 16, none of these pays, for one reason (Derived; tt-attacks §2). Every INT32 or tensor-core instruction costs at least 16 units per 32-bit word it outputs: an int8 `mma` m16n8k16 costs 2,048 for 128 words, and IADD3, LOP3, IMAD or IDP4A cost 16 for one. H_ref at d = r = 16 pays exactly 16 per checked value, one k16 output slot. So *slice rank deficiency* cannot pay (a step's increment still needs its k16 instruction unless it is known to be zero); *Strassen* cannot pay (each of its 7 products still costs a k16 instruction, at least 28 per word), and Winograd's pre-sums are not matrix products; and *int4 and dp4a* cannot pay (two int4 limbs per side cost 32 per word, dp4a 64).

Only three routes cost less than 16 per word: free copies of structurally equal checked values, FP32 adds on integer bit patterns (8 units, §3.1), and tables shared across many rows. §3.2's Π is chosen against each (§5 items 12 and 13). A lookup is free under W1, but its entry must be built online (8–16 units) or fetched as pre-salt data (345 per byte), so draft 2's "32 units per lookup" is obsolete. IMAD.WIDE, which outputs two words, is priced per word by W1 but its rate is unmeasured (tt-attacks H4; Unverified).

This is why decision 2 is more than a convenience: the statement can only be true in a model like M_4090.

**(b) A concrete constant.** Asymptotic hardness is consistent with every constant speedup. [KW] Assumptions 6.3 and 6.4, "no algorithm in o(·) of the best known time", cannot give 1%.

**(c) A joint, direct-product form.** The requirement is joint across units that share weights and preprocessing (decision 8). Single-instance hardness does not compose by itself. No concrete direct-product theorem is known, and for algebraic problems amortization is often real: many matrix-vector products with one matrix form a matrix product, and shared noise admits shared tables (§5 item 12).

**(d) Hardness for structured instances, not only uniform ones.** Lemma 1 shows that cheap decoding forces structured noise. So an assumption about uniformly random operands, the most defensible kind, cannot by itself give γ < 1/2 for useful work.

**Lemma 1** (Proved). Let each unit's checked values be the noised product `C' = (A + E)(B + F)` alone, with additive noise E and F. Let H_ref get the useful output by decoding, `C = C' − D` with `D = A·F + E·(B + F)`, at arithmetic cost c_dec, and expand the noise at cost c_noise.

1. An adversary that commits A = B = 0 has `C' = E·F = D(0, 0, E, F)` and C = 0. Expanding the noise and running the honest decode on zero inputs gives it a correct unit. Hence `γ ≥ 1 − (c_dec + c_noise)/W_ref`: with cheap decoding, output-only checks certify almost nothing.
2. If instead E and F are uniform, so that C' costs a full product, then D contains A·F, which costs another product for generic A. An H_ref built from plain GEMMs (decision 5) spends at least two products (three with the standard decode), while an adversary with A = 0 spends one. Hence, for such an H_ref, γ ≥ 1/2, or 2/3 with the standard decode.

*Proof.* Part 1 is the identity D(0, 0, E, F) = E·F = C'(0, 0). For part 2, the adversary's useful output is 0, so its only cost is C' = E·(B + F), one product. ∎

So γ ≤ 1% needs two things together:

- checked values beyond the output: intermediate state, as in [KW]'s transcript, or a non-additive encoding;
- noise cheap enough to remove, which makes the checked instances structured.

The hardness assumption must therefore be about those structured instances. For products that need no decoding, such as FLOP padding on uniform operands, an assumption about uniform operands does suffice (§6, D3).

### 4.3 The options

| | Assumption | Kind | Supports γ ≤ 1%? | Remarks |
|---|---|---|---|---|
| S | SHAKE256 as a random oracle, collision resistance, beacon min-entropy | Standard | No. It certifies only hash calls, which are free here | Still needed for binding and freshness |
| U | Unconditional arithmetic lower bounds | Theorems | No: about 3n² against n³ | |
| R1 | Monotone circuits (no subtraction or negation) | Restricted model. Provable: for the Boolean matrix product, n³ conjunctions are necessary (Paterson 1975; Mehlhorn–Galil 1976) | Only inside the model | Excludes subtraction, and so Strassen, by fiat. No real adversary is monotone |
| R2 | Bilinear or commutative algebraic models | Restricted model | No. False by Strassen (7/8 per level) and Winograd (1/2) | Too generous to the adversary |
| R3 | Schoolbook-forced (tensor-core) model: only int8-range values are multiplied; every other operation is priced by M_4090 | Restricted model | Yes, inside the model | Turns the overflow argument into an axiom. Whether real adversaries fit the model is the conjecture itself |
| R4 | R_copy: the adversary fixes before the salt which checked positions share one produced word, and pays 16 per word (tt-attacks §6) | Restricted model. Provable, with a bound that depends on the noise (§4.4) | Only inside the model | Excludes adaptivity, FP32 adds and shared tables by construction |
| C1 | Uniform GEMM is tight in M_4090 | Concrete conjecture, falsifiable | Not for useful work (Lemma 1, part 2: γ ≥ 1/2). Yes for padding | The most defensible statement: [F]'s assumption made precise |
| C2 | TT, the tight noised transcript: [KW] Assumption 6.4 extended to adversarial inputs, concrete, joint and integer, in M_4090 | Concrete conjecture, falsifiable | Yes, at large shapes (§5, item 1) | **Recommended, and decided** (§4.4, 9.5) |
| C3 | Local hardness of globally structured noise ([KW] Conjecture A.1); or Pearl's Assumption 1 with its jackpot policy | Conjecture; Pearl adds a heuristic policy | Open for the first. No for Pearl: FP8, with at least 5% built-in allowances (§7) | |

**Restricted model or conjecture?** A restricted model makes the bound provable, but only against adversaries that stay inside it. Its defensibility rests on the same cost arguments as the conjecture: limbs, priced additions and the per-word floor. So it is not a weaker assumption, only a different packaging, and it hides the adequacy question inside a definition. A concrete conjecture in M_4090 states the same claim openly, and one fast kernel refutes it. Restricted models stay useful as Lean targets that rule out named attack classes (§6, D6).

### 4.4 Recommendation

Adopt one named conjecture, C2 below, and prove everything else in Lean (decided, 9.5).

**Assumption TT(γ_0): tight noised transcript.**

- Π is §3.2's: the named noise distribution (E_L and F_R uniform on {−3, …, 3}, the inner factors E_R and F_L uniform on {±1}, rank 16, E_R per group of 16 indices), the checked values being the running sums after every step of depth d = r = 16, and the milestone domain D.
- Consider every adversary in the game of §3.3: free unbounded preprocessing whose hash calls count, at most q free hash calls in total, online M_4090 cost at most T surely, and adversarial weights and activations.
- Let K' be the set of units whose checked values are correct. The useful output is not required.

Then:

~~~text
Pr[ ∑_{u in K'} m_u·k_u·n_u > T / (1 − γ_0) ] ≤ ε_TT(q),        target γ_0 = 0.5%
~~~

**The per-word form at d = 16** (tt-attacks §2, §7). H_ref pays exactly 16 units per checked value, and a unit has m·k·n/16 of them. So under W1, TT(γ_0) is equivalent to: *no adversary obtains correct checked words for less than 16 units each on average, up to γ_0.* This makes the conjecture's content visible. The known routes below 16 are free copies, FP32 adds and shared tables (§4.2 (a)), and each needs a key shared by many positions, which §3.2's Π denies (§5 items 12 and 13).

Why this one:

- **It isolates the conjecture in the checked computation** (red-team A8). TT is the game itself restricted to the checked values and weighted by m·k·n, so the Lean reduction from TT to G_γ is short bookkeeping; the content is in TT. By Lemma 1 any γ ≤ 1% scheme with cheap decoding needs an assumption about structured instances, and TT says nothing about decoding, which the reduction handles.
- **Its relation to [KW].** [KW] Assumption 6.4 is the zero-input case: two random rank-r matrices. TT extends it to adversarial inputs and makes it concrete (γ_0), joint (K') and integer (red-team A8). It has the four ingredients of §4.2 and nothing more.
- **It is defensible and falsifiable.** At d = 16 every known speedup class meets the per-word floor, and Π's choices close the routes below it (§4.2 (a), §5). KW conjecture the asymptotic version. One kernel that beats the schoolbook transcript by more than γ_0 at the §3.1 prices refutes it; the evidence to collect is a benchmark suite over the attack classes of §5.
- **It constrains the protocol** (Proved: Lean `Sanity.tt_admitsRef_bound`, `Sanity.tt_false_of_gamma0_ge_one`; Lean correction 8). In any cost model that runs H_ref at W_ref, TT with error below 1 implies `(1 − γ_0)·W_mm ≤ W_ref` on every in-domain workload, so Ω* ≥ 1 − γ_0. TT is unsatisfiable for γ_0 ≥ 1.
- **A cleaner variant is open.** TT restricted to zero inputs would be a statement about a single public distribution. KW assert that under their conjecture zero inputs are as hard as any others; no reduction from arbitrary committed inputs to zero inputs is known.

**A restricted model with a provable, noise-dependent bound: R_copy** (tt-attacks §6). Before the salt, the adversary partitions each unit's N_u checked positions into classes, pays 16 per class, and is correct on u only if the values within each class are equal. If the checked values are independent and each takes any fixed value with probability at most 1/2, then `Pr[∑_{u in K'} 16·N_u > cost/(1 − γ_0)] ≤ ∑_u 2^(−γ_0·N_u)`. With zero noise the one-class adversary wins, so the bound depends on the noise. R_copy captures the per-word floor and free copies, but excludes adaptivity, FP32 adds and shared tables by construction, and real running sums are not independent. It is a Lean witness, not evidence for TT.

**The Lean split.** Assuming TT(γ_0), prove the following.

1. **G_γ** with `γ = 1 − (1 − γ_0)/Ω*`, where Ω* is the largest overhead over the shape domain D, fixed by Π. This reduction is conservative: it credits only the transcript's m·k·n and treats all other protocol arithmetic as skippable, the worst case by Lemma 1. A refined reduction would also credit the noising, and needs a version of TT that counts it.
2. **Compute transparency**, from G_γ and sampling, by Theorem 1.
3. **Usefulness:** H_ref computes A·B exactly.
4. **Optionally, restricted-model lemmas** that rule out named attack classes, such as R_copy (§6, D6).

TT then appears as one named hypothesis in the Lean statement, as the POUS assumptions do.

**Lean status** (`lean/submissions/pouw/NOTES.md`, revision of 22:00Z).

- *Proved.* Every pinned statement is proved:
  - `GammaFromTT` (item 1);
  - `Theorem1`, `WorkWeightedSampling` and `EndToEnd` (item 2);
  - `Usefulness`, `Int32Decode` and `NoisedKBound` (item 3);
  - `MilestoneRequirement` and `MilestoneExhaustion`, in budget form for the named instance `D1.m1`, together with the witnesses (`TTWitness` and R_copy) and a Sanity lemma for each degenerate case.
- *The named instance.* `D1.m1` has §3.2's distribution: E_L and F_R in {−3, …, 3}, the inner factors E_R and F_L in {±1}, and E_R per (epoch, weight, group of 16). Its domain is the milestone shapes, at most 2^64 units with collision-free noise queries, and at least 2^16 rows per (group, weight). Its W_ref, `m1Wref`, is the red team's recount, pinned as `MilestoneWref`. With the int8 limb split added after Daniel's 03:35Z sub-word rule (red-team P7-4), Ω = 65769/65536 and γ = 14017/1644225 ≈ 0.8525% (§6). The earlier record was 8221/8192 and 1749/205525.
- *Audit.* The package passes Verity's Lean audit with `leanchecker --fresh`, on the axioms `propext`, `Classical.choice` and `Quot.sound` only.
- *Review.*
  - **Granted by the red team** (22:18Z, phase D) on the 22:10Z package. As the named statement reviewer it signed all 54 pins.
  - A 55th pin, `milestoneERSeparated`, says that E_R queries for distinct (weight, group) pairs are disjoint (red-team D1). It was added at 22:30Z, with `check.sh` passing on 652 declarations, and the red team signed it (phase F), so all 55 pins are signed.
  - `m1Wref` now includes the limb split (P7-4). Noise expansion is still omitted, at about 10^-6; γ stays 0.85%, well inside the 199/198 budget.
  - Whether M_4090 runs H_ref at `m1Wref` (`AdmitsRef`) is Derived from the instruction schedule, not proved; TT is the conjecture.

**Budget.** For small values, `γ ≈ γ_0 + (Ω* − 1)`. So γ ≤ 1% leaves about 0.5% for the protocol's arithmetic overhead: noising and decoding, with hashing excluded. §5, item 1, says what that costs.

## 5. Known sources of gap

Each item gives the source, its size where known, and how the statement handles it. This extends [N] §'Known sources of work gap' to M_4090 under W1. Items 10–13 are new in draft 3.

1. **Decoding skipped on degenerate inputs.** H_ref decodes the useful output. An adversary whose activations make the useful product trivial (zero, or low rank with known factors) skips the decode, even though the useful output is checked.
   - *Size* (Derived under W1; `llm-shapes` §3, tt-attacks §3, red-team A4 and B3). The conservative reduction treats all of H_ref's arithmetic beyond m·k·n as skippable:

~~~text
Ω − 1 ≈ (2r + 20)/n + (6r + c)/k + r/(G·m) + (r + 20)/R_w,      c = 32
~~~

   - The terms, in order: X1 = (A + E)·F_L and forming E, with packing A′ into int8 at 20 units per entry; the rank-2r correction, whose factors are about 20 bits wide and so need three int8 limbs; combining the limbs, two INT32 instructions per output entry in the cheapest schedule found; the per-group product E_R,g·(B + F) over a full group; and u's share of F_L·F_R and B + F for its weight, (r + 20)·k·n units per weight and epoch, where R_w is the number of rows the weight serves. This is the red team's machine-checked recount (B3), which the coordinator adopted at 21:35Z. The refined reduction also credits the noising, (r + 12)/n.
   - r cannot go below 16: int8 `mma` stops its accumulator at most every 16 in k, and d ≤ r (§3.2).
   - At [N]'s Kimi-K3 expert shape (1024, 3584, 3072), γ ≈ 5.4% (4.5% refined), not draft 2's 1.4–3.0% in MAC count (§6).
   - *Handling:* counted in γ, since inputs are worst case (decided, 9.2) and W_ref is input-independent. With k = n, γ ≤ 1% needs k ≳ 36,000 (29,000 refined). Milestone 1 gives γ ≈ 0.85% (§6).
   - *A trade-off with hashing* (Derived; `llm-shapes` §1). Hashing the running sums costs 2,100/d units per MAC, plus 521/n for committing A_u. With d = r, (skippable share) × (hashing) ≥ 2,100·(2/n + 6/k), plus a floor of 20/n + c/k that no r removes. At k = n = 4,096 the product is 4.1, so a 0.5% share would need about 820× hashing, while r = 16 is already the smallest the hardware allows. Folding before hashing lowers the hashing, not this floor (item 7, §6 D2).
2. **Algorithmic constant factors and slice rank:** Strassen (1/8 of the multiplications per level), Winograd's trick (1/2), table methods (a factor t), and rank-deficient noise slices.
   - *Size:* large in operation counts (§4.2 (a)). In M_4090 at d = 16, none pays: every INT32 or tensor-core route costs at least 16 units per checked word, as H_ref does (§4.2 (a); tt-attacks §2).
   - *Strassen above d = 16.* One level inside a step saves 1/8 of the step, less c units per output word for the post-additions, so it pays above a checked width of 8c. With IADD3, which does two additions per instruction, c ≈ 8–14 and the break-even is 64–112 (red-team A6). With FP32 adds on biased non-negative values, c ≈ 4–7 and the break-even is about 32–56 (tt-attacks §5). Zero-input operands (|E| ≤ 48) have the headroom for the 9-bit pre-sums.
   - *Slice rank* (red-team A5, B7). Pearl's two-sparse ±1 factor makes every depth-r slice rank-deficient: each column is e_a − e_b, so the rank is at most r − 1, and 13.5 of 16 on average. Under per-MAC pricing that is worth 8.9% at r = 16. §3.2's dense ±1 inner factors give a singular slice core in 9.2% of steps (mean rank 15.91), worth 0.58%, above γ_0 (tt-attacks §2). Under W1's full-shape pricing at d = 16 both are moot.
   - *Handling:* inside TT, with d = r = 16 (§3.2). A d = r = 32 variant would have to count FP32 adds, where c = 4 is the break-even (tt-attacks §5).
3. **Correlated instances and amortization:** shared weights, shared per-epoch weight noise, shared low-rank factors, batching.
   - *Size:* unknown in general. This is what [KW]'s direct-product conjecture is about. The one concrete attack found, shared noise tables, is item 12.
   - *Handling:* the game is joint, with one budget T (§3.3), and TT is stated jointly. Batching many activation rows against one weight is just a larger m, which D bounds.
4. **Unbounded preprocessing on fixed weights** (decision 8).
   - *Size:* a growing factor in RAM models (Williams 2007; Larsen–Williams 2017). Under W1 a lookup is free, but an entry built online costs 8–16 units and one fetched from pre-salt data costs 345 per byte. A table can depend on B but not on the fresh F, and the part of each step that involves F, (A + E)[:, S]·F[S, :] = ((A + E)[:, S]·F_L[S, :])·F_R, costs about m·r·n, the whole honest step at d = r (red-team A1, and its answer on W1).
   - *Handling:* the preprocessing phase is free and unbounded, and TT must hold with it. Tabulating the noise itself is item 11.
5. **Model of computation and concurrency:** whether a MAC counts as one operation or two, how a tensor-core instruction is priced, and whether concurrently running units add up.
   - *Size:* measured, concurrent CUDA-core work adds at most about 5% to throughput, without lowering the M_4090 cost (§3.1).
   - *Handling:* M_4090 prices both sides per instruction, a tensor-core instruction by its full shape. Concurrency belongs to the deferred capacity model, not to γ.
6. **Operand range and cheaper datapaths.** int4 tensor cores cost 1/2 unit per MAC.
   - *Size:* if noised operands carried at most 4 bits per entry, int4 would give a 50% gap. Entries in [−112, 111] need two int4 limbs per side, 32 units per word at d = 16. FP16 with FP16 accumulate (2 per MAC) and FP8 are not exact for 7-bit products (red-team A12).
   - *Handling:* noised operands carry about 7–8 bits per entry (§3.2). 2:4 sparsity saves nothing per product (§3.1).
7. **Checked granularity against hashing cost.** Every checked value must be committed before the challenge, and SHAKE256 costs about 2,100 units per int32 value (measured, §3.1).
   - *Size:* output-only checks cost about 2,100/k units per MAC, but they fail for useful work (Lemma 1). Running sums at depth d cost 2,100/d per MAC: 131× at d = 16, 66× at d = 32. Reading each accumulator after every 16-deep step also costs real time, 1.30× the bare tensor-core time (1.01–1.04× at d = 32), which under W1 is overhead, not W_ref (§3.1).
   - *Handling:* hashing is free in γ, so this is overhead, not gap. Folds that are linear over Z, Z/2^32 or GF(2) commute with the product: the adversary folds the weights first, `L(C'^(ℓ)) = ∑_{steps ≤ ℓ} (A + E)[:, S]·((B + F)[S, :]·R)`, at about m·k·t instead of m·k·n (`llm-shapes` §2). That covers IADD3 trees and XOR trees, Pearl's XOR/rotate fold [M] among them. Nonlinear folds cost 8–32 units per checked value and need their own assumption (§6 D2).
8. **Uncovered non-matmul work (f).**
   - *Size:* zero for the pure matmul workload. [N] estimates 0.5–1% for Kimi-K3's attention glue (Unverified).
   - *Handling:* it adds to ε (§3.5).
9. **Stale values, salt predictability and grinding.**
   - *Size:* unbounded if unhandled ([N] §'PoUW protocol conditions', conditions 1–6).
   - *Handling:* noise depends on the salt and on the commitment, so preprocessing cannot see it. Free hash calls allow grinding: choosing among q/|U| noise draws per unit by varying A_u, or dropping units whose noise is unfavourable. TT is stated in the same game with the same q, so grinding is inside ε_TT(q) and γ_0, not an extra q·p term (red-team A10). With §3.2's outer factors, 44.9 bits per row or column, 2^64 calls buy only a handful of duplicate rows, under 0.1% of one unit (tt-attacks §4). [W] §4.6 notes that Pearl's security definitions do not yet cover grinding or shared work.
10. **Operand reads skipped on degenerate inputs** (red-team A1). If memory traffic were priced additively, H_ref would pay to read A and B and stage them through shared memory: 0.5% for A at n = 2^16, 8% per pass over B, and 12.5–25% for staging. A zero-input adversary generates E and F on chip and reads nothing, so γ ≥ 6–29%.
    - *Handling:* W1 makes online data moves free, and a correct unit's weight free on first fetch (§3.1). Not a gap under W1.
11. **Tabulation channels** (tt-attacks V1, H1–H4; red-team W1-1, W1-2). Salt-independent preprocessing can enumerate every value of the noise factors, with no H calls, and store the zero-input transcript for each. The channels, and how W1 closes each:
    - *σ*: a stored checked value costs 4 × 345 = 1,380 units to fetch, against 16 to compute, and noised rows do not recur, so the attack loses by 86×.
    - *Program text*: a branch trie leading to straight-line code that materializes each stored value from an immediate. Unpriced, this breaks TT by 25–100% at d = 16 (W1-1). W1 prices program text as pre-salt data and an immediate move as an instruction of its class.
    - *Dummy weights and activations*: σ stored as the weights or activations of units that are never computed. W1 prices the first fetch of a unit's operands unless the unit is correct (W1-3). A correct unit costs about m·k·n and frees k·n bytes, at least 16 units per byte, while a stored byte saves at most 4 (red-team, on W1's final wording).
    - *Atomics and reductions*: as free adders they give four free loads and four free atomic adds per checked value, γ ≈ 79% at m = 2^16 (H1). W1 prices each lane operation as an INT32 instruction.
    - *Unpriced opcodes and register-plus-register addresses* (H4): W1 prices every opcode class and allows one register plus an immediate per address.
    - *Memory as a computer* (H5): byte stores concatenate values, and a data-dependent load then evaluates any function from an online table, so every instruction could be replaced by free memory traffic. W1 prices every instruction whose address, guard or enclosing branch depends on data, at 16 per lane per 32-bit word. That includes implicit flows, so a key paid for once cannot be reused through a register set under a branch, a mux tree behind one paid predicate, or a wide load that returns four words. Every lookup route then costs at least 16 per word. That is not enough to kill the shared-table attack of item 12 by itself: only the table-build cost under the group bound (at most 2^21 rows per E_R) defeats it, so the group rule stays load-bearing (red-team phase E).
12. **Shared noise tables** (tt-attacks V3 and §3; red-team B8). If E_R and F were shared per (epoch, weight), each transcript row would be a fixed function of that row's 16 entries of E_L. The adversary splits them into halves (7^8 values each), tabulates both halves once per (epoch, weight) and step, and gets each checked value from two free loads and one FP32 FADD: about 9 units against 16. It breaks even at about 6,400 units per (epoch, weight), saves 41% at 10^5 units and tends to 44%. Inside one unit it pays once m ≳ 2.6 × 10^7 rows share one noise core.
    - *Handling:* E_R is per (epoch, weight, group of G = 16 consecutive indices), and D bounds m·G ≤ 2^21, 12× below the break-even. At m = 2^12 the tables would cost 400× what they save. The honest per-group product costs r/(G·m), 0.024% at milestone 1.
13. **Structural copies from the factor distribution** (tt-attacks §2 and §4). Two transcript columns are equal whenever the matching columns of F_R are (take B = 0), and likewise rows of E_L. With an outer ±1 factor at n = 2^16, 36.9% of columns are redundant: a 37% attack.
    - *Handling:* the ±1 factors are the inner ones (§3.2). With outer factors in {−3, …, 3}^16, the expected number of equal pairs is 6.5 × 10^-5 columns per weight and 2.4 × 10^-7 rows per unit.

## 6. Candidate directions, tagged by assumption

| | Direction | Assumption | Reaches γ ≤ 1%? | Cost | Role |
|---|---|---|---|---|---|
| D1 | [KW] transcript, fully hashed: §3.2's Π, running sums at d = r = 16, SHAKE256 Merkle commitment, the useful output by decoding | TT(γ_0) + ROM | Only at large shapes: γ ≈ 0.85% at milestone 1; with k = n it needs k ≳ 36,000; LLM shapes give 2.5–7% | Arithmetic per §5 item 1. Hashing 2,100/d per MAC: 131× at d = 16. Accumulator reads 1.3× in real time | **Recommended first end-to-end milestone.** The security comes from TT, not from the hashing |
| D2 | D1 with each checked value folded nonlinearly before hashing | TT + a no-shortcut assumption for the fold | Same floor as D1 | Fold 8–32 units per checked value (LOP3 tree 8, IDP4A 16, byte `mma` 32): 0.5–2× the GEMM at d = 16. Hashing falls to 0.13–2.2× | Later. Linear folds are broken (§5 item 7). Uncredited, the fold is skippable and γ rises to 35–67%. Credited, it lowers γ only by dilution: 1.9% at 4,096² with a third of the certified work useful |
| D3 | FLOP padding: extra GEMMs on H-derived uniform int8 operands, with no useful output and output-only checks | C1(γ_0) + ROM | Yes for the padding share, with γ = γ_0, since there is no decode | Hashing about 2,100/k per MAC for the committed outputs | The cleanest statement, but it certifies only padding |
| D4 | Noise whose correction is cheaper than D1's ([KW] Problem 3.2; random rotations, [KW] App. A). The candidate D4-s: inner factors are signed partial permutations on the same 8 of every 16 rows of each step, rank 8 at d = 16, outer alphabet [−48, 48] (`internal/pouw/llm-relaxations.md` §3) | TT for that distribution. At d = 16 the adversary pays one k16 instruction per step whatever the rank, so d ≤ r binds only above d = 16 (tt-attacks §8: correct, under its conditions) | Near the floor: about 2.0% at 4,096² (1.95% plus 2/n to 4/n for the gather of E, which H5 prices), and 1% for k ≳ 18,700, e.g. Llama-3-70B's down projection. The class floor is 1.89% (k ≳ 17,800; below) | As D1, with a rank-8 correction | **The open research direction.** tt-attacks (§8) finds it safe at d = 16 with one fix. As specified, adjacent steps cancel or sum to rank 1 often enough that an adversary who finishes only lucky groups saves 0.5% with probability 2^-24.6 per group at k = 4,096 (2^-15.7 at k ≤ 3,200), which refutes TT(0.5%) at those shapes. Fix: reject X_{S+1} when rank(X_S + X_{S+1}) ≤ 1. It needs full-shape tensor pricing: under per-MAC pricing it loses 50% |
| D5 | Recursive noising of the correction products | TT for the correction products too | No. The correction is an (m, 6r, n) product whose inner dimension, about 96, is not large next to its own noise rank, so each level costs more than the last (`llm-shapes` §5) | — | Fails |
| D6 | Restricted-model lemmas in Lean: R_copy (§4.4), and in the schoolbook-forced model R3 the named attack classes (Strassen-type algorithms with limbs, lookups, int4 limbs) | None beyond the model | Inside the model | — | Evidence for TT, and a Lean target |
| D7 | Noise-cancelling polarization (NCP), added 28 Sep: full-rank noise that cancels inside one checked GEMM of inner dimension 3k, the stacked [A + E_1, A + E_2, −(A + E_3)] times [B + F_1 ; B + F_2 ; B + F_3], whose output is A·B, with no decode ([new-crypto.md](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/docs/pouw/new-crypto.md) §2) | TT_NCP(γ_0): a new structured conjecture whose zero-input core has rank k | Yes, at LLM shapes too: γ ≈ 0.51% at the milestone and 0.66% at 4,096² under TT_NCP(0.5%), for k ≥ 1,067 and a P whose checkpoint matrices are independent | Arithmetic ≈ 3×; hashing ≈ 394× per useful MAC at d = 16 | **Candidate for transformer shapes**, red-teamed; Lean for the barrier, the algebra and the reduction |

Notes on D1:

- **Integer noise differs from [KW]'s.** Over the integers with int8 headroom the noise cannot be uniform over rank-r matrices, and [KW] Lemma 6.5 is over a finite field. §3.2 names bounded factors instead, and TT is stated for them.
- **Milestone 1** (Derived). (m, k, n) = (2^12, 2^16, 2^16), d = r = 16, §3.2's Π, and the milestone domain of §3.2.
  - By §5 item 1 (red-team B3, machine-checked), each unit's own work is m·k·n + 2·m·k·r + 6·m·r·n + 20·m·k + 32·m·n: Ω = 16429/16384 and γ ≈ 0.77%. The group share adds 0.024% (γ ≈ 0.80%), and the per-weight share at 2^16 rows adds 0.055%. So Ω* = 8221/8192, Ω* − 1 = 232/2^16 ≈ 0.354%, and γ = 1749/205525 ≈ **0.85%** under TT(0.5%). Pricing the int8 limb split of the two wide decode intermediates, after the 03:35Z sub-word rule (red-team P7-4), adds one more 1/2^16: Ω* = 65769/65536 and γ = 14017/1644225 ≈ 0.8525% (Lean `MilestoneWref`, updated 06:00Z).
  - The Lean states the milestone in budget form: γ = 1 − 0.995/Ω_max, at most 1% exactly when Ω_max ≤ 199/198, a 0.505% overhead (Lean `GammaBudget`, `MilestoneRequirement`). Its earlier count `milestoneWref` (Ω = 2053/2048, γ ≈ 0.742%) omitted the limbs, the packing and the per-epoch share, and is retired. The 65769/65536 above is the count the Lean leaves to M_4090, and it is within 199/198.
  - The transcript is m·k·n/16 = 2^40 int32 values, about 4.4 TB per unit. Hashing it costs 131× the GEMM in units. In time, SHAKE256 at 626–696 GB/s takes 6.3–7.0 s, against 0.058 s for the GEMM at the sustained 302 T MAC/s, or 0.076 s with the accumulator reads (`gpu-constants`). Memory is about 10 GB.
  - That fits "end to end at high overhead first" (decided, 9.4).
- **LLM shapes cannot reach 1% at any hashing overhead** (`llm-shapes` §1). The frontier of γ against hashing, conservative / refined, with d = r:

| Shape | (k, n) | d = r = 16, 131× | d = r = 32, 66× | d = r = 64, 33× |
|---|---|---|---|---|
| Kimi-K3 expert ([N]) | (3584, 3072) | 5.4% / 4.5% | 8.6% / 7.3% | 14.4% / 12.3% |
| Square | (4096, 4096) | 4.6% / 4.0% | 7.4% / 6.4% | 12.5% / 10.8% |
| DeepSeek-V3 expert down | (2048, 7168) | 6.9% / 6.6% | 11.2% / 10.7% | 18.7% / 17.8% |
| Llama-3-8B down | (14336, 4096) | 2.5% / 1.9% | 3.9% / 2.9% | 6.5% / 4.8% |
| Llama-3-70B down | (28672, 8192) | 1.5% / 1.2% | 2.2% / 1.7% | 3.6% / 2.7% |
| Milestone shape | (65536, 65536) | 0.77% / 0.72% | 0.96% / 0.89% | 1.34% / 1.23% |

  - These figures omit the per-group product and the per-epoch share, which m would otherwise enter: the group term adds 0.02–0.1 points for m from 4,096 down to 1,024 (tt-attacks §3), and the milestone row becomes 0.85% with both (above).
  - At typical transformer shapes γ is 2.5–7% at 131× hashing, 1.5% at the largest layer found. Less hashing always costs γ. With k = n, 1% needs k ≳ 36,000.
  - The floor is the decode (§5 item 1): folds lower the hashing, not γ (D2), and D5 fails. What would move LLM shapes below 1% is a cheaper correction (D4), relaxing worst-case inputs (question 8), or diluting with 4–10× certified work that is not useful.
  - **A floor for the whole class** (Derived; only its first step, that A = B = 0 makes the whole correction skippable, is Proved; `internal/pouw/llm-relaxations.md` §2). Take the class of additive noise on int8 tensor-core operands, useful output by an exact integer correction, worst-case inputs, under W1. Its skippable share is at least (4 + ρ)/n + c_corr/k, with per-step noise rank ρ ≥ 6, and c_corr ≥ 48 units per output entry for k ≤ 4,681 (80 above). The correction's input-dependent factor sums at least k/16 products, so it needs two or three int8 limbs. Each limb group costs one k16 instruction per output tile, and each group beyond the main accumulator costs an INT32 combine per entry. So D1's (6r + 32)/k is about 2.7× the floor, and D4-s nearly meets it. Even at the floor, with ρ = 6, γ ≥ 1.89% at k = n = 4,096, and 1% needs k ≳ 17,800 (red-team C3). D4-s, at rank 8, gives about 2.0% (1.95% before H5 prices its gather) and 18,700. Changing the correction, the int8 format or the additive form cannot reach γ_0 at LLM shapes; dropping worst-case inputs can.

Not viable, and why:

- **Output-only checks with low-rank noise:** γ ≈ 1 (Lemma 1, part 1).
- **Independent full-rank noise with a separate decode** ([N] direction 2): γ ≥ 1/2 for useful work (Lemma 1, part 2). Full-rank noise itself is not the obstacle. Correlated full-rank noise that cancels inside the checked GEMM (D7) leaves no decode to skip (new-crypto.md §1: only the class of running-sum transcripts fits γ ≤ 1%).
- **Hash-dominated work** (the first draft's D1–D3): excluded by decision 1, since hash calls are free.
- **Pearl's FP8 scheme:** FP8 is outside the domain, and its policy allows at least 5% by design (§7).
- **A keyed SNARK as the work** (the first draft's D5; [KW] Remark 2.3): the work would live in the proof system's hashing and field arithmetic, not in the matmul, and nothing bounds a prover's cost to within 1%.

## 7. Prior work: Komargodski–Weinstein and Pearl

**[KW]**, arXiv 2504.09971v4 (13 Nov 2025), by Ilan Komargodski and Omri Weinstein.

- *Construction (cuPOW).* Rank-r noise on both operands, derived by a random oracle from (σ, A, B). The whole r-blocked transcript of the noised product is hashed (Alg. 6.2/6.4), or each intermediate block serves as a ticket (Remark 2.1). The useful output comes from decoding in O(n²r).
- *Definitions.* Def. 5.1 bounds success by `max(C·(t'/t)·ε, 2^-λ)` for some constant C, against provers "with polynomial time preprocessing". Def. 6.2 states transcript unpredictability with a constant C "for every iterative numerical algorithm", a class the paper does not define formally.
- *Assumptions.* 6.3: no o(n^ω) algorithm multiplies random matrices. 6.4: no algorithm computes all intermediates of a random rank-r product in o(n^(ω_r + 1)/r). Both are asymptotic.
- *Claims and open problems.* KW "conjecture that our protocol has optimal security" and list a PoUW from standard assumptions as open (Problem 3.3). §5.1 is the trivial scheme, where a useless miner is (1 + 1/c)× faster at overhead c. App. A (random rotations, Conjecture A.1, in the word-RAM with O(n³) preprocessing) and Problem 3.2 (better noise) are relevant to D4. App. B gives a Poisson-process definition for mining.
- *Relevance.* KW is the closest prior art. Its Assumption 6.4 is the zero-input case of TT; TT extends it to adversarial inputs and makes it concrete, joint and integer (red-team A8).

**Pearl whitepaper [W]** (Sep 2026): FP8 (E4M3).

- Rank-32 noise lines and NoisyQuantize with δ = 1/2; tickets are hashes of output tiles.
- A jackpot policy with ε_pred = 1/16, ε_tame = 1/64, ε_idle = 1/64, τ_idle = 8 and σ_min = 1.
- Assumption 1: informal quantized-subspace hardness.
- The work model "intentionally excludes the work required for quantization, noise generation, hashing, commitment verification, and memory movement" (§3).
- A state window D ≈ 3 gives up to D-fold preprocessing of the B side (§4.6). The batched and grinding security definitions "must account for" transcript grinding and shared work, but are not given (§4.6).

**Pearl PR #311 [PR]**, "feat(fp8): certificate-v4 + mining": open, not a draft, last updated 27 Sep 12:17Z.

- Since #337 (merged into it on 27 Sep, 07:52Z) the jackpot policy is the "M/Z census" of `zk-pow/src/api/fp8/jackpot_policy.rs`. It keeps entry liveness (τ_idle = 8, ε_idle = 1/64) and the noise floor (σ_min = 1). It sets the unpredictable-summands budget to `floor(k·|I_A|·|I_B|/20)`, which is 5%, down from the whitepaper's 1/16. The tamed-products check is gone.
- δ is now device-dependent (1/2 on Blackwell, 1 on Hopper), and Hopper (H100) support was added.
- The PR deletes the integer miner's noise generation.

**Pearl's integer miner [M]** on `master`, which #311 removes.

- int7 × int7 → int32. The noise rank must be a power of two divisible by 32, and the Go bindings set `MIN_NOISE_RANK = 128`, so Pearl rejects r = 16 (red-team B7).
- E = A_L·A_R, with A_L uniform in [−32, 31] and each column of A_R equal to e_a − e_b, two ±1 entries of opposite sign by construction. So noise entries lie in [−63, 63]; red-team B4 checked the generator (`generate_permutation_matrix`, `matvec_sparse_perm` in `zk-pow/src/circuit/pearl_noise.rs`). KW's Lemma 6.5 (uniform rank-r noise) does not apply.
- Because 1ᵀ·A_R = 0, every depth-r slice of the noise is rank-deficient, not just most (red-team B7; §5 item 2).
- Accumulator tiles are XOR/rotate-folded at k-checkpoints, followed by one keyed BLAKE3 compression per tile.
- Relevance: it is the only deployed instance of KW on an int8 datapath. Its slices are rank-deficient (§5 item 2), and its fold is linear over GF(2) (§5 item 7).

## 8. Corrections

**To the note [N].**

1. **Authors.** [N] calls the paper Komargodski–Schen–Weinstein (KSW). arXiv 2504.09971v4 (13 Nov 2025) and its abstract page list only Ilan Komargodski and Omri Weinstein. The definitions [N] cites (Def. 5.1, Def. 6.2, Remark 2.1, the asymptotic assumption) do match v4.
2. **Decoding can be skipped even when the useful output is checked.** [N]'s default says "Then decoding cannot be skipped" (§'Open questions with proposed defaults'). But the operator chooses the activations, and on degenerate ones the useful output is free, so the decode's share still counts in γ (§5, item 1). [N]'s 5.2% is the whole honest overhead at its shape; under W1, γ there is about 5.4% (§6).
3. **Independent full-rank noise with a separate decode cannot reach γ ≤ 1%.** This is [N]'s direction 2 and the setting of its Theorem 9.1. For useful work γ ≥ 1/2 (Lemma 1, part 2). Correlated full-rank noise that cancels inside the checked product can (D7). Theorem 9.1 remains correct as stated, but its (H) charges only the noised product, a third of the honest cost.
4. **Model of computation.** [N]'s default, counting a multiply-add as 2 operations, is superseded by M_4090 (decision 2). In operation-count models the 1% claim is false (§4.2 (a)): Winograd's trick halves the multiplications, a larger constant than the Strassen level [N] lists.
5. **A transcript does not block in-block Strassen.** [N] says such savings are "blocked only if the checked transcript forces the standard accumulation order at the checked granularity". A transcript fixes only the order of blocks. Inside a block, what blocks Strassen at d = 16 is M_4090's per-word floor (§4.2 (a)).
6. **Unequal units.** [N] Theorem 3.1 assumes equal-work units. Theorem 1 here is the work-weighted form, and it needs work-weighted sampling.

**To the first draft (17:24).** (1) The H100 unit was about 1 fs, not 1 ps. (2) The int8 exactness bound fails at k = 2^17 (now superseded by §3.2's int7 bounds). (3) FP8 allowances are 5% under PR #311, or 6.25% under the whitepaper, not about 6%. (4) The charging barrier and the hash-based directions D1–D3 are moot under decision 1. (5) Its Strassen figures were operation counts. (6) Mining mode, certificate mode, the H100 unit and the verification-cost property are superseded by decisions 2–4. (7) A reduction with "nothing about the complexity of matrix multiplication" is incompatible with γ ≤ 1% (§4).

**To draft 2 (19:37).** Finding ids are listed under Sources.

1. **§3.1:** memory pricing is W1, not additive (A1: γ ≥ 6–29%) nor free (tt-attacks V1, H1–H4; W1-1), amended at 21:35Z by W1-3 (activations) and W1-4 (texture and b1 `mma` as a named assumption); prices measured: DRAM 345, not 328; SHAKE256 2,100 per int32, not 2,150; capacity 5%, not 11% (A12; `gpu-constants`).
2. **§3.2:** shape domain in Π (A2); at most 2^64 units (B1); W_ref reads the layout, per-epoch work apportioned (B3; Lean correction 2); m ≥ 1 (Lean correction 3); int7 and noised exactness bounds (A14; Lean correction 4); named noise, inner ±1, per-group E_R (A4, A5; tt-attacks §3–§4); running sums at d = r = 16 (A7; tt-attacks §4).
3. **§3.3:** workload before H (Lean correction 1); preprocessing's H calls counted, s independent of (H, σ) (A3); ideal commitments and η = ε_TT(q), replacing `(q + |U|)·2^-λ + ε_A` (A10; Lean correction 7); γ over D (A2); side conditions (A15).
4. **§3.4:** grinding is inside ε_TT(q) and γ_0, not "q times the weak-noise probability" (A10).
5. **§3.5:** Theorem 1 in budget form with the wrapper remark (A9), proved in Lean; the [N] Theorem 7.1 citation fixed (A14).
6. **§4.1–§4.2:** Lemma 1's two wording fixes (A11); the per-word floor at d = 16 replaces the 9-bit-limb, 32-units-per-lookup and 16-units-per-addition arguments (tt-attacks §2, §5; A6).
7. **§4.4:** "weakest sufficient assumption" and "Assumption 6.4 made concrete" withdrawn (A8); Π named; per-word form (tt-attacks §7); Lean correction 8; R_copy (tt-attacks §6).
8. **§5 item 1, §6:** draft 2's r·(1/n + 2/k) held only with E_R shared (A4); recomputed under W1 with limbs, combine, noising, group and per-epoch shares (A4, B3; `llm-shapes` §3): milestone γ ≈ 0.85%, not 0.7–0.8%; times from measured rates (0.058 s GEMM, 6.3–7.0 s SHAKE256).
   - *Sources disagree.* The change list and `llm-shapes` §1 give 0.77% (0.72% refined; 0.96% at d = r = 32), which is the per-unit count only. The red team's machine-checked recount (B3) adds the per-group product (0.024%) and the per-weight share at 2^16 rows (0.055%), and prices packing and B + F at 20 units per entry, not `llm-shapes`' 16, which holds only if Y is defined on the biased operand. That gives 0.851%, and 1.09% at d = r = 32 by the same formula. The coordinator's 21:35Z entry names the recount for §5 and §6, so it is used.
9. **§5:** items 10–13 new (A1; tt-attacks V1, H1–H4, V3, §2; W1-1, W1-2; B8); Strassen's c = 8–14 with IADD3 (A6), 4–7 with FP32 adds (tt-attacks §5), so "width at most 128" is withdrawn; slice rank (A5, B7); linear folds broken by commutation (`llm-shapes` §2).
10. **§6:** LLM shapes cannot reach 1% (`llm-shapes` §1); D2's fold costs 8–32 per checked value, not 16/r per MAC (`llm-shapes` §2; A6); D5 fails (`llm-shapes` §5); D4 is the open direction.
11. **§7:** Pearl's range [−63, 63] is correct, Lean correction 5 withdrawn (B4); every Pearl slice is rank-deficient, and Pearl needs rank ≥ 128, not R ∈ {64, 128} (B7).
12. **§9:** questions 9.1–9.6 decided; 7–9 new.
13. **W1 amended by H5** (tt-attacks, 22:05Z; wording tightened by red-team phase E): every instruction whose address, guard or enclosing branch depends on data, implicit flows included, costs 16 per lane per 32-bit word. Without the rule, memory computes any function for free and TT is false for every Π. The group rule on E_R stays load-bearing.
14. **After the red team's review of draft 3:**
    - D constrains the layout as well as the shapes, and the verifier rejects declarations outside D (C1);
    - the summary's packing term is 20/n, as in §5 (C2);
    - the class floor at ρ = 6 is 1.89% with 1% at k ≳ 17,800, not 1.95% and 18,700 (C3).

## 9. Questions for Daniel

**Decided on 27 Sep** (draft 2's questions 9.1–9.6, each at its default):

1. **Probability accounting:** a tail bound at every budget; online work only; free preprocessing; free hash calls, counted in q (§3.4).
2. **Degenerate inputs:** the requirement is worst case over all weights and activations, degenerate ones included (§3.3).
3. **Operand range:** int7 useful operands, with noised operands on the int8 datapath (§3.2).
4. **Hashing overhead:** about 130× for milestone 1 only (131× at d = 16, §6).
5. **The named conjecture:** TT(0.5%) is the single named hypothesis, to be backed by a falsification benchmark on a 4090 (§4.4).
6. **Admissible hardware:** RTX 4090 adversaries only (§3.1).

**Decided on 28 Sep** (the questions raised by the campaigns, each accepted at its default):

7. **The accounting W1** (§3.1). Instructions are priced per instruction at the measured rates, oblivious online data moves are free, data-dependent accesses and branches cost 16 per lane, and pre-salt and supplied bytes are priced at first fetch, except the operands of correct units. It is the only accounting found that avoids both the 6–29% floor of additive memory pricing and the tabulation attacks of free memory (§5 items 10 and 11). The coordinator amended it at 21:35Z with red-team W1-3 (activations are free on first fetch only for a correct unit) and W1-4 (excluding texture filtering and b1 `mma` is a named assumption until they are priced). *Decided (28 Sep): W1 as amended is the cost model.*
8. **LLM shapes under worst-case inputs.** D1 cannot reach 1% at LLM shapes at any hashing overhead (§6). The options:
   - keep worst-case inputs, target large shapes for milestone 1, and treat LLM shapes as research (D4);
   - relax to approved weights (R-w): B is the approved model's weights, committed in advance and checked once at approval, so the weight noise can be dropped and the decode shrinks to E_L·(E_R·B);
   - relax to chain-consistent activations (R-a): the approved model computes the activations from committed inputs that the prover does not choose, and the verifier checks each sampled unit's output against the next unit's committed input, so the decode is credited. This rests on a model-specific heuristic and on an extended TT that credits the decode. The inputs must not be the prover's: a prompt of one repeated token keeps every row identical.

   γ at d = r = 16 and 131× hashing in every cell, conservative / refined, with m = 4,096 (`internal/pouw/llm-relaxations.md` §1, Derived):

| (k, n) | Worst case | R-w | R-a |
|---|---|---|---|
| (4096, 4096) | 4.62 / 3.97% | 2.43 / 1.76% | 1.26 / 0.50% |
| (3584, 3072), Kimi-K3 expert | 5.38 / 4.52% | 2.84 / 1.95% | 1.51 / 0.50% |
| (14336, 4096), Llama-3-8B down | 2.54 / 1.87% | 1.62 / 0.95% | 1.27 / 0.50% |
| (7168, 7168) | 2.91 / 2.53% | 1.62 / 1.24% | 0.94 / 0.50% |
| (65536, 65536), milestone shape | 0.79 / 0.75% | 0.69 / 0.65% | 0.55 / 0.50% |

   Approving the weights roughly halves γ but leaves LLM shapes above 1%. Only R-a reaches γ ≈ γ_0. Under worst-case inputs, the best design found (D4-s, §6; safe at d = 16 with one fix) lowers γ to about 2.0% at 4,096² (the class floor is 1.89%), and reaches 1% for k ≳ 18,700.
   *Decided (28 Sep): milestone 1 keeps worst-case inputs, and transformer shapes are research (D4, and now NCP, D7). R-a is to be revisited when a workload with committed, prover-independent inputs is in view.*
9. **Checked depth: d = r = 16 or 32.** At 16: 131× hashing, about 1.3× real time for the accumulator reads, and TT has the per-word form (§4.4). At 32: 66× hashing and 1.01–1.04× reads, but TT loses its per-word tightness, FP32 adds bring Strassen to break-even (§5 item 2), and γ ≈ 1.09% on the milestone domain (0.96% in `llm-shapes` §1, which omits the per-group product and the per-epoch share), so it misses 1% at m = 2^12. *Decided (28 Sep): d = r = 16.*

10. **Full-rank noise (added 28 Sep; decided 01:23Z).** NCP (D7) is the construction that reaches γ ≤ 1% at transformer shapes under worst-case inputs (details in [new-crypto.md](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/docs/pouw/new-crypto.md) §5). *Decided, all three at their defaults:*
    - NCP is the full-rank-noise construction, with TT_NCP(0.5%) as its named conjecture. It is the main candidate for transformer shapes, and D1 is kept as the baseline.
    - About 400× hashing at checked depth 16 is accepted for the first build.
    - About 3× honest arithmetic is accepted.
11. **Sub-word extraction in W1 (decided 28 Sep 03:35Z).** Daniel decided that W1 prices sub-word extraction like PRMT, at 16 units per word, instead of treating byte-granular oblivious moves as free (§3.1). Its effects:
    - The adversary's scalar-pipe route can no longer pack two products into one FP32 instruction. The multiplicative-complexity assumption A1 behind Theorem D needs only c = 2, about 2.7× below the best known algorithm ([milder-assumptions.md](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/docs/pouw/milder-assumptions.md) §2.4).
    - On the honest side, NCP's permutation P must move whole 4-entry words to stay free. With a word-granular P, γ at 4,096² is about 0.69% (was 0.66%), and 0.51% at the milestone shape ([new-crypto.md](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/docs/pouw/new-crypto.md) §2).
    - Milestone 1's reference already priced its packing as PRMT, but not the int8 limb split of the two wide decode intermediates X1 = (A + E)·F_L and G_g, which the red team found (Phase 7, P7-4). Pricing it raises Ω* from 1 + 232/2^16 to 1 + 233/2^16; γ stays 0.85% (0.8525%). The Lean record `m1Wref` is being updated.
12. **NCP's checked values and P (decided 28 Sep 07:40Z by the coordinator with the red team, Phase 10; raised by the PoUW MVP).**
    - NCP's checked values are route U's accumulator: C^U_t = −β·colsum(Y) + Σ_{l < 16t} (X + β)·Y mod 2^32, with β = 128. The final value is A·B. The earlier definition was the unbiased running sums.
    - C^U differs from the unbiased sums by public per-weight data, so every bound proved mod V₀ transfers. The named conjecture TT_NCP(0.5%) is restated over C^U.
    - This keeps γ at the signed route-U figures: 0.694% at 4,096², 0.887% at n = 2,048 and ≤ 0.995% on the MVP's domain. The unbiased sums would give γ = 1.08% at n = 2,048.
    - β = 129 (20 units, γ 0.823% at n = 2,048) is allowed once the kernel's SASS confirms the IADD3 it needs.
    - The word-granular P becomes v1.1, a second repair enforcing MinRank's hypothesis (c). It is unchanged at k = 4,096. Details: [new-crypto.md](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/docs/pouw/new-crypto.md), last section.

## Sources

- Campaign reports of 27 Sep 2026, in the project store, cited by finding id:
  - `internal/pouw/red-team.md`: phase A findings A1–A15 (draft 2), phase B findings B1–B8 (the Lean statements), and W1-1 to W1-4 (the accounting).
  - `internal/pouw/tt-attacks.md` with `internal/pouw/tt-attacks-sim.py`: verdicts V1–V6, holes H1–H4 in W1, and §2–§7; "(Sim)" figures come from the script.
  - `internal/pouw/llm-shapes.md`: §1–§6 (the Pareto frontier, folds, the honest reference term by term).
  - `internal/pouw/gpu-constants.md`: measured RTX 4090 prices; run ids `r20260927-…` in the evidence store, campaign `pous-pouw`.
  - `lean/submissions/pouw/`: `NOTES.md` (status, proposed corrections 1–11), `STATEMENTS.md`, and the pinned theorems in `Pouw/Pinned.lean`.
  - `internal/pouw/coordinator-inbox.md`: the working decisions (W1 final wording, 21:21Z).
- [N] "Sparse verification for compute transparency: results, proofs, and the PoUW problem" (Dan Reuter, 14 Sep 2026), [store copy](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/internal/pouw/sparse-verification-note.md). Cited by heading and theorem number.
- [F] Notion, [FASR Work Test (Daniel Reuter)](https://app.notion.com/p/FASR-Work-Test-Daniel-Reuter-3bf399515d9e812a9ffff80b5c27b73d). Fetched 27 Sep 2026; the page was last edited 17 Aug 2026.
- [KW] I. Komargodski, O. Weinstein, *Proofs of Useful Work from Arbitrary Matrix Multiplication*, [arXiv:2504.09971v4](https://arxiv.org/abs/2504.09971) (13 Nov 2025).
- [W] Pearl Research, [*Pearl Floating Point Scheme Specification*](https://pearlresearch.ai/Pearl_Whitepaper.pdf) (Sep 2026).
- [PR] pearl-research-labs/pearl [PR #311](https://github.com/pearl-research-labs/pearl/pull/311), "feat(fp8): certificate-v4 + mining", as of 27 Sep 2026, 12:17Z. The policy is `zk-pow/src/api/fp8/jackpot_policy.rs` on branch `fp8-scheme`.
- [M] Pearl `master`: `miner/miner-base/src/miner_base/noise_generation.py` (the noise factors), `zk-pow/src/circuit/pearl_noise.rs` (the generator the red team checked) and `miner/pearl-gemm/csrc/gemm/pow_utils.hpp` (the XOR/rotate fold and BLAKE3 compression).
- [Ada] NVIDIA, [*NVIDIA Ada GPU Architecture*](https://images.nvidia.com/aem-dam/Solutions/geforce/ada/nvidia-ada-gpu-architecture.pdf), whitepaper V2.02, appendix table, RTX 4090 column.
- Lower bounds and algorithms:
  - J. M. Landsberg, "New lower bounds for the rank of matrix multiplication", SIAM J. Comput. 2014.
  - R. Raz, "On the complexity of matrix product", STOC 2002.
  - M. S. Paterson, "Complexity of monotone networks for Boolean matrix product", Theor. Comput. Sci. 1975; K. Mehlhorn, Z. Galil, "Monotone switching circuits and Boolean matrix product", Computing 1976.
  - S. Winograd, "A new algorithm for inner product", IEEE Trans. Computers 1968.
  - V. Strassen, "Gaussian elimination is not optimal", Numer. Math. 1969.
  - V. L. Arlazarov, E. A. Dinic, M. A. Kronrod, I. A. Faradzev, "On economical construction of the transitive closure of a directed graph", 1970 (the Four-Russians method).
  - R. Williams, "Matrix-vector multiplication in sub-quadratic time (some preprocessing required)", SODA 2007; K. G. Larsen, R. Williams, "Faster online matrix-vector multiplication", SODA 2017.
  - M. Ball, A. Rosen, M. Sabin, P. N. Vasudevan, "Proofs of work from worst-case assumptions", CRYPTO 2018.
