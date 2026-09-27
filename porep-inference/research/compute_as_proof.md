# Compute-as-proof: can verified inference throughput replace memory-hardness?

Agent: compute-as-proof (overnight campaign 2026-09-02). Status: complete (2026-09-03 01:10).
Sections 1-5 are in the order they were written (dated); the summary below was written last.
Scripts and generated tables live in `research/compute_as_proof/` (`bandwidth_model.py` ->
`tables.md`; `fingerprint_check.py`). No GPU measurements; every number is a roofline estimate or
a published figure, and the uncertainty that matters most is called out in Section 4.2.

## Summary / recommendations

**Question.** Can verified inference throughput replace memory-hardness as the proof that weights
and KV are resident in HBM, at ~0 decode overhead?

**Short answer.** Half yes. The *bandwidth* half of the idea is right and is in fact what the PoRep
design was already relying on without saying so; the *verified-inference* half is the wrong tool
for residency and the right tool for a different job (authenticity). Separating the two gives a
design with ~0.3-1% runtime overhead and a stronger, per-GPU residency guarantee than PoRep's
chunk challenges, at the price of a trusted on-node challenger that holds secrets and ~1% of the
fleet in trusted verifier GPUs.

**Findings.**

1. *Throughput bounds relocation, not recomputation, and that is enough.* For data the workload
   reads every step, "recompute instead of store" is not an available attack: weights are
   incompressible public data, and regenerating even 0.1% of a batch's KV costs > 100x the step's
   compute budget (T3). Memory-hardness only ever protects data that is *not* read. Encoding
   weights and live KV with PoRep (5-8x decode cost) buys nothing under this threat model.
