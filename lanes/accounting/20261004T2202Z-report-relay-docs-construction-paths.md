---
id: 20261004T2202Z-report-relay-docs-construction-paths
campaign: pous
lane: accounting
kind: report
status: closed
repo: danielreuter/verity
origin: old-accounting (bc-b729c175), relayed for @top's migration (the 44 store:pous/ files the PoUW and PoUS registries cite) from store:pous/docs/construction-paths.md
---

> Relayed verbatim from the Cursor store by old-accounting: `store:pous/docs/construction-paths.md`, sha256 `a3e2af321381e471d7b3cc6b9b8b8a18a7cf92b79101fead02e106060379a18c`, unchanged since it was written before the 30 Sep snapshot, so it is also in `art:8bd64630…42e9` at that path. Only the store's `cursor:` front matter is replaced. Relative and `/cursor/stores/…` links point into that store.

# Construction paths toward a proved timed POUS

Research memo, 27 Sep 2026. Target: [problem statement](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/docs/problem-statement.md) (timed game, perfect isolation, trusted encoder, public bit-exact decode, ρ = 18/19, 1.05 space, Δ ≈ 1 ms). Sources: [POUS audit](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/docs/pous-audit.md), the report `research/paper4/report.md`, and the sms5 memos under `internal/sources/porep-inference/` (the sms5 memos are unreviewed and are cited as such). Cost figures are H100, batch ≤ 8, fused decode-then-GEMM, from the report's §5 unless marked *est.* The budget at the 2× line is about 8 IMAD-priced int32 slots per byte, or 13.1 ARX instructions per byte under the measured two-pipe rule; after a ChaCha8 offset about 4.5 slots remain.

## Bottom line

> **Update (27 Sep, 08:36 UTC), from the [sms5 ideal-model review](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/docs/sms5-review-ideal.md):** P1 at w = 2048 fails the target game. Factoring costs about 2^112, which is inside the 2^128 preprocessing budget, and the factors then answer any challenge with two square roots in about 0.3 ms. P1 needs w ≥ 3072 (raising its decode cost), a lower preprocessing cap, or a shorter deadline plus a sequentiality assumption. Its ideal-model proofs hold with conditions. The [sms5 reductions review](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/docs/sms5-review-reductions.md) confirms the break independently. It puts 3072 bits at the edge of the budget, needs about 3300–3500 bits for real margin, and costs design (a) at 190 int32/B at 3072 bits, above the 150 int32/B prefill budget. So P1's prefill-only fallback also fails as costed. The P3/P4 ranking is unaffected.

A deadline helps substantially with a trusted encoder, but not where the report looked. It cannot shrink anything an offline attacker sets: modulus sizes, lattice or DCR parameters, the lossy-mode indistinguishability of any Moran–Wichs-style proof. So it never brings a per-block trapdoor design below the roughly 68 int32/B cost of one 2048-bit modular multiplication. What it does, precisely, is this:

- It caps every brute-force completion at log_2 Q ≈ 20–34 bits instead of 100–128. That makes about 2-kbit blocks viable, and at 2048 bits it turns RW–SMS from untimed-marginal-to-false into a candidate.
- It kills expensive online reconstruction: large-dimension Coppersmith, the two-layer lattice route, and table-free kangaroo walks. For two-round Rabin designs this opens a structural margin of about 0.2w that does not exist untimed.
- Above all, it makes **trapdoor-free sequential encodings** admissible, and those are the only family within about 2–3× of the cost budget. In them every compact state can only be expanded by a long chain of hash calls, as in depth-robust labelings.

The report's claim that a deadline "does not repair RSA because the compression is bought offline" is only half right. By its own Proposition 6 the kangaroo step is online, so a deadline caps RSA's loss at about 2 log_2 Q + 20 ≈ 80 bits (versus 204). RSA stays dead on cost regardless.

