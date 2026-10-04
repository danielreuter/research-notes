---
id: 20261004T2202Z-report-relay-docs-sms5-review-ideal
campaign: pous
lane: accounting
kind: report
status: closed
repo: danielreuter/verity
origin: old-accounting (bc-b729c175), relayed for @top's migration (the 44 store:pous/ files the PoUW and PoUS registries cite) from store:pous/docs/sms5-review-ideal.md
---

> Relayed verbatim from the Cursor store by old-accounting: `store:pous/docs/sms5-review-ideal.md`, sha256 `70acecb5cda2b8761206f1e0b395e315ad66550358d433f72327167ad9144bb1`, unchanged since it was written before the 30 Sep snapshot, so it is also in `art:8bd64630…42e9` at that path. Only the store's `cursor:` front matter is replaced. Relative and `/cursor/stores/…` links point into that store.

# SMS5 ideal-model completion bound: adversarial review

Review, 27 Sep 2026, of `research/sms5/ideal/tradeoff.md` (Lemma A, Theorem 1, models M1–M3), `tradeoff.py`, and the parts of `sms5/spec.md` they use, against the [problem statement](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/docs/problem-statement.md) and Track A in [construction paths](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/docs/construction-paths.md) §4. I checked the proofs line by line. `tradeoff.py --all`, re-run on a scratch copy, reproduces all 32 rows of §4. An [independent solver](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/internal/sms5-ideal-review-check.py) (exact log-binomials, exact history count, integer g*, log_2 M in place of w) agrees on every k below.

## Verdicts

| Claim | Verdict | Conditions |
|---|---|---|
| Lemma A, M1 | **GRANTED** | The encoding is injective and the counting is correct (term ratio ≥ T−1, (T−1)/(T−2) ≤ 1+2/T, ((g+1)/g)^g ≤ e). Theorem 1 needs its per-run form (F4). |
| Lemma A, M2 | **GRANTED WITH CONDITIONS** | Holds on the event that the y_j and the v_j are distinct on G′ (F5). The identity factor g!/(g−h)! and the pool (M−g)!/M! are correct. |
| M3 has M2's bound | **GRANTED WITH CONDITIONS** | (M−2g)^(−g) plus a 2g^2/M collision term; the proof still has to be written (F6). |
| Theorem 1 | **GRANTED WITH CONDITIONS** | Fix the adversary class (F2), use log_2 M (F3), add the collision terms (F5), require an exact-record check (F7). The union over `<2B^(k−1)` histories and the conditional product are correct. |
| M1 as a model of RW–SMS | **NOT GRANTED** (the memo agrees, §2) | Its numbers depend on Conjecture B1'. |
| M2/M3 at w = 2048 in the target game | **NOT GRANTED** | "No inverse oracle" fails against 2^128 preprocessing (F1). |
| §4 tables | **GRANTED** | Reproduced exactly and independently. |

## Findings

| # | Sev | Location | Witness and fix |
|---|---|---|---|
| F1 | **High** | §0 Adversary, §5, §6; problem statement step 2 | Factoring a 2048-bit N costs about 2^112 < 2^λ = 2^128. A_1 factors N and keeps σ = (p,q). A_2 answers any index with two RW inversions: about 2^10.3 squarings of work (≪ Q) and a depth of about 2,450 dependent 1024-bit modmuls, i.e. 0.25–0.37 ms at spec.md's 0.10–0.15 µs floor, inside Δ = 1 ms. It passes with probability 1. **Fix:** w ≥ 3072 (≈ 2^128, no margin), or preprocessing ≤ 2^112, or Δ below the inversion depth plus a sequentiality assumption (outside M1–M3). |
| F2 | **Medium** | §0 Budget, §1.3, §1.4, §1.5; A3 | The two adversary classes are both valid but not interchangeable. **(a)** The memo's: state carried between rounds is unbounded and T covers all audit work, gaps included. **(b)** The target game's: state is at most ρ\|C\| at each challenge and each answer gets ≤ Q queries, so Lemma A applies per round with T_r = 0, T := Q. Mixing them is unsound: with carried state, during an idle gap the adversary brute-forces the dropped t bits of every block (B 2^t queries). In (b) the table's T is the per-answer Q and §1.5's 10-bit slack disappears: M1 gives k = 117/142 against truncation's 113/136. With a per-answer Δ, class (a) pays an extra log_2 k (§1.4 treats Δ as the whole audit window). |
| F3 | Low | §0 "I write w", §1.3, `gstar` | log_2 φ(N) ≥ w − 1.4 · 10^(−6), but g*(w − log_2 M) ≈ 360 bits exceeds the 2.5-bit constant, so the history union is vacuous at exactly g*. **Fix:** use log_2 M. g* moves by at most 1 block and no k changes. |
| F4 | Low | §1.2 vs §1.3 | The lemma fixes T_r; Theorem 1's replay length depends on Π. The proof only needs "each run makes ≤ T queries" (at most gT positions). If \|σ\| ≤ S, the count is 2^(S+1). |
| F5 | Low | §1.1 "bijections σ_j"; Theorem 1 | The real σ_j maps the canonical root r (a_1 bypasses it) to (v,h), so it is not a bijection of D. The proof needs only public maps and distinctness. The theorem leaves out that event's failure probability, B^2 2^(−w), and M3's 2g^2/M. |
| F6 | Low | §2 "(2.3)" | No §2.3 exists. I checked M3: g preimages of y_j at full price, one pool on D minus 2g points, ratio ≤ (M−2g)^(−g), identity count unchanged. |
| F7 | Low | §0 "exact records"; problem statement step 4 | A vk that only checks decoding accepts both c and N−c, freeing one bit per block. **Fix:** make vk a commitment to C, or check that c is the canonical root. |
| F8 | **Medium** | A7 | Exact rational evaluation is infeasible: M^g has 5.3 · 10^11 bits and binom(B, g) has 6.4 · 10^7. A7's B = 2^28 is not the script's 275,590,552 (the k values are the same). λ′ should be 128, which costs nothing. |
| F9 | Info | §2; spec.md §5 | M1's numbers depend on B1'. spec.md's Theorem 1 (vacuous) and its A3 are superseded, and Lemma 5(iii)–(iv) is a heuristic over 𝔽_p. None of spec.md belongs in Track A. |