2. *The pure throughput argument gives eps <= (1 + delta) BW_alt/(eta BW_HBM)*: ~3% on H100 (PCIe
   DRAM path) and ~10% on GB200 (NVLink-C2C to Grace LPDDR5X) at 30% slack, 5-25% at realistic
   slack; worse when decode is compute-bound (short context, B >= 500); aggregate across GPUs
   (consolidation of two GPUs' batches onto one is invisible at short context); and requiring a
   per-step roofline model of the workload, a per-turn nonce for freshness, and a separate filler for
   empty HBM. Large-batch weight streaming from DRAM is never hidden in practice: the batch at which
   compute would cover it (B* ~ 3,500-14,000 tokens/step/GPU) exceeds what HBM capacity allows for
   KV (T2). Small-batch KV is the *easiest* case (one 80K sequence reads 3 GB per 30 ms step).
3. *PoRep's own chunk challenges do not distinguish HBM from a DRAM mirror.* 64-B chunks + Merkle
   paths at 1e7/s are ~7 GB/s and ~5 us latency, both within PCIe/C2C; a GB200 superchip has 480 GB
   of LPDDR5X. The HBM-vs-DRAM distinction in the PoRep design also comes from the workload's
   throughput. Only a challenge that reads *more bytes within the deadline than any non-HBM path can
   deliver* binds data to a specific GPU's HBM.
4. *Verification options.* (a) Sampled recompute and (b) TOPLOC commitments are the only things
   that bind KV; both need trusted GPUs (verifier cost ~0.85x the prover's per turn at 80K context
   -- TOPLOC's "100x faster validation" collapses when attention dominates), ~0.8% of the fleet at a
   1% sampling rate. (c) Secret-precomputed Freivalds (u = W r, 2 GB of verifier state) binds the
   linear layers' weights with ~0 verifier cost and is hardware-feasible, but cannot bind attention
   over KV and proves nothing about location. (d) PoSW/VDFs give lower bounds on time; residency
   needs upper bounds; the only useful residue is "fresh randomness must enter the context".
5. *Recommended design (Section 4):* plaintext weights and KV; residency by a **timed compact proof
   of retrievability** (Shacham-Waters private PoR with a 2-10%-of-HBM random challenge set and an
   HBM-bandwidth deadline; one int8 GEMV on the prover, 61-bit MAC check on the verifier):
   eps <= ~1% per GPU on GB200 (0.2% on H100) at 0.3% of HBM time (T4); **filler = verifier-secret
   random data**, no memory-hardness needed; **sampled model execution at ~1%** solely to bind
   committed KV pages to real declared sequences (laundering otherwise capped at the honest KV write
   rate, ~50 MB/s per GPU). Prover overhead ~0.3-1%; verifier: ~1 GB/s KV ingest per node,
   372 MB of tags per GPU (or none with PRF-offset tags), ~20 ms of CPU per challenge, plus ~1% of
   the fleet as trusted GPUs.

**Assumptions that carry the design.** A tamper-resistant on-node challenger holding secrets
(key compromise = total break; PoRep's public challenges have no such point -- mitigate by
rotation, per-GPU keys, or the SIS/Ajtai publicly verifiable variant); attested GPU model and a
bounded set of non-HBM tiers (the security parameter is BW_alt/BW_HBM, which grew from 1.9% on H100
to ~5.6% on GB200 and will grow with NVLink-attached memory -- compensate with larger challenges);
p99.9 response jitter of a high-priority fingerprint kernel under decode load <= ~0.3 ms (unmeasured;
the single most important measurement to make); ~1% of the fleet as trusted GPUs; a gateway that
stamps a per-turn nonce and logs tokens; a declared, preallocated HBM map.

**Residual risks.** The declared workspace (~3% of HBM) is unproven and a memory-light,
compute-heavy covert job (a sub-GB model trained in the workspace, or state streamed from DRAM at
450 GB/s) is invisible to *any* memory-residency scheme -- that is compute accounting's job
(veritor). Laundering of covert bytes as KV is rate-capped and detected fleet-wide within an hour
at a 5% fraction but could persist for hours at sub-GB scale on a small fleet. Sparse/linear
attention models need far less KV in HBM, weakening the premise that the workload *should* fill it
(the map-based design still fills HBM, with filler). If the verifier must be public (no secrets),
the memory-hard filler and DRG line become necessary again -- that is the setting where the
campaign's PoRep work belongs.

**Recommendations.** (1) Stop encoding weights and live KV. (2) Use the campaign's remaining H100
time to measure the response-time distribution of an int8-tensor-core fingerprint GEMV over 8-18 GB
launched at high stream priority under a vLLM decode load (p50/p99/p99.9 vs idle) -- this decides
eps_max. (3) Keep the DRG/PoS work explicitly as the public-verifier fallback. (4) Size the
TOPLOC/inference_verification machinery at ~1% of conversations as the authenticity (and
compute-accounting) layer and calibrate an fp8 KV-page tolerance on real hardware. (5) Put the
per-turn nonce, the token log and the KV write stream into the gateway design now.

---

## 1. Framing and the bandwidth model (2026-09-02 23:05)

### 1.1 The claim being tested

Decode-phase inference reads every (active) weight byte and every KV byte of every active sequence
once per step. If a verifier (i) can be convinced that the emitted tokens were produced from the
committed weights W and the committed KV of each sequence, and (ii) trusts a clock, then a step time
t_step implies that (W + K) bytes were delivered to the SMs within t_step, i.e. a bandwidth of
(W + K)/t_step. If that number exceeds what any non-HBM tier can deliver, the data must have been in
HBM. Residency would then be proven by the workload itself, with no encoding and no decode overhead.

Notation used throughout:

* W = bytes of weights a GPU must read per decode step (its shard; for MoE at large batch this is
  essentially all of its experts, see 1.3).
* K = sum over active sequences of ctx_i x kv_bytes_per_token = KV bytes read per step.
* B = sequences (tokens) per step per GPU; t = step time; tokens/s = B/t.
* BW_HBM = HBM bandwidth; BW_alt = aggregate bandwidth of every tier that could substitute for HBM
  *capacity* (host DRAM over PCIe or NVLink-C2C, a Mooncake DRAM/SSD pool over RDMA). Peer-GPU HBM
  over NVLink is *not* capacity-creating (every peer's HBM is itself claimed and challenged), so
  NVLink is excluded from BW_alt except where noted.
* eps = fraction of the claimed (W + K) that is *not* in HBM.

Hardware numbers (per GPU), from CONTEXT.md and vendor specs:

| | H100 SXM (HGX) | GB200 (NVL72) |
|---|---|---|
| HBM capacity / bandwidth | 80 GB / 3.35 TB/s | 186 GB usable / 8 TB/s |
| Host DRAM path | PCIe Gen5 x16: 64 GB/s peak, ~50 GB/s achieved | NVLink-C2C 900 GB/s bidirectional = 450 GB/s per direction; Grace LPDDR5X ~512 GB/s per superchip shared by 2 GPUs (~256 GB/s each when both stream) |
| RDMA to a KV pool | 1x 400G CX-7 per GPU: 50 GB/s (shares the PCIe x16 with host traffic) | 1x 800G CX-8 per GPU: 100 GB/s |
| BW_alt used below | 50-64 GB/s (PCIe + NIC share one x16) | 350-550 GB/s (C2C limited by LPDDR share, + NIC); nominal 450 |
| Peer NVLink (not capacity-creating) | 450 GB/s per direction | 900 GB/s per direction |
| Dense tensor peak | bf16 990 TFLOPS, fp8 1979 | bf16 2.5 PFLOPS, fp8 5, fp4 10 |

BW_alt/BW_HBM is the number that will matter: **1.5-1.9% on H100, ~4.4-6.9% on GB200**. Everything
below is a multiple of it.

### 1.2 The core inequality

Suppose the honest step is memory-bound, t = (W + K)/(eta_mem BW_HBM) with eta_mem the achieved
fraction of peak (0.6-0.9 for decode kernels). An adversary that holds a fraction eps of (W + K)
in a slower tier needs eps (W + K)/BW_alt extra seconds unless it overlaps that fetch with the HBM
reads (it can: the fetch is independent of the SM work), so the step takes
max(t, eps (W + K)/BW_alt). For the adversary to be *indistinguishable from an honest step that
is a factor (1 + delta) slower than roofline*,

    eps <= (1 + delta) * BW_alt / (eta_mem * BW_HBM).

With delta the slack the verifier must grant for kernel inefficiency, scheduling gaps, all-to-all
waits, and so on. Plugging in:

| | H100 | GB200 |
|---|---|---|
| eta_mem = 0.8, delta = 0 (idealised) | 1.9-2.4% | 5.5-8.6% |
| eta_mem = 0.7, delta = 0.3 (realistic slack) | 3.5-4.4% | 10-16% |
| delta = 1.0 (operator allowed 2x roofline) | 5.4-6.8% | 16-25% |

So the *pure* throughput argument caps eps at a few percent on H100 and ~10% on GB200, and the cap
is proportional to how much slack the verifier grants. It is never "eps -> 0"; it is "eps <= a
hardware ratio times the tolerated inefficiency". It is also an *aggregate* bound over (W + K):
the adversary can spend its eps budget on weights or on KV as it likes.

Two regime questions from the task statement are answered by the same inequality:

* **Large-batch weight amortisation.** Streaming *all* weights from the slow tier is hidden only when
  the step is compute-bound long enough: 2 P_active B / (eta_c FLOPS) >= W / BW_alt, i.e.
  B >= B* = (W/BW_alt) eta_c FLOPS / (2 P_active). For dense bf16/fp8 models the ratio W/P_active
  is 1-2 bytes/param and B* = eta_c FLOPS/(2 BW_alt) x bytes/param, which is B* ~ 1,500 tokens/step
  per GPU at NVLink-class BW_alt (450 GB/s) and ~14,000 at PCIe-class (50 GB/s), independent of
  model size and TP degree. For Kimi-K2.5-class MoE the ratio W/P_active per GPU is ~2.5 bytes/active
  param (each GPU reads all its experts but a token uses 8/384 of them), so B* ~ 16,000-23,000 on
  GB200. HBM capacity for KV caps B far below these numbers in every realistic deployment (B <= 35
  at 80K context on GB200; B <= 256-512 by `max_num_seqs` in chat serving), so **weights can never be
  streamed from DRAM without a visible slowdown** -- the "keep the weights in DRAM at batch 256"
  worry does not materialise. Section 1.3 has the numbers.
* **Small-batch KV.** Per-sequence KV reads are the *easiest* thing to bound, not the hardest: at
  80K context one sequence's KV is 2.8-3.0 GB (Kimi-K2.5 fp8 MLA) and is read every 20-30 ms, i.e.
  100-150 GB/s *per sequence*. Two sequences' KV already saturate PCIe; one saturates the RDMA NIC.
  The bound on eps is the same aggregate inequality; the question is only whether the verifier can
  tell how much K there is (Section 3).

### 1.3 Numbers for the target workload

Model: Kimi K2.5 (1.04T total, 32B active, 61 layers, 384 routed + 1 shared expert, top-8, MLA with
kv_lora_rank 512 + rope 64 -> 576 values/token/layer; 35 KB/token in fp8, 38 KB/token including the
block scales the vLLM blog implies at 3.8 GB/100K). Routed experts NVFP4 (0.5625 B/param incl. E4M3
block scales): 570 GB; attention + shared expert + dense layer + embeddings ~9.3B params, assumed fp8:
9.3 GB. Decode DP8+EP8 (vLLM x Mooncake blog): each GPU holds 1/8 of the routed experts (71 GB) and
all attention/shared weights (9.3 GB) = **80 GB weights per GPU**, leaving ~100 GB for KV after
~6 GB workspace, i.e. **B <= 33 sequences at 80K context**.

Expert coverage per step: 8 GPUs x 32 tokens = 256 tokens pick 8 of 384 experts each; the expected
number of distinct experts touched per layer is 384 (1 - (1 - 8/384)^256) = 382 (99.5%), so every
GPU reads essentially all of its 71 GB of experts every step. With B = 32 at 80K:

    W = 80 GB, K = 32 x 80,000 x 35 KB = 90 GB (97 GB at 38 KB/token)
    memory time at 8 TB/s: 21-22 ms
    attention FLOPs (absorbed MLA): 2 x 64 heads x (576 + 512) x ctx x 61 layers = 8.5 MFLOP x ctx
        = 680 GFLOP/token -> 22 TFLOP/step; at ~50% of 2.5 PFLOPS bf16 -> ~17 ms (overlaps only partly)
    step ~ 22-30 ms -> 1,070-1,450 tokens/s/GPU; implied bandwidth 5.7-8 TB/s

Pure-throughput eps bound at delta = 0.3: 450 GB/s x 0.025 s x 1.3 / 170 GB = **8.6%**; with the
LPDDR-limited 256 GB/s: 4.9%. On an H100 node serving Llama-3.1-70B fp8 TP8 at 80K context
(B <= 43, W + K = 79 GB/step, t ~ 24 ms) the same bound is 64 GB/s x 0.024 x 1.3 / 79 GB = **2.5%**.

Interpretation: if the verifier can (a) pin the workload's byte count per step and (b) verify that
the step time is within 30% of roofline, plaintext weights + plaintext KV are already "eps <= 3-9%
hard" against relocation to DRAM, with zero encoding. The PoRep target in CONTEXT.md (eps = 0.1 at
5-8x decode cost, or eps -> 0 at l = 2) is met or beaten at eps = 0.1 -- but not at eps -> 0, and
only under (a) and (b), whose cost and fragility are the subject of Sections 2-3.

### 1.4 What the throughput argument cannot do (preview)

Three gaps, each treated later:

1. **Recomputation vs relocation.** The argument bounds *relocation* (data in a slower tier). It does
   not need to bound *recomputation* because neither weights (incompressible public data) nor active
   KV (regenerating eps of 80K tokens of KV costs eps x 5-27 PFLOP per sequence per step, vs a
   ~2-4 PFLOP/s budget for the whole step) can be recomputed on the fly. This is why memory-hardness
   is unnecessary *for the data the workload reads every step*: the workload's own read is the
   proof of storage. Memory-hardness only ever mattered for data that is *not* read.
2. **Unused capacity.** At B = 8 the KV region is 3/4 empty and honest; nothing about throughput
   proves anything about empty HBM. A filler is required, and Section 4 argues it needs no
   memory-hardness either when the challenger is a trusted on-node device.
3. **Per-GPU attribution.** Throughput is a fleet-level quantity. In the weight-dominated regime
   (short contexts) two GPUs' batches can be consolidated onto one with almost no change in step time
   (t ~ W/BW_HBM is flat in B), freeing the other GPU's HBM entirely while the token stream "from"
   both GPUs looks honest. Only a challenge that a specific GPU must answer from its own HBM fixes
   this; Section 4 gives one with ~1% overhead.

### 1.5 Model output (research/compute_as_proof/bandwidth_model.py, table T1/T2)

Roofline model: eta_mem = 0.8 of HBM peak; compute at 0.5 of dense bf16 peak (conservative -- NVFP4
experts and fp8 attention would run faster, which shortens t and *tightens* every eps bound below);
step = max(t_mem, t_comp) + 0.2 min(.,.). "fits" = W + K + workspace <= HBM.

| config | B | ctx | W/step | K/step | t | tok/s/GPU | implied BW | eps d=0 | eps d=0.3 | eps d=1 |
|---|---|---|---|---|---|---|---|---|---|---|
| Kimi-K2.5 NVFP4, GB200 DP8+EP8 | 32 | 80K | 80 GB | 90 GB | 30 ms | 1,054 | 5.6 TB/s | 8.0% | 10.5% | 16.1% |
| Kimi-K2.5 NVFP4, GB200 DP8+EP8 | 8 | 80K | 80 GB | 22 GB | 17 ms | 471 | 6.0 TB/s | 7.4% | 9.7% | 14.9% |
| Kimi-K2.5 NVFP4, GB200 DP8+EP8 | 128 | 8K | 80 GB | 36 GB | 21 ms | 6,139 | 5.6 TB/s | 8.1% | 10.5% | 16.2% |
| Kimi-K2.5 NVFP4, GB200 DP8+EP8 | 512 | 2K | 80 GB | 36 GB | 37 ms | 13,912 | 3.2 TB/s | 14.3% | 18.5% | 28.5% |
| Kimi-K2.5 NVFP4, GB200 DP8+EP8 | 1500 | 500 | 80 GB | 26 GB | 85 ms | 17,600 | 1.3 TB/s | 36% | 47% | 72% |
| Llama-3.1-70B fp8, H100 TP8 | 16 | 80K | 8.8 GB | 26 GB | 13 ms | 1,197 | 2.6 TB/s | 2.4% | 3.2% | 4.9% |
| Llama-3.1-70B fp8, H100 TP8 | 256 | 8K | 8.8 GB | 42 GB | 21 ms | 12,158 | 2.4 TB/s | 2.7% | 3.4% | 5.3% |
| Llama-3.1-70B fp8, H100 TP2 | 64 | 2K | 35 GB | 10 GB | 19 ms | 3,372 | 2.4 TB/s | 2.7% | 3.4% | 5.3% |
| Llama-3.1-70B fp8, H100 TP2 | 512 | 500 | 35 GB | 21 GB | 78 ms | 6,572 | 0.7 TB/s | 8.9% | 11.5% | 17.7% |

Weight-streaming threshold B* (all weights from BW_alt hidden by compute) vs the largest B that fits:

| config | W/GPU | W/BW_alt | B* | max B @80K | @2K | @500 |
|---|---|---|---|---|---|---|
| Kimi-K2.5, GB200 | 80 GB | 178 ms | 3,500 (14,000 at fp4 peak) | 35 | 1,424 | 5,697 |
| Llama-70B fp8, H100 TP8 | 8.8 GB | 138 ms | 3,900 (7,700 at fp8 peak) | 40 | 1,638 | 6,553 |
| Llama-70B fp8, H100 TP2 | 35 GB | 552 ms | 3,900 | 6 | 248 | 992 |

Reading the tables:

* In the memory-bound regime (long context, or any B up to a few hundred) the throughput bound is
  a hardware constant: **eps <= ~3% (H100) / ~10% (GB200) at 30% slack**. It does not improve with
  batch, context or model; it only depends on BW_alt/BW_HBM and on the slack.
* In the compute-bound regime (B >= ~500 at <= 2K context) the argument degrades quickly: the step
  is long relative to the bytes read, so the implied bandwidth falls and a 15-70% relocation becomes
  invisible. Pure compute-as-proof is weakest exactly where the workload is compute-bound. HBM
  capacity keeps B below B* for weights, so *total* weight streaming stays visible, but partial
  relocation at these eps levels does not.
* The attention term matters on GB200 with 64-head MLA at 80K (t_comp ~ 19 ms vs t_mem 27 ms): a
  verifier that models the step as "bytes / bandwidth" would grant too little slack and flag honest
  operators, or grant too much and loosen eps. The verifier must model the workload's roofline,
  which means it must know the model, the batch and the context mix every step.


---

## 2. What must be verified, and how (2026-09-02 23:40)

The throughput inequality of Section 1 has two inputs the verifier does not observe directly: the
byte count per step (W + K) and the fact that the emitted tokens were computed *from* those bytes.
Both need the tokens to be bound to the committed weights and committed KV. Four ways to do that,
each assessed on verifier cost, prover overhead, soundness, and whether the on-node hardware
verifier of CONTEXT.md (a Merkle/hash checker at 1e6-1e7 challenges/s) could run it.

### 2.1 What is being bound, precisely

For sequence s at step t the prover claims: "token y_t was sampled from logits computed by model
W over context (x_0..x_{t-1}) whose KV is the committed pages P_s". Any check is against a
*recomputation*, and GPU recomputation is not bit-exact across batch composition, kernel choice,
TP degree or GPU type (Thinking Machines 2025: 80 distinct outputs from 1000 temperature-0 runs;
batch-invariant kernels cost 20-50%). So every practical check is statistical with a tolerance,
and the adversary's room is "any substitution whose effect is inside the tolerance". TOPLOC's
measured margins (Llama-3.1-8B/70B, bf16, k = 128 of the last hidden state every 32 tokens):
honest cross-hardware/TP/attention-kernel variation gives <= 17 exponent mismatches of 128 and
mantissa error mean/median <= 4.2/4; a different model, a different prompt, or fp32-vs-bf16
generation gives >= 38 exponent mismatches (all of 128 for a model swap). Their paper flags that
fp8 vs bf16 generation is *not* reliably separable across hardware, and KV-cache compression was
not tested. That is the frontier of what tolerance-based verification can see today.

### 2.2 (a) Recompute a sample of tokens on a trusted GPU

Verifier holds: the public weights, the full token history of the checked sequence (the prover
must log every prompt and output token; ~10 KB/s per GPU for the agentic trace), and either its
own KV for the sequence (if it has been *following* the conversation from turn 1) or nothing (cold
check = re-prefill the whole context).

Costs (table T5, Kimi-K2.5 at 80K, 2,048 in + 900 out per turn, roofline model):

* prover GPU-time per turn ~2.1 GPU-s (decode share of a B = 32 step x 900 steps + prefill);
* verifier following the conversation (prefill 2,948 tokens against its own KV): ~1.75 GPU-s,
  i.e. barely cheaper than the prover -- at 80K context the attention FLOPs dominate both sides and
  TOPLOC's "100x faster validation" (measured at short contexts on 8B models) shrinks to ~1.2x on
  this workload, 3x for Llama-70B TP8;
* verifier cold check of one turn: 27.6 GPU-s (the 80K prefill is 5 PFLOP linear + 27 PFLOP
  quadratic attention), 13x the prover's turn.

Fleet cost: following a fraction f of conversations costs ~f x (0.85) of the prover fleet in
trusted GPUs (f = 1% -> ~0.8%); cold checks at one per GPU-hour cost 27.6/3600 = 0.8%. The verifier
following 1% of conversations on a node holds 1% x 8 x 33 ~ 3 conversations' KV = ~9 GB -- trivial.
Storage for followed KV is not the constraint; trusted GPU-time is.

Soundness: catches model swap, precision swap (bf16/fp32), prompt/context truncation, wrong
sampling parameters (with the inference_verification Gumbel/STL machinery: revealed exponential
noise makes "was this token sampled from these logits" a calibrated likelihood test), and -- the
property we need here -- **KV inauthenticity**: the verifier's recomputed KV pages must match the
prover's committed pages within fp8-ulp tolerance (the pages themselves are compared exactly
against their commitments; the recompute-vs-page comparison is approximate). Misses: substitutions
inside the tolerance (fp8 vs bf16 weights when the verifier's hardware differs; mild KV
quantization -- untested by TOPLOC), and *speculative decoding with a small draft* (TOPLOC's
stated limitation: the large model produces the checked hidden states, the small model the tokens;
irrelevant to residency since the large model is still run).

Detection power for the residency use (covert data masquerading as KV of a fraction phi of live
sequences): a followed conversation catches it at its next turn with certainty. A GB200 decode node
has 8 x 33 = 264 slots; a turn occupies a slot for ~32 s (900 steps x 30 ms + reload), so ~35,000
turns and ~1,000 new conversations start per node-hour. Following f = 1% of them (~10 per
node-hour) catches phi = 5% within an hour with probability 1 - 0.95^10 = 40% per node, with
certainty across >= 100 nodes, and with > 99.99% within a day on a single node. The *hidden-selection* requirement
is essential: the prover must not learn which conversations are followed. That is automatic if the
verifier ingests *all* new KV pages and all tokens anyway (Section 4 makes it do so for tagging),
because its observable behaviour is then identical for followed and unfollowed conversations.

On-node hardware verifier: cannot run this. It needs trusted GPUs (TEE-attested or owned by the
governance body) at ~1% of the fleet, plus the token log. That is a different trust anchor from the
Merkle checker of CONTEXT.md and is the main cost of the compute-as-proof route.

### 2.3 (b) TOPLOC-style activation commitments

The prover commits to the top-k (k = 128) values/indices of the final hidden state every 32
tokens (258 B; ~8 B/token; 0.5 MB/s per GPU at 60K tok/s fleet-wide -- nothing). Prover overhead: a
top-k over d_model = 7,168 per 32 tokens, ~0. Verifier cost: *identical to (a)* -- the verifier
still recomputes the forward pass; what the commitment buys is (i) the prover is bound *before*
it knows which chunks will be checked, so checks can be retroactive and sparse, (ii) storage of
evidence is 1000x cheaper than raw activations, and (iii) a robust tolerance metric that survived
cross-GPU/TP/kernel variation with zero false positives in the paper. What the verifier must hold:
weights, token history, the 258-B commitments; and the KV of the prefix or the compute to rebuild
it. It does not reduce the need for trusted GPUs, and a hardware Merkle checker cannot evaluate it.

For *residency* the commitment adds nothing that the KV-page commitments of Section 4 don't already
give: the hidden state is a function of the KV, and we commit the KV directly.

### 2.4 (c) Freivalds-style checks of Y = X W against a commitment to W

Classical Freivalds needs W r for a random r, i.e. a full pass over W per check -- as expensive as
one decode token. The useful variant is the *secret precomputed fingerprint*: the verifier draws a
secret r per weight matrix once, computes u = W r (one pass over the public weights: for Kimi-K2.5
that is 384 x 60 experts x (2048 + 2048 + 7168) + attention ~ 2 GB of u-vectors in fp32), and then
checks any revealed (X, Y) pair with ||Y r - X u|| <= tau in O(B (d_in + d_out)) FLOPs -- ~1 MFLOP
for B = 32, d = 7,168. This is the homomorphic-MAC / algebraic-PRF pattern of the verifiable
outsourcing literature (Fiore-Gennaro 2012, Zhang-Blanton 2014), specialised to a verifier that
may see the plaintext matrix once.

* Verifier cost: ~0 per check; 2 GB of state; must refresh r every ~30 checks (each accept/reject
  leaks <= 1 bit about r). Hardware-feasible: it is dot products, not a model run.
* Prover overhead: it must *reveal* X_l and Y_l for the checked (layer, step) -- 2 x 460 KB for
  B = 32 -- and, to make retroactive checks possible, commit (hash) every layer's activations every
  step: 61 x 2 x 460 KB = 56 MB/step = ~2 GB/s of hashing per GPU, ~1-3% of INT32 throughput.
  Alternatively no commitments and only *live* challenges ("reveal layer l of the current step")
  -- the prover then knows which layer is checked but not in advance.
* Soundness: over a field, 1/|F| per check. In floating point it is a tolerance test: a substituted
  W' passes iff ||X (W - W') r|| <= tau. A 4-bit requantisation of fp8 weights perturbs X W by ~3%
  relative; honest cross-kernel noise is ~0.1%; the check separates them, but only at the layer
  level and only for the *linear* layers. **Attention is not a fixed-weight matmul**: scores q K^T
  and the softmax-weighted P V involve the per-sequence KV; a fingerprint K r would have to be
  maintained incrementally by the verifier for every live sequence and layer (it can -- 4 B per
  token per layer -- but softmax is nonlinear and the check does not go through). So (c) can bind
  the *weights* used in the MLP/projection layers with a hardware-feasible verifier, and cannot
  bind the *KV*.
