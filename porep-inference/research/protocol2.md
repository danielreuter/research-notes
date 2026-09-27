# Protocol v2: HBM accounting for secret, adversarial weights with an encoded replica and bandwidth challenges

Agent P1, 2026-09-03. Companion to `research/challenger2.md` (measurements). This document is the spec: roles,
admission, the challenge loop, the dedication and locality arguments, what is proven vs heuristic, parameters
for an 8x H100 node and for GB200, and costs. Numbers marked (m) were measured on pod c today; (p) are
published; (e) are estimates.

**One-screen version.** Prover P (the operator's node) commits to its secret weights (`comm_D`, Merkle root),
*then* receives a seed derived by the verifier V from `comm_D`, encodes `R = Enc_seed(D)` (layered DRG
labeling, 64-128 KB blocks) as the only copy in HBM, and streams `R` once to the on-node challenger C
(sealed device, never sees the seed), which computes one 8-byte Shacham-Waters tag per 32 KB sector under
its own secret and keeps only the tags (20 MB per 80 GB). Every ~200 ms C doorbells all GPUs of the node at
once with a nonce; each GPU's agent kernel (inside the serving process, 1024-thread CTAs that take the SMs
exclusively) reads 131072 random 32 KB sectors (4 GB) and returns the 64 KB position-wise linear MAC; C checks
it against the same random combination of tags in 3.6 ms of CPU and requires arrival within `T + 0.5 ms`
(`T` = 1.31 ms on H100). Locality: anything not in HBM must come over PCIe at <= 55 GB/s, so at most
2.5 % of the store can be elsewhere (GB200: 4.8-8.5 %). Dedication: `R` cannot be recomputed from `D` in
time (3.6 ms chain per block vs 1.8 ms deadline) and is incompressible without the seed, so `D = 0` costs the
same HBM as real weights. Consistency: `V_node` (holds the seed, sees nothing else) opens one random decode
cone per second and learns 32 B of `D` per opening (2.7 MB/day). KV pages are sealed under slot keys and
re-keyed on move; pool copies cannot answer. The prover's own kernels must have bounded CTA lifetime, or
the honest tail blows the deadline -- the one hard requirement this spec places on the serving stack.

**Update 2026-09-03 20:30 (merged phase-2 kernels, `challenger2.md` final entry).** (1) Bounded CTAs are
in: with the K1/K2 defaults at the security point (l=4, d=6, r=3, drU, mixer 1) the honest tail under the
Qwen-7B B=16 encoded-weights load is p99.9 - idle p50 = 0.34 ms (unfused, `POREP_BPC=2`), 0.17 ms
(`fusedmm`, `POREP_FUSED_BPC=auto4`), 0.11 ms (`auto2`); the persistent variants give 1.8-2.4 ms. Slack 0.5 ms
holds with margin; 0.3 ms holds for the fused modes. (2) The seed is now a 128-bit key in the kernels
(`replica_seed | replica_key`, Section 2). (3) **The 32 KB block of the security point breaks the
dedication bound at X = 4 GB**: the chain is 1.61 ms per block vs the 1.81 ms deadline (Section 5). The
spec therefore requires 64 KB blocks (`n = 2048`: 3.16 ms, 1.75x) at X = 4 GB, or X <= 1.6 GB with 32 KB
blocks (1.53x, `eps_max` 3.5 %).

## 0. Setting and goal

A GPU with HBM capacity `H` runs inference for an operator we audit. The operator declares a memory map
`weights | KV pool | filler | workspace` covering `H`, with the workspace `A_max` (1-3 %) declared and
unproven. The weights `D_W` are **secret and adversarial** (worst case all zeros); KV pages `D_KV` are
operator-produced; the filler is data the operator does not need. Goal (unchanged from threat_model.md): for
every declared store, *possession* (the committed bytes exist), *locality* (they are in this GPU's HBM, not
in host DRAM / a peer GPU / a pool / an SSD), and *dedication* (they cannot be produced on demand from fewer
bytes held anywhere). v2 adds: the verifier never learns `D_W` beyond a quantified leak, and nothing in the
scheme may depend on the entropy of `D`.

Mechanisms: (1) **the encoded replica** `R = Enc_seed(D)` (layered DRG labeling, `porep/`) is the only copy
in HBM and is decoded transiently on read; it gives dedication (the keyed labeling costs the same for
`D = 0`), incompressibility (pseudo-random to anyone without the seed), and replica-id binding (one replica
per GPU slot). (2) **Bandwidth challenges** over `R` with a Shacham-Waters linear MAC give locality with
residual `eps = B_tier / B_HBM * (1 + slack / T)`. (3) **Commit-before-seed + sampled consistency openings**
bind `R` to a `D` fixed before the seed was known (without this the operator picks `D` after the seed and
makes `R` anything it likes, e.g. all zeros: the encoding is a bijection for a fixed seed). (4) **Slot keys**
make pool / peer copies of KV pages useless for answering challenges without a re-encode.

