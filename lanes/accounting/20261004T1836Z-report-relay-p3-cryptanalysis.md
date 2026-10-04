---
id: 20261004T1836Z-report-relay-p3-cryptanalysis
campaign: pous
lane: accounting
kind: report
status: closed
repo: danielreuter/verity
origin: old-accounting (bc-b729c175), relayed for memory-accounting's 18:25Z question from store:pous/docs/p3-cryptanalysis.md
---

> Relayed verbatim from the Cursor store by old-accounting: `store:pous/docs/p3-cryptanalysis.md`, sha256 `f9fc17037a78b286b97e3473c13517566a19bc965e59ccb130c5b24f0ef2801d`, unchanged since it was written, so it is also in `art:8bd64630…42e9` at that path. Only the store's `cursor:` front matter is replaced. Relative and `/cursor/stores/…` links point into that store.

# P3 cryptanalysis: the two-layer invertible encoding

27 Sep 2026. Attacks on [P3](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/docs/p3-scheme.md) §1 as drafted in `Pous/Model/Invertible.lean`. Scripts are in `internal/p3-cryptanalysis/`: `toy_labels.py` (bit-exact toy with a Feistel PRP), `graph_savings.py` (operating point) and `arx_diffusion.py` (concrete P).

**Headline.** **P3.1, the costed variant, is broken**: its digests alone (25% of C) answer every block in 3 rounds. P3 with full-label keys survives at the operating point, but only inside γ. The transpose lets the adversary hold lower labels one column at a time, which whole-label pebbling cannot see. That saves about 1% of C at D = 20 on a sparse base-path DRG, and 18% on a graph that meets every hypothesis of Theorem P3. So **N10 as stated is false**, and the proof target must change before we invest in it.

**Setting.** m = 8192, n = 220 labels per segment, component width w_c ≈ 37 bits, ρ = 18/19, γ ≈ 0.019, Q = 2^13, k = 135. D = 20 counts oracle rounds (one batch of H or P queries each), so one label level costs 2 rounds; if D counts levels, read the D = 40 rows. W is free to the adversary, the worst case (attack 4). X is the saving in labels per segment: X > γn ≈ 4.2 beats the target p₀ = ρ + γ, and X > n/19 ≈ 11.6 beats 18/19 outright.

| # | Attack | Saving | Online cost | Verdict |
|---|---|---|---|---|
| 1 | Column hole across the transpose | \|U\|\|R\|/n labels per segment: ~1% of C at D = 20 on a sparse DRG, 18% on the counterexample graph | 2dR + 2dU − 1 rounds, ≤ 450 queries, no P⁻¹ | **Breaks N10 and Theorem P3 as stated**; inside γ at the operating point |
| 2 | Meet in the middle through P and P⁻¹ | Same form, 0.9–1.8% of C at D = 20; guessing adds ≤ 13 bits per dropped label | 2dR + 2dU + 1 rounds, ≤ n P⁻¹ | No gain beyond 1 |
| 3 | Shared P: slides, related inputs | 0 in the ideal model; equal-W segments dedupe in the Lean model | — | Doesn't break the spec; **breaks the Lean model** if reused per segment |
| 4 | Adversarial W, all zeros | 0 alone; a free W powers 1, 2 and 7 | — | Doesn't break; enabling condition |
| 5 | Amortization, sequential vs simultaneous | 0 extra | Q >10× slack; D binds | Doesn't break |
| 6 | Concrete ARX or int8-MMA P at a ≈ 1.5 | None found beyond 1; the proof does not apply, and γ is vacuous if H is equally light | — | **Breaks only the instantiation** |
| 7 | P3.1: store only digests | 75% of C | 3 rounds, 2n + 2 queries | **Breaks P3.1** |

## 1. Column hole: partial components across the transpose

Top label u needs x²_u = (c¹_w[u])_w: one 37-bit component of each lower label, not the lower labels. The adversary drops the top labels on a low-depth set U. For each u ∈ U it stores x²_u only on lower nodes w ∉ R, where R is a layer-1 set it can rebuild from W before the deadline. An ancestor-closed R costs nothing, since source keys H(0, v, ∅) are constants.