* Residency: none. A correct X W computed from DRAM-resident W passes. (c) is a correctness tool
  that would plug into the throughput argument for the weight part only.

### 2.5 (d) Proof-of-sequential-work binding between consecutive tokens

Decode already *is* sequential work: token t+1 depends on token t through the KV. No additional
binding is needed to prevent parallel shortcuts, and the recompute checks of (a)/(b) verify the
chain. What PoSW/VDF machinery provides is the *opposite* direction -- a lower bound on elapsed
time ("this took at least T"). Residency needs an *upper* bound on time per byte ("this was fast, so
it came from HBM"), which no sequential-work proof can give; it needs a trusted clock at the
challenger and freshness of the inputs. The freshness requirement is real for operator-generated
load: a prover that knows the prompts in advance can compute the whole response slowly from DRAM
and replay the tokens at HBM-consistent intervals. Fix: the challenger injects a fresh nonce token
(or a random request id in a fixed prompt slot) per turn; the response tokens then cannot exist
before the nonce is revealed, and their timing is meaningful. Cost: one token in 2,948 per turn.
So (d) contributes one idea -- fresh randomness must enter the context -- and no cryptography.

### 2.6 Summary of Section 2

| option | verifier holds | verifier cost | prover overhead | binds W | binds KV | residency | hardware verifier? |
|---|---|---|---|---|---|---|---|
| (a) recompute sample | weights, token log, own KV for followed convs | ~f x prover fleet (f = 1% -> 0.8%) | 0 (+ token log) | yes (tolerance) | yes (tolerance) | only via throughput | no: trusted GPUs |
| (b) TOPLOC commitments | as (a) + 8 B/token | as (a); retroactive | ~0 | yes | yes | only via throughput | no |
| (c) secret Freivalds | u = W r, 2 GB | ~0 per check | reveal X, Y; optional 2 GB/s hashing | yes, linear layers | no | none | yes |
| (d) PoSW | -- | -- | -- | -- | -- | wrong direction | -- |

Conclusion: under pure compute-as-proof the *only* thing that binds KV is (a)/(b), which needs
trusted GPUs at ~1% of the fleet, and even then residency comes solely from the throughput
inequality with its 3-10% eps and its slack sensitivity. Section 4 separates the two jobs.

---

## 3. Attacks and what the governance verifier is actually establishing (2026-09-03 00:05)

### 3.1 Three different goals hiding in "the HBM holds this workload"

* **G1 residency**: the committed contents (weights, live KV pages, filler, declared workspace)
  are physically in this GPU's HBM now, so nothing else can be. This is what PoRep's challenges
  aim at.
* **G2 authenticity**: the committed contents are what they are declared to be -- the KV pages
  really are the model's KV for real declared sequences, the filler is verifier-known, the
  weights are the public ones. Without G2, covert data is laundered as "KV".
* **G3 activity (compute accounting)**: the GPU's compute and bandwidth are being spent on the
  declared workload rather than on something else. This is the veritor / PoUW question; residency
  neither gives it nor needs it.

The compute-as-proof thesis proves G1 *through* G3-type evidence (verified tokens per second).
That is indirect, and the indirection is where the attacks live.

### 3.2 Attack: smaller / quantised model, or truncated context, with plausible tokens

Caught by (a)/(b) at TOPLOC's margins for model swaps, prompt/context changes and bf16/fp32 swaps.
The residual is compression inside the tolerance. On the target workload the weights are already
NVFP4 and the KV fp8; the next step down (2-3 bit weights, 4-bit KV) moves activations by several
percent and fails TOPLOC-style thresholds set at the ~0.1-1% cross-hardware noise level. An
adversary who generates its own load does not care about output quality, so detection must come
from the verifier's recompute, not from users; that is what (a)/(b) provide. Residual risk: low
for the target workload; higher for a bf16 deployment where fp8 substitution halves W and is at the
edge of TOPLOC's separability.

### 3.3 Attack: correct tokens, DRAM-resident data, slower steps padded with idle

The verifier sees real tokens at a lower rate. Whether that is a problem depends on which G it
wants:

* For G1 the verifier must enforce t <= (1 + delta) t_roofline(W, K, B, ctx) *per step*, which
  requires it to know W, K, B and the context mix (declared per step, verified by sampling) and to
  model the roofline (Section 1.5 shows the attention term matters). Every unit of slack delta
  loosens eps proportionally: at delta = 1 the bound is 5-7% (H100) and 16-25% (GB200). Honest
  stacks run at 60-80% of roofline with a long tail (all-to-all waits, preemptions, chunked-prefill
  interleaving), so delta ~ 0.5-1 is realistic and **eps ~ 5-25% is what pure compute-as-proof
  delivers in practice**.
* If the verifier instead only requires "declared tokens were real", the padded-idle adversary
  passes and keeps HBM for itself. Low load is indistinguishable from covert use, exactly as idle
  compute is indistinguishable from undeclared compute in veritor's compute accounting.
* At low load the honest operator has empty HBM (B = 8 leaves ~75 GB of the KV region unused on
  GB200). Nothing throughput-based can say anything about it. A filler is needed regardless, and
  once a filler with its own challenges exists, the natural thing is to use the same challenge
  for the workload data (Section 4).

### 3.4 Attack: consolidation (per-GPU attribution)

Two GPUs each declare B = 16 at 80K; one GPU actually serves all 32 (it fits) while the other is
free. Step time on the busy GPU rises from 21.5 to 30 ms (T1) -- a 40% increase, inside a delta = 0.5
slack. At 8K context (B = 64 -> 128) the step goes 18 -> 21 ms, 15%, invisible at any realistic
slack. Tokens are attributed to GPUs only by the operator's say-so; NVLink at 900 GB/s moves the
few-hundred-KB activations anywhere in the rack in microseconds. **Pure compute-as-proof gives a
fleet-aggregate residency statement, not a per-GPU one**, unless every GPU is made to answer
something from its own HBM at HBM speed -- which is a bandwidth challenge, not a throughput
observation (Section 4).

### 3.5 Attack: precompute-and-replay for operator-generated load

Covered in 2.5: without a per-turn nonce in the context, timing proves nothing for prompts the
operator knew in advance. With it, fine. The challenger must sit in the request path (a stamping
proxy); in the agentic setting there is already a gateway.

### 3.6 Attack: faked activation commitments

Commitments are checked by recompute; forging them means predicting the verifier's forward pass,
i.e. doing it. The real loophole is the one in 3.5 (compute it honestly *somewhere*, slowly, and
attach honest commitments): commitments certify the computation, not its location or its time.

### 3.7 Nondeterminism

Not a soundness problem for (a)/(b) -- TOPLOC-style thresholds absorbed every honest
cross-GPU/TP/kernel variation tested -- but it forces the *KV authenticity* check to be
approximate: the verifier's recomputed KV differs from the prover's committed fp8 pages by an ulp
in a few percent of entries (pre-quantisation noise ~1e-3 relative flips fp8 rounding near
boundaries). So the check is: committed pages == revealed pages (exact, cheap, via the page tags of
Section 4) AND revealed pages ~ recomputed pages (fraction of entries off by > 1 fp8 ulp below a
threshold). Requiring bit-exactness would force batch-invariant kernels on the prover at 20-50%
throughput, which would destroy the "zero overhead" premise; the two-stage exact/approximate check
avoids that.

### 3.8 Structural caveat: the premise "decode must read all KV" is a property of today's models

Sparse attention (DeepSeek-V3.2 DSA reads ~2K of 80K positions per query after a cheap indexer
pass), linear-attention hybrids with constant-size state, and further KV compression all reduce K
per step by one to two orders of magnitude. With DSA the honest operator *could* legitimately keep
KV in Grace DRAM (72 MB/token of gathered KV at B = 32 is ~2.3 GB/step, 5 ms over C2C). For such
models the throughput argument for KV disappears and only weights remain anchored -- and so does
the governance premise that KV "should" fill HBM. Any residency scheme must therefore be stated
against the declared memory map, not against an assumed access pattern; Section 4 does that.

### 3.9 Where this leaves pure compute-as-proof

It works, at eps = 3-25% depending on hardware and slack, with ~1% of the fleet as trusted GPUs,
a per-step roofline model of the workload, a per-turn nonce, a filler for empty HBM (unaddressed),
and no per-GPU attribution. That is a weaker guarantee than the PoRep target and a far more
complex verifier -- but at zero prover overhead versus 5-8x. The next section shows that the
zero-overhead property survives while the weaknesses are removed, once the residency job is
separated from the verification job.

---

## 4. Hybrid: separate residency from verification (2026-09-03 00:35)

### 4.1 A finding about the PoRep design first

The PoRep construction's challenges (random chunk + Merkle path, ~1 ms deadline, 10-100 per block
per second, 1e6-1e7/s aggregate) **do not distinguish HBM from host DRAM either**. A 64-B chunk
fetched over PCIe or C2C arrives in 2-10 us, three orders of magnitude inside the deadline, and
the aggregate challenge traffic (1e7/s x ~1 KB of chunk + path) is 1-10 GB/s, deliverable by PCIe.
A GB200 node has 480 GB of LPDDR5X per superchip -- enough to mirror both GPUs' entire encoded HBM
contents. An adversary that keeps the *encoded* blocks in DRAM answers every chunk challenge on
time and uses HBM for something else. What stops it is only that the *workload* then has to read
its encoded weights and KV from DRAM at 450 GB/s, i.e. 15-20x slower -- which is the throughput
argument of Section 1, not the PoRep challenge. So both designs, as stated, rest on the same
throughput observation for the HBM-vs-DRAM distinction. What PoRep adds is "stored, not
recomputed" (proof of space), which for weights (incompressible public data) and live KV (T3:
recomputing eps of a batch's KV costs > 100x the step's compute budget for any eps > 0.1%) rules
out an attack that was never available. **For data the workload reads every step, the 5-8x decode
cost buys nothing that plaintext does not already have.** Memory-hardness is needed only for data
that is *not* read -- and Section 4.3 shows that with a trusted on-node challenger it is not
needed there either.