## 1. Roles and trust

| role | where | holds | trusted for |
|---|---|---|---|
| **P** prover | the operator's node: GPUs, host, driver, serving stack | `D`, seeds, `R`, all commitments | nothing |
| **C** challenger | sealed on-node device (DPU/FPGA class) with a ~1 us clock, CSPRNG, PCIe (or NVLink) endpoint to every GPU of the node, a doorbell/mailbox path, key storage; attested to V | MAC secret `(alpha, k)` per GPU; the tags `sigma_j`; `comm_R` roots; the challenge log | integrity of timing and of the MAC check; **confidentiality of `(alpha, k)`**. C sees `R` (pseudo-random without the seed) and **never the seed** |
| **V** verifier | remote governance verifier + a small on-node HSM/TEE function `V_node` holding V's seed key | `comm_D`, `comm_R`, the seed key `K_seed`, the consistency-opening log; the verdict stream from C | honest; learns `D` only through sampled openings (Section 6) |

Separation of duties is deliberate: C can compute tags only because it sees all of `R`; it cannot decode `R`
because it never gets the seed. `V_node` knows the seed but sees only the sampled openings. Neither device
alone holds enough to reconstruct `D`; if the deployment accepts a single sealed device that holds both, the
two roles collapse into one box and the confidentiality of `D` rests on that box's isolation (the same class
of assumption as a TEE). Collusion of C and V is out of scope (the same as key compromise: a total break of
the MAC; mitigations are per-GPU keys and re-tagging, Section 8).

Why the seed must be secret from C but need not be interactive: soundness only needs the seed to be
fixed *after* `comm_D` as a function P cannot steer; `seed = PRF_{K_seed}(gpu, store, slot, epoch, comm_D)`
does that (steering it means grinding `comm_D`, and each trial costs a full encode with no better than
random chance of a compressible `R`). Confidentiality needs `K_seed` unknown to C, since anyone holding both
`R` and the seed decodes `D` (`D_i = R_i XOR H(seed, ..., parents)`).

## 2. Data layout and commitments

* Chunk = DRG node, 32 B (`chunk_bytes`); block = encode/decode unit. The measurements in this document
  were made at the phase-1 point, 64 KB blocks (`n = 2048`, `l = 3`, `d = 4`, 3 double rounds, mixer 0); the
  **security point after the phase-2 kernel/graph work is 32 KB blocks: `PoRepParams(chunk_bytes=32,
  n_chunks=1024, layers=4, degree=6, rounds=3, mixer=1, parent_sampler="dru")`** (kernels2.md, graphs2.md),
  so block = sector there. **Sector = 32 KB** = the challenge read unit and tag unit (4-8 KB sectors are also
  within 2-15 % of peak, 32 KB is the register-file limit for position-wise accumulators, `challenger2.md`).
  The block size matters for one thing in this spec: the regeneration latency bound of Section 5 scales with
  `l * n` (see the 2026-09-03 note there).