Attacks that did **not** break the ideal bounds: cycle-walking or Hellman tables on the shared π_2 (no better than truncation); an ℓ-bit filter on v_j; unordered storage plus truncation in M2 (reaches log_2 T − 2.4); adaptive W (fixed before Π); work between audits (the state is bounded at every challenge).

## Does the timed bound survive at w = 2048, B = 2^28?

**In M1–M3, yes. In the target game at λ = 128, no (F1).** Here S = (18/19)(w+8)B, and T is the per-answer Q in class (b), or total work in class (a):

| T | M2: u, k for 1% | M1 (B1'): u, k | Truncation attack: u, k |
|---|---|---|---|
| 2^20 | 2.60%, **175** | 3.88%, 117 | 4.00%, 113 |
| 2^34 | 1.92%, **238** | 3.21%, 142 | 3.34%, 136 |

With a per-answer Q in class (a) (T = kQ), k is 205/304 (M2) and 128/160 (M1). Nothing changes at B = 275,590,552 or at λ′ = 128.

## Track A

- **A2: safe as stated (M1),** reading "T queries" per run and σ ∈ {0,1}^S. The pool factor is exact (M^(−g)). The M2 follow-on needs: σ_j arbitrary public maps, a hypothesis `Dist` (y_j distinct, v_j distinct), the identity factor g!/(g−h)!, and the pool (M−g)!/M!.
- **A3: safe after restatement.** As written it has no adversary class, and its g* uses w:

~~~text
A3'. |Hist| = (B^k - 1)/(B - 1). For each history h there are s_h(Pi) in {0,1}^S and a
deterministic R_h(s, i), <= T queries per run, giving the round-(|h|+1) answer on index i.
If |Hist| * Gamma(g) <= 2^-lambda' (Gamma = Lemma A; M2/M3 on Dist), then
Pr[pass] <= ((g-1)/B)^k + 2^-lambda' (+ Pr[not Dist]).
(a) stateful A2, total work <= T: s_h = sigma. (b) target game: s_h = state at challenge, T := Q.
~~~

- **A7: not safe as stated** (F1, F3, F8). Restated:

~~~text
A7'. log2 M >= 2048 - 1.4e-6, B = 2^28, S = floor(18/19 * 2056 * B), lambda' = 128.
Log form, certified rational bounds on log2 e and log2 C(B,g) <= B*H2(g/B), a few blocks of margin:
  M1 (B1'-conditional): g = 258,033,293 (T = 2^20), 259,824,025 (T = 2^34)
  M2:                   g = 261,446,274 (T = 2^20), 263,285,578 (T = 2^34)
Exact in Q: ((g-1)/B)^k <= 1/100 for k = 117, 142, 175, 238. Record: w = 2048 < lambda = 128 (F1).
~~~

Not reviewed: Theorem 2, hash-chained reveal, Conjecture B1'-M2, Assumption RW-IC.