The one thing that does bind data to a *specific GPU's HBM* is a challenge whose answer requires
reading more bytes within the deadline than any non-HBM path can deliver. Latency cannot do it
(PCIe round trips are ~1-2 us, kernel scheduling jitter ~5-10 us; a deadline cannot be tightened
below ~50 us); bandwidth can.

### 4.2 The residency primitive: a timed compact proof of retrievability

This is Shacham-Waters' privately verifiable PoR (2008: PRF-based homomorphic linear
authenticators; the verifier sends random indices and coefficients, the prover returns one
aggregated block and one aggregated tag) with two changes: the challenge set is a few percent of
the whole store (gigabytes, not kilobytes), and the response has a wall-clock deadline set by HBM
bandwidth. Concretely, with 4 KB pages p = 1..N over the *entire declared HBM map* (weights, KV
pool, filler, workspace excluded):

* **Tags.** Verifier secret s in Z_q^1024 (q = 2^61 - 1), page words m_{p,i} (32-bit). Tag
  t_p = <s, m_p> mod q, 8 bytes per page (0.2% of HBM; 372 MB per GB200 GPU, stored on the
  verifier, or stored on the prover Shacham-Waters style as t_p + PRF_k(p) so the verifier keeps
  only k). Who computes tags: the verifier, from the public weights (once), from the KV stream as
  pages are written (Section 4.4), and from the filler it generates itself.