* **Seed width and how the seed is carried (updated 2026-09-03, after K1's A2 change on `p2/k1`)**: the
  seed is a 128-bit secret key mixed into every hash state. The kernels now take it as four 32-bit key words
  `k0..k3` XORed into hash state words 3..6 (`PoRepParams.key_words()`; all three mixers; bit-exact reference
  in `porep/reference.py`; the KATs are unchanged when `k1..k3 = 0`). In the API the words are split as
  `replica_seed` (`k0`, a 32-bit int, the phase-1 field) and `replica_key` (`k1..k3`, <= 24 hex digits = 96
  bits). **The protocol's `seed` is all 128 bits: `(replica_seed, replica_key) = split_32|96(PRF_K_seed(gpu,
  store, slot, epoch, comm_D))`.** K1's text calls `k0` a "public-ish domain-separation" word; in this
  protocol it is *not* public -- it is the low word of the secret seed, and domain separation between slots
  comes from the replica id being *inside the PRF input* (two slots get independent 128-bit seeds), not from
  a label field. Nothing else in the spec changes: `Enc_seed`, `H(seed, layer, id, parents)`, the
  consistency-opening cone and the re-keying on slot moves all read "seed" as this 128-bit value. Two
  residual notes: (i) `replica_key` alone is 96 bits, so an implementation that leaves `replica_seed` at the
  default `0x7E57` has a 96-bit secret -- acceptable against brute force, but the spec requires all four
  words keyed; (ii) words 4..6 are IV constants in the unkeyed ChaCha-style design (ChaCha keys words
  4..11), so S2 should confirm the keyed initial state for the injection schedule (K1 raised the same point;
  W = 16 leaves words 7..15 for a 256-bit key if wanted). `PoRepParams.tag()` appends `_k` when a key is set
  and never includes the key.
* `comm_D`: Merkle root (BLAKE3 compression; Pearl's GPU BLAKE3 at ~0.6-1 TB/s (e) makes an 80 GB tree ~0.1-0.2 s)
  over 32-B chunks of `D` (depth 32 for 80 GB; a path is ~1 KB). For KV, one root per page (64 KB: depth 11)
  plus a manifest of resident pages. For the filler, `D = 0` and no commitment is needed beyond the size.
* `comm_R`: the same tree over the stored layer `R_{l-1}`.
* Tags (Design A, Section 4): `sigma_j = PRF_k(j) + sum_i alpha_i m_{j,i} mod p`, `p = 2^61 - 1`, `m_{j,i}` the
  8192 32-bit words of sector `j`, 8 bytes per sector: 20 MB per 80 GB GPU (0.025 %), 46 MB for 186 GB.

## 3. Admission (per GPU, per store)

~~~text
P -> V   : comm_D, size, layout params (chunk, n, l, d, rounds, sector), replica id (gpu, store, slot, epoch=0)
V -> P   : seed = PRF_K_seed(replica id, comm_D)  # 128 bits -> (replica_seed | replica_key) key words k0..k3; never sent to C
P        : R = Enc_seed(D)  (GPU encode, once: 6.3 GB/s with the phase-1 encoder at l=3 (m) -> ~13 s for 80 GB; latency-bound, not optimised)
P -> V,C : comm_R
P -> C   : stream R over PCIe (80 GB at B_H2D, Section 7);  C: sigma_j for all sectors, Merkle root == comm_R
C        : stores {sigma_j}, comm_R, (alpha, k); arms the challenge loop for this store
V_node   : consistency openings begin (Section 6)
~~~

Filler = the encoding of zeros under its own replica id: it needs no plaintext, no commitment beyond its
size, and it is exactly as hard to hold as weights (this is the v2 point: dedication does not depend on
`D`). The KV pool is admitted empty (its slots hold filler until pages are sealed into them).

## 4. The bandwidth challenge (locality + possession of the whole sample)

**Prover kernel** (`porep/challenge/challenge_kernels.cu`, mode `sw`): for challenge `(nonce, X, S)`, positions
`t = 0..n-1`, `n = X / S`, sector `j_t = H(nonce, t) mod N`, coefficient `nu_t = H'(nonce, t)` (32-bit, odd);
response `mu[i] = sum_t nu_t m_{j_t,i} mod p` for every word position `i < S/4` (64 KB at `S = 32 KB`). One CTA
of 1024 threads per SM walks its share of the sectors with 128-bit per-position accumulators; one Mersenne
reduction per position at the end; a 4 us reduce kernel folds the per-CTA partials. Measured (m): 3.09-3.12
TB/s at 32 KB sectors = 97-98 % of the sequential-read ceiling (3.18 TB/s) and 93 % of the 3.35 TB/s spec;
X = 4 GB in 1.29 ms back-to-back, 1.31 ms as an isolated Poisson launch.

**Verifier check** (C, on receipt at time `t_resp`):

~~~text
accept iff  t_resp - t_issue <= T + slack    and    sum_t nu_t sigma_{j_t}  ==  sum_t nu_t PRF_k(j_t) + sum_i alpha_i mu[i]   (mod p)
~~~

Cost per challenge at `X = 4 GB, S = 32 KB`: 131072 PRF evaluations + 131072 + 8192 multiplications mod p:
**3.6 ms of one core in NumPy** (measured with the reference `Verifier.check`, splitmix PRF; ~0.5 ms in C
with AES-NI), trivial on an FPGA; at 5/s per GPU, 8 GPUs: 15 % of one core. State: the 20 MB of tags.
Tagging at admission: 140 MB/s in NumPy (10 min per 80 GB on one core; ~50-100x faster in C/AVX: 10-20 s,
or in the stream as `R` arrives at 55 GB/s with an FPGA).