The cost is n − |U||R|/n labels, while white/green pebbling of the same strategy counts (n − |U|) + (n − |R|) > n pebbles. **A lower pebble costs the labeling adversary |U|/n of a label, not 1.** Toy check (n = 16): bit-exact recovery at 0.871 of C, saving exactly |U||R|/n, no P⁻¹ calls.

At n = 220 (greedy low-depth sets, so lower bounds):

| G | D = 20 | D = 40 |
|---|---|---|
| base path + 7 uniform parents (d′ = 8) | 2.2 (1.0%) | 5.7 (2.6%)† |
| DRSample, d′ = 6 | 2.7 (1.2%)† | 6.7 (3.0%)† |
| complete DAG | 0.1 | 0.5 |
| 40% sources + complete core | 39 (18%) | 44 (20%) |

† Not (½, D/2n)-DR at this D: some set of at least n/2 nodes has depth ≤ D/2, so plain pebbling already breaks it. DRSample with d′ = 2 fails even at D = 20 (77% of nodes in a depth-10 set).

With a base path and no lower label held whole, R is a prefix (|R| = dR) and DR forces |U| < n/2, so X < D/4 labels per segment. **Holding lower labels whole breaks this bound** (see N10′ attacks).

**Counterexample.** 88 sources plus a complete DAG on 132 nodes meets every hypothesis of Theorem P3:
- DepthRobust(½, 0.1): any 110 nodes include at least 22 core nodes, which form a path.
- 1 ≤ (1−α)L and D < βn.
- (H): re-pebbling a top node needs at least 112 core pebbles, so at least 224 > n − 1 pebbles in all.

Yet 82% of C answers every block in 3 rounds (toy at n = 20: 0.840 of C, bit-exact). So "B5 with PebblingHard replaced by white/green hardness" is false for the transpose connector.

## 2. Meet in the middle through P and P⁻¹

Meet at c¹ from both sides. Decode the stored top labels with P⁻¹ to get columns T of every lower label; add the stored U-columns; then rebuild any low-depth R forward from W. U must be descendant-closed, because its T-children's keys need c²_U, so with a base path U is a suffix. The saving has the same form: 1.9–3.9 labels at D = 20.

Guessing adds little. Searching for one missing component costs 2^{w_c} = 2^37 > Q, and guess-and-check yields at most log₂Q ≈ 13 bits per dropped label (0.16%). This holds while w_c > log₂Q, i.e. n < 630.

## 3–5. Shared P, adversarial W, amortization

**Shared P.** Keys H(salt, s, ℓ, v, ·) make every P input uniform and independent, with no iterated keyed round to slide on. But the Lean `KQ` is (layer, node, parents), with no salt or segment index. If one ω serves N segments, equal-W segments (zero tiles, padding, repeated weights) get identical C (toy: `identical=True`). Add (salt, s) to `KQ`.

**Adversarial W.** The salt comes after W, so W cannot shape P's inputs; all zeros is simply the free-W case. A free W is what attacks 1, 2 and 7 rebuild from, while a secret W would cost |R| stored labels and cancel the saving. The claim must hold for a free W.

**Amortization.** The attacks need at most about 2(n + |R| + |U|) ≤ 700 queries per answer. Over 135 challenges they make ≤ 2^14.9 P⁻¹ queries, against the 2^22 margin. Two challenges share a segment with probability k²/2N ≈ 1.5%, and kQ background queries rebuild about 0.2% of segments, so neither reveal order helps. Attack 1 beats pebbling with no inverse queries at all, so bounding inverse queries cannot close N10.

## 6. Concrete P

At a ≈ 1.5 instructions/B, a 32-bit ARX butterfly has 4 stages, so each output word depends on at most 16 of 256 words: 512 bits, about 14 of the 220 components. Full dependency needs 8 stages (3/B), and about 16 (6/B) with margin. int8-MMA is triangular: output plane 0 depends only on input plane 0 (0/50 leaks), and that map is GF(2)-affine (20/20).