* **Challenge.** A fresh seed; from it, a random page subset S of size cN (c = 2-10%) and four
  int8 coefficient vectors r^(1..4) over S. Response mu^(j) = sum_{p in S} r^(j)_p m_p as integer
  vectors (4 x 1024 x 64-bit = 32 KB). This is one memory-bound GEMV: 4 fingerprints x 1 MAC per
  byte on the int8 tensor cores (T4: 30 us of compute for 18.6 GB; the read at 90% of 8 TB/s is
  2.6 ms).
* **Check.** For each j: <s, mu^(j)> mod q == sum_{p in S} r^(j)_p t_p mod q. Verifier work:
  |S| + 1024 modular MACs per fingerprint = 18 M MACs for a 10% challenge on GB200 (~20 ms on one
  CPU core; trivially in FPGA/ASIC).
* **Deadline.** honest = |S| x 4 KB / (0.9 BW_HBM) + fixed overheads; deadline = honest + margin.

Soundness (cryptographic): a response with mu' != mu passes with probability 1/q over the secret s;
a prover missing any page p in S can only answer if all four r^(j)_p = 0 (2^-32) since it has no
information about m_p that is consistent with a fresh r (weights are public but must still be
*fetched*, which is the bandwidth case). Standard PoR extractability applies to the "is it stored
anywhere" question.