**Soundness.** (i) MAC: `mu' != mu` passes with probability `1/p ~ 2^-61` over the secret alpha (P never
sees alpha or any tag; a MAC mismatch is therefore a certain violation, and an honest P never produces one --
integer arithmetic is deterministic). A prover missing sector `j_t` must guess `nu_t m_{j_t}`: `R` is
pseudo-random to everyone but P itself, and P *has* the seed, so for P "missing" means "not stored anywhere
reachable in time" (Section 5 bounds regeneration). (ii) Timing: the honest response time is `T = X /
B_HBM,eff` plus fixed overheads; the deadline slack is set from the measured honest tail under load
(`challenger2.md`; pass criterion: p99.9 jitter <= 0.3 ms). (iii) Every GPU of a node (and of an NVLink
domain) is challenged **simultaneously** (same instant, independent nonces): otherwise the idle peers' PCIe
links and HBM become additional tiers for the challenged GPU (8 x 50 GB/s of host DRAM reachable over
NVLink). With simultaneous challenges each GPU's deficit competes for its own links only.

**Timing model and the prover-side requirement** (measured, `challenger2.md`). Honest kernel time on an
idle H100: `T` = 0.547 / 1.314 / 2.590 ms at X = 1.6 / 4 / 8 GB (32 KB sectors), p99.9 - p50 = 0.09-0.13
ms. The tail under a concurrent decode workload depends on *how* the challenge kernel is scheduled, not on
HBM contention (once running, it owns the SMs and reads at the idle rate):

| how the challenge kernel reaches the GPU | p99.9 - honest p50 | verdict |
|---|---|---|
| separate process / CUDA context (time-slicing, no MPS) | ~2.5 ms at any X (waits for the load's time slice; kernels > 2.5 ms are preempted once) | unusable at 0.3 ms slack |
| same process, own stream, plaintext-model decode step | 0.37-0.42 ms (0.32-0.37 over the under-load p50); stream priority makes no difference | marginal pass |
| same process, own stream, phase-1 **encoded-weights** decode step (persistent-CTA decode kernels) | 1.8-2.0 ms, max 5.7 ms | fails 6x |
| same, decode kernel launched with one CTA per block (`grid = nblocks`) | 0.37-0.41 ms (identical to the plaintext step; the load runs 2 % faster) | marginal pass, slack 0.5 ms |
| same process, synthetic load whose every kernel has bounded CTAs | 0.18 ms | pass |
| **final (merged phase-2 kernels, security point (4,6,3) drU mixer 1, Qwen-7B B=16, 5/s):** unfused `POREP_BPC=2` (K1 default) | 0.34 ms (p99.9 1.66) | pass at 0.5 ms slack |
| final: unfused `POREP_BPC=0` (persistent) | 1.82 ms (p99.9 3.15) | fails |
| final: `fusedmm` persistent (K2 default) | 2.40 ms (p99.9 3.72) | fails |
| final: `fusedmm` `POREP_FUSED_BPC=auto4` | **0.17 ms** (p99.9 1.49), load step +1.0 % | pass, recommended default |
| final: `fusedmm` `POREP_FUSED_BPC=auto2` | 0.11 ms (p99.9 1.44), load step +1.2 % | pass |
| final: plaintext Qwen step (reference; cuBLAS + attention only) | 0.38 ms (p99.9 1.70) | marginal |

So the protocol requires that the challenge kernel be launched **inside the serving process** (the "agent
kernel" of the plan: same context, dedicated stream; doorbell = a mapped-memory flag or a host-side thread of
the serving stack woken by the challenger device), and it constrains the prover's *own* kernels: every kernel
in the serving process must have **CTA lifetime <= ~50 us or honour a yield flag**, because the challenger
cannot start on an SM until that SM's resident CTAs exit. This is not a trust assumption: a prover whose
kernels are not preemptible simply misses deadlines and fails the audit; it is an engineering requirement
that the phase-1 persistent-grid decode kernels currently violate (`grid = min(nblocks, 528)`, CTAs living
0.3-3 ms; fix: `grid = nblocks`, or a polled device flag, `challenger2.md` 10:15 and 12:05 entries -- the
fix was verified on the encoded-weights Qwen load and costs nothing). With that fixed the measured slack
requirement is **0.5 ms** (p99.9 = idle median + 0.37-0.41 ms, plus margin), i.e. `(1 + slack/T)` = 1.9 /
1.38 / 1.19 at X = 1.6 / 4 / 8 GB: the argument for the largest X the HBM-time budget allows.

Two more measured design rules for the kernel: it must **take the SMs exclusively** while it runs (the
1024-thread CTA holding 87 % of the register file does; 128-thread CTAs that co-reside with the load's GEMMs get
about half the HBM bandwidth and a median that depends on the load), and stream priority is irrelevant. The
doorbell path (C -> P): C writes nonce + doorbell into a PCIe-mapped mailbox; a host thread of the serving
process blocked on it launches the kernel (~10-20 us), or a resident 1-warp listener CTA launches it from
the device (CUDA device graph launch, ~2 us; it occupies 1/64 of one SM's warp slots permanently). The
response path: the 64 KB `mu` vector is DMA'd to C (~10 us + 64 KB / B_PCIe ~ 3 us). All of this sits
inside the 0.4 ms slack; C measures doorbell-to-last-byte with its own clock.

**Decision rule.** MAC mismatch: violation, immediately. Late responses: count over a sliding window; with
the deadline at the honest p99.9 an honest GPU is late ~1e-3 of the time, an adversary with `eps > eps_max`
is late on *every* challenge, so "5 late in the last 100" separates the two with false-positive probability
`C(100,5) 1e-15 ~ 8e-8` per window and detection within 5 challenges (1 s at 5/s). The rule tolerates an
*intermittent* cheater that is in violation < 4 % of the time; a sequential test (CUSUM on the late
indicator) or a longer window tightens that at the cost of detection latency, and Section 8 gives the
Poisson detection probability for intermittent cheating. Timing failures leak nothing about alpha; the
accept/reject bit of the MAC leaks at most one bit per *rejection*, which only a violating prover triggers.

## 5. Dedication: why the encoded replica forces dedicated memory even for D = 0

The adversary's cheap alternatives to storing `R` and what bounds them:

1. **Store something smaller than `R`.** `R` is the keyed labeling of a graph whose per-node label is
   `R_{l-2}[i] XOR H(seed, layer, id, parents)`; for a fixed `D` committed before the seed it is
   indistinguishable from random to anyone without the seed (PRF assumption on the mixer), and for P, who
   has the seed, it is still incompressible *as a function of D alone* unless P can regenerate it faster
   than the deadline (next item). Choosing `D` after the seed to make `R` compressible is excluded by
   commit-before-seed + consistency openings (Section 6); an operator that commits to `D = 0` is fine -- its
   `R` is exactly as random and as large as anyone's.
2. **Regenerate the challenged sectors from `D`** (cheap to hold when `D` is zero/compressible). Each block
   is a strictly sequential chain of `l * n` hashes (predecessor edges + ZigZag reversal); the stored layer of
   a sector cannot be produced before the whole chain has run. Latency bound: `l n t_hash` per block, all
   blocks in parallel; work bound: `X / 32 B * l` hashes at ~300 ALU ops each vs the GPU's INT budget.
   **Measured** (`challenge_regen.py`, `regen.csv`: the phase-1 encode kernel on a 1-block buffer = one
   chain): `(l=3, n=2048)`: **3.61 ms per 64 KB block** (588 ns per node, sequential), `(3, 4096)`: 7.21 ms
   per 128 KB block, `(2, 2048)`: 2.43 ms, `(3, 2048, 2 rounds)`: 3.30 ms. Against the deadline `T + 0.5 ms`:
   X = 4 GB (1.81 ms): 64 KB blocks give a 2.0x margin, 128 KB 4.0x; X = 8 GB (3.09 ms): 64 KB blocks give
   only 1.17x -> use 128 KB blocks (2.3x). The work bound alone is weak (4 GB = 3.75e8 hashes; at the INT
   issue limit of ~300 ops/hash that is ~3.4 ms of the whole GPU vs a 1.81 ms deadline -> eps <= ~50 % by
   work), so the **latency bound must be made binding: require `l n t_hash,seq >= 2 x (X / B_HBM + slack)`**.
   Cheaper mixers (RQ1: injection-ARX ~2x faster per hash, tensor-core mixer ~3x) shorten the chain
   proportionally and must be compensated with larger `n` or smaller `X`. **Measured at the phase-2 security
   point (2026-09-03 20:20, `regen_final.csv`, merged K1 kernels, mixer 1 drU): (l=4, d=6, r=3) with 32 KB
   blocks (`n = 1024`) = 4096 sequential nodes at 392 ns each = 1.61 ms per block -- BELOW the 1.81 ms
   deadline at X = 4 GB (0.89x), so the latency bound is not binding there and the adversary could
   regenerate un-stored filler blocks inside the window (the work bound alone caps this at eps ~ 50-75 %, useless).
   Fixes, all measured: 64 KB blocks (`n = 2048`, same params) = 8192 nodes, 3.16 ms = 1.75x (1.96x with
   0.3 ms slack); or X = 1.6 GB (deadline 1.05 ms) keeps 32 KB blocks at 1.53x but raises `eps_max` to
   3.5 %; r = 4 at 32 KB gives only 1.89 ms (1.04x). (l=2, d=6, r=3) distinct at 32 KB: 0.83 ms (0.46x, unsound
   anyway). Requirement for the parameter owners: at X = 4 GB the block must be >= 64 KB (`l n >= 8192`
   nodes) -- K2's 64 KB fusedmm path costs +6 % e2e over 32 KB (37.5 vs 35.3 ms at B = 16, fused2.md) and
   is the price of the dedication bound; 128 KB blocks (6.3 ms, 3.5x) would restore the comfortable margin the
   phase-1 point had. The chain time is the K1 encoder's dependent-chain latency on one CTA, an upper bound on
   what a purpose-built single-chain kernel would need (6 SMEM loads + 3 double rounds + feed-forward is
   ~300-400 cycles), which is why the 2x rule is the minimum, not a comfort margin.** CPU regeneration (~65 ns/hash --
   kv_systems.md's "a CPU core is ~9x faster than a GPU thread" -- 0.4 ms per block) is fast in latency but
   its product must cross PCIe: it is a `min(200 cores x 0.5 GB/s, B_PCIe)` = 55 GB/s tier, covered by the
   locality bound. Single-block *decode* is 30 us (the consistency-opening cone, Section 6, is cheap).
3. **Serve from a copy elsewhere** (host DRAM, peer GPU, pool over RDMA, SSD): the locality bound, Section 7.
   A copy encoded under another key (pool copy under the portable key, a peer's slot) needs decode +
   re-encode under the challenged slot key = the chain of item 2 per block.
4. **Share one replica between two claims** (two slots, two GPUs): excluded by the replica id in every label.
5. **Junk KV**: `Enc(junk)` costs the same as `Enc(real)`; the accounting is satisfied (this is a proof of
   space, not of reality; reality checks are compute-as-proof's job and out of scope here).

The residual is the pebbling attack surface of the graph itself (RQ3: `eps ~ 0` for `(3,4)` in both regimes
by the phase-1 simulations) and the mixer's PRF quality (RQ4).

## 6. Consistency openings (bind R to the pre-seed comm_D) and the leak

`V_node` (holding the seed) samples a chunk `i` of a block at Poisson rate `q` and P returns the **decode cone**
of `i`: `D_i` with its path to `comm_D`, and the stored-layer labels `R_{l-1}[c]` with paths to `comm_R` for
every chunk `c` in the cone (`i`, its `d` layer-(l-1) parents, their layer-(l-2) parents, ...: `1 + d + d^2 =
21` chunks at `(l=3, d=4)`, ~22 KB with paths, or one multi-leaf proof). `V_node` recomputes `R_{l-2}[i]`,
`R_{l-2}[parents]`, ..., down to `D_i`, and accepts iff it matches the opened `D_i`. Cost: 21 hashes + 22
Merkle paths (~700 BLAKE3 compressions), ~50 us of CPU.

* **Soundness**: a prover whose `R` is inconsistent with `comm_D` on a fraction `f` of chunks (e.g. encodes
  a different `D'` there to make `R` cheap) is caught per opening with probability `f`; after `Q` openings the
  undetected fraction is `f <= ln(1/delta) / Q` (99 %: `4.6 / Q`). At `q = 1/s`: `f <= 0.13 %` after one
  hour, `5e-5` after a day. Sampling must be unpredictable (fresh randomness, random times) and must cover
  recently sealed KV pages (Section 7 sets `q_KV` per seal).
