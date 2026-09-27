---
cursor:
  subagentId: "bc-a2881cda-5857-5d2a-82bd-458f6b99d672"
---

lane: flock-soundness · kind: handoff · from: proximity-gap scoping (bc-a2881cda) · created: 2026-09-27T17:35Z · repo: danielreuter/verity · about: PR #127, PR #163, `Accounting/`

# proximity-gap scoping → flock-soundness: A2's constant is beaten by the birthday attack, plus three optional gains

Found while surveying ArkLib and VCVio for Daniel (`docs/arklib-survey.md`). The first item is a correctness issue in
your open PRs #127 and #163; the rest are optional.

## 1. A2 as stated is false for the generic birthday attack (0.17 bits)

`SHA512ExpectedTimeCR` bounds a finder's success by `E[cost]/2^256.5`, and DESIGN §3 justifies it by
$\min(1, q^2/2^{513}) \le q/2^{256.5}$. That argument covers finders whose query count is fixed, or chosen at random in
advance. It does not cover finders that stop adaptively.

**The counterexample.** Hash distinct inputs until the first collision.
- It succeeds with probability 1.
- Its expected cost is $E[\tau_N] = \sum_{i \ge 0} \prod_{j<i}(1 - j/N) \approx \sqrt{\pi N/2} + \tfrac23$, which is
  $2^{256.326}$ for $N = 2^{512}$.
- A2 caps it at $2^{256.326}/2^{256.5} = 0.886$.
- Mixing with probability $p$ gives success $p$ at cost $p\,E[\tau_N]$, violating A2 by a factor of 1.128 at every $p$.
- Checked exactly at $N = 2^{16}$ to $2^{32}$, and by simulation at $2^{20}$ (1,283.7 queries on average, against 1,284.06
  predicted).

**The sharp generic bound.** In the random-oracle model, $\Pr[\text{collision}] \le E[Q]/E[\tau_N]$, attained by the
attack above. The proof:
- Let $a_i = \Pr[\text{the finder makes an } i\text{-th fresh query with no collision yet}]$ and $w_i = (i-1)/N$.
- Then $\Pr[\text{collision}] \le \sum_i a_i w_i$, with $a_{i+1} \le a_i(1-w_i)$ and $\sum_i a_i \le E[Q]$.
- So $a_i = c_i b_i$, with $c_i = \prod_{j<i}(1-w_j)$ and $b_i$ non-increasing.
- The weighted mean of the increasing $w_i$ is largest at constant $b$ (Chebyshev's sum inequality), where it equals
  $\sum_i c_i w_i / \sum_i c_i = 1/E[\tau_N]$.

**The fix.** Replace $2^{256.5}$ by $E[\tau_N] = \sqrt{\pi/2}\cdot 2^{256}\,(1+o(1))$, or by a clean $2^{256}$ (0.5 bit, and
safe).
- Every link term moves by 0.17 to 0.5 bit: audit B's $t\cdot 2^{-205.6}$ becomes $t\cdot 2^{-205.4}$ or $2^{-205.1}$.
- The fix touches `Assumptions.SHA512ExpectedTimeCR`, the finder bound in `flock_batched_linkSoundE`, DESIGN §3's table,
  and the claim text for Table 1.
- **Making it checkable:** VCVio (in your manifest) proves `romCRAdvantage_le_birthday` for strict query bounds. An
  expected-query lemma in VCVio's random-oracle model would show A2's constant is at least consistent with the ideal
  model. Your call whether that is worth a file.

## 2. Optional: what ArkLib at our pin proves that sharpens the table bound

None of these changes the protocol; they change only the analysis. The numbers come from
`internal/arklib-survey/eta_retune.py`, which recomputes `tableError` with Bound.lean's own terms.

- **Lists.** `Code.finset_card_le_pairwiseJohnson` holds over any alphabet, so it covers interleaved codes read
  column-wise. It gives $\lfloor n(A-D)/(A^2-nD)\rfloor$: 7, 13, 17, 19, 21, 22 at the six m = 33 levels, against today's
  50 … 1,600. That shrinks $L_0$ for the knowledge extractor and every $L$-multiplied term.
- **Folds.** `TensorMCA.tensorFoldBad_probability_le`, with `fullSetLevelWitness_interleaved_of_exactAgreement`, charges
  one exceptional set per fold level: $h\cdot E$ instead of $(2^h - 1)\cdot a$. This is DKT26 Corollary 7.8, and it is
  paper Lemma 9 proved in general, with the full common agreement set.
- **η.** With those two results and DKT26's count, the slack is free.
  - At the unchanged `fast100` query counts, the per-table bound is $2^{-202.0}$ at $\eta = 1/100$, $2^{-205.2}$ at
    $1/200$ and $2^{-207.5}$ at $1/1000$, against $2^{-195.5}$ today.
  - Alternatively, the same 100 bits per level needs about 6% fewer queries at $\eta = 1/1000$ (201/101/67/51/41/34/29).
    That one is a spec change for Daniel.

**Ask.** Please take (1) into #127 and #163 before they merge, or tell me why the constant is right. (2) is for you to
weigh after the A1 rewire.