Soundness (physical): a prover with a fraction eps of the map outside HBM must move eps |S| 4 KB
over BW_alt inside the margin: **eps_max = margin x BW_alt / (c x HBM)**. From T4:

| GPU | c | read | margin 0.1 ms | margin 0.3 ms | overhead @1/s | @10/s |
|---|---|---|---|---|---|---|
| H100 | 2% (1.6 GB) | 0.53 ms | 0.4% | 1.2% | 0.05% | 0.5% |
| H100 | 10% (8 GB) | 2.65 ms | 0.1% | 0.2% | 0.3% | 2.7% |
| GB200 | 2% (3.7 GB) | 0.52 ms | 1.2-1.5% | 3.6-4.4% | 0.05% | 0.5% |
| GB200 | 10% (18.6 GB) | 2.58 ms | 0.2-0.3% | 0.7-0.9% | 0.3% | 2.6% |

The two GB200 columns are BW_alt = 450 / 550 GB/s. Compare Section 1: the same hardware gave eps
~10% by throughput at 30% slack. The fingerprint gives ~1% at ~0.3% overhead, per GPU, with no
model of the workload and no slack parameter other than the timing margin.

Time-multiplexing does not help the adversary: challenges are Poisson, the seed is unannounced,
and there must be **no "prepare" signal** -- a 40 ms warning would let a GB200 swap 18 GB of covert
data out and 18 GB of committed pages in over bidirectional C2C before the seed arrives. A covert
burst of X GB is caught by any challenge that lands during it, with probability ~X/HBM x (challenge
hits) -- at 1 challenge/s and bursts of 100 ms, a persistent covert user is caught within seconds.

Engineering uncertainty (the load-bearing one): the response-time distribution of a
high-stream-priority fingerprint kernel launched under a running decode workload. Decode CTAs
already resident keep their SMs and bandwidth until they retire (tens of us); if the p99.9 spread of
honest response times is ~0.1-0.3 ms the table holds; if it is ~1 ms, eps_max degrades to 2-3% at
c = 10% or the challenge must grow (c = 30%: 7.7 ms read, 0.8% overhead at 1/s, eps_max 0.7% at
1 ms margin). Also to verify: that pausing decode launches for one challenge (~3 ms) is acceptable
as inter-token jitter; that the operator-controlled agent kernel cannot *shorten* the honest time
(it cannot: physics) and that its only degree of freedom, delay, hurts only itself. Measurement on
a real GPU is the first thing to do with the campaign's H100 time.

### 4.3 Filler without memory-hardness

Empty HBM must be filled with something the prover cannot regenerate. A PRNG filler with a public
seed fails (a GPU regenerates xorshift output at ~10 TB/s, faster than reading it), which is why
proof-of-space constructions are memory-hard. With a *trusted on-node challenger* the fix is
trivial: **the filler is random data generated by the verifier from a seed the prover never
sees.** It is information-theoretically incompressible for the prover, so it must be stored; the
verifier computes its tags as it generates it (streaming, once), and can regenerate any page for
spot checks. Cost: pushing the filler to the GPU once (100 GB over PCIe Gen5 ~2 s, or over C2C
~0.3 s) and again whenever the KV region shrinks. The filler needs no DRG, no layers, no hash
agent, and no decode; the PoRep encode/decode machinery is unnecessary for it.

Practical layout: the honest serving stack already preallocates the KV block pool
(`gpu_memory_utilization`), so the map is static: weights | KV pool | workspace | filler, with the
filler sized to whatever the pool does not need at the deployment's target batch. Inside the KV pool,
blocks not currently owned by a live sequence hold *stale* KV whose tags remain valid until a live
sequence overwrites them through the tagged write path (4.4); they are still committed, still
challenged, and cannot be repurposed without a tag update, which the verifier grants only for
writes that belong to a live sequence's expected KV slots.

### 4.4 Authenticity: where compute-as-proof is actually necessary