* **Leak**: exactly one chunk of `D` (32 B) per opening to `V_node`; the other opened labels are one-time-pad-
  like without the rest of their cones and cones of independent random samples essentially never overlap.
  At `q = 1/s`: 2.7 MB/day = 3.4e-5 of an 80 GB model per day (1.2 % per year). The leak goes to `V_node`
  only; if `V_node` is an HSM/TEE that outputs accept/reject, nobody learns `D`. Zero-leak alternative: a
  SNARK over the same relation (Filecoin PoRep proves exactly this; proving cost hours per 80 GB at
  admission, not pursued).
* **What consistency does not need**: the bandwidth challenge itself needs no openings (Design A) -- the MAC
  binds every byte; openings exist only to pin `R` to the pre-seed commitment.

## 7. KV pages, slot keys, re-keying, and the tag-ingest problem

KV pages are sealed at ~1000/s per GPU (32-64 KB each), loaded from the Mooncake pool at 1.7-6.7 GB per
session turn (kv_systems.md), and evicted. Tags for Design A must be computed by C from the encoded bytes,
i.e. C would have to ingest every re-encoded page: ~50 MB/s of new KV per GPU is trivial, but pool loads
(~50 GB/s per GPU on prefix hits, 400 GB/s per 8-GPU node) exceed a DPU's ingest. Two ways out, both in the
spec; the deployment picks by its C hardware:

