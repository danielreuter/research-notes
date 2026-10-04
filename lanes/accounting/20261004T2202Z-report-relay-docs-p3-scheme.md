---
id: 20261004T2202Z-report-relay-docs-p3-scheme
campaign: pous
lane: accounting
kind: report
status: closed
repo: danielreuter/verity
origin: old-accounting (bc-b729c175), relayed for @top's migration (the 44 store:pous/ files the PoUW and PoUS registries cite) from store:pous/docs/p3-scheme.md
---

> Relayed verbatim from the Cursor store by old-accounting: `store:pous/docs/p3-scheme.md`, sha256 `3045e7adfcc4a04e8c327c09deff452cbd78acc622676e3db790052680c2ee52`, unchanged since it was written before the 30 Sep snapshot, so it is also in `art:8bd64630…42e9` at that path. Only the store's `cursor:` front matter is replaced. Relative and `/cursor/stores/…` links point into that store.

# P3: layered local-decode DRG labeling with a trusted encoder

Spec, 27 Sep 2026, revised 12:50Z (band graph at k = 12, after the prover proved `columnHard_of_bounds` and `basePath_columnHard'`), following the [P3 cryptanalysis](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/docs/p3-cryptanalysis.md), the forward-only counterexample (`lean/submissions/p3-forward/NOTES.md`) and the column-saving findings (`lean/submissions/p3-column/NOTES.md`: the sampled graph has a 129-node low-depth set at d = 10, and the game gets ⌊(D+1)/2⌋ rounds). The operating graph is chosen in §2a. Lean names refer to `lean/pous` and `lean/submissions`; see the [guide](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/docs/lean-trusted-layer.md).

**Summary.**

- **The operating point below fails the deadline budget (§2b, added 15:05Z).**
  - Daniel's measurements put honest single-block answers at Δ ≥ 80–300 µs. The adversary's sequential speed must be taken at CPU or ASIC figures.
  - That gives D ≈ 240–480 oracle rounds per answer on one CPU core, and 7,000–15,000 on an ASIC. The band certificate covers only about 20–28.
  - An ASIC regenerates an entire 220 KB segment in 18–36 µs, well inside the deadline.
  - P3 at 1 KB labels is not viable. What remains is a prefill-only "P3-slow" with deliberately sequential label derivation and 8 KB labels, at roughly 1.6–1.9× prefill (est.).

- **Secure-first operating point for workstream 1 (§2c; performance deliberately ignored; corrected after `docs/p3-instantiation.md`):**
  - **Parameters:**
    - B(220, 12) with the proved certificate (X = 3 at depth 10);
    - labels of m = 65,560 B;
    - SHAKE256-based 10-round Feistel permutations: Π under a wide sponge H (rate m, capacity 512 bits, parents newest-first) and a tweakable P_T;
    - Δ = 0.5 ms strict plus the verifier's network round trip r (from the measured honest 64 KB tails), with verifier-driven sequential reveal.
  - **Margin.** A level costs 3 sequential wide calls, and one call takes at least 242 µs on a CPU core. So within 0.5 ms the adversary gets **at most 1 of the 10 certified levels**, and reaching 10 would need a Keccak-f 13.5× faster than the floor.
  - 2× holds for r up to about 2.9 ms.
  - Segment 14.4 MB, k = 132 for 1%. Decode costs about 13,200 SASS/B: roughly 2,100× at decode batch and 85× at prefill.
  - Server-side encoding is sound with a verifier-drawn salt and a verifier-computed vk.

Everything after this block describes the pre-§2b operating point, except §2c.

- **2× at decode batch is not reachable with P3.** The certifiable operating point costs about 55 ARX instructions per byte, against a 2× line of 13.1. The estimated R_seq is about 5.8×, or about 7.5× with barriers. Reaching 2× would need a fully diffusing mixer at under 0.9 ARX/B, while the measured floor for full diffusion is 3.
- **2× at prefill is reachable**, at an estimated 1.44×.
- **Security.** The pinned N10 (`InvExPostFactoTwoLayer`) is false: the transpose lets the adversary hold lower labels column by column. The corrected target, N10′, prices holdings per component and takes *column hardness* as its hypothesis (§3).
- **Operating point (decided, §2a):** the **band graph B(220, 12)**, where each node's parents are the previous 12 nodes. It replaces the sampled base path + 7.
  - It is certified by the proved `basePath_columnHard'` plus two elementary family lemmas, F1 and F2. No MILP is involved.
  - m = 8192, n = 220, L = 2, D = 20 oracle rounds (d = 10 game rounds);
  - X = 5 labels, γ = 0.042, k = 423, at 55 ARX/B;
  - the refined per-round lemma would give X = 3 and k = 229.
  - P3.1 needs λ_d ≥ m/L, and `KQ` gains (salt, segment).
- **Depth robustness.** P3 needs only d < βn at game depth d = ⌊(D+1)/2⌋, not DepthRobust(½, 0.1). k is the timing-margin knob, and k = 12 has none (§2a).
- **Unchanged:** the one-way schemes are proved end to end: `DenseMeets` (S1) and `StackedAuditSeq` (S2).

## 1. The scheme (changes marked ▲)

- **Model:** `Pous.Invertible.p3Model`, a random oracle H plus a public ideal permutation P of m-bit labels, with P^(±1) queries.
  - ▲ `KQ` must include (salt, segment index). Without them, segments with equal W get identical C (attack 3).