Residency of *committed* pages does not stop an operator from committing covert data *as* KV pages
of fake or padded sequences (the verifier cannot tell KV from anything else by looking at bytes).
Two controls bound this laundering channel:

1. **Tags are updated only through the KV write path of live sequences.** New KV is produced at
   35 KB/token, 52 MB/s per GB200 GPU at 1,500 tok/s; the prover streams (page, offset, old slice,
   new slice) to the verifier, which updates t_p <- t_p + <s_slice, new - old> (lying about `old`
   only breaks the prover's own tag). Pages loaded from the Mooncake pool carry tags computed by
   the verifier of the node that generated them under a fleet key. A covert job can therefore
   rewrite at most the honest KV write rate, ~50 MB/s per GPU -- 0.0006% of HBM write bandwidth --
   and only into slots the verifier expects a live sequence to write.
2. **Sampled model execution (Section 2.2)** checks that a live sequence's committed pages are the
   model's KV for its logged token history: exact page-vs-tag, approximate page-vs-recompute
   (fp8-ulp threshold). Following f = 1% of conversations from turn 1 costs ~0.8% of the fleet in
   trusted GPUs (one verifier GPU per ~6 decode nodes) and catches a 5% laundering fraction within
   an hour fleet-wide, within a day on any single node; hidden selection is
   automatic because the verifier ingests every KV page and every token regardless. Cold checks
   (27.6 GPU-s per 80K turn) are an occasional backstop for conversations not followed from birth.

This is the residual role of "verified inference" in the design: **not residency, but binding the
committed KV bytes to a declared workload**. It also yields, for free, the G3 evidence (real tokens
from the real model at a measured rate) that a compute-accounting layer would want.

### 4.5 The full protocol and its overhead

Per GPU, steady state:

| component | who | prover runtime cost | verifier cost |
|---|---|---|---|
| plaintext weights, plaintext KV (no encoding) | -- | **0** (vs 5-8x decode in PoRep) | -- |
| KV write stream to verifier (tags) | prover copies 35 KB/token D2H (2x with `old`) | 105 MB/s per GPU, <0.2% of PCIe; no GPU compute | 1 MAC/byte: 0.1 GMAC/s per GPU |
| timed fingerprint challenge, c = 10%, 1/s (Poisson) | GPU reads 18.6 GB + 30 us int8 GEMV | 0.3% of HBM time; one ~3 ms decode pause per second | 18 M mod-q MACs/s per GPU |
| filler = verifier-secret random data | verifier generates + tags once | refill only when the KV pool shrinks (2 s per 100 GB) | one-time |
| tag storage | verifier | -- | 372 MB per GPU (or 0 with PRF-offset tags on the prover) |
| token log + per-turn nonce | proxy | 1 token / 2,948 | ~10 KB/s per GPU |
| sampled recompute, f = 1% followed conversations | trusted GPUs | 0 | ~0.8% of fleet GPU-time (Kimi @80K; 0.3% for Llama-70B TP8) |

Total prover runtime overhead: **~0.3-1% of HBM time plus ~1% of the fleet in trusted verifier
GPUs**, against 5-8x decode slowdown for PoRep on both weights and KV, or ~3-5x for a "PoRep on KV
only" hybrid (KV is 53% of the bytes at B = 32 / 80K, and the encode-on-append of 35 KB/token is
cheap, but every decode step would still decode 90 GB of KV).

Guarantee: with margin 0.3 ms and c = 10%, every GPU holds >= 99% of its declared map (H100: 99.8%)
in its own HBM at every challenge; the declared map covers all of HBM except the declared workspace
(~6 GB, 3%); committed KV pages belong to real sequences of the declared model up to a laundering
fraction that a 1% following rate detects within an hour at phi >= 5%; and the KV-page rewrite
channel is capped at the honest KV write rate.

### 4.6 The other hybrids the task asked about

* **Compute-as-proof for weights + PoRep for KV.** Weights are the *easy* half (public, static,
  read fully every step, tags computable from the public file); KV is where PoRep's decode cost
  lands on the hot path (90 of 170 GB per step at the target point). This hybrid keeps most of the
  cost and none of the per-GPU binding. Not recommended.
* **Challenges that demand the actual activation of a random (token, layer).** The prover returns
  h_l(s, t) on request; the verifier checks it later by recompute. It proves the prover had
  plaintext KV and weights *available* at that moment -- not where they were. A DRAM-resident prover
  computing slowly answers correctly. It adds nothing over (a)/(b) for residency; as a
  live-challenge form of TOPLOC it is a fine authenticity check (2 x 460 KB per challenge) but the
  page-tag route is cheaper and exact.
* **Fingerprint challenge as the matmul itself.** The fingerprint is a GEMV over the HBM
  contents; in the matrix-structure direction of CONTEXT.md one could make the challenge *be* a
  decode-step GEMV over the weights with a challenger-chosen input vector (y = W r for fresh r,
  read all of W in W/BW_HBM). The response then also certifies the weights' values (Freivalds-style
  against u = W r for the verifier's own r), but only for the weight region and only at GEMV
  granularity; the plain page fingerprint covers weights, KV and filler uniformly and is simpler.

### 4.7 A sanity check of the algebra (research/compute_as_proof/fingerprint_check.py)

A CPU simulation of the tag / integer-fingerprint / mod-q check on random pages, including a
prover missing pages, a prover substituting one byte, an incremental tag update with an honest and
a lying `old` slice, and a Shacham-Waters-style PRF-offset tag.

### 4.8 Script output

~~~text
tags for 4096 pages: 0.2s
honest response            -> [True, True, True, True]
missing one page           -> [False, False, False, False] (coeffs of that page: [191, 38, 106, 5] )
one page quantised         -> [False, False, False, False]
incremental update, honest -> [True, True, True, True]
incremental update, lying  -> [False, False, False, False]
PRF-offset tags on prover  -> [True, True, True, True]
random forged response     -> [False, False, False, False]
~~~

The integer-response / mod-q-tag split is what lets the prover run the fingerprint as a plain
int8 GEMV (no modular arithmetic on the GPU) while the verifier keeps 61-bit soundness.

---

## 5. Verdict (2026-09-03 01:00)

**Is there a design where "this HBM holds and serves this workload" is achieved with ~0 runtime
overhead?** Yes, but not the one in the task's framing. Verified inference throughput *by itself*
proves residency only up to eps = BW_alt/BW_HBM times the slack the verifier grants (3-25%), only
in aggregate across GPUs, only for models whose decode reads all of W and K every step, and only
with a per-step roofline model of the workload and ~1% of the fleet in trusted GPUs. The design
that does achieve the goal keeps the zero-overhead property and drops the indirection:

1. Plaintext weights and plaintext KV. No encoding, no decode, 0 overhead. Justified because for
   data the workload reads every step the only attack is *relocation*, never *recomputation*
   (weights incompressible; KV regeneration costs > 100x the step's compute for eps > 0.1%).
2. Residency by a **timed compact proof of retrievability**: Shacham-Waters private PoR with
   GB-scale random challenge sets and an HBM-bandwidth deadline. eps <= ~1% per GPU (0.2% on
   H100) at 0.3% of HBM time (c = 10%, one Poisson challenge per second, 0.3 ms margin). Binds to
   the specific GPU. No workload model, no slack parameter, standard cryptography; the one novel
   assumption is physical (BW_alt/BW_HBM and ~0.3 ms timing jitter).
3. Empty HBM filled with **verifier-secret random data** -- information-theoretically
   incompressible for the prover, no memory-hardness, no DRG, no hash design question.
4. **Sampled model execution** (TOPLOC-style recompute, ~1% of followed conversations, ~0.8% of the
   fleet in trusted GPUs) only to bind committed KV pages to the declared workload, closing the
   "covert data laundered as KV" channel, whose bandwidth is anyway capped at the honest KV write
   rate (~50 MB/s per GPU) by the tagged write path.

Total: ~0.3-1% prover runtime overhead + ~1% of the fleet in verifier GPUs, versus 5-8x decode cost
for PoRep on weights + KV (or 3-5x for PoRep on KV alone), with a stronger residency statement
(per GPU, HBM-specific) than PoRep's chunk challenges give (Section 4.1: they do not distinguish HBM
from a DRAM mirror; that distinction was always coming from throughput).