* **Design A for static stores (weights, filler), Design B for the KV pool.** Design B = Merkle-only: no
  tags; the challenge response over KV sectors is the vector of per-sector keyed fingerprints `h_t` (mode `fp`,
  1 MB per 4 GB at 32 KB sectors; 1.9 TB/s in the current kernel, 60 % of the MAC kernel -- a warp-per-sector
  version would close the gap), and C **audits** `a` random challenged sectors per challenge: P opens them
  (32 KB + page-root path each, ~2 MB for `a = 64`), C recomputes `h_t` and the paths against the page roots
  it recorded at seal. Detection is probabilistic: `1 - (1 - eps)^a` per challenge (`a = 64`: 47 % at
  `eps = 1 %`, 6 % at 0.1 %; at 5 challenges/s that is 99 % within 1.4 s / 14 s). Cost on C: ~0.5 M mulmods +
  64 x 11 hashes per challenge (~2 ms of a core). The audited sectors leak nothing (pseudo-random `R`).
* **Design A everywhere with a bounded untagged window**: C ingests re-encoded pages as fast as it can
  (measured PCIe H2D rate, Section 7); pages not yet tagged are excluded from challenges and accounted as
  unproven, capped like `A_max` (a few GB); the cap bounds what a cheater gains.

**Seal (KV page fills):** P computes the page's `comm_D` (plaintext page hash; also the pool's dedup key),
requests `seed = PRF_K_seed(gpu, slot, epoch, comm_D)` from `V_node` (~1000 req/s per GPU, 32 B each), encodes
the page on the side stream into a second slot and flips the page table at the step boundary (kv_systems.md),
publishes `comm_R,page` to C, and (Design B) the page is challengeable as soon as C has the root; (Design A)
after C has ingested it. **Pool load (prefix hit):** the pool copy is encoded under the portable key
(`comm_D` only); P decodes and re-encodes under the destination slot's seed (kv_systems.md's model: 38-60
GB/s per GPU with an SMEM-resident encoder, so ~30-110 ms per turn start; the phase-1 bulk encoder measured
here does 6.3 GB/s at l=3 and is not the tool for this), then as for a seal. **Eviction / slot reuse:** epoch++ for the slot; the old
labels are dead (their replica id is gone) and cannot answer future challenges; C drops the slot's tags/roots.
**Filler shrink/grow** as the pool resizes: the freed filler blocks are re-keyed as KV slots (epoch++), the
reverse on shrink; a SnapDeals-style update is unnecessary because the filler needs no plaintext.

