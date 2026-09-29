---
cursor:
  subagentId: "bc-9e538dc5-64c5-5aad-b845-7ae98c178569"
---

lane: flock-soundness · kind: draft · status: open, for review before the lifetime numbers change · repo: danielreuter/verity · follows `note:20260927T0600Z-review-knowledge-soundness` §4(d) and [PR #124](https://github.com/danielreuter/verity/pull/124) (`table_knowledge_sound_joint`)

# The link term δ_link, on paper

*Update 08:22Z: the joint form is `ε_c⁻ + K·Adv₀ + N₀/(eK)`, with no factor 2 (no Markov step). So every combined
number below improves. Strict time becomes `2√(t·2^-221.5)` for audit B (2^-69.8 at t = 2^80), and §5's expected-time
option is `t·2^-206.6`, at c = 2. `DESIGN.md` §3 has the current table.*

*Update 15:10Z: expected-time collision resistance is of record (Daniel, 14:34Z), with the term
`t·N_s(8N₀/e)/2^256.5`. `DESIGN.md` §3 in PR #127 derives it from the plurality value layer at c = 2: the link
finder recovers one commit string twice, `2(1+k)t` per string. §5's c = 4 form below predates the tight joint form.
The Lean plan is `note:20260927T1510Z-draft-expected-time-link-plan`.*

**Result.** Under strict-time collision resistance, the knowledge and link terms of one audit together cost about
$2\sqrt{t\cdot 2^{-220.5}}$ for audit B at m = 33. That is $2^{-69.3}$ at $t=2^{80}$, against the review's first
estimate of $2^{-65.3}$. It is still far above every other term of the audit bound (`docs/lifetime-soundness.md` §3).
The square root is inherent to strict-time rewinding here: the link collision finder must run the extractor, whose run
count trades off against the knowledge term's missing-position term. An expected-time assumption or the random-oracle
column removes it (§5).

## 1. What δ_link is

This is the lifetime doc's §3, step 2(c). In an audit hit, $u^*$ (the first wrong drawn unit) is fixed before the
session's first coin. Acceptance forces one of three things:

- (a) a tree-layer mismatch ($\delta_{\rm tree}$);
- (b) the table accepts while its extractor fails (the knowledge term);
- (c) the extractor succeeds but recovers, behind some commit string of $u^*$, a value other than $X$'s ($\delta_{\rm link}$).

$X$'s value layer is "the value the extractor recovers most often behind each commit string". It must depend only on
the state at registration, so that the draw is independent of the wrong set.

## 2. The value layer, the way the table extractor fills its table

Fix the registration state. $X$'s value layer is defined the way the extractor of `Knowledge.lean` fills its table,
one layer up.

- **Auxiliary procedures.** Run $K_d$ of them, independent of the audit's draw. Each draws its own unit set, runs the
  session to its level-0 caps, and extracts every drawn table from $K$ session reruns. The same reruns serve all $J$
  tables.
- **The value layer.** $X(c)$ is the first value any auxiliary procedure recovered behind the tree-layer commit string
  at $c$, and a fixed value where none did.

$X$ depends on the auxiliary randomness, but not on the audit's draw or coins. So the draw is still independent of the
wrong set, and the audit bound averages over $X$.

Then (c) needs the actual extraction to recover a value $v\ne X(c)$ at some $c$ of $u^*$. As in
`off_firstTable_le`, that happens in one of two ways:

- **It conflicts** with the auxiliary procedure that supplied $X(c)$. Two independent procedures from registration
  recover different values behind one commit string, which is an `hm96` binding break and hence a SHA-512 collision.
  Over the $K_d$ pairs, this costs $K_d\,\mathrm{Adv}_{\rm link}$.
- **It recovers a position no auxiliary procedure recovered.** With $r_c$ the probability that one procedure recovers
  $c$, and the actual recovery probability at most $r_c$, this costs $\sum_c r_c(1-r_c)^{K_d}\le N_s/(eK_d)$.

So $\delta_{\rm link}\le K_d\,\mathrm{Adv}_{\rm link}+N_s/(eK_d)$. At the best $K_d$ this is
$2\sqrt{N_s\,\mathrm{Adv}_{\rm link}/e}$.

- **The finder's cost.** It runs two procedures, each $K+1$ sessions, so about $2Kt$ hash evaluations:
  $\mathrm{Adv}_{\rm link}\le(2Kt)^2/2^{513}$ and $\delta_{\rm link}\le 2\sqrt{N_s/e}\cdot 2Kt/2^{256.5}$.
- **An auxiliary extraction that fails** only lowers $r_c$. So this term needs no success guarantee, and so no
  block amplification and no $\varepsilon_{\min}$ truncation.

## 3. Combined with the knowledge term, one $K$

Charge (b) with `table_knowledge_sound_joint` at the same $K$, averaged over the state at the caps. It is linear in
`adv₀`, so no Jensen step is needed:
$2\varepsilon_c^-+2K\,\mathrm{Adv}_0+2N_0/(eK)$. Then

$$\text{(b)}+\text{(c)}\;\le\;2\varepsilon_c^-+\frac{2N_0}{eK}+K\Big(2\,\mathrm{Adv}_0+\frac{4\sqrt{N_s/e}\;t}{2^{256.5}}\Big)
\;\approx\;2\varepsilon_c^-+2\sqrt{\frac{8N_0\sqrt{N_s/e}\;t}{e\cdot2^{256.5}}},$$

at $K\approx\sqrt{N_0\,2^{256.5}/(2\sqrt{N_s/e}\,t)}$. The $\mathrm{Adv}_0\approx t^2/2^{511}$ term is negligible.
This is the review's $\min_{\varepsilon_{\min}}[\ldots]$ without its factor 128: the knowledge term's $2N_0/(eK)$
plays the role of $\varepsilon_{\min}$.

## 4. Numbers (m = 33, $N_0=2^{21}$; add 1 to each exponent at m = 35)

The exponent is $\log_2\big(8N_0\sqrt{N_s/e}/(e\,2^{256.5})\big)$.

| Audit | $N_s$ | exponent | $t=2^{64}$ | $2^{80}$ | $2^{100}$ | $2^{110}$ |
|---|---|---|---|---|---|---|
| A | $2^{18.7}$ | $-225.3$ | $-79.7$ | $-71.7$ | $-61.7$ | $-56.7$ |
| B | $2^{28.3}$ | $-220.5$ | $-77.3$ | $-69.3$ | $-59.3$ | $-54.3$ |
| C | $2^{34.3}$ | $-217.5$ | $-75.8$ | $-67.8$ | $-57.8$ | $-52.8$ |
| D | $2^{40}$ | $-214.7$ | $-74.4$ | $-66.4$ | $-56.4$ | $-51.4$ |

Entries are $\log_2$ of $2\sqrt{t\cdot2^{\rm exponent}}$. For comparison, the lifetime doc's $\delta_{\rm hash}$ is
$t\cdot2^{-229.3}$ for audit B, which is $2^{-149.3}$ at $t=2^{80}$.

**Refinements, small.**

- **Accepted-run deviation.** The coupling's bad event already requires acceptance, so (A′)'s deviation term can
  count only accepted runs' openings. That is a one-line change to `bad_pointwise`.
  - A prover can then make only a $\ln(2/\varepsilon)/(2Q_0)$ fraction of positions rare (the review's refinement).
    That shrinks the missing term by about $2^{-1.7}$ at $\varepsilon\ge\varepsilon_c^-$, so the combined bound
    improves by about $2^{-0.85}$.
- **Per-unit reads.** The link conflict counts positions over all commit strings. Restricting it to $u^*$'s reads
  would need the finder to target $u^*$, which the auxiliary draws don't do.

## 5. What would remove the square root

- **Expected-time collision resistance** (CDGSY24, "Untangling the Security of Kilian's Protocol", ePrint 2024/1434,
  Theorem 2). *Corrected 07:40Z: an earlier version said about $t\cdot2^{-220}$, from a quadratic form of the
  assumption, which is false.*
  - **The assumption.** A finder making $T$ SHA-512 evaluations in expectation succeeds with probability at most
    $T/2^{256.5}$. That is the generic bound, since $\min(1,q^2/2^{513})\le q/2^{256.5}$. It can't be quadratic: a
    finder that makes $2^{256.5}$ evaluations with probability $T/2^{256.5}$ gambles its way past $T^2/2^{513}$.
  - **The extractor.** It runs the session once and, only if that run accepts, reruns until $k=cN_0/e$ reruns have
    accepted. With $a=\Pr[\text{accept}\wedge\neg\text{opens }p]\le\varepsilon$, a position $p$ is missed with
    probability $(a/(a+q_p))^k\le(\varepsilon/(\varepsilon+q_p))^k$. Summed, that is
    $N_0\max_q q(\varepsilon/(\varepsilon+q))^k\le N_0\varepsilon/(e(k-1))\approx\varepsilon/c$, so the joint form's
    missing term is about $2\varepsilon/c$. An extraction costs $(1+k)\,t$ in expectation, whatever $\varepsilon$, and
    it needs no estimate of $\varepsilon$.
  - **The link finder.** It samples auxiliary extractions until one recovers the position the actual extraction
    recovered. Over positions, that is $\sum_c r_c/r_c\le N_s$ extractions in expectation, by Wald, about
    $N_s(cN_0/e)\,t$ evaluations.
  - **The bound is relative.** $u^*$ is wrong, so acceptance itself is the bad event. Per state, bound (b) by
    $\min(\varepsilon,\,\cdot)$, which turns the conflict term $2K\mathrm{Adv}_0\propto1/\varepsilon$ into
    $\sqrt{2cN_0\mathrm{Adv}_0/e}\approx t\cdot2^{-244}$. Then
    $\Pr[\text{hit}\wedge\text{accept}]\,(1-2/c)\le\delta_{\rm tree}+2\varepsilon_c^-+N_s(cN_0/e)\,t/2^{256.5}$.
  - **The constant.** $c=4$ minimizes $c^2/(c-2)$, which gives $t\cdot N_s(8N_0/e)/2^{256.5}$ and doubles the other
    terms. For audit B that is $t\cdot2^{-205.6}$, or $2^{-125.6}$ at $t=2^{80}$. For A–D it is $t\cdot2^{-215.2}$,
    $2^{-205.6}$, $2^{-199.6}$ and $2^{-193.9}$.
  - **The status.** The assumption isn't in Table 1, and adding it is a spec decision (`DESIGN.md` §3, PR #127).
- **The random-oracle column** (lifetime doc §7). The extractor reads the commit strings and openings off the queries
  made before registration, so $\delta_{\rm tree}$, $\delta_{\rm link}$ and the knowledge term collapse into one
  $t^2/2^{511}$.
- **A protocol change.** Open the linked values to the verifier in the clear, with no hiding across units, or commit
  to them with an extractable scheme. Both change the privacy model.

## 6. Recommendation

- **Record this bound** as the strict-time knowledge-plus-link row of the lifetime doc. It is roughly $2^{-69}$ at
  $t=2^{80}$, audit B.
- **Label the audit's partial-integrity guarantee** "strict-time CR: about $2\sqrt{t\cdot2^{-220}}$", next to the ROM
  column.
- **Decide** whether the integrity profile should quote the ROM column, or add an expected-time CR assumption, for
  the audit's value layer.

The table theorems and `δ_tree` are unaffected.

**Lean.** The same `Extract.lean` machinery applies, with procedures as the runs and the value layer as the table.
Formalizing it needs the audit game (`oneStageC`, lane `audit-lean`) and the `hm96` layout. Coordinate there after
the review.