- **Per segment:**
  - layers V_1, V_2 of n labels;
  - white edges: a DAG G in each layer;
  - green edges: the transpose, so node v of layer 2 takes component v of every layer-1 label (w_c = m/n ≈ 37 bits);
  - W enters at V_1, and C is V_2.
- **Labels:**
  ~~~text
  c^(1)_v = P(W_v ⊕ H(salt, s, 1, v, c^(1)_(par(v)))),
  c^(2)_v = P((c^(1)_u[v])_u ⊕ H(salt, s, 2, v, c^(2)_(par(v)))).
  ~~~
- **Decode:** L = 2 parallel passes per segment: key, then P^(−1), then transpose.
- ▲ **Graph:** the band graph B(n, k), par(v) = {v − k, …, v − 1}, with k = 12 in both layers (§2a).
  - The sampled base path + 7 is *not* (1/2, 11/220)-depth-robust: MILP finds low-depth sets of 125–129 nodes at d = 10.
  - DRSample at d′ = 2 or 6 fails too.
- ▲ **P3.1 (digest keys):** needs λ_d ≥ m/L = 4096 bits. At λ_d = 1024, storing the digests alone (25% of C) answers every block in 3 rounds (attack 7). P3.0 keys on full parent labels.
- ▲ **Concrete H and P** need full diffusion, which for 32-bit ARX means 8 butterfly stages, a ≥ 3 ARX/B, and about 6 with margin (attack 6).
  - At a ≈ 1.5, an output word depends on only 16 of 256 input words.
  - If H is that light too, labels split into 16 lanes and γ becomes vacuous.
  - Naive int8-MMA is triangular and GF(2)-affine on its low plane.

## 2. Security theorem (conditional on N10′)

Let X(G, D) be the best column saving in labels per segment, and `c_lab = 2⌈log_2 Q_tot⌉ + c_0 = 118` at log_2 Q = 30.

~~~text
Theorem P3′ (target). Assume ColumnHard G ⌊(D + 1)/2⌋ n X (saving ≤ X labels per segment) and N10′. Then
  TimedINC (p3 p) D Q β* 2^−λ'',  β* = (B − N(X + 1))(m − c_lab) − log₂(2B) − λ'';
  AuditSecure .sequential (Theorem1iiSeq, proved) with p₀ = ρ + γ,
    γ ≈ (X + 1)/n + (c_lab + 1)/m,  k = ⌈ln(1/δ)/ln(1/(ρ + γ))⌉,  ε ≤ 2^−128 at λ'' = 128 + (k − 1)·log₂B;
  Meets (p3 p) .sequential D Q k ε.
~~~

γ = 0.019 + X/n. The value of X is set by the graph (§2a). Component guessing stays within c_lab only while w_c > log_2 Q, i.e. n < m/log_2 Q ≈ 270. n = 220 passes.

## 2a. Choosing the operating graph

*Cost* is P3.1 at λ_d = m/L, a = 3, L = 2: a(6 + d′) + 1 ARX/B. R_seq uses the two-pipe fits, before the roughly 30% barrier overhead. k is for 1% at log_2 Q = 30. X is an integer, as in `ColumnHard`. "Tolerated d" is the largest game depth at which the certificate still holds with γ ≤ 0.042: this is the timing margin.

| Option | Parents | Certified X at d = 10 | γ | k | ARX/B (decode / prefill) | Tolerated d (D ≤) | Lean certificate |
|---|---|---|---|---|---|---|---|
| **(a) band B(220, 12)** | 12 | **5** | 0.042 | **423** | **55** (≈ 5.8× / 1.44×) | 10–11 (20–22) | **proved theorem plus F1, F2** |
| (a) band B(220, 12), refined per-round bound | 12 | 3 | 0.033 | 229 | 55 | same | one more lemma |
| (a) band B(220, 16) | 16 | 4 | 0.037 | 298 | 67 (≈ 6.9× / 1.51×) | 12 (24) | same lemmas |
| (a) band B(220, 28), for DepthRobust(½, 0.1) | 28 | 3 | 0.033 | 229 | 103 (≈ 10.2× / 1.74×) | 14 (28) | same lemmas |
| band B(220, 10) (previous choice) | 10 | 5, with zero slack | 0.042 | 423 | 49 (≈ 5.3×) | 10 (20) | F1 fails; needs the exact count u_10 = 110 = n/2 |
| complete DAG | n − 1 | 1 | 0.024 | 157 | about 350 (≈ 32×) | above 20 | trivial |
| (b) band B(220, 7), D = 13–14 | 7 | 3 | 0.033 | 229 | 40 (≈ 4.4×) | 7 | same lemmas |
| (c) base path + 11 / + 15 / + 23 | 12 / 16 / 24 | uncertified (u_10 ≥ 106 / 96 / 83) | ≥ 0.039 | ≥ 291 | 55 / 67 / 91 | ? | MILP only |
| sampled base path + 7 (old) | 8 | uncertified: attack 3.53, family bound 5.34, mixed strategies unbounded | ≥ 0.035 | ≥ 261 | 43 | fails at 10 | not feasible (DR premise false) |
| EGS, grates, DRSample | O(log n) | — | — | — | — | — | needs a formalized expander: large |