Consistency openings for pages: `q_KV` such that every sealed page has probability `>= 1 %` of one opening
during its residency (32 B of KV plaintext per opening: a fraction of one token's K or V vector in one
layer -- low sensitivity but not zero; log it).

## 8. Locality bound and parameters

`eps_max(tier) = B_tier / B_HBM,eff * (1 + slack / T)`, `T = X / B_HBM,eff`. An adversary keeping a fraction
`eps > eps_max` of the challenged store off-HBM cannot finish inside `T + slack` even with perfect overlap of
the tier fetch and the HBM read; with `eps < eps_max` it is invisible (the irreducible residual). Intermittent
covert use of the "freed" HBM for a fraction `f` of the time is caught by a Poisson challenge landing in a
covert interval: `P(detect within N s) = 1 - exp(-lambda f N)` (moving `eps H` in and out over the tier takes
`eps H / B_tier` >= 80 ms per direction at 4 GB over PCIe, so covert intervals cannot be shorter than that).

Measured tier bandwidths (pod c, `challenger2.md` 11:05 entry): pinned host DRAM -> GPU over PCIe Gen5 x16 =
55.5 GB/s with the copy engine, 51.3 GB/s for a kernel reading mapped host memory -- **the same for
sequential and for random 4-64 KB sectors**, so an adversary answers the challenge over the offloaded
fraction with the same MAC kernel, straight from host memory, at 51 GB/s. NIC (RDMA to a pool or peer node)
and NVMe hang off the same x16 link (`nvidia-smi topo`: NIC0 at PIX), so all PCIe-attached tiers together
are bounded by `B_PCIe` = 55.5 GB/s = 1.8 % of `B_HBM,eff` = 3.04 TB/s (= X / idle p50). Parameter sets:

| | 8x H100 SXM (x86 host, HGX) | GB200 NVL72 (per GPU) |
|---|---|---|
| `H`, `B_HBM,eff` (challenge kernel) | 80 GB, 3.04 TB/s (m; isolated launches) | 186 GB, ~7.4 TB/s (e: 93 % of 8 TB/s) |
| X, sector, `T` | 4 GB (5 %), 32 KB, `T` = 1.31 ms (alt.: 8 GB, 2.59 ms) | 9.3 GB (5 %), 32 KB, `T` = 1.25 ms (alt.: 18.6 GB, 2.5 ms) |
| slack (deadline - `T`) | **0.5 ms** = under-load p99.9 (0.37-0.42 over idle p50 with library kernels, 0.18 with bounded-CTA kernels) + margin (m) | 0.5 ms (assumed equal) |
| tiers | PCIe-attached (host DRAM, NIC, NVMe): 55.5 GB/s (m); peer HBM over NVLink4 450 GB/s (p; not capacity-creating under simultaneous challenges) | Grace LPDDR5X over C2C: 450 GB/s link (p), 256 GB/s per GPU when both GPUs of a superchip stream (p); NIC 100 GB/s (p) |
| `eps_max` = B_tier / B_HBM (1 + slack/T) | PCIe: 1.8 % x 1.38 = **2.5 %** (8 GB: x 1.19 = 2.2 %; 1.6 GB: 3.5 %); if the challenger must live in a separate context (slack 2.5 ms): 5.3 % | C2C: 6.05 % x 1.40 = **8.5 %** (X = 10 %: 7.2 %); LPDDR-limited: 3.4 % x 1.40 = 4.8 % (X = 10 %: 4.1 %) |
| rate | 5/s Poisson (3.8/s at 8 GB), all 8 GPUs simultaneously | 5/s, all 72 GPUs of the NVLink domain simultaneously |
| HBM time / load cost | 5 x 1.31 ms = **0.66 %** (load stalls exactly `T` per challenge, measured) | 0.63 % |
| detection | steady cheater above `eps_max`: every challenge late, 5-of-100 rule fires in 1 s; intermittent fraction `f`: `1 - exp(-5 f N)` | same |
| regeneration margin (Section 5) | phase-1 point: 3.6 ms vs 1.8 ms at 64 KB blocks (2.0x). **Security point (4,6,3) drU mixer 1: 32 KB blocks = 1.61 ms (0.89x, fails); 64 KB blocks = 3.16 ms (1.75x) -> block >= 64 KB at X = 4 GB, or X <= 1.6 GB at 32 KB (1.53x)** | same rule; B200 INT issue x1.15 only |