H over full parent labels blocks partial evaluation, so we found no extra compression. But P is distinguishable with two queries, so the ideal proof does not describe it. If H's absorb and squeeze use the same pass (§6), labels split into 16 independent 512-bit lanes. The 118-bit loss c_lab then applies per lane, and γ ≈ 1/n + 16·119/m ≈ 0.24, which is vacuous. With a ≥ 3, P3.1 costs L(4a + 0.5) ≥ 25 ARX/B (49 with margin), against the 13.1 ARX/B 2× line.

## 7. P3.1 digests

Store every label's λ_d-bit digest in both layers, Lλ_d/m = 25% of C. Round 1 computes all keys from the digests, round 2 all layer-1 labels P(W ⊕ k), and round 3 the challenged top label (toy: `ok=True`, 0.250 of C). The condition (L−1)λ_d ≥ 2εm does not exclude this. The mixed strategy saves u(m − λ_d) − (L−1)nλ_d, which is non-positive only if **λ_d ≥ m/L** (4096 bits at L = 2).

## Strongest attack and what it implies

**Outright, attack 7:** P3.1 at λ_d = 1024 keeps 25% of C. Take λ_d ≥ m/L or key on full labels (P3), then re-cost §6. Since a concrete P also needs a ≥ 3, the 2× cost target is out of reach as drafted.

**For P3 itself, attack 1.** State N10 for a column-level game, where a lower label can be held component by component at 1/n each. Its hypothesis must bound X(G, D), the best column saving over admissible (U, R) and that game's mixed strategies, in place of white/green hardness. For the parameters:
1. Pin G with a base path and certify its DR at n = 220; DRSample with d′ = 2 or 6 fails at D = 20.
2. Add X/n to γ. For base path + uniform parents at D = 20, X is at least 3.9, not the greedy 2.2, so γ ≥ 0.037 and k ≥ 288 (see N10′ attacks).
3. Keep D ≤ 20 oracle rounds. At D = 40 the sparse graphs lose DR.
4. Add (salt, s) to `KQ`.

## N10′ attacks

27 Sep, against `lean/submissions/pebbling/ColumnAwareDraft.lean`: the game `colRoundF`, the hypothesis `ColumnHard`, and the targets `n10prime` and `basePath_columnHard`. The script `internal/p3-cryptanalysis/n10prime_attacks.py` (log beside it) checks each holding two ways:
- it replays the holding through a transcription of `colRoundF`;
- for the annealed holdings, it also replays them bit-exactly against toy labels at n = 220, with no P⁻¹ calls.

A game round is one label level: D = 20 oracle rounds give 10 levels.

**Headline.** The column game holds up. I found no forward strategy it misprices, and meet-in-the-middle, guessing, partial columns and coded columns all fit its per-line charge. What breaks is the X certificate and the instantiation at the operating point.

| Attack | Saving at n = 220 | Verdict |
|---|---|---|
| Whole lower labels as separators | 27.5 labels (12.5% of C) on a certified base-path DRG at 10 levels; 3.90 on the sparse d′ = 8 instance | **Breaks `basePath_columnHard`**, and breaks 18/19 on a base-path DRG |
| Staggered recovery, no whole lowers | 3.71 on the sparse instance (exact solver); certified ≤ 5.31 | **Refutes X ≈ 2.2** and ⌈D/4⌉ = 3 |
| D units in `n10prime` | 68.4 labels (31%) on the sparse instance at 20 levels | **Breaks the instantiation as drafted** |
| Per-segment `n10prime` with q_inv ≤ Q | — | **Inapplicable at the operating point** |
| Meet in the middle through P⁻¹ | ≤ 1 line per decode | Inside the charge; the prover is right |
| Guessing, partial columns | ≤ log₂Q ≈ 13 bits per answer | Inside the 20.8-bit per-line concession |
| Coded (XOR) holdings | 0 | Column pricing is tight |

**Whole lower labels as separators.** A lower label held whole costs n columns. But it gives its column to every dropped top, and it lets the lower labels after it be rebuilt. The saving is Σ over dropped tops u of |lowers whole by round τ(u) − 1|, minus n·|held lowers|. My §1 bound X < D/4 assumed no lower is held whole; it is false in general.