**Assumptions**

* A trusted, tamper-resistant on-node challenger holding secrets (tag key, filler seed), with a
  ~10 us clock, a PCIe/C2C path to each GPU, ~1 GB/s ingest per node for the KV write stream, and
  the ability to push ~100 GB of filler per GPU at bring-up and on pool shrink. Compromise of the
  key is a total break (PoRep's public Merkle challenges have no such single point); mitigations:
  per-GPU keys, rotation (re-tagging 186 GB takes ~3 s over PCIe), or the publicly verifiable
  variant with SIS/Ajtai homomorphic hashes (prover computes 1024 MACs/byte on writes, ~0.1% of
  tensor throughput; ~40 parallel {0,1}-subset fingerprints).
* Attested GPU model (HBM bandwidth spec sets the deadline) and a bounded BW_alt: host DRAM path +
  NIC. NVLink peers are not capacity-creating. Future NVLink-attached memory pools at ~1-2 TB/s
  would raise BW_alt; the fix is a larger c (30% -> 0.8% overhead at 1/s, eps still <= 1%).
* Response-time jitter of a high-priority fingerprint kernel under a running decode workload
  <= ~0.3 ms at p99.9. Unmeasured; the first thing to test with GPU time.
* Trusted GPUs for sampled recompute (~1% of fleet), a token log and a per-turn nonce via the
  request gateway, and a tolerance for the KV-page authenticity check that passes honest
  cross-kernel fp8 rounding noise and fails >= 4-bit substitutions (TOPLOC shows this for hidden
  states; KV pages need their own calibration).
* A declared, mostly static HBM map (preallocated KV pool), so "everything not weights/KV/workspace
  is filler" is well defined.

**Residual risks**

* Declared workspace (~6 GB, 3% of a GB200) is unproven; a covert job that fits there and streams
  its state from DRAM at 450 GB/s is not excluded. Memory residency does not bound *compute*: a
  ~500M-parameter training job in the workspace at full tensor throughput is invisible to any
  memory-governance scheme; that is compute accounting's job (veritor).
* Laundering channel: covert bytes written as "KV" of live sequences at <= 50 MB/s per GPU into
  expected slots, detected fleet-wide within about an hour at a 5% fraction (f = 1% following);
  a sub-GB covert dataset per GPU could survive for hours at low fractions on a small fleet.
* Models with sparse/linear attention legitimately need far less KV in HBM; the map-based design
  still fills HBM (with filler), so residency holds, but the "workload needs this HBM" premise
  weakens and the honest operator is paying for filler bandwidth (0.3%) rather than serving.
* If the challenger cannot be trusted with secrets (public-verifier setting), the filler must be
  memory-hard again and the tags must be public homomorphic hashes; the PoRep/DRG work is the
  right tool *there*, not here.

**Recommendations for the campaign**

1. Stop encoding weights and live KV; the 5-8x decode cost is buying a property plaintext already
   has under the threat model. Redirect the GPU time to measuring the fingerprint kernel's
   response-time distribution under a vLLM decode load (int8-mma GEMV over 8-18 GB, high-priority
   stream, Poisson launches from the host; record p50/p99/p99.9 of completion vs an idle GPU).
   Note the H100's INT32 budget of ~5 ops/byte makes a CUDA-core fingerprint compute-bound at
   4 columns; use tensor cores.
2. Keep the DRG/PoS line only as the fallback for a public-verifier deployment; state that
   dependency explicitly in its write-up.
3. Treat sampled model execution (TOPLOC/inference_verification machinery) as the authenticity and
   compute-accounting layer, sized at ~1% of conversations, and calibrate an fp8 KV-page tolerance
   on real hardware (the one measurement TOPLOC did not do).
4. Fix the challenger's request-path role (per-turn nonce, token log, KV write stream) in the
   system design now; all three are cheap and all three are load-bearing.

---

## References consulted

* Ong et al., TOPLOC: A Locality Sensitive Hashing Scheme for Trustless Verifiable Inference,
  arXiv 2501.16007 (ICML 2025): k = 128 top activations per 32 tokens, thresholds T_exp = 38,
  T_mean = 10, T_median = 8 for bf16; robustness across GPU/TP/attention kernels; limitations on fp8
  vs bf16 separability, untested KV compression, speculative decoding.
* Komargodski & Weinstein, Proofs of Useful Work from Arbitrary Matrix Multiplication, arXiv
  2504.09971 / ePrint 2025/685 (ESA 2026 invited): low-rank-noise encoding, 1 + o(1) overhead,
  transcript unpredictability; and the project owner's veritor `docs/compute-accounting/` analysis
  of its GPU costs (15-40% for MLP shapes, >= 50% for attention) and of idle-vs-undeclared compute.
* Shacham & Waters, Compact Proofs of Retrievability, ePrint 2008/073 (Asiacrypt 2008 / JoC 2013):
  PRF-based homomorphic linear authenticators, random-coefficient aggregate challenges; Ateniese et
  al., Provable Data Possession (CCS 2007).
* Ren & Devadas, Bandwidth Hard Functions for ASIC Resistance, ePrint 2017/225 (TCC 2017); Blocki,
  Ren & Zhou, Bandwidth-Hard Functions: Reductions and Lower Bounds (CCS 2018) -- red-blue pebbling;
  relevant only to the public-verifier fallback.
* Fiore & Gennaro, Publicly verifiable delegation of large polynomials and matrix computations
  (CCS 2012); Zhang & Blanton, Efficient Secure and Verifiable Outsourcing of Matrix Multiplications,
  ePrint 2014/133 -- algebraic-PRF / homomorphic-MAC verification of Mx, the pattern behind 2.4.
* Cohen & Pietrzak, Simple Proofs of Sequential Work (Eurocrypt 2018); Boneh, Bonneau, Bunz &
  Fisch, Verifiable Delay Functions (Crypto 2018) -- lower bounds on elapsed time only.
* Thinking Machines, Defeating Nondeterminism in LLM Inference (2025); LMSYS SGLang deterministic
  mode (2025); vLLM `VLLM_BATCH_INVARIANT` -- 20-50% cost of bit-exact kernels.
* vLLM x Mooncake Store blog (2026-05-06) and CONTEXT.md for the target workload; Moonshot Kimi K2.5
  model card (1T/32B, 61 layers, 384 experts, MLA kv_lora_rank 512 + rope 64, 64 heads, d = 7168);
  NVIDIA GB200 NVL72 specifications and NVIDIA technical blog (NVLink-C2C 900 GB/s bidirectional,
  1.8 TB/s NVLink per GPU, 8 TB/s HBM3e, 17 TB LPDDR5X per rack); SemiAnalysis InferenceX GB200 page
  (186 GB usable, 900 GB/s unidirectional NVLink).
* Project repositories skimmed for context: `toploc/README.md`, `inference_verification/README.md`
  (Gumbel-max sampling verification with revealed noise, STL, TOPLOC metrics), `veritor/README.md`
  and `veritor/docs/compute-accounting/*`, `veritor/docs/notes/datacenter-realities.md`.
