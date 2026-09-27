# Phase 3, session 3: the honest-vs-attacker response curve, and the KV-admission (nesting) problem

2026-09-05.  Answers the "first hardware deliverable" of the 2026-09-05 plan (`next-constructions-and-hardware-tests.md`)
with what can be computed from measurements we already have plus one new solver sweep; maps the plan's four hardware
questions onto phase 1-3 results; and works out the one item in the plan's theoretical target that changes the
protocol rather than the graph: "security when the new KV depends on old encodings".

Compute: one A40 CPU pod, 8 solver tasks, 125 s ($0.10); pod terminated.  Only the plot script ran on the laptop.

## 0. Summary

- **Response curve** (2).  With a storage deficit eps* = 5.26 % (95 % declared / 90 % retained), the best whole-word
  attacker answers a uniform 32 B probe within Delta with probability
  P_att(Delta) = 1 - (eps* - eps_depth(Delta / t_min)), where eps_depth(D) is the largest fraction of a block
  regenerable within D dependent mixer rounds (the depth-game envelope).  For the phase-2 shipping point
  (l = 4, drU d = 6, 64 KB) at the measured CPU speed t_min = 58 ns: the attacker misses **3.7 % of probes at
  Delta = 60 us, 3.3 % at 100 us, and 0 % from Delta* = 130 us** (D* = 2244 rounds) on.  The honest proxy
  (D2H read out of HBM under an HBM-saturating load) is late on 0.13 % of probes at 60 us and 0.08 % at 100 us
  (device side; 0.3 % / 0.14 % host side), and its maximum over 3000 samples is 266 us.
- **The margin is 1.8x** between honest p99.9 (73 us) and the attacker's Delta* (130 us) at 64 KB, and it
  costs the attacker nothing to take 1.5-2 of the 5.26 points below Delta*.  This is the weakest number in the
  design.  Block size fixes it more cheaply than layers or connectors: 128 KB blocks give Delta* = 367 us
  (5.1x) and leave the attacker 4.7 % short at 100 us; 256 KB gives 598 us (8.2x); l = 5 gives 274 us (3.8x);
  DSaG-4 connectors give 246 us (3.4x) but hold the full 5.26 % deficit up to 120 us.
- **Audit policy** (2.4).  k = 1024 probes (32 KB returned) with m = 8 tolerated misses at Delta = 100 us:
  honest false reject 1.4e-7 (device proxy) / 2e-5 (host proxy) per audit; attacker pass 1.2e-7 (64 KB stack),
  4e-13 (128 KB), 3e-15 (DSaG-4), 4e-14 (l = 5).  k = 256 / m = 4 leaves the 64 KB stack at 8e-2 per audit,
  which is why the probe count is not a free parameter.  A strict all-on-time rule is unusable at any k ≥ 256.
- **Against an 8 ns circuit inside the boundary** every construction the decoder can afford fails (Delta* =
  18-82 us, inside the honest tail).  The physical assumption has to exclude hidden compute, or blocks have to be
  ≥ 1 MB; the bulk protocol does not help because its work bound also assumes the declared GPUs' hash rate.