**The certificate for B(n, k)** (prover's §4, brute-force checked for n ≤ 16):

- **F1.** A set S with |S| ≥ n/2 contains a path of at least k|S|/(n − |S| + k) nodes. At k = 12 that is 11, which exceeds d = 10. The bound is tight (blocks of k alternating with gaps of k), so k ≥ d + 1 is needed and k = 12 is the least that passes at n = 220.
- **F2.** `|L_(d−1)(L_0)| ≤ 2|L_0| + d − 1` exactly when k ≥ d − 1.

F1 and F2 feed the proved `basePath_columnHard'`, giving X = d/2 = 5. For larger k, the exact low-depth count (runs of d separated by gaps of k) through the proved `columnHard_of_bounds` gives X = ⌈u_d (d−1)/n⌉: 4 at k = 16 and 3 at k = 28.

**Does P3 need DepthRobust(½, 0.1)? No.** Its only depth hypothesis is `basePath_columnHard'`'s: DepthRobust(½, β) with d < βn at game depth d = ⌊(D+1)/2⌋, i.e. βn ≥ 11. Alternatively, `columnHard_of_bounds` needs just the low-depth bound at depth d.

The 0.1 came from the superseded whole-label route (Theorem P3 with D < β_DR n and an illustrative β_DR), and from the stacked one-way audits S2 (the bridge's D + 1 ≤ βn). Neither is on P3's path.

**What k buys is timing margin.** For the band, βn ≈ k regardless of n. So k fixes the largest adversary depth the certificate survives: k = 12 holds only up to d = 10 (or 11 via the exact count), which means *no* slack if τ_min is even 10% optimistic. But the column saving grows with d for every k, and at n = 220 it makes γ vacuous beyond d ≈ 14. So the most margin any band can buy is about 1.4× in adversary speed (k = 28, D ≤ 28), at almost twice the cost.

**Recommendation: B(220, 12) at D = 20.**

- It is the cheapest graph with a kernel-checkable certificate built on theorems already proved: `basePath_columnHard'` plus F1 and F2, moderate effort.
- The certified values are X = 5, γ = 0.042 and k = 423, which is about 2.1 ms of sequential answers at Δ = 5 µs. The refined lemma brings k to 229.
- Cost is 55 ARX/B, versus 49 for k = 10, which has zero slack and needs a sharper count.

Two conditions:

1. Track C must bound τ_round and the honest latency before this is pinned. If any margin is needed, take B(220, 16): d ≤ 12, 67 ARX/B.
2. k = 28 only makes sense if a roughly 1.4× speed margin is mandated.

The complete DAG is the trivially certified fallback, but it costs about 32×. The sampled and random-parent graphs are dropped: they cannot be certified, and they are no better at the same degree.

## 2b. Deadline budget (15:05Z)

**Inputs.** From Daniel's prior measurements (`internal/prior-gpu-notes.md` §4):

- **Honest answers.** Tiny probes (one sector to pinned host memory) have p50 of about 10 µs, p99.9 of 73 µs under load, and a maximum of 266 µs. A strict all-on-time policy needs Δ ≳ 300 µs. A policy that tolerates a few late answers, paid for in k, can use Δ ≈ 80–100 µs.
- **Adversary.** Its sequential step must be priced at CPU or ASIC speed, not GPU speed: a light ARX hash takes 58 ns on one Xeon core and 5–10 ns on an ASIC.
- **Precedent.** The previous design failed exactly this check (a 1.61 ms regeneration chain against a 1.81 ms deadline).

The latencies below are my estimates from before `docs/p3-instantiation.md` landed; §2c uses its measured primitives.

**Latency of one P3 label level** (H then P; the game's depth d counts levels, and a level is 2 oracle rounds). The conservative primitives are:

- P is a 1 KB ARX permutation with 8–16 butterfly stages for full diffusion. That is about 2 dependent ops per stage at 0.15 ns on an ASIC, and about 32 cycles per stage for 16 AVX-512 registers on one CPU core.
- H is either a **sequential sponge** or a tree hash. The sponge has rate 512 B over the same permutation and absorbs the newest parent first, so all 12 absorptions sit on the critical path. That overcounts: when the oldest parent arrives last, a level costs 3 calls (§2c). The correction only widens the gap below.

| Adversary | H | Per level | d at Δ = 300 µs (80 µs) | D = 2d at 300 µs | Regenerate a whole segment (440 levels) |
|---|---|---|---|---|---|
| ASIC | sponge, P3.1 (12 digests of 512 B) | 41–82 ns | 3,700–7,300 (980–1,960) | 7,400–14,700 | **18–36 µs** |
| ASIC | sponge, P3.0 (12 full labels) | 65–130 ns | 2,300–4,600 | 4,600–9,200 | 29–57 µs |
| ASIC | tree | 17–34 ns | 8,900–17,900 | above 17,000 | 7–15 µs |
| one CPU core | sponge, P3.1 | 1.2–2.5 µs | 120–240 (32–64) | 240–480 | 0.55–1.1 ms |
| one CPU core | sponge, P3.0 | 2.0–3.9 µs | 77–150 | 150–300 | 0.9–1.7 ms |

The band certificate tolerates d ≤ 10 at k = 12, and at most about 14 for any band at n = 220 (§2a). So the gap is 3–700×. Two consequences:

- The coarser "regeneration versus deadline" check fails outright against an ASIC: the adversary can store nothing and rebuild each challenged segment. Against a CPU it passes by only 1.8–3.7×.
- The column certificate is about 40× stricter than that check (d ≈ 10 of a 440-level chain).

**What would restore P3.** One floor applies to every "slow round" design. With t_op the fastest dependent-op latency (0.15 ns on an ASIC, about 0.28 ns on a CPU), honest decode must perform at least LΔ/(d_max t_op m_bytes) inherently sequential operations per byte. The honest decoder parallelizes across labels, but each label's chain is sequential for everyone.

1. **Larger segments or higher degree.** For the band, tolerated depth is d < k regardless of n, with n ≳ max(22d, 2dk/(k−d)) for γ and F1, and cost ≈ a(6+k) + 1.
   - CPU, d ≈ 240: k ≈ 480, 5 MB segments, about 1,500 ARX/B.
   - ASIC: k in the thousands, 100 MB-scale segments.
   - **Dead.** Sparse depth-robust families would lower the degree, but they still need MB-scale segments and a formalized expander.
2. **Deliberately slow sequential rounds.** Put a tweaked hash chain in each label's key derivation (its ROM sequentiality is B3, proved), sized so that one level takes at least Δ/d_max on the fastest allowed hardware. With 1 KB labels the floor is 390 ops/B (ASIC, 300 µs), 104 (ASIC, 80 µs), 209 (CPU, 300 µs) or 56 (CPU, 80 µs). **Dead at decode batch.**
3. **Bigger labels, combined with option 2.** The floor falls as 1/m. At 8 KB labels it is 49 (ASIC, 300 µs) or 13 (ASIC, 80 µs) ops/B; at 32 KB, 12 or 3.3.
   - Segments grow to 220 × m: 1.8 MB, i.e. a portable 8-CTA cluster's DSMEM, at 8 KB; 7 MB, i.e. L2 with multi-pass decode, at 32 KB.
   - Full diffusion needs more stages (a ≈ 4.1 at 8 KB), so the base is about 75 ARX/B.
   - **Best case:** 8 KB labels at Δ ≈ 80 µs against an ASIC gives about 90 ARX/B, roughly 1.6× at prefill and about 8× at decode, plus cluster synchronization (est.).
4. **Sequential reveal with batched answers** does not change D: the adversary gets the same wall time per answer and works on all k in parallel. Batching only cuts the honest round trips. What does shrink Δ is the tolerant late-answer policy (3–4×) with bounded-CTA serving kernels.
5. **Excluding ASIC and FPGA responders** (by attestation or physical argument) cuts D by about 20×. Even then d ≈ 32–64 at 80 µs, which still needs option 2 or 3.

**Is P3 viable?**

- **Not at decode batch.** It was about 5.8× before timing, and meeting the deadline adds at least about 100 ops/B or segments too large to fuse.
- **At prefill, only as "P3-slow":** 8 KB labels, a per-label sequential chain sized for the fastest allowed adversary, the tolerant Δ ≈ 80 µs, and 1.8 MB cluster-resident segments. Estimated at about 90–125 ARX/B, i.e. 1.6–1.9× prefill.
- Its proof reuses N10′ and the band certificate, with one change: a label level costs c oracle rounds, so the game gets ⌊(D/c + 1)/2⌋ levels, with B3 supplying the chain's sequentiality.
- It adds one timing assumption: the chain step's minimum latency on the allowed hardware.

**Recommendation.** Mark the §2a operating point invalid, and stop P3 for decode-time weights. Keep P3-slow as the prefill candidate, pending three Track C measurements:

1. honest single-block answer tails under a tolerant policy with bounded CTAs;
2. the chain step's latency on one CPU core and on an FPGA;
3. the cost of decoding 1.8 MB segments in cluster DSMEM.

§2c reconciles these latencies with `docs/p3-instantiation.md`.

## 2c. Secure-first operating point (workstream 1; corrected after `docs/p3-instantiation.md`)

**Daniel's decisions.** Get P3 working end to end with proved security; performance doesn't matter. The adversary's step is the faster of one CPU core and one GPU core (no ASIC). Answers are strict: all on time.

**Deadline: Δ = 0.5 ms on the server-side path, plus the verifier's network round trip r and its jitter.** This is set by the measured honest 64 KB tails ([`docs/p3-gpu-measurements.md`](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/docs/p3-gpu-measurements.md), L40S under load).

- Device-side, the maximum was 288 µs, and none of 190,000 steady-state rounds exceeded 0.29 ms.
- The earlier 300 µs is only 4% above that maximum. It fails about 1.5% of honest audits on the harness host clock.
- 0.5 ms assumes a native responder in the serving process, on a high-priority stream.
- r has not been measured. The adversary is charged the whole allowance T = 0.5 ms + r, since the real transit may be shorter.

The primitives and CPU latencies come from [`docs/p3-instantiation.md`](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/docs/p3-instantiation.md) (its §1–2 is the byte-exact spec; latencies measured on this VM). This version fixes two errors in the 15:20Z draft:

- a level costs 3 sequential calls, not 13;
- the ARX butterflies the draft chose leave about 1.7× on one core and fail on one SM at 300 µs, and fail outright at 0.5 ms.

**Construction.**

- **Graph.** B(220, 12) in both layers, with the transpose connector. Certificate: the proved `band_twoWay_220_12`, X = 3 at game depth 10. This needs a trivial monotonicity lemma: `ColumnHard` at depth 10 implies it at any smaller depth.
- **Labels.** m = 65,560 B = 220 × 298 B, so w_c = 2,384 bits (width confirmed below).
- **Segment tag.** tag_s = salt ‖ u64(s), 32 B. The 24-byte salt is drawn by the verifier after W is committed. The tag is injective, which is the (salt, segment) fix to `KQ`.
- **Π and P_T.** Both are 10-round Feistel networks with SHAKE256 round functions.
  - Π acts on m + 64 B, is untweaked, and has domain byte `0x48`.
  - P_T acts on m B, with domain byte `0x50` and the tweak T = tag_s ‖ ℓ ‖ v inside every round function.
  - Security rests on SHAKE256 as a random oracle plus the published Feistel indifferentiability proofs: 10 rounds, and the keyed ideal-cipher form for the tweak.
- **H.** A standard sponge over Π: rate m, capacity 512 bits, IV 0.
  - It absorbs a header block B_0 (domain string, tag_s, ℓ, v, number of parents), then the parents **newest-first** (`c_(v−1), …, c_(v−12)`), then one pad10\*1 block. The key is the rate part of the final state.
  - This is fix (a) of the narrow-state finding. Every intermediate state and every key is at least m bits, so a cached state costs as much as a label. The digest variant P3.1 stays dropped.
  - The header replaces the draft's IV(salt, s, ℓ, v). A rate IV is XORed into the first parent, so (h, c) and (h′, c ⊕ h ⊕ h′) would collide.
- **Labels.** `c^(1)_v = P_(tag_s, 0, v)(W_v ⊕ H(tag_s, 0, v, c^(1)_(par(v))))` and `c^(2)_v = P_(tag_s, 1, v)(transpose(c^(1))_v ⊕ H(tag_s, 1, v, c^(2)_(par(v))))`.
- **Honest work.** 14 Π calls plus 1 P_T call per label per layer, in parallel across labels.

**A level costs 3 sequential calls, not 13.** Newest-first costs the honest decoder nothing, but it does not put all 12 absorptions on the adversary's critical path.

- If the input that arrives last is the oldest parent `c_(v−12)`, the other 11 parents are absorbed in advance. The level then costs `Π(c_(v−12))`, Π(pad) and P_T.
- A sparse dropped set, such as every 12th node, recovers entirely through such edges.
- A top whose key is ready costs 1 call.

So with D wide calls per answer, the adversary gets d = ⌊(D−1)/3⌋ + 1 levels, and depth 10 takes D = 28. Newest-first stays because it is free, but it gets no credit until a weighted certificate exists.

**Timing at T = 0.5 ms (i.e. r = 0).**

- A SHAKE-Feistel call is serial. Each of its 10 rounds absorbs and squeezes half a label through one Keccak-f chain: 4,830 Keccak-f calls at this width. More cores don't help, unlike ARX butterflies or tree hashes.
- Keccak-f measured 244 ns on one Xeon core. The sizing floor is 50 ns, which is 5× below the measurement and about 2× below AVX-512 XKCP.
- A GPU thread takes 1–2 µs per Keccak-f, so the CPU core sets the step.
- In the table, "Speed-up to reach d = 10" is how much faster the adversary's step must get to fit 28 calls in T.

| Wide permutation, m = 65,560 B | Faster with more cores? | t_call | d within T (certified: 10) | Speed-up to reach d = 10 |
|---|---|---|---|---|
| **Feistel-10, SHAKE256 (chosen)** | no (serial sponge) | 242 µs at the floor, 1.18 ms measured | **1** (D = 2; 0 measured) | **13.5×** (66× vs measured) |
| Feistel-10, SHA-256 (SHA-NI) | output lanes | 130–180 µs | 1 | 7–10× |
| Feistel-10, BLAKE3 | tree chunks | 9–25 µs | 7–19 | **fails** (at most 1.4×) |
| ARX butterfly, 28 stages (the 15:20Z draft) | every stage | 11.1 µs measured per CPU core (`p3-gpu-measurements.md` §4), 9 µs per SM (est.) | 15 per core, 19 per SM | **fails** |

The ARX row corrects `p3-gpu-measurements.md` §4 too: that section's d_phys = 4 at 0.5 ms still charges 13 calls per level.

**Resulting margin.** At the floor, the adversary finishes 2 wide calls per answer, fewer than the 3 that one recomputed level costs, so it gets at most 1 of the 10 certified levels.

- Reaching depth 10 needs 28 calls in 0.5 ms, i.e. a Keccak-f of 3.7 ns or less. That is 13.5× below the floor and 66× below the measurement. Daniel's 2× requirement holds with a 6.8× reserve.
- The margin falls as 28 × 242 µs / T = 6.76 ms/T with the round-trip allowance. The certificate itself (D ≤ 30) holds up to T = 7.5 ms.

| Round-trip allowance r | T | D | d | Speed-up to reach d = 10 |
|---|---|---|---|---|
| 0 (on-node verifier, µs-scale) | 0.5 ms | 2 | 1 | 13.5× |
| 0.5 ms | 1.0 ms | 4 | 2 | 6.8× |
| 1.5 ms | 2.0 ms | 8 | 3 | 3.4× |
| **2.9 ms (the 2× limit)** | 3.38 ms | 13 | 5 | 2.0× |

So the 64 KB point meets 2× for any verifier round trip up to about 2.9 ms. The draft's "3.3–5×" was wrong on both counts.

**Label width: m = 65,560 B confirmed.**

- It is the byte-aligned multiple of n nearest 64 KB (220 × 298 B). Components are whole bytes, and w_c = 2,384 bits ≫ log_2 Q (the §2 condition n < m/log_2 Q).
- Per-byte cost does not depend on the width: a Feistel-10 call is about 440 SASS per label byte at any m. Width trades only segment size and latency floor against timing margin.
- Timing alone needs less. For serial sponges t_call ≈ (m/13.6 B) × 50 ns at the floor. So 2× needs m ≳ 19.4 KB per ms of T: about 10 KB at T = 0.5 ms, and the full 64 KB only at T ≈ 3.4 ms.
  - The 8 KB variant (m = 8,140 B) no longer meets 2× at 0.5 ms: d = 6, 1.7×.
  - 16.5 KB (m = 16,500 B = 220 × 75 B, 3.6 MB segments) gives d = 3 and 3.4× at T = 0.5 ms, with 2× up to T ≈ 0.85 ms.
  - 1 KB fails.
- **Keep 64 KB for workstream 1.** It is the only width that keeps 2× without knowing r, since it tolerates up to about 2.9 ms. The 13.5× at r = 0 also covers any error in the floor.
- 16,500 B is the fallback, if r turns out small and 64 KB answer tails or 14 MB segments block the end-to-end tests.

**Chosen point:** n = 220, k = 12, m = 65,560 B, SHAKE-Feistel Π and P_T, wide sponge H with newest-first absorption, Δ = 0.5 ms strict plus the verifier's round trip.

- **Margin:** d ≤ 1 of 10 certified levels at T = 0.5 ms, and 13.5× in Keccak-f speed over the floor. The 2× requirement holds for r ≲ 2.9 ms.
- **Segment:** 220 × 65,560 B ≈ 14.4 MB (the stored top layer), plus a transient lower layer during decode. That is about 4,850 segments at 70 GB.
- **Decode:** 2 × 15 wide calls per label, about 13,200 SASS/B (11,000–16,600), priced single-pipe.
  - That is roughly **2,100× at decode batch and 85× at prefill**, or about 1 s of decode per GB of weights per forward pass (est.).
  - A segment's latency floor is 30 sequential wide calls, about 0.2 s on a GPU, with all segments running in parallel.
  - This is enough for end-to-end tests on a small model (Qwen2.5-0.5B).
- **Encode** (by the server, and again by the verifier or a trusted GPU for vk): the same total work as one decode pass.
  - Each segment is a chain of 2 × 220 × 15 = 6,600 calls: about 8 s on one CPU core at the measured Keccak-f, about 45 s on one GPU thread.
  - With segments in parallel, that is about a minute for 70 GB on one H100 (est.).
- **Audit:** k = 132 for 1%, unchanged. `γ = 4/220 + 73/524,480 = 0.0183`, with c_lab ≈ 72 at B ≈ 2^20 and Q = 2^14. At this width the c_lab term is negligible, so X sets k.
- **vk:** the root of a SHA-256 Merkle tree over the top labels, with leaf `SHA256(0x00 ‖ tag_s ‖ v ‖ c^(2)_v)`.
  - An answer is the 65,560 B block plus about 21 × 32 B of path.
  - Measured honest 64 KB answers (L40S, under load, device clock) have p50 17–42 µs, p99.9 30–93 µs and a maximum of 288 µs. There are no H100 data at 64 KB yet.

*ASIC, out of scope by Daniel's decision:* an unrolled Keccak-f at 2–5 ns gives t_call = 10–24 µs. At T = 0.5 ms that is d = 7–17, past the certificate at the fast end.

**Reveal mode.** With a 242 µs wide call, all three modes fit. The choice rests on honest tails and the Lean game.

| Mode | Honest | The adversary's budget per answer | At m = 65,560 B, r = 0 |
|---|---|---|---|
| **Verifier-driven sequential, strict Δ = 0.5 ms + r per answer** | measured 64 KB: maximum 288 µs device-side; none of 190,000 steady-state rounds above 0.29 ms | T = 0.5 ms + r, so D ≤ 2 | **d ≤ 1, 13.5×; the Lean `SeqResponder` game exactly** |
| (a) all at once, one Δ_all for all k blocks | 8.7 MB over PCIe, about 0.18 ms. At 6.8 MB the measured p99.9 is 0.22 ms and the maximum 0.58 ms, so strict needs Δ_all ≈ 1 ms + r | the whole Δ_all for every answer, so D ≤ 4 | d ≤ 2, 6.8×; the `SimResponder` game |
| (b) hash-chained on the GPU (next index = H(answer)) | about k × 5 µs locally, with no network round trips; unmeasured | the pooled slack (about 0.5 ms, set like Δ), spendable on one answer, so D ≤ 2 | d ≤ 1, 13.5×; needs a pooled-budget game |

**Use verifier-driven sequential reveal with strict Δ = 0.5 ms plus the verifier's round-trip allowance.** It has measured honest tails and matches the pinned Lean game. The audit takes 132 × (one answer plus r), a few ms plus 132r.

- (a) is now a valid fallback if round trips matter.
- (b) remains the performance follow-up once measured.

**Server-side encoding: confirmed**, under three conditions:

1. the server commits to W (a hash) before any salt exists;
2. the verifier draws the 24-byte salt in tag_s uniformly after the commitment;
3. the verifier (or a trusted GPU) computes vk from its own Enc(W, salt) and never accepts it from the server. Optionally it compares its Merkle root with the server's C at setup, which catches a wrong encoding deterministically rather than by audit sampling.

P3's encoder is deterministic and public given (W, salt, the public primitives), and has no secret to erase. The timed game's adversary already sees ω and has unbounded preprocessing, so it can run Enc itself. Having the server compute Enc changes nothing in the game, and the Lean model's `enc` with a uniform salt in `Coins` describes it exactly. What would break it is a server-chosen or server-predictable salt, which breaks the model's "W before coins" order.

**New nodes for the lemma DAG:**

- **the Lean model change:**
  - two ideal permutations, Π and a tweakable P_T (an ideal cipher keyed by T);
  - H defined as the sponge, with header and padding;
  - `KQ` = tag_s;
- the ideal-permutation-model sponge lemma: full-width intermediate states give no saving (the pilot re-proof of the dense scheme has started);
- **the round count:** a level costs 3 wide calls (oldest parent last), and a top whose key is ready costs 1.
  - So N10′ assumes `ColumnHard G (⌊(D−1)/3⌋ + 1)`.
  - Here D ≤ 2 at T = 0.5 ms (and D ≤ 13 at the 2× limit T = 3.38 ms). The depth-10 certificate is margin.
- depth monotonicity of `ColumnHard`;
- **the named assumption:** Keccak-f is an ideal permutation (SHAKE256 a random oracle), carried into P3's multi-stage storage game.
  - RSS shows this step is not automatic. The argument is that no data path narrows below the full width.
  - Feistel indifferentiability (ePrint 2015/876, 2015/874) is imported, not formalized.

**Measurements that would move the point:**

- **the verifier's network round trip r and its jitter:** this sets T, and it decides between 64 KB and the 16.5 KB fallback;
- Keccak-f latency on one Xeon 8470 core, and a lane-parallel Keccak-f on one SM. These confirm the 50 ns floor, and that the GPU does not set the step.
- honest 64 KB tails on an H100, with a native in-process responder under vLLM serving (the L40S runs used a Python harness and synthetic loads);
- SHAKE-Feistel decode and encode throughput on an H100, against the 13,200 SASS/B estimate.

A DSMEM cluster no longer matters: the serial sponge gains nothing from more cores.

## 3. The corrected central node, N10′ (column-aware)

**Why the old N10 fails.** A top label needs only component v of each lower label. The adversary drops top labels on a shallow set U, and stores their columns only on lower nodes outside a set R it can rebuild from W in time. That costs n − |U||R|/n labels. White/green pebbling instead charges the same strategy (n − |U|) + (n − |R|) pebbles, because a lower pebble is worth only |U|/n of a label to this adversary.

No inverse queries are involved, so bounding P^(−1) use cannot help. Depth robustness plus (H) doesn't bound it either: the counterexample graph has 40% sources and a complete core, and it loses 18%. The prover's counterexample instead guesses single components at cost 2^(−w_c).

**The target statement:**

- **Column game** Γ_col(G, D).
  - Holdings: whole top labels at cost 1, and lower components (w, u) at cost 1/n each.
  - Moves:
    - forward on a lower label (needs its whole key parents; W is free);
    - forward on top label u (needs its whole key parents and component u of every lower label);
    - reverse from top u plus its key (yields component u of every lower label).
  - `ColumnHard G s D`: from weight at most s, not all n top labels within D rounds.
- **N10′.** `ColumnHard G s D` implies B5's bound with exponent s + 1, where freshness is charged **per P-input**, i.e. per whole column, m bits. That keeps the per-item loss at c_lab/m rather than c_lab/w_c.
  - Charging per component would lose c_lab = 118 ≫ w_c = 37 bits per component, and the bound would be vacuous.
  - Needs w_c > log_2 Q.
- **N10′a (column Claim 12).** An upper bound on X(G, d) over *all* column strategies, in game rounds d = ⌊(D+1)/2⌋. **Proved** as `PousP3Column.columnHard_of_bounds` (a low-depth bound u plus a rebuild bound gives X), and as `basePath_columnHard'` (DR(½, β) with d < βn, plus the rebuild bound F2, gives X = d/2). Depth robustness alone doesn't bound strategies that hold lower labels whole, so the rebuild hypothesis is needed. For the band graph both are elementary (§2a).

**Does the trusted encoder help?** Unchanged: fully on the pebbling side (no red pebbles), yes on extraction (W is fixed before the oracle), not on the core. The column attack also works with a free W, which is the worst case the game must allow.

**Ways to avoid the transpose altogether** (option 2 of §7): connectors that move whole labels (a whole-label permutation network, or ZigZag's identity edges) give X = 0. The cost is log n extra passes, or losing the formalized Claims 12–14 route, since ZigZag's analysis in Fisch §4 has not been formalized.

## 4. What is proved end to end (one-way labels)

| Scheme | W lives on | C stores | Challenges over all of C | Rate | Decode | Status |
|---|---|---|---|---|---|---|
| S1, dense single layer | every node | every label | yes | 1 | hashes every earlier label: Θ(n_seg)/B | **done**: `Pous.Pinned.DenseMeets` (PASS) |
| S2, SDR-shaped stack | last layer | last layer | yes | 1 | re-derives the lower layers (slower than the deadline) | **done**: `StackedAuditSeq`, `StackedAuditOnePercent` (PASS) |
| S3, stack with all labels stored | every node | every label | no | 1 | local | fails tightness (`b1_free_fraction`) |

## 5. The lemma DAG

| # | Node | Status | Lean |
|---|---|---|---|
| N1 | `p3Model`, labels | **done**, but ▲ `KQ` must add (salt, s) | `Pous.Invertible` |
| N2 | `Correct`, `SpaceBound`, `CodeHoldsW` | to state (routine) | — |
| N3 | Transpose facts | **done** | `TransposeMixing`, `ReverseNeedsAllChildren` |
| N4 | Band B(n, k): F1 (DR(½, β) with βn ≥ k\|S\|/(n − \|S\| + k)) and F2 (rebuild bound iff k ≥ d − 1), then `norm_num` at n = 220, k = 12, d = 10 | to state (moderate: gaps of a sorted finset, runs with time labels); brute-force checked n ≤ 16 | feeds `basePath_columnHard'` |
| N4r | Refined per-round bound: band X = 3 | to state | — |
| N5–N8 | Claims 12–14; no red pebbles (★). Off P3's critical path now; used by S2. | **done** | `B2Stacking`, `FischClaim13`, `FischClaim14` |
| N9 | B5 (one-way) and the bridge | **done** | `B5ExPostFactoBounded`, `PousBridge.b2ToB5` |
| N10 | Old invertible reduction (white/green hypothesis) | **refuted** (column attack; forward-only counterexample; red team verifying) | `InvExPostFactoTwoLayer`: withdraw it and the named assumption `InvertibleLabels` |
| **N10′ ★★** | **Column-aware reduction** (§3) | **to state** | — |
| **N10′a** | ColumnHard from a low-depth bound plus a rebuild bound (any DAG), and the base-path corollary; N10′ assumes `ColumnHard G ⌊(D+1)/2⌋` | **done** (three axioms, kernel-replayed) | `PousP3Column.columnHard_of_bounds`, `basePath_columnHard'`, `lowerReach_basePath_empty` |
| N12 | Weighted digests: no gain iff λ_d ≥ m/L (attack 7 is tight) | to state | — |
| N14 | ColumnHard + N10′ + averaging over segments give TimedINC | to state | — |
| N15 | Theorem 1(ii), sequential | **done** | `Pous.Pinned.Theorem1iiSeq` |
| N17 | Parameter certificate and `Meets` for B(220, 12): X = 5, k = 423 (229 with N4r) | to state | `Pous.Meets` |

## 6. Cost after the fixes

With a ARX/B per fully diffusing pass (a ≥ 3) and L = 2:

- P3.1 at λ_d = m/L: digest, key absorb (d′/L passes), key squeeze and P^(−1), which gives a(3L + d′) + 0.5L;
- P3.0: L((d′ + 2)a + 0.5).

The estimated R_seq uses the report's two-pipe fits at b ≤ 8 and the prefill slope at b = 8192. Add about 30% for barriers at decode batch.

| Variant | d′ | a | ARX/B | decode b ≤ 8 | prefill |
|---|---|---|---|---|---|
| **P3.1, band B(220, 12) (operating point)** | 12 | 3 | **55** | **≈ 5.8×** | ≈ 1.44× |
| P3.1, band B(220, 12), with diffusion margin | 12 | 6 | 109 | ≈ 10.7× | ≈ 1.78× |
| P3.1, sampled base path + 7 (uncertifiable) | 8 | 3 | 43 | ≈ 4.7× | ≈ 1.36× |
| P3.0, band B(220, 12) | 12 | 3 | 85 | ≈ 8.5× | ≈ 1.63× |
| P3.1 with a certified d′ = 2 DR graph (none known) | 2 | 3 | 25 | ≈ 3.1× | ≈ 1.25× |

**Verdict.** The 2× line of 13.1 ARX/B needs a ≤ 12.1/(6 + d′): 0.67 at the band's d′ = 12, and 1.5 even at d′ = 2. Both are below the full-diffusion floor a ≥ 3. So **2× at decode batch is unreachable with CUDA-core ARX mixing for any d′ or L**. 2× at prefill is reachable (1.3–1.9×).

## 7. What would restore 2×

1. **Tensor-core mixing.** Implement H and P as int8-MMA layers with nonlinear steps between them, keeping the int32 side at about 1 instruction/B or less and the MACs at about 200/B or less. They need full diffusion at under 0.9 ARX-equivalent per byte. This is the only single lever that reaches 2×. It is unanalysed: naive MMA is affine and triangular (attack 6).
2. **Different graphs and connectors.**
   - Cost grows with d′, and the band needs k ≥ d + 1 (F1 is tight). Any certified graph with d′ ≤ 2 at d = 10 would cut the cost to about 25 ARX/B. None is known: band-like graphs need about d parents, and sparse expander families (EGS, grates) would need a formalized expander. That is still above the line unless combined with option 1.
   - Whole-label connectors remove the column loss (X = 0, k back to 135) but add passes.
3. **Fewer passes per layer.** Merge the key squeeze into a tweakable wide permutation keyed by the parents' digests, giving a(2L + d′). This still needs a ≤ 1.2 at d′ = 2, so only together with option 1.
4. **Relax the regime:**
   - prefill-only certification, which fits now at 1.3–1.9×;
   - partial coverage, R = 1 + φ(R_c − 1), which reaches 2× at φ ≈ 1/(R_c − 1) ≈ 20%;
   - accept about 5× at decode batch, which is about drU's measured cost but with a proof path.
5. **Open problems, in order:**
   1. state N10′ with the ⌊(D+1)/2⌋ round fix;
   2. prove N4 (band F1 and F2 at k = 12), then N4r;
   3. withdraw `InvExPostFactoTwoLayer` and `InvertibleLabels` once the red team confirms;
   4. fix `KQ`;
   5. Track C: measure a tensor-core mixer, and a fully diffusing 3/B ARX pass.