My ranking puts first the sequential local-decode encodings with proofs in the parallel random-oracle model: layered ZigZag/DRG across blocks (P3), and its in-block variant (P4). Next is timed RW–SMS as the proof-infrastructure and prefill-only path (P1). Tensor-core mixing (P5) is the enabler that could close the remaining 2–3× gap. Two parts of the time model decide the parameters of the leading paths. First, the per-answer deadline: the measured drU stack is only safe up to about 130–370 µs, not 1 ms. Second, which hardware sets τ_min. Both are underspecified today (§5).

| Rank | Path | Model / assumption | Role of the deadline | Decode cost vs budget | Proof status, Lean fit | Verdict |
|---|---|---|---|---|---|---|
| 1 | **P3** Layered local-decode DRG (ZigZag / drU class) | parallel ROM; depth-robust graphs | the whole security | drU(4,6,4): 30 ARX/B, **4.52× measured**; needs about 2.3× cheaper | pROM proofs exist for ZigZag (Fisch) and data-carrying labelings (Pietrzak); combinatorial core Lean-friendly | pursue |
| 2 | **P4** In-block sequential wide permutation (32–128 KB tiles) | parallel ROM on small graphs; ideal slow-inverse permutation | the whole security; needs per-answer Δ ≲ 50–150 µs | *est.* 8–16 ARX/B (2–4 passes), 1.6–2.4× | M1 counting reused; small-graph pebbling certifiable | pursue |
| 3 | **P1** Timed two-round Rabin–Williams (RW–SMS / design (a)) | ideal permutation + RW-IC(Q) or 2RG-C; factoring | necessary: loss budget and lattice margin | 100–127 int32/B: 12–20× at decode batch, 1.5–1.9× prefill (*est.*) | ideal-model theorem proved (unreviewed); query counting very Lean-friendly | pursue as infrastructure and the prefill path |
| 4 | **P2** Prime-field Square–Mix–Square (sms5 `spec.md`, no trapdoor) | ideal slow-inverse permutation + VDE sequentiality | the whole regeneration argument | 20–30 int32/B (*est.*), about 4–5× | same proof as P1 (M1); VDE sequentiality weakened (ePrint 2024/873) | park |
| 5 | **P5** Tensor-core-native mixing layer for P3/P4 | heuristic RO; no analysed object | supplies the sequential step | up to about 120–200 int8 MACs/B available | none; cryptanalysis and measurement | side track |
| 6 | **P6** Timed single-round RSA (report's B3) | ideal TDP; RSA-IC(Q) | loss drops from 204 to about 80 bits | 840–930 int32/B, above 100× | ideal theorem proved; instantiation marginal | drop |
| 7 | **P7** Moran–Wichs / lossy twin plus a deadline | DCR, LWE | none: the report's remark applies fully | 10^2–10^7× | proved | drop |

## 1. When a deadline buys security with a trusted encoder

### 1.1 What the report's argument shows, and what it does not

It shows three things, and these are general:

- **Twin-route proofs gain nothing.** This covers MW over Damgård–Jurik, lattice surjective lossy functions, and any HILL-entropy proof. The only computational step is indistinguishability of the two modes of pp. pp is available before any challenge, so the adversary attacks it in preprocessing with 2^λ work. The audit bound is information-theoretic in the hybrid and never mentions the responder's time. As a lemma: *a deadline cannot improve any proof whose computational hops concern data fixed before the first challenge.*
- **Key sizes are offline.** Factoring N, recovering a lattice trapdoor, and precomputing tables all happen in preprocessing. Moduli therefore stay at 2048–3072 bits, and one modular multiplication stays at 68–93 int32/B. This is the real reason no trapdoor-per-block design gets under about 12× at decode batch, with or without a deadline.
- **Cheap-online attacks survive.** These are attacks whose expensive part is offline and whose online part is cheap. Examples: the three-dimensional Coppersmith attack on one Rabin round (microseconds; it recovers w/3 bits), and the degree-4 lattice on an affine-mixed two-round design (a five-dimensional lattice, w/4 to w/10 bits, microseconds; `sms5/reduction/reduction.md` Exp. B).

It does not show:

- **RSA.** Proposition 6's own accounting caps the shift at t ≤ 2(t_on − 1), because recovering the shift j is an interval discrete log solved online by a kangaroo walk in 2^(t/2) steps. Only the walk to a short representative, and any precomputed table, are offline. With a shared table of 2^s entries the generic bound for discrete logs with preprocessing is S T^2 ≳ 2^t (Corrigan-Gibbs–Kogan, ePrint 2017/1113), matched by Bernstein–Lange (ePrint 2012/458). That gives t ≲ s + 2 log_2 Q. At log_2 Q = 30 and s ≈ 20–24 (a table costing about 1–4 bits per block), the saving is about 80 bits, down from 204. Add n/e + 1. At n = 3072, e = 257 that is about 93 bits against a budget of about 95. So the deadline bounds RSA's deviation to about twice the ideal loss, but it does not restore RSA-IC's constant.
- **Theorem 5 itself.** The loss log_2 T + log_2 g is in the *online* budget T. The report's own B3 row shows that T = 2^30 lets 3072-bit blocks pass in the ideal model, where T = 2^100 needs 4352.
- **Anything whose best attack is online search or online lattice reduction**, and every sequential design (report Proposition 11(c)).

### 1.2 The criterion

**Cheap re-derivation lemma** (trivial, but it is the right lens). Suppose a public algorithm R and advice z satisfy C = R(pp, W, z). Then storing z compresses C to |z| bits, and expanding it costs whatever R costs online.

- *Untimed:* security at ρ needs every such (R, z) with |z| < ρ|C| to be infeasible. Corollary: the trapdoor must act on about ρ|c| bits of every block. A narrow trapdoor whose output publicly determines the rest of a wide block compresses the block to the narrow part. So trapdoor cost is paid per byte, and that is exactly the report's missing primitive.
- *Timed:* R may exist, provided it cannot finish within (D, Q). The trapdoor becomes optional when every short-z re-derivation is a chain of more than D sequential steps.

A deadline therefore helps exactly when every good compression needs expensive online expansion. Where that expansion is a search or a lattice reduction, the gain is a few tens to hundreds of bits per block. Where it is a sequential chain, the gain is a change of design class.

The target of the timed game, stated so the report's Theorem 1 bridge carries over:

~~~text
TINC(beta, pi; D, Q): for every preprocessing A1 (work <= 2^lambda) with |sigma| <= beta,
and every responder A2 that, given sigma, the history of earlier indices and a block index i,
halts within D sequential steps and Q operations:
    Pr[ |{ i : A2(sigma, h, i) = c_i }| > (rho + gamma) B for some history h ]  <=  pi.
~~~

The bridge's compressor (report Theorem 1(ii)) calls the responder once per block, so its expander is per-block (D, Q)-bounded and runs the B calls in parallel. The union over histories is the one used by `sms5/ideal/tradeoff.md` Theorem 1. A timed bridge is therefore routine; it is lemma A4 in §4.

### 1.3 Mechanisms, with numbers

**(a) The brute-force budget.** Every design admits truncation: drop t bits and search 2^t completions online. So the per-block loss is at least log_2 Q, plus log_2 g when blocks share an oracle (the M2 model). The loss must stay below about 0.03w for the audit to have margin (the report's ε′ = 1/32).

- Untimed (Q = 2^100–2^128): blocks of at least about 4–5 kbit.
- Timed (Q ≈ 2^20–2^34): about 1.2 kbit per-block-oracle (M1) and about 2 kbit shared-oracle (M2).

At w = 2048 the untimed truncation attack alone saves about 92–120 bits against RW–SMS's budget of about 95–100 bits (94.8 at 5%, about 100 at 18/19), so the untimed statement is marginal to false. The timed statement (loss 48–62 proved in M2, 21–35 in M1) has room. For RW–SMS, then, the deadline is necessary, not optional; the audit's reading was right on this point.

**(b) Expensive online reconstruction.** Near Coppersmith's N^(1/2) bound, recovering all but δ bits of a Rabin root needs a lattice of dimension about w/δ. That costs about 2^21 decodes at δ = 128 and 2^33 at δ = 32, seconds to hours (`reduction.md` Lemma 3). Within 1 ms only lattices of dimension about 6 or less run, and these recover about 40% of a root (`redesign.md` toy [1]), not 50%. The two-round "half-bits" accounting then charges an algebraic attacker about 1.2w stored bits instead of about w: a margin of about 400 bits per 2048-bit block, which is absent untimed. The same bound kills the two-layer backwards route, table-free kangaroo, index calculus and Gröbner-basis attacks. The leakage assumption the transfer needs weakens to "about 40% of a root is not recoverable within 1 ms", far from the known attack boundary.

**(c) Sequential re-derivation.** Here the deadline is the whole security and the trapdoor disappears. Examples are layered depth-robust labelings with local decoding (ZigZag), in-block chained permutations, and VDE rounds. Parallel-ROM proofs exist (§3, P3). The trusted encoder still helps: soundness only has to hold against a verifier who knows the correct labeling. That is the weaker PIE-style game, not a proof of space against a cheating labeler (Fisch, ePrint 2018/702, appendix on PIEs), and it removes the costliest part of proof-of-space soundness. The only measured member is drU(4,6,4) at 4.52×, against at least 12× for any per-block trapdoor.

**(d) Trapdoor-accelerated sequential functions (RSW-style) add little.** The trapdoor shortens the expensive direction. Under decode-on-every-use the expensive direction must be encoding, and then it is either infeasible (Rabin roots, which is P1) or sequential (Sloth, which is P2). Time-lock *labels* that decoding needs (the SDR shape) make decoding as slow as encoding. Mirror (USENIX Security 2016) used RSA puzzles this way, for trapdoor-fast replica generation, and fell to a storage-saving attack (Guo et al., IPOR2). A trusted encoder does not need a fast sequential encoder anyway: encoding is one-off and parallel across chains.

**(e) The sms5 timed analysis.** It is right to charge the total online budget T and to prefer sequential reveal, which gains about 37 bits per block. Its tables at T = 2^20–2^34 are mechanism (a). What it leaves implicit is that T = Δ · Θ_max depends on which hardware answers. `spec.md` assumes GPU-class latencies (0.15 µs per 1279-bit squaring), about 100× slower than the problem statement's 1 ns floor.

### 1.4 Best compression attack per family, and its online cost

| Family | Best compression attack | Online cost | Killed by a 1 ms deadline? | Effect |
|---|---|---|---|---|
| MW-DCR, lattice SLF | none (information-theoretic in the hybrid) | — | n/a | nothing to gain |
| One Rabin/RSA round, small e | Coppersmith, 3-dim lattice (w/3, or n/e bits) | µs | no | one round stays broken |
| One RSA round, any e | shift and kangaroo | 2^(t/2) (or √(2^t/S) with a table) | partly | saving 204 → about 80 bits |
| Two RW rounds, affine mixer | degree-4 lattice (w/4) | µs | no | broken |
| Two RW rounds, dense XOR or ARX | truncation; half-root lattices; two-layer route | 2^t; up to 2^21–2^33 decodes | truncation capped; lattices mostly killed | loss log_2 Q + O(1); margin 0.2w |
| Prime-field VDE (Sloth, MinRoot) | regenerate by root chains; parallel smoothness speedup | 2 × 1278 squarings; about 20× speedup needs 2^29 processors | depends on τ_min and Δ | secure only if Δ is below the regeneration time |
| Local-decode DRG (drU, ZigZag) | drop sparse labels and re-derive locally; drop clusters and re-derive by chains | depth about L for sparse drops; long chains otherwise | sparse drops no, chains yes | 0.59% freed (measured attack); safe only up to Δ* ≈ 130–367 µs |
| Ideal permutation (model) | truncation | 2^t | capped | loss log_2 Q |

### 1.5 Verdict

The deadline is necessary for every design within about 20× of the budget. It shrinks per-block trapdoor designs by about 2.5× (narrower blocks) and adds a real structural margin. It makes trapdoor-free sequential encodings admissible, which is the decisive effect. It does not close the cost gap on its own: the best proved-shape candidates sit at 2–5× (sequential) or 12–20× (trapdoor).

## 2. Assumptions in this vicinity

| Assumption (what we would assume) | Standard / falsifiable? | Known attacks | Effect of timing |
|---|---|---|---|
| Sequential squaring, RSW: `x^(2^T) mod N` needs about T sequential squarings without φ(N) | widely used, falsifiable; strong-AGM ⇒ factoring (Katz–Loss–Xu, ePrint 2020/730); generic-ring equivalence (Rotem–Segev, CRYPTO 2020) | none generic; hardware speed is the risk | it *is* a timing assumption, but its asymmetry points the wrong way for decoding (1.3(d)) |
| VDE sequentiality (Sloth ePrint 2015/366, MinRoot 2022/1626): a p-bit root needs about log p sequential multiplications | falsifiable | parallel smoothness attacks cut latency (ePrint 2024/873); one-round blocks fall to Coppersmith (61-bit design broken) | Q caps the massive-parallel attacks; τ_min decides everything |
| Factoring / Rabin root extraction | standard | NFS, offline | none: sets the modulus |
| Leakage-resilient Rabin (PIR_γ, 2RG-C): (1/2 − γ)w leaked bits and T work do not give the root | non-standard, per-instance falsifiable; proven only at O(log w) bits (Fischlin–Schnorr); false at γ ≤ 0 | Coppersmith | large: timed version needs only "about 40% leaked, 1 ms" |
| RW-IC / RSA-IC: the map loses no more than an ideal permutation | construction-specific, two-stage, not Naor-falsifiable | RSA-IC refuted (kangaroo); RW-IC open (kangaroo stacking for design (a)) | RW-IC(Q ≤ 2^34) is what P1 needs; RSA-IC stays off by about log_2 Q + 20 |
| Strong RSA, Φ-hiding | standard | Φ-hiding lossiness below 1/4 (Kiltz–O'Neill–Smith, ePrint 2011/559) | none (offline distinguishers) |
| Lossy TDFs (Peikert–Waters, ePrint 2007/279), MW20 HILL route (ePrint 2020/814) | standard (DCR, LWE) | cost only | none |
| Ideal permutation / cipher / RO in the parallel-query model | idealised; compression proofs (sms5 Lemma A; report Theorem 5) | instantiation-specific (RSA fails) | loss log_2 Q; inverse cost ≥ D |
| Depth-robust graphs + pROM labeling (Alwen–Serbinenko 2014/238; Alwen–Blocki–Pietrzak 2016/875; Pietrzak 2018/194; Fisch 2018/702) | graph facts are unconditional; ROM for labels | τ_min of the concrete hash; reverse-decoding shortcuts (Fisch's PIE counterexample) | this is the timed assumption |
| Generic ring model for ℤ_N (Aggarwal–Maurer; Rotem–Segev) | idealised | misses Coppersmith (integer representation) | fine for sequentiality, wrong for leakage |
| Auxiliary-input ideal models (Coretti–Dodis–Guo, ePrint 2018/226; CDGS, ePrint 2017/937) | idealised | presampling does not fit instance-dependent advice (`redesign.md` §1.4) | relevant only if advice is about the oracle |
| Hourglass near-incompressibility (van Dijk et al., CCS 2012): RSA signatures compress by O(log) bits | conjecture | the memos say it fell; the attack I can place is the report's kangaroo, which beats the concrete constant | timed, it is the RSA-IC row |
| Tensor-core-native hash or PRG | none analysed; cuPoW (ePrint 2025/685) rests on a low-rank linear-systems conjecture and is a proof of useful work, not a hash | linear layers over ℤ/2^8 invert by elimination | would need a per-step latency and RO-likeness |

## 3. Candidate paths

**P1: Timed RW–SMS / design (a).** The codeword is `C_j = RWInv(σ_j(RWInv(W_j + t_j)))` with a 2048-bit Williams modulus and a dense XOR or keyed ARX mixer σ_j.

- *Reduction:* regeneration reduces to factoring (proved). Compression uses the ideal-model Lemma A plus the sequential-audit theorem, proved in M1 and M2 (`tradeoff.md`, unreviewed), then transfer by RW-IC(Q). For design (a) the equivalent is the two-root game, conjecture 2RG-C (`redesign.md`).
- *Deadline:* necessary (1.3(a), (b)).
- *Cost:* 100–127 int32/B; 12–20× at decode batch, 1.5–1.9× at prefill (*est.*, kernel unmeasured).
- *Attacks:* truncation (log_2 Q + 2); the open item is kangaroo stacking on Coppersmith for design (a).
- *Lean:* very good. Finite permutations, query counting, a union over histories; RW-IC enters as a registered axiom.
- *Role:* the only trapdoor path with a nearly complete proof package, the natural home for the shared lemmas, and the prefill-only fallback.

**P2: Prime-field Square–Mix–Square.** The same two rounds over p = 2^1279 − 1 with no trapdoor (`sms5/spec.md`). Regeneration is 2556 sequential squarings.

- *Reduction:* M1 with a slow inverse (spec.md Theorem 1) plus VDE sequentiality.
- *Deadline:* the regeneration argument. It is about 0.4 ms at GPU latency but a few µs at an ASIC-class 1 ns. So it holds only if the responder is the GPU or the per-answer Δ is in the µs range. The loss budget at 1279 bits (about 38 bits) is tight.
- *Cost:* 20–30 int32/B (*est.*), about 4–5×.
- *Attacks:* those of P1, plus parallel root algorithms (ePrint 2024/873).
- *Lean:* as P1.
- *Verdict:* park. It is no cheaper than P3, and it rests on a sequentiality assumption that is now dented.

**P3: Layered local-decode DRG (ZigZag / drU).**

- *Sketch:* L layers. Each label is `e^(ℓ)_i = Enc(H(salt, ℓ, i, e^(ℓ)_(par(i))), e^(ℓ−1)_i)`, with a depth-robust graph within each layer and an expander or superconcentrator between layers. Store the last layer. Decode is L parallel passes of one keyed hash per block, and it needs no separate RO keystream, because the salt enters every label.
- *Reduction:* labeling in the parallel ROM is reduced to parallel pebbling by an ex post facto compression argument. Pietrzak (ePrint 2018/194) proves this for arbitrary state, including data-carrying labels with data committed before the salt, which matches "W fixed before setup". Fisch (ePrint 2018/702, Claim 12 and §4) shows that stacked depth-robust layers leave an unpebbled path of length βn after (1−ε)n pebbles, with O(log 1/ε) layers, and treats ZigZag's forward/reverse (encode/decode) edges.
- *Deadline:* all of the security.
- *Cost:* 30 ARX/B, 4.52× measured. It must reach about 13 ARX/B, either through fewer or cheaper layers or through P5.
- *Attacks:* the measured attack frees 0.59% at W = 2n. Local re-derivation of sparse drops is inherent: the free fraction is at least 1/(cone size + 1). The safe deadline is only Δ* ≈ 130 µs at 64 KB and 367 µs at 128 KB against a 58 ns-per-label adversary (OPTIONS P1, as I read it).
- *Lean:* the combinatorics (depth robustness, the stacking lemma, independent sets) is very Lean-friendly. The ex post facto step needs an oracle framework.

**P4: In-block sequential wide permutation.**

- *Sketch:* P3 confined to one 32–128 KB tile: n_c chunks, L alternating-direction passes, and in-tile depth-robust edges with short parent digests. Blocks are independent (tweaked by index), and decoding is local to the GEMM tile.
- *Reduction:* two parts. (i) In the "ideal slow-inverse permutation" model (a free forward oracle; the inverse costs more than D rounds), the M1 Lemma A gives loss log_2 Q + O(1) per 262,144-bit block, so γ ≈ 10^(−4), with no composition issue because oracles are per block. (ii) A small-graph pebbling proof that the concrete tile network realises a slow inverse even from partial codeword knowledge.
- *Deadline:* the regeneration depth is about L n_c · τ_H (roughly 1000 hash latencies), so the per-answer Δ must be about 10–150 µs, or the responder must be the GPU.
- *Cost:* *est.* L × (about 3 for a Philox-class pass) plus chaining, which is 8–16 ARX/B, or 1.6–2.4×.
- *Attacks:* sparse chunk drops, the PIE-style reverse-decoding shortcut, and ASIC τ_min.
- *Lean:* M1 counting as in P1; the tile graph can be certified by exhaustive check at toy size and by certificate at full size.

**P5: Tensor-core mixing layer.** Replace the ARX label function of P3 or P4 by int8 MMA-based mixing: a public random int8 matrix on 64–128-byte chunks, interleaved with a cheap nonlinear step, since linear layers over ℤ/2^8 invert by elimination. It moves about 20 ARX/B of P3 to a pipe with 120–200 MACs/B of headroom. The timed game asks less of it than a random oracle would: a latency floor per step, and no algebraic shortcut for partial inversion. Nothing is analysed yet. This is the one lever that could bring P3 under 2× at decode batch, and it doubles as the report's "+10% falsifier".

**P6: Timed single-round RSA.** The kangaroo is capped as in 1.1, but the cost is 840–930 int32/B. The row stays only to correct the report's remark.

**P7: Twin route plus a deadline.** The report's remark applies without qualification.

## 4. Recommendations and the first Lean lemmas

I recommend three tracks: **A** (P1 infrastructure, shared by everything), **B** (P3 and P4, the main bet), and **C** (P5, measurement and cryptanalysis, no Lean). Before B's parameters mean anything, three decisions are needed: the per-answer deadline, the τ_min device, and whether prefill-only certification is acceptable (it makes P1 viable).

**Track A** (all finite and combinatorial; the harness's axiom registry takes RW-IC and factoring):

- **A1** Compression lemma: an injection of a finite event E into bit-strings of length ≤ ℓ gives |E| < 2^(ℓ+1); probability form over a uniform finite type.
- **A2** Lemma A in M1 (`tradeoff.md` §1.2), with exact binomials in place of (eT)^g: for deterministic (A_1, A_2), S bits and T forward queries to B independent uniform permutations of Fin M, `Pr[|G| ≥ g] ≤ 2^S · binom(B, g) · ∑_(h ≤ g) binom((g+1)T, h) · M^(−g)` up to the pool-count factor. Then the M2 version with the identity term.
- **A3** Sequential-audit plug-in: Pr[pass] ≤ (g*/B)^k + 2^(−λ′) by a union over fewer than 2B^(k−1) histories.
- **A4** Timed bridge: the report's Theorem 1(ii) with resource annotations. A product-form cheater that is per-block (D, Q)-bounded yields a compressor whose expander makes one (D, Q)-bounded call per block.
- **A5** Rabin regeneration leg: x^2 ≡ y^2 (mod N) and x ≢ ±y imply 1 < gcd(x − y, N) < N.
- **A6** Cheap re-derivation lemma (1.2), untimed and timed forms.
- **A7** Parameter certificate: at w = 2048, B = 2^28, S = (18/19)(w+8)B and T ∈ {2^20, 2^34}, the M1 and M2 thresholds and k for δ = 1% as rational inequalities, cross-checked against `tradeoff.py`.

**Track B:**

- **B1** Independent-set bound: a graph of maximum degree Δ has an independent set of size at least n/(Δ + 1). Corollary: the free fraction under local re-derivation, which is the lower bound any P3/P4 claim must respect.
- **B2** Depth-robustness definitions and the stacking lemma (Fisch 2018/702, Claim 12). Each layer (αn, βn)-depth-robust, with balanced superconcentrators between layers taken as a disjoint-path hypothesis. Then (1−ε)n pebbles, at most δn extra per level and δ < ε/2, leave an unpebbled path of length βn ending in the last layer. Pure combinatorics.
- **B3** Hash-chain sequentiality in a finite parallel-query model: D rounds of q queries produce a chain of length D + 1 with probability at most (D+1)q/M. This needs a small oracle-algorithm framework; the harness has none yet.
- **B4** A certificate format for the depth robustness of a concrete tile graph (P4 at toy size by `decide`, full size by a checked certificate).
- **B5** (research) Pietrzak's ex post facto reduction (2018/194, Theorem 10, with the §8 data-carrying extension) in the finite model.

**Track C:** measure an in-tile 2-pass and 4-pass P4 kernel, and a P3 kernel with an MMA label function, inside the fused GEMM. Run the sparse-drop and reverse-decoding attacks on the P4 tile graph.

## 5. Flags on the problem statement

1. The store copy of "What timing changes" (read at 06:03 UTC) still has the older wording ("whether and when it does … is open"). This memo follows the constructive framing from the follow-up.
2. **Δ is underspecified and probably too loose.** Is it per answer under sequential reveal, and with all-at-once reveal is it one deadline for all k answers or one per answer? Honest lookup latency with an on-node verifier and a persistent kernel is µs-scale. Sequential designs scale with D = Δ/τ_min, and the memos' drU stack is safe only up to about 130–367 µs. Target the smallest per-answer Δ that honest latency permits.
3. **Which hardware sets τ_min and Θ_max?** Perfect isolation suggests the responder is the GPU itself, but the time model says "any hardware the operator could use". The two readings differ by 10–1000× in D. "No step faster than 1 ns" needs a named step (hash call, 32-bit op, modular squaring).
4. The 4.5-slot budget assumes an RO offset. Sequential designs fold the salt into their labels, so their budget is the full 2× line (8 IMAD, or 13.1 ARX two-pipe).
5. The storage bound "whenever a challenge arrives" should say that working memory during a response (other HBM regions) is unrestricted, with (D, Q) as the only online limit. Otherwise it is ambiguous under sequential reveal.
6. The idealised floor k = 86 ignores the per-block loss. Realistic k is design-dependent: about 200–800 for P1, and about ln 100 / ln(1/p*) with p* from the pebbling bound for P3 and P4.

## References

Fisch, *Tight Proofs of Space and Replication*, ePrint 2018/702 · Fisch, *PoReps: Proofs of Space on Useful Data*, ePrint 2018/678 · Moran–Wichs, *Incompressible Encodings*, ePrint 2020/814 · Damgård–Ganesh–Orlandi, *Proofs of Replicated Storage Without Timing Assumptions*, ePrint 2018/654 · Garg–Lu–Waters, *New Techniques in Replica Encodings with Client Setup*, ePrint 2020/617 · Cecchetti–Fisch–Miers–Juels, *PIEs*, ePrint 2018/684 · Pietrzak, *Proofs of Catalytic Space*, ePrint 2018/194 · Alwen–Serbinenko, ePrint 2014/238 · Alwen–Blocki–Pietrzak, ePrint 2016/875 · Mahmoody–Moran–Vadhan, ePrint 2011/553 · Cohen–Pietrzak, *Simple Proofs of Sequential Work*, ePrint 2018/183 · Lenstra–Wesolowski, *Sloth*, ePrint 2015/366 · Khovratovich–Maller–Tiwari, *MinRoot*, ePrint 2022/1626 · Biryukov et al., *Cryptanalysis of Algebraic VDFs*, ePrint 2024/873 · Katz–Loss–Xu, ePrint 2020/730 · Rotem–Segev, *Generically Speeding-Up Repeated Squaring Is Equivalent to Factoring*, CRYPTO 2020 · Corrigan-Gibbs–Kogan, ePrint 2017/1113 · Bernstein–Lange, ePrint 2012/458 · Kiltz–O'Neill–Smith, ePrint 2011/559 · Peikert–Waters, ePrint 2007/279 · Coretti–Dodis–Guo, ePrint 2018/226 · Coretti–Dodis–Guo–Steinberger, ePrint 2017/937 · van Dijk et al., *Hourglass Schemes*, CCS 2012 · Armknecht et al., *Mirror*, USENIX Security 2016 · Komargodski et al., *Proofs of Useful Work from Arbitrary Matrix Multiplication*, ePrint 2025/685.