- **KV admission is the protocol problem** (3).  Any rate-1 encoding with a fast decoder, applied to *server-chosen*
  plaintext, admits the **nesting attack**: admit a KV page whose plaintext is an existing replica page R_old, store
  only the new replica, answer probes on the old page by *decoding* (l = 4 dependent rounds, ~0.25 us).  Per-page
  nonces do not help (the plan's point 4); no encoding-level fix exists because a correct encoder must encode
  every plaintext.  Remedies: (A) **epoch re-keying** of every replica, 13-20 s of GPU per 80 GB per epoch, with
  the epoch length set by the KV admission rate (3-7 % of GPU time in decode-dominated serving, 75-115 % for
  agentic 30K-prefill turns, infeasible when prefill-saturated); or (B) **computation integrity**: KV certified as
  the model's output on tokens cannot be steered to equal a replica, and weights cannot nest weights because the
  key is drawn after `comm_D` (already the protocol).  **Weights-only PoUS is nesting-free as it stands; KV PoUS
  needs A or B.**  A trusted encoder (plan #3) does not help: the attack chooses the message, it does not
  compress it.
- **Of the plan's constructions**, #1 (sparse graph) and #2 (slow-encode / fast-decode) describe the phase-2
  kernel (24 parent reads per decoded word; encode depth l(n-1), decode depth l); what is open is unchanged (the
  finite bound and the arbitrary-compression bridge), and the DSaG connectors of #2 are ported (`dsag3.md`).

## 1. The plan's four hardware questions against what exists

| plan question | status | where | gap |
|---|---|---|---|
| Q1 honest audit latency | measured as a **proxy**: D2H copies of 4-32 KB sectors from a 40 GB HBM pool, 3000 probes, idle / HBM-saturating / GEMM load, device- and host-observed | `spotcheck3.md` 3.4, `spotcheck3/probe_latency.py` | no GPUDirect RDMA READ measurement: needs two hosts with RDMA NICs (not available on RunPod).  The proxy includes ~8 us launch overhead a NIC does not pay and excludes the network hop; its *tail* (73-266 us under load) is queueing behind the serving kernels' HBM traffic, which a NIC read via PCIe would also see in some form.  Gate closure / guard interval not modelled. |
| Q2 compressed-state attacker | pebbling-model attacks (window / cheapest / random / checkpoint placements; depth and work metrics) on the exact graphs; t_min measured for the exact mixer on CPU and GPU; response curve in 2 | `spotcheck3.md` 3.1-3.3, `dsag3.md`, `spotcheck3/depth_game.py`, `spotcheck3/dsag_game.py curve`, `spotcheck3/response_curve.py` | whole-word storage model (no partial labels, no cached hash intermediates, no cross-block compression); the regeneration is a solver, not an implemented responder.  An implemented responder can only move Delta* left. |
| Q3 serving decode | **measured** in vLLM 0.28 (weights) and the harness (KV, both): H100, Qwen2.5-7B bf16, B = 8, 30K / 118K, shared vs unique prefixes | `REPORT2.md` 5-7, `CATALOG.md` 3.5-3.7, `research/kv2.md`, `research/vllm2.md` | encoded KV inside vLLM designed, not built; embedding table / norms plaintext (7 %). |
| Q4 KV admission / refresh | **measured** for admission (side-stream sealing, 3.7 ms per 64 KB page hidden, TPOT -2..-7 %) and pool re-key (6.3 GB/s at 64 KB, encode-bound) | `research/kv2.md` items 1-6, `CATALOG.md` 3.7 | the *global* refresh the plan asks about is the nesting-attack epoch protocol of 3.2; its cost is derived from the measured encoder, not measured end to end. |

## 2. The response curve

### 2.1 Model

The attacker must retain at most (1 - eps*) of the declared bytes, eps* = 5.26 %.  Given the deadline Delta it
drops from every block the largest set it can regenerate within D = Delta / t_min dependent mixer rounds and takes
the remainder of the deficit as positions it cannot answer.  With uniform probes over the block,

    P_att(Delta) = 1 - max(0, eps* - eps_depth(Delta / t_min)),

where eps_depth(D) is the envelope, over the placement families (`window`, `cheapest`, `random` in
`depth_game.py`; plus `ckpt` and the exact fixed-k cliff points from `dsag_game.py curve`), of the largest saving
whose every dropped word has minimum regeneration depth ≤ D, with all retained words free and unbounded
parallelism (`spotcheck3.md` 3.1, `dsag3.md` 4; values in 2.2).  Concentrating the deficit on a subset of blocks
never helps the attacker because eps_depth is concave-increasing in the saving.  Spreading the deficit inside a
block *does* help: dropping exactly eps* of every block is a step function at cliff(eps*) x t_min, but dropping
eps_depth(D) "for free" and the rest "for real" is better below the cliff, and that is what the curve shows.

The honest side is the D2H latency proxy of `spotcheck3.md` 3.4 (4 KB sector, 40 GB pool, HBM-saturating load,
3000 samples), interpolated log-linearly between its quantiles: device-side p50 / p99 / p99.9 / max = 9.7 / 14.4 /
73 / 266 us; host-observed 19.6 / 27.6 / 125 / 287 us.

t_min: 58 ns (one Xeon 8470 core, injection-ARX R = 4, D = 6; `chain_cpu.c`), 288 ns (one H100 thread,
`chain_gpu.cu`), 8 ns assumed for a purpose-built circuit.  The physical assumption "99.9 % of memory is HBM,
other hardware disconnected" must also exclude hidden compute for 58 ns to be the binding number.

![response curve](spotcheck3/response_curve.png)

### 2.2 eps_depth envelopes and the resulting curve (drU d = 6; `response_curve.py`)

Percent of a block regenerable within D rounds (log-log interpolated between grid points; the truth is a
staircase between them):

| construction | D = 512 | 1024 | 2048 | 4096 | 8192 | D* at 5.26 % | Delta* CPU / GPU / ASIC | D* / l(n-1) | margin vs 73 us |
|---|---|---|---|---|---|---|---|---|---|
| l = 3 identity, 64 KB (retracted) | 2.49 | 3.71 | 8.59 | 51.6 | all | 1422 | 82 / 409 / 11 us | 0.23 | 1.1x |
| **l = 4 identity, 64 KB (shipping)** | 0.93 | 1.56 | 3.91 | 23.4 | all | **2244** | **130 / 646 / 18 us** | 0.27 | **1.8x** |
| l = 4 identity, 128 KB | 0.37 | 0.54 | 0.98 | 2.34 | 14.1 | 6322 | 367 / 1821 / 51 us | 0.39 | 5.1x |
| l = 4 identity, 256 KB | 0.24 | 0.39 | 0.64 | 1.27 | 3.12 | 10306 | 598 / 2968 / 82 us | 0.31 | 8.2x |
| l = 5 identity, 64 KB | 0.15 | 0.24 | 0.49 | 3.12 | 52.2 | 4718 | 274 / 1359 / 38 us | 0.46 | 3.8x |
| l = 5 identity, 128 KB | 0.07 | 0.10 | 0.15 | 0.34 | 2.49 | 9874 | 573 / 2844 / 79 us | 0.48 | 7.9x |
| DSaG-4 bfly11, 64 KB | 0 | 0 | 0 | 4.40 | all | 4243 | 246 / 1222 / 34 us | 0.52 | 3.4x |
| DSaG-4 full butterfly, 64 KB | 0 | 0 | 0 | 4.40 | all | 4223 | 245 / 1216 / 34 us | 0.52 | 3.4x |
| DSaG-4 full butterfly, 128 KB | 0 | 0 | 0 | 0 | 13.4 | 5717 | 332 / 1647 / 46 us | 0.35 | 4.6x |

P_att at the 5.26 % deficit, CPU t_min (per-probe attacker miss q = 1 - P_att), against the honest proxy:

| construction | 30 us | 60 us | 100 us | 150 us | 200 us | 300 us | 500 us |
|---|---|---|---|---|---|---|---|
| l = 4 identity 64 KB | 0.957 | 0.963 | 0.967 | 1 | 1 | 1 | 1 |
| l = 4 identity 128 KB | 0.951 | 0.953 | 0.953 | 0.957 | 0.957 | 0.971 | 1 |
| l = 4 identity 256 KB | 0.950 | 0.951 | 0.951 | 0.954 | 0.954 | 0.960 | 0.983 |
| l = 5 identity 64 KB | 0.949 | 0.950 | 0.950 | 0.954 | 0.958 | 1 | 1 |
| DSaG-4 bfly11 64 KB | 0.947 | 0.947 | 0.947 | 0.959 | 0.978 | 1 | 1 |
| DSaG-4 butterfly 128 KB | 0.947 | 0.947 | 0.947 | 0.947 | 0.947 | 0.983 | 1 |
| honest, device proxy | 0.9965 | 0.9987 | 0.9992 | 0.9995 | 0.9996 | 1 | 1 |
| honest, host proxy | 0.991 | 0.997 | 0.9986 | 0.9992 | 0.9995 | 1 | 1 |

Observations.

1. **Below the cliff the attacker is not at the (1 - eps*) plateau.**  For the shipping point it recovers 1.5-2.0
   of the 5.26 points for free at any Delta in the honest range (the plan's "loss term eta" is a real attack, not
   only a proof artefact): the effective per-probe deficit is 3.3-3.7 %.  The connectors are what pin the attacker
   to the plateau (eps_depth = 0 to D = 2048, `dsag3.md` 4); l = 5 and 128 KB blocks get within 0.3-0.5 points of
   it.
2. **Block size beats layers and connectors per unit of decode cost.**  Doubling n raises D* 2.8x for the identity
   stack (2244 → 6322) at a measured +19 % on KV pages and an estimated -10..-20 % weight-decode throughput
   (1 CTA/SM 128 KB kernel, not built; the fused kernel's SMEM budget is 64 KB) (`CATALOG.md` 3.11 table).
   l = 5 raises it 2.1x for +18-25 %; connectors 1.9x for ~1.3x (`dsag3.md` 7).  256 KB blocks (D* = 10306) are
   where the honest tail (max 266 us) is cleared with a 2x reserve at CPU t_min.
3. **D* is 27-52 % of the full-regeneration depth l(n-1)**: dropping 5 % costs the attacker a quarter of a full
   re-encode on the identity stack and half with connectors.  The connectors' effect is to make "drop a little"
   cost almost as much as "drop everything".
4. The **checkpoint** family (store parts of lower layers) is never the best at eps ≤ 20 %; the contiguous
   **window** is best on the identity stack at every eps; with connectors the families tie.
5. **ASIC row**: Delta* = 18 / 51 / 82 us for 64 / 128 / 256 KB at l = 4, inside the honest tail.  Not fixable
   by the graph at any affordable block size; it is a boundary assumption.

### 2.3 What the honest curve is and is not

A copy-engine D2H read of a random 4 KB sector out of a 40 GB HBM pool while an HBM-saturating kernel runs.  The
idle tail is 15 / 43 us (p99.9 / max); under load 73 / 266 us.  The load-dependent tail binds; it is queueing of
the read behind the serving kernels' HBM traffic, which a NIC reading HBM through PCIe/BAR1 also meets (behind a
different queue).  The plan is right that the real one-sided GPUDirect RDMA READ, with the reply path, gate
closure and guard interval, must be measured on two RDMA-connected hosts, which RunPod does not provide.

### 2.4 Audit policy: k probes, m tolerated misses (CPU t_min)

| construction | Delta | attacker q | k / m | honest reject (device / host) | attacker pass |
|---|---|---|---|---|---|
| l = 4 identity 64 KB | 100 us | 3.26 % | 256 / 4 | 1.9e-6 / 3.6e-5 | **7.8e-2** |
| l = 4 identity 64 KB | 100 us | 3.26 % | 1024 / 8 | 1.4e-7 / 2.0e-5 | 1.2e-7 |
| l = 4 identity 64 KB | 60 us | 3.70 % | 1024 / 8 | 1.2e-5 / 4.9e-3 | 3.0e-9 |
| l = 4 identity 64 KB | 150 us | 0 | any | | **1** (above the cliff) |
| l = 4 identity 128 KB | 100 us | 4.72 % | 256 / 4 | 1.9e-6 / 3.6e-5 | 6.2e-3 |
| l = 4 identity 128 KB | 100 us | 4.72 % | 1024 / 8 | 1.4e-7 / 2.0e-5 | 3.8e-13 |
| l = 4 identity 128 KB | 150 us | 4.26 % | 1024 / 8 | 8.0e-9 / 1.8e-7 | 2.3e-11 |
| DSaG-4 bfly11 64 KB | 100 us | 5.26 % | 1024 / 8 | 1.4e-7 / 2.0e-5 | 2.9e-15 |
| l = 5 identity 64 KB | 100 us | 4.97 % | 1024 / 8 | 1.4e-7 / 2.0e-5 | 4.1e-14 |

A strict all-on-time rule rejects 18-30 % of honest 256-probe audits at 100 us (device / host proxy) and is
unusable; m = 8 of 1024 gives 1e-7..1e-5 honest rejects per audit.  Traffic: 1024 x 32 B = 32 KB returned per
audit.  The attacker-pass numbers hold below the cliff only: above Delta* no k helps, so the margin of 2.2 is the
security parameter and k is the amplification.  One audit per second at 1024 / 8 catches every construction in the
table within seconds except the 64 KB stack at 256 / 4.

### 2.5 What the curve establishes and what it does not

It establishes: the deadline range in which the whole-word attacker loses, for the exact graphs and the measured
mixer speed on the measured hardware classes; the honest latency the same deadline must accommodate on one
hardware proxy; and that the margin at the phase-2 shipping point is 1.8x with a 3.3 % effective deficit at
100 us.  A measured attack faster than the solver's depth x 58 ns (a faster ARX chain, or a representation
outside the whole-word model) moves Delta* left.  The arbitrary-compression bound is the open theoretical item
(`dsag3.md` 8-9); the curve is not evidence for any deadline against hardware outside the assumed boundary.

## 3. KV admission: the nesting attack and what it costs to stop it

### 3.1 The attack

Replica of block i: R_i = Enc(key, i, D_i), Enc invertible, decode of one word = l dependent mixer evaluations
(~0.25 us at CPU t_min; 490 GB/s in bulk on an H100).  KV plaintext is whatever the server declares; the verifier
cannot check it against anything (it is the model's state on private prompts).

The server admits a new KV page j with plaintext **D_j := R_i** for an existing replica page i (weights or KV),
computes R_j = Enc(key, j, R_i), stores R_j, discards R_i.  Probe on page j: served from R_j.  Probe on page i,
word w: R_i[w] = Dec(key, j, R_j)[w] in l = 4 dependent rounds.  Storage one page, declared two, response time far
below any Delta.  Chained (D_(j+1) := R_j, ...) it frees m - 1 pages per m admitted at depth (m - 1) l.  Under the
bulk protocol (A) the same attack decodes eps x 4 GB at 490 GB/s = 0.4 ms for eps = 5 %, inside the 1.2 ms read.

Nothing at the encoding level fixes it: the honest decoder is a public deterministic function of (R_j, metadata)
and a correct encoder must encode *every* plaintext, R_i included.  Per-page nonces make duplicate plaintexts
(D_j = D_i) cost a full re-encode (l(n-1) rounds) but do nothing for D_j = R_i.  A Fiat-Shamir pad
pad_j = PRF(key, j, H(D_j)) is a public function of committed data and the attacker encodes R_i under it.  A
statistical "plausible bf16" filter is defeated by embedding R_i in mantissas at 2x expansion, which still leaves
occupancy at 67 %.  Comparing decoded pages with stored replicas is defeated by any public invertible map.

### 3.2 Remedy A: epoch re-keying

Draw a fresh replica key at every epoch boundary and re-encode *every* replica (weights and KV) under it.  A nest
made in epoch t (D_j = R_i under key_t) is dead after the boundary: a probe on page i under key_(t+1) needs
Enc(key_(t+1), i, Dec(key_t, i, R_i)), a full l(n-1)-round chain, i.e. the ordinary regeneration bound of 2.
Inside an epoch the attacker frees at most the bytes admitted in that epoch (each admitted page frees one page;
chains do not beat the ratio), so the occupancy claim degrades to (declared - admitted-this-epoch) / M.  Policy:
re-key when admitted-since-last-rekey ≥ delta M, delta = the occupancy slack (5.26 % minus the regeneration
eps_depth at the chosen Delta; ~4 GB per H100 at 128 KB blocks, ~2.5 GB at 64 KB).

Cost: the re-key is encode-bound and in place, page by page (64 KB scratch, no double space): measured 6.3 GB/s
at (3,4,3) / 64 KB (`kv2.md` item 6; one sequential chain per block, ~350 blocks in flight) and estimated
4-6 GB/s at (4,6,4): **13-20 s of GPU time per 80 GB per epoch**, plus a per-page epoch bit the tap must know
during the transition (accept either key for pages in the announced transition set).  Epoch length is set by the
KV admission rate:

| serving regime (Qwen2.5-7B, 56 KB of KV per token) | KV admission per GPU | epoch at 4 GB slack | re-key GPU time |
|---|---|---|---|
| decode-dominated agentic, B = 8, 240 tok/s | 13 MB/s | 300 s | **4-7 %** |
| agentic with a 30K-token prefill per turn, B = 8, one turn per minute per sequence | 0.23 GB/s | 18 s | **75-115 %** |
| prefill-saturated (one 30K prompt per second) | 1.7 GB/s | 2.4 s | 540-830 % (infeasible) |
| 72B on 8 GPUs (320 KB/token), decode-dominated B = 8 | 77 MB/s per node (32 GB slack) | 415 s | 3-5 % |
| 72B on 8 GPUs, one 30K prompt per second | 9.6 GB/s per node | 3.3 s | infeasible |

Prefix-cache hits count as admissions (a page pulled from the Mooncake pool is re-encoded under the slot key: a
new declaration).  A faster encoder helps linearly, with a ceiling set by on-chip memory for blocks in flight
(SMEM 30 MB + L2 50 MB on H100 → ~1000 64 KB blocks → 15-20 GB/s), i.e. 3-4x at most.  Epoch re-keying is
therefore affordable for decode-dominated serving and unaffordable wherever prefill admits more than ~0.1 GB/s of
KV per GPU.

### 3.3 Remedy B: computation integrity

If KV pages are certified as the output of the declared model on declared tokens (the verified-computation-graph
layer), the server cannot choose a page equal to a replica: that would require steering a transformer's KV to a
target string.  Weights cannot nest weights because the replica key is drawn after `comm_D` (commit-before-seed,
`protocol2.md`), and model updates are then admissions like KV.  With B in place remedy A is unnecessary and the
storage-to-answer question reduces to the single-block bound of 2.  Without B, **weights-only PoUS** (declare and
encode only the weights; KV stays plaintext and uncounted) is nesting-free and is the "model weight residency"
application; **KV PoUS needs A**.

### 3.4 Remedy C (rejected): trusted encoder

Moran-Wichs encodings (plan construction #3) are incompressible for *any* message; the nesting attack is not a
compression of one message, it is a choice of message.  A trusted encoder that encodes what the server sends still
encodes R_i, and would have to refuse pages equal to a public invertible function of an existing replica, which it
cannot decide.  #3 is a weights-only option with a trusted setup, and would additionally need to see every admitted
KV byte (GB/s in prefill regimes).

## 4. The plan's construction shortlist against phase 1-3 data

| plan construction | where we are | what is open |
|---|---|---|
| #1 sparse graph with hash/XOR | The phase-2 decoder reads l x d = 24 parents per decoded 32 B word (not "thousands": that figure describes the whole-block model of the goal-mode proof, not the kernel).  Graph: drU d = 6, 4 layers; bidirectional game eps ≤ 0.05 % at W = n.  Blocki et al.'s log-indegree constructions are not needed at n = 2048-8192. | The finite (alpha, beta) bound at n = 2048 / 4096 / 8192 for drU (attack searches are the wrong kind of evidence, as the plan says); the arbitrary-state reduction (the Pietrzak route needs 512 B labels, `dsag3.md` 9). |
| #2 slow-encode / fast-decode (PIE / Fisch) | This *is* the construction: encode depth l(n-1) (8188 rounds at 64 KB), decode depth l.  PIE's addition is the connectors; ported and swept (`dsag3.md`).  Fisch's expander edges were dropped in phase 1 for cost; the DSaG connectors are the cheaper substitute. | Arbitrary-compression argument for the invertible stack (PIE Conjecture 1 analogue); the linear-connector lemma (`dsag3.md` 8.3). |
| #3 trusted encoder (Moran-Wichs) | Not built.  Does not address nesting (3.4); needs trusted encoding bandwidth; weights-only. | Concrete parameters only if a weights-only trusted-setup variant is wanted; low priority. |

The plan's four theoretical-target items: (1) arbitrary compression at 95 / 90: open (unchanged); (2) bounded
decode work per useful byte with intermediate state charged: 24 parent reads + 4 mixer evaluations per 32 B word,
scratch = one block in SMEM (fused) or one layer of KV in HBM (attention path); (3) local admission of new KV:
side-stream sealing does it at 3.7 ms per page with no refresh of existing pages *except* the nesting epoch of
3.2; (4) security when new KV depends on old encodings: the nesting attack of 3.1 is the concrete failure,
remedies 3.2-3.3.

## 5. Results table in the plan's format

H100 SXM, Qwen2.5-7B-Instruct bf16, B = 8, ~30K context, vLLM 0.28 for weights (unique prefixes; shared-prefix
rows in `vllm2.md`), harness for KV.  "Decode slowdown" is time per output token vs plaintext.  Honest timeout and
attack columns from 2 at Delta = 100 us, k = 1024, m = 8, CPU t_min.

| construction / version | trust assumptions | security parameters | serving config | decode slowdown | KV admission / refresh | honest timeout rate | best measured attack and success | proved bound / unresolved |
|---|---|---|---|---|---|---|---|---|
| stack (4,6,4) drU, 64 KB, identity (phase-2 shipping point) | tap-timed probes; HBM-only server; no hidden compute (t_min ≥ 58 ns); key drawn after `comm_D` | l = 4, d = 6, R = 4, n = 2048; Delta = 100 us, k = 1024, m = 8; declared 95 % | weights in vLLM, KV in harness | weights 4.2-5.1x (30K), 2.4-2.6x (118K); KV session 2.71x; both 3.67x session / 6.30x late TPOT | admission 3.7 ms/page hidden; nesting epoch re-key 13-20 s per 80 GB per ~2.5 GB admitted (see 3.2) | 1.4e-7 / 2e-5 per audit | eps_depth(1724) = 2.0 %: attacker misses 3.26 % per probe, passes 1.2e-7 per audit; **Delta* = 130 us, margin 1.8x** | no proof; whole-word model; bidirectional game eps ≤ 0.05 % at W = n; arbitrary compression open |
| same, 128 KB blocks | same | n = 4096 | same; unfused weight path | KV +19 % (measured); weights est. -10..-20 % throughput (kernel not built) | same, 4 GB slack | same | attacker misses 4.72 %, passes 3.8e-13; Delta* = 367 us, margin 5.1x | same |
| same, 256 KB blocks | same | n = 8192 | same | not measured (est. a further +15-20 % on KV) | same | same | misses 4.9 %, Delta* = 598 us, margin 8.2x | same |
| DSaG-4 (4,6,4) drU + bfly11 connectors, 64 KB | same | + 11 connector stages per layer | same | est. 1.3x row 1 (`dsag3.md` 7); not built | same | same | misses 5.26 % (plateau to 120 us), passes 2.9e-15; Delta* = 246 us, margin 3.4x; work game 0 leakage to W = 8n | same; connector lemma open |
| stack (5,6,4) drU, 64 KB | same | l = 5 | same | +18-25 % over row 1 (harness 4.88x vs 4.14x at R = 3) | same | same | misses 4.97 %, passes 4.1e-14; Delta* = 274 us, margin 3.8x | same |
| any of the above vs an 8 ns circuit inside the boundary | boundary violated | | | | | | Delta* = 18-82 us inside the honest tail: **fails** | |
| weights-only PoUS (KV not declared) | as row 1 | as row 1 | same | weights only: 4.2-5.1x / 2.4-2.6x | none (no admissions) | same | as the block rows | nesting-free by construction |
| KV PoUS without computation integrity | as row 1 + epoch re-keying | + epoch delta = slack | decode-dominated only | row 1 + 4-7 % | 13-20 s per 80 GB per epoch | same | as the block rows within an epoch | occupancy degrades by admitted-this-epoch / M |

## 6. What to do next

1. **Move the shipping point to 128 KB blocks** (D* 2.8x, margin 5.1x) before more kernel work: the 1.8x margin
   and the 3.3 % effective deficit at 64 KB are the first things a reviewer will attack.  Build the 1 CTA/SM 128 KB
   weight kernel (or a split-block fused variant) and measure the weight-side cost the table only estimates.
2. **Decide the KV story.**  Weights-only PoUS now (nesting-free; the model-weight-residency application).  KV
   PoUS only together with computation integrity, or with epoch re-keying restricted to decode-dominated
   deployments with the 4-7 % stated.  The plan's "arbitrary, changing KV remains a requirement" is a protocol
   property, not a graph property.
3. **Real RDMA measurement** (a two-host RDMA cluster, not RunPod): one-sided GPUDirect READ of 32 B - 2 KB from
   random HBM addresses under the vLLM decode load, p50 / p99 / p99.9 / max over 1e6 samples, with the reply path
   and gate closure.  Until then 73 / 266 us is the planning tail.
4. **Implemented responder**: a CPU program that regenerates the solver's optimal dropped set for a 64 KB / 128 KB
   block and answers a probe, wall-clocked against 2244 / 6322 rounds x 58 ns (a dependent chain does not
   parallelise; the check is the constant, not the algorithm).
5. Theory (unchanged from `dsag3.md`): finite (alpha, beta) for drU at n = 2048-8192; additive depth profile; the
   linear-connector lemma; the arbitrary-compression bridge.  State the nesting attack as a lemma about
   server-chosen plaintext so the reduction is scoped to certified plaintext or to epochs.

## 7. Files

- `spotcheck3/dsag_game.py` (mode `curve`): per-position depth distributions per (construction, k, placement),
  8 tasks → `spotcheck3/dsag_curve.csv` (338 rows), `spotcheck3/dsag_curve.log`.
- `spotcheck3/response_curve.py`: eps_depth envelopes from `eps_main/big/cliff.csv`, `dsag_eps_main/extra.csv`
  and `dsag_curve.csv`; writes `response_curve.csv` (P_att per construction / t_min / Delta), `response_curve.png`,
  the envelope, cliff and audit-policy tables.
- Inputs reused: `spotcheck3/probe_latency.py` results (`spotcheck3.md` 3.4), `spotcheck3/chain_cpu.c` /
  `chain_gpu.cu` (t_min), `kv2.md` item 6 (re-key throughput), `vllm2.md` / `kv2.md` (serving overheads).