The tier residual on Grace systems (8.5 % by the C2C link, 4.8 % by LPDDR bandwidth) exceeds the plan's
"eps <= 5 % per GPU" target at 5 % HBM per challenge; reaching it needs the LPDDR-limited accounting (valid
when both GPUs of a superchip are challenged at once and the host has no other memory), or `X = 10 %` with
slack <= 0.3 ms (`6.05 % x 1.12 = 6.8 %`, still above), or a trusted read of the C2C link counters during the
challenge window (threat_model.md option). On x86/PCIe hosts the residual is **2.5 %**, inside the target
with margin, and 2.2 % at X = 8 GB.

## 9. What is proven, what is heuristic

Proven (given the stated assumptions): the MAC's `1/p` forgery bound and its all-or-nothing binding of the
sampled sectors (Shacham-Waters, information-theoretic in alpha); the locality bound as a consequence of
measured tier bandwidth and the measured honest response distribution (physics plus statistics, with the
decision rule's FP/FN computed from the measured tail); the sampling bounds for consistency (`f <= 4.6/Q`)
and for Design B audits; the leak accounting of Section 6; replica-id separation.

Heuristic: the mixer as a PRF keyed by the seed (RQ4; needed for "R is pseudo-random without the seed" and
for the `1/p` argument's premise that P cannot predict a missing sector without storing it); the sequential
chain time `t_hash` (a dependency-depth estimate, not measured on a GPU thread -- the regeneration margin in
Section 5 should be measured with the phase-1 encode kernel at `grid = 1` before deployment); the pebbling
tolerance of `(3,4)` (RQ3 simulations, no theorem); that the operator-controlled agent kernel cannot answer
faster than physics (it cannot) and that its only freedom, delay, hurts only itself; the trust placed in C
and `V_node` (attestation and physical protection are not designed here); the honest tail under loads other
than the ones measured (the drain-wait model -- jitter = lifetime of the load's resident CTAs -- is measured
on one H100 with CUDA 12.4 for three loads; other drivers, MIG/MPS configurations or GPUs may schedule
differently, and the slack must be re-measured per deployment); the published NVLink / C2C / LPDDR numbers
used for the peer and Grace tiers (not measured here: single-GPU pod).

## 10. Cost summary (per H100 GPU, steady state)

| component | prover | C | V / V_node |
|---|---|---|---|
| encoded replica (weights, KV, filler) | decode on read: the RQ1/RQ2 numbers (phase 1: 3.9-4.2x weights at B=16; target 1.5-2x) | -- | -- |
| bandwidth challenge, X = 4 GB at 5/s | 0.66 % of HBM time, one 1.3 ms stall per 200 ms (m) | 5 x (131 k PRF + 139 k mulmod) = 5 x 3.6 ms NumPy (m) ~ 2 % of a core; 20 MB tags | verdict log |
| admission | encode 80 GB (~13 s with the phase-1 encoder, m), stream R to C (80 GB / 55 GB/s = 1.5 s, m), Merkle roots (~0.2 s GPU) | 2e10 mulmod + 2.5 G BLAKE3 compressions once (~1 s FPGA / tens of s CPU) | seed derivation, one PRF |
| consistency openings, q = 1/s | 22 KB per opening | -- | 50 us CPU per opening; leak 32 B of D per opening (2.7 MB/day) |
| KV seal / load / evict | +1 PRF request per seal (1000/s), re-encode on pool load (30-110 ms per turn start, phase 1) | Design B: 2 MB audit ingest per challenge, page roots 32 B per page; Design A: page ingest at PCIe rate | 1000 seed PRFs/s per GPU |
| re-keying / key rotation | re-stream R to C (1.5 s per 80 GB at 55 GB/s) | recompute tags | -- |