Take a 99-node path followed by a complete 121-node core. It is a base-path graph, and DepthRobust(½, 0.05): any 110 nodes include at least 11 core nodes, which form a path, so βn = 11 > 10 levels. Holding every seventh path lower whole rebuilds the whole path segment in 6 rounds, while 4-deep blocks of path tops wait for it. That gives 20.5 labels analytically. Annealing finds 27.5 labels (14 held lowers, 92 dropped tops), recovered in 20 oracle rounds. This is more than the 11.6-label gap, so 18/19 fails on a DR base-path graph. No bound of the form f(D) follows from a base path plus DR; X must be certified per graph over the full game, held lowers included. (With the draft's placeholder `hDR : True`, the bare path already refutes the target.)

**Staggered recovery; X ≈ 2.2 is not an upper bound.** The number 2.2 is a greedy lower bound for one strategy family. Tops need not all wait for the same prefix: a top recovered at round τ can use every lower that is whole by τ − 1, so shallow tops are recovered last and get more free columns.

On the sparse instance behind 2.2 (base path plus 7 uniform parents) at 10 levels:
- The exact MILP over strategies without held lowers finds **3.71 labels**, which exceeds the target's ⌈D/4⌉ = 3. The HiGHS dual bound after 600 s certifies ≤ 5.31 for that class; DR would give < 4.5 if certified for this graph.
- Annealing from that solution, with held lowers allowed, reaches **3.90** (2 held lowers).
- With held lowers, the MILP relaxation is vacuous, so nothing yet certifies X for this graph. A per-instance certificate needs a stronger formulation, for example separator cuts.

At X = 3.90, γ = 0.037 and k = 288, against the draft's 0.029 and 194; at 5.31, k = 483.

**D units.** A label level costs H then P, 2 oracle rounds; a top whose key was computed early can take 1. So D oracle rounds give ⌊(D+1)/2⌋ levels. `n10prime` passes the same D to both `Prog.Bounded` and `ColumnHard`. That is sound, but it asks for X at 20 levels. There the sparse instance is not (½, 20/n)-DR, and annealing saves 68.4 labels (31%, 69 held lowers) in 39 oracle rounds. Either state `ColumnHard G ⌊(D+1)/2⌋` together with a lemma that a level costs two oracle rounds, or accept X at 20 levels.

**Per-segment vacuity.** `n10prime` covers one segment (k ≤ n = 220) with a per-answer `q_inv`, and requires X + q_inv ≤ k. The timing link only gives q_inv ≤ Q = 2^13 per answer, and the meet-in-the-middle variant already uses about 217. So as stated the theorem does not reach the operating point. Lift it to all N segments, with q_inv counting distinct inverse queries across all answer programs: at most kQ ≈ 2^20, against B − XN ≈ 2^27.

**Where N10′ holds.**
- **Meet in the middle.** Decoding top t reveals column t of every lower, which only helps to complete lower labels. Holding those ≤ n columns instead gives a forward holding one line larger. So each decode saves at most one line, exactly what the bound charges. Variant B saves 1.9 labels for about 217 charged lines.
- **Guessing and partial columns.** P is all-or-nothing, so a partial column needs search. Checking a guess costs a P⁻¹, charged a full line, and an unchecked guess succeeds with probability 2^{−g}. That is at most log₂Q ≈ 13 bits per answer, inside the log₂Q_tot ≈ 20.8 bits the bound concedes per line.
- **Coded holdings.** Every column a dropped top needs is released, meaning its lower turns whole, only after its deadline. By induction on deadlines, the stored state must determine each such column, so storage is at least their count. XORs don't help.

**What it implies.**
1. Replace `basePath_columnHard` with a per-instance certificate over the full game, held lowers included.
2. Take X ≥ 3.9 at 20 oracle rounds for the sparse instance, so k ≥ 288.
3. Fix the D units, and lift `n10prime` to all segments with a global count of distinct inverse queries.
4. Prefer graphs whose intervals have many outside parents: d′ = 8 uniform resists separators, and path-plus-core does not.

## Band graph cross-check

27 Sep, against `lean/submissions/p3-column/BandCertificate.lean`, which proves X = 3 at each point below. The graph is B(n, k): each node's parents are the k nodes before it. The game is `colRoundF` as fixed, where a lower label becomes whole once its parents are whole or all n of its columns are held.

With the inverse rule, a whole top u whose parents are whole also yields column u of every lower label in the next round. The script `internal/p3-cryptanalysis/band_crosscheck.py` (log beside it) runs three searches:
- a MILP over holdings with no whole lower labels, solved to proven optimality;
- an anneal with whole-held lower labels as separators;
- an anneal over meet-in-the-middle holdings, whose lower labels are promoted through decoded columns.

Every best holding was replayed through the transcribed game and bit-exactly against toy labels at n = 220.

| Graph, depth | Exact optimum, no whole lowers | + whole lowers | + key-gated P⁻¹ | Best that needs P⁻¹ | Certificate |
|---|---|---|---|---|---|
| B(220, 12), d = 10 | **2.33** (certified optimal) | 2.33 | 2.33 | 1.02 | 3 |
| B(220, 12), d = 11 | **2.73** (certified optimal) | 2.73 | 2.73 | 1.27 | 3 |
| B(220, 16), d = 12 | **2.67** (certified optimal) | 2.67 | 2.67 | 1.25 | 3 |

**Nothing exceeds 3, so I found no mismatch between the Lean game and the real game.**
- **The optimal holding** holds no lower label whole. It drops about 90 tops in runs of 7–9 consecutive nodes, with k held tops between runs. Each run is a chain, and each top is recovered at the latest round its height allows.
- **Whole lower labels never helped**, consistent with the certificate's rebuild lemma: a held lower label buys at most one extra rebuilt label, so it nets at most 2|U| − n < 0.
- **Promotion through P⁻¹ pays only when the dropped set is a short suffix.** Other dropped tops leave their held children undecodable. That meet-in-the-middle holding saves about 1 label (5 dropped tops, about 170 promoted lowers, 215 inverse queries). The 1.02 at d = 10 matches the prover's `inverse_rule_sim.py`.

**Caveats.** Optimality is certified only for holdings without whole lower labels. Whole lowers and inverse moves were searched heuristically, backed by the two arguments above. The tightest point is d = 11, at 0.27 labels below the certificate.

**Parameters.** At X = 3, γ = 0.033 and k = 229, against 288 for the sparse graph at X ≥ 3.9.

## Narrow-state H

27 Sep. **Verdict: confirmed.** Any H whose m-bit output comes from one internal state narrower than m breaks the instantiation of both P3 and `DenseMeets` outright. The theorems stay correct in their model, which treats H as a monolithic random oracle with m-bit outputs. This is the multi-stage gap of Ristenpart–Shacham–Shrimpton (EUROCRYPT 2011), whose counterexample is a hash-based proof of storage.

**Against the exact definitions.** In `Invertible.lean` and the salted `KQ'` of `ColumnAwareDraft.lean`, the labels are c¹_i = P(W_i ⊕ H(tag, 0, i, lower parents)) and c²_u = P(x²_u ⊕ H(tag, 1, u, top parents)), where x²_u is column u of every lower label. In `Dense.lean`, C_i = H(i, C_{<i}) ⊕ W_i. Every key enters only through H's output, and a sponge's output is a function of its state after absorbing. So the adversary stores that state per key and never touches the parents again. With W free:
- **P3:** squeeze all 2n stored states in parallel; compute every c¹_i = P(W_i ⊕ k¹_i); transpose to get every column; compute every c²_u = P(x²_u ⊕ k²_u). That is 3 rounds, independent of n and of the graph's depth, so the depth-robust graph is bypassed entirely.
- **Dense:** C_i = squeeze(state_i) ⊕ W_i, all in parallel, in 1 round.

**Demonstration** (`internal/p3-cryptanalysis/narrow_state.py`). My Keccak-f[1600]/SHAKE-256 matches `hashlib.shake_256` bit for bit on every test vector, which lets the script snapshot the 1600-bit pre-squeeze state. Both schemes regenerate bit-exactly from the stored states alone:

| Scheme | Stored | Rounds |
|---|---|---|
| P3, n = 64, band k = 12, m = 8192 | 2n × 1600 bits = **39.1% of C** | 3 |
| Dense, 32 blocks of 8192 bits | 32 × 1600 bits = **19.5% of C** | 1 |

At the operating point (m = 8140) P3 stores 2 × 1600/8140 = 39%. For other hashes the saving scales with the state; these rows are estimated from each construction, not demonstrated:

| H | State before output | P3 stored | Dense stored (ℓ = 8192) |
|---|---|---|---|
| SHAKE-128/256 (any Keccak XOF) | 1600 bits | 39% (demonstrated) | 20% (demonstrated) |
| BLAKE3 XOF (256-bit chaining value + 512-bit block) | ≈ 800 bits | ≈ 20% | ≈ 10% |
| SHA-256, input then counter (MGF1-style) | 256-bit midstate + partial block, ≤ 830 bits | ≤ 20% | ≤ 10% |
| SHA-256, lane index first, each lane re-absorbing all input | ≈ one 256-bit lane per lane output | **no saving** | **no saving** |

**Calibration against Daniel's previous campaign** (`internal/sources/porep-inference/CATALOG.md` §3.15–3.16). The campaign met this as the "cached-seed" and "cached-key" attack and found it decisive; it maps onto our case like this:
- **Cached key (§3.16, family B).** The attack is "void at κ = b … decisive below it" for a key of width κ on a word of width b, so their design needed "full-width key derivation".
- **Cached seed (§3.15).** Their public hash/XOR proof had to make "every lane … absorb the full parent tuple (cached-seed attack)", and that is what forced their 48 lanes.
- **Our case is the cached-seed form.** P3's key is already full width (κ = m), yet it still compresses to a 1600-bit seed. The threshold is therefore on the hash's state: the attack is void only when the state is at least m.

**Fixes, and whether the ideal-model proof transfers.** Indifferentiability does not carry over to storage games (RSS), so no fix transfers automatically. Each surviving fix needs what the catalog calls "a concrete-refinement argument": a proof in the model of H's inner primitive, where a stored state is an object the adversary is charged for.

| Fix | Stops this attack? | Does the proof transfer? |
|---|---|---|
| (a) Wide sponge, state ≥ m, on P itself | **Yes.** The state is m bits, so storing it saves nothing | **Yes, after a refinement in the ideal-permutation model**, which is natural because P is already ideal in `p3Model`. It is the catalog's lever (1), "absorbing parents once (removes ×lanes, ~48×)". Mid-absorption states also cost m bits, so they act as pebbles of full price that the refined game must allow. Cost is about ⌈m/r⌉ + ⌈dm/r⌉ wide P calls per key |
| (b) Keys that don't factor through a small state: lane index absorbed first, each lane re-absorbing the full input | **Yes.** No lane shares a prefix state; the order matters, since counter-last is the vulnerable MGF1 form | **Yes, after a refinement** modeling the compression function. It is the catalog's lane design, costing m/256 ≈ 32 full re-absorptions of the parent tuple per key |
| (c) Label width at most the hash state (m ≤ 1600) | Yes for this attack | **No, the operating point collapses.** Columns become ≤ 7 bits, below log₂Q ≈ 13, so column guessing returns (§2), and the 118-bit c_lab loss becomes 7% of a label (γ ≈ 0.08). The catalog's floor agrees: the whole-label pointer loss "forces w > ~10.5K bits at 18/19" |
| (d) Newest-parent-first serial absorption (`internal/prior-ai-advice-p3.md` §1) | **No.** The stored state is taken after every parent is absorbed, so the order is irrelevant | Not applicable. It is a timing lever against pre-absorbing older parents, not a storage defense. It remains useful alongside (a) |

**What to do.**
1. Instantiate H as a wide sponge on P, with state ≥ m, or as lane-first full-width derivation.
2. Re-prove N10′ and B5 against that concrete H in the ideal-permutation model, rather than citing indifferentiability.
3. State the requirement in `Meets` and `DenseMeets` explicitly: H's output must not be regenerable from fewer than m (respectively ℓ) stored bits. Without it, "no named assumption" holds only for a monolithic random oracle, which no real hash is.
4. Re-cost §6 with the extra wide calls per key.
