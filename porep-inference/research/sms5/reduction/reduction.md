# RW–SMS v1: advice-aided completion — reductions, attacks, minimal assumption

2026-09-21. Scope: the exact map of the brief (Williams $N$, $w \in \{2048, 3072\}$, two RW inversions with a dense public XOR between them). Inputs read: `template_bound.md` §3, §5; `tdp_review.md` §2.3, §6; `tdp.md` §1.2, §4.2–4.3; `sms5/spec.md` Lemma 5. Everything from the brief that I rely on was re-verified at toy scale (`rwsms_toy.py`: bijectivity, the four selector classes, fibre size 16 with exactly one canonical record, the half-bits and affine-mixing attacks; `frontier.py`: the closed-form numbers of §1, §3 and Theorem 2). Labels: **[P]** proved, **[H]** heuristic (standard lattice heuristics, or verified numerically at toy size), **[C]** conjectured.

## 0. Two facts used throughout

Record $\mathrm{rec}_j = (c_j, a_1, a_2, h_j)$, width $w + 4$ bits. Decoding is public and deterministic: $D_j(\mathrm{rec}) = a_1\bigl((a_2 c^2 + hN) \oplus K_j\bigr)^2 - t_j$.

**F1 (tiny fibre, publicly recognised canonical member) [P].** For two-prime $N$ with $\gcd(y_j, N) = \gcd(v_j, N) = 1$, $D_j^{-1}(m_j)$ has exactly 16 elements (four roots per layer; a wrong selector leaves a non-residue), and exactly one has $r, c \in J_N^+$: that one is $\mathrm{rec}_j$. The predicate $\mathrm{Canon}_j(\mathrm{rec})$ := "$a_1, a_2 \in \mathcal{A}$; $c \in J_N^+$; $z := a_2c^2 + hN < 2^w$; $r := z \oplus K_j \in J_N^+$; $D_j(\mathrm{rec}) = m_j$" costs two squarings and two Jacobi symbols, uses no trapdoor, and holds only for $\mathrm{rec}_j$. For an arbitrary odd $w$-bit $N$ (with the gcd conditions) the fibre has at most $2^{4 + 2\omega(N)} \le 2^{470}$ elements at $w = 2048$ ($\omega(N) \le 233$). Verified: 120/120 toy blocks, fibre 16, one canonical.

**F2 (the honest $v$ is not uniform) [P].** $z_j = r_j \oplus K_j$ is uniform on $[0, 2^w)$, so $v_j = z_j \bmod N$ has mass $2^{1-w}$ on $[0, 2^w - N)$ and $2^{-w}$ on $[2^w - N, N)$. Worth under one bit to an attacker, but a trapdoor-free simulator must reproduce it (§2.1).

## 1. The advice-aided completion problem

**Definition 1 (AAC game, ROM).** Parameters $w, B, s, T$. (1) $(N, p, q) \leftarrow \mathrm{Gen}(w)$; the adversary chooses $W = (m_j)_{j < B}$ knowing $N$; $\mathrm{salt} \leftarrow \{0,1\}^{256}$; $t_j = H(\mathrm{salt}, j)$, $K_j = H(\mathrm{salt}, j, \mathrm{mix})$; $C = (\mathrm{rec}_j)_j$; $(p, q)$ erased. (2) $\sigma \leftarrow A_1^H(N, W, \mathrm{salt}, C)$, $|\sigma| \le sB$, $A_1$ unbounded. (3) $j \leftarrow [B]$; $\mathrm{rec}' \leftarrow A_2^H(\sigma, N, W, \mathrm{salt}, j)$ within $T$ decode-equivalents (one decode = two $w$-bit modular squarings). Success: $\mathrm{rec}' = \mathrm{rec}_j$. Write $G(\sigma) := \{j : A_2 \text{ correct on } j\}$.

**Definition 2.** RW–SMS is **$(s, T, \epsilon)$-hard** if every $(A_1, A_2)$ succeeds with probability $\le \epsilon$; it has **loss $L$** if $|G(\sigma)| \le (sB + \lambda)/(w - L)$ except with probability $2^{-\lambda}$. The ideal-permutation completion theorem gives $L = \log_2 T + \log_2 g$; at $s = 0.95w$, $T = 2^{30}$, $g \approx 2^{27}$ this is $\epsilon \approx 0.977$ and $k \approx 200$ challenged blocks give a 1 % pass rate. By `template_bound` Lemma 3 this property *is* audit soundness given $W$; there is nothing weaker to prove.

**Frontier.** Saving := $(w + 4) - $ (bits stored per block). Truncation buys $\log_2 T$. The scheme claims $\varepsilon = 5\,\%$: no adversary saves $0.05w = 102$ bits ($w = 2048$; 154 at 3072) with $T = 2^{30}$. An attack is *decisive* if it saves 60–200 bits ($s/w \in [0.90, 0.97]$) in time $\le 2^{30}$; *irrelevant* if it saves $\le \log_2 T + O(1)$, or if it needs the adversary to hold more than $w$ bits about the block. Realistic online budgets are smaller: one H100 does $\approx 4 \cdot 10^9$ 2048-bit squarings/s, so $k = 200$ blocks in $\Delta \in [0.25, 1]$ ms allow $T_\Delta \approx 2^{11}$–$2^{13}$ per block per GPU and $2^{18}$–$2^{20}$ with 100 GPUs; $T = 2^{30}$ is a generous cap.

## 2. Reductions

### 2.1 Trapdoor-free simulation (route a) [P]

**Lemma 1.** In the programmable ROM there is an efficient $\mathrm{Sim}(N, W, \mathrm{salt})$ that, *without the factorisation*, outputs $(C, H)$ within statistical distance $2B(1/p + 1/q)$ of the real game and knows every record. Per block: draw $a_1, a_2 \leftarrow \mathcal{A}$ and $r, c \leftarrow J_N^+$ (rejection on Jacobi and range); $v := a_2c^2$; accept $v$ with probability 1 if $v < 2^w - N$ and $1/2$ otherwise (else redraw $c$); $h \leftarrow \{0,1\}$ if $v < 2^w - N$, else $h := 0$; $z := v + hN$; program $K_j := z \oplus r$ and $t_j := a_1 r^2 - m_j$. *Proof.* $(a_1, r)$ is uniform on $\mathcal{A} \times J_N^+$, so $t_j$ is uniform on $\mathbb{Z}_N^*$; the rejection step gives $z$ exactly the distribution of F2, i.e. uniform on $[0, 2^w)$, so $K_j$ is uniform; the record is canonical by construction; the only deviation is that real $y_j, v_j$ may be non-units. $\square$

So a reduction can run $A_1$ on a perfectly distributed codeword for its own factoring challenge $N$. What does a successful $A_2$ then yield? By F1 the only correct output is $\mathrm{rec}_j$, which the reduction itself placed into $A_1$'s input. **Extraction yields nothing**: in a completion game the correct answer is a deterministic function of $A_1$'s input, and Lemma 1 says that input needs no secret.

### 2.2 Embedding a fresh target (route b) [P]

Let the reduction hold $y^* = a x^2$ with $x$ known (the Rabin-to-factoring embedding), set $t_{j^*} := y^* - m_{j^*}$, and hope $A_2$ returns a root $r^* \ne \pm x$. If $(x \mid N) = +1$ the canonical root *is* $\pm x$. If $(x \mid N) = -1$ (probability $1/2$) the reduction cannot form $\mathrm{rec}_{j^*}$: (i) an arbitrary record decodes to $m_{j^*}$ with probability $\le 16 \cdot 2^{-w-4}$ and is caught by one decode; (ii) the record built from $r' = \min(x, N - x)$ decodes correctly but fails $\mathrm{Canon}_{j^*}$ at the Jacobi test: caught with probability 1 at cost $O(w^2)$. (iii) If canonicalisation were dropped (encoder picks a random root per layer), (ii) becomes undetectable, and $A_2$ returns exactly the record it was shown. Detection is a red herring; determinism is the obstruction.

### 2.3 The obstruction is generic: no black-box reduction [P]

**Theorem 2 (no fully-black-box reduction, programmable ROM).** Let $\mathcal{P}$ be any single-stage assumption (an efficient challenger against one stateful adversary: factoring, RSA, QR, any falsifiable assumption). Let $\ell$ bound $\log_2$ of every fibre $D_j^{-1}(m)$ over all odd $w$-bit $N$ satisfying the gcd conditions ($\ell \le 470$ at $w = 2048$; $\ell = 4$ if $N$ carries a two-prime proof). For every $s \ge \ell + \lambda$, every $T$, every $\epsilon < 1 - O(B/\sqrt N)$: if a PPT oracle machine $R$ satisfies "$R^{A_1, A_2}$ breaks $\mathcal{P}$ whenever the oracle $(A_1, A_2)$ breaks $(s, T, \epsilon)$-hardness", then there is a PPT algorithm breaking $\mathcal{P}$ with advantage within $q_2 2^{-\lambda}$ of $R$'s, $q_2$ the number of $A_2$-calls. In particular against factoring: any such $R$ factors.

*Proof.* Let $F$ be a random function into $\{0,1\}^{\ell + \lambda}$ and define the (inefficient) attacker $\mathcal{A}_F$. $A_1$: for each $j$ query $H$ for $t_j, K_j$, form $\kappa_j := (N, \mathrm{salt}, j, m_j, t_j, K_j)$, check that $N$ is odd, the gcd conditions and $\mathrm{Canon}_j(C_j)$, output $\sigma_j := F(\kappa_j, C_j)$ if they hold and $\bot$ otherwise. $A_2(\sigma, j)$: recompute $\kappa_j$ from the current $H$, enumerate $D_j^{-1}(m_j)$ (unbounded work), output the member $\mathrm{rec}$ with $F(\kappa_j, \mathrm{rec}) = \sigma_j$, or $\bot$. In the honest game $\mathcal{A}_F$ answers every block from $\ell + \lambda$ bits per block, so $R^{\mathcal{A}_F}$ breaks $\mathcal{P}$ for every $F$, hence for random $F$. Fully-black-box reductions must work for such oracles (this is the sense of MW20 Theorem 8.1 and Wichs 2013).

Simulator $M$ (efficient, stateful). On an $A_1$-call: perform the same checks with the same $H$-queries; for each consistent $j$ look up $(\kappa_j, C_j)$ in a table and return its tag, else store it with a fresh uniform tag; inconsistent blocks get $\bot$. On an $A_2$-call: recompute $\kappa_j$ from the *current* $H$-answers; if the table holds $(\kappa_j, C)$ with tag $\sigma_j$, return $C$, else $\bot$.

Faithfulness. Tags are fresh uniform values per distinct $(\kappa_j, C_j)$ in both worlds. The real $A_2$ returns non-$\bot$ iff $\sigma_j = F(\kappa_j, \mathrm{rec})$ for some fibre member; if $R$ obtained $\sigma_j$ from an $A_1$-call on $(\kappa_j, C_j)$ then $\mathrm{rec} = C_j$ except for a collision inside the fibre (probability $\le 2^{\ell} \cdot 2^{-\ell-\lambda}$), and $M$ returns the same $C_j$; otherwise $F(\kappa_j, \cdot)$ is independent of $R$'s view and a match has probability $\le 2^{-\lambda}$. Reprogramming $H$ between the phases changes $\kappa_j$ and is treated identically in both worlds. So $R^M$ is efficient and breaks $\mathcal{P}$. $\square$

*Remarks.* (i) This is Moran–Wichs Theorem 8.1 carried into the programmable ROM. MW20's own ROM construction escapes because its codeword carries a fresh $pk$ and its lossy hybrid has fibres of size $2^{\Omega(|C|)}$, so a short tag stops identifying the record once $R$ feeds a hybrid codeword; a deterministic rate-$(1 - 4/w)$ encoding with a shared $N$ has fibre 16 under *every* $N$ and *every* oracle table. The brief's Theorem 3 (HILL obstruction) is the same fact seen from the hybrid side. (ii) The theorem covers every redesign with deterministic public decoding and short public parameters: extra rounds, any mixer, randomised root choice (fibre still 16). (iii) Standard caveats: it does not exclude reductions that use $A_2$'s code or time bound non-black-box, two-stage assumptions (§2.5), or idealised-model compression arguments, which are not reductions. The unbounded $A_2$ is the same device as in MW20 8.1; the point is what a reduction can *extract*, which is nothing.

### 2.4 One-more roots, self-reducibility, hard-core bits (routes c–e)

*One-more / chosen-target* [P]. One-more-inversion assumptions concern a target whose root the adversary has not seen; here $A_1$ sees all $B$ roots and $A_2$ must reproduce one from $s$ bits. A $T$-bounded $A_2$ that output a *non-canonical* fibre member would factor $N$ by Prop. 1, so the only outputs to reason about are the ones $A_1$ saw: the problem is compression, not inversion. The adversary's only influence on targets is $m_j$ before the salt. *Random self-reducibility* [P]: $y \mapsto ys^2$, $r \mapsto rs$ cannot transport advice that is an arbitrary function of $r$; it yields Prop. 1 and nothing about advice. *Hard-core bits* (ACGS, Håstad–Näslund) quantify over adversaries without side information; $s$ bits of arbitrary side information cost a factor $2^{s}$, vacuous at $s \approx 0.95w$. The informative literature is leakage/auxiliary-input one-wayness (DGO19's "$B$-leakage TDP", Dodis–Kalai–Lovett): Rabin is *not* $w/2$-leakage secure (Coppersmith) and nothing is known between $O(\log w)$ and $w/2$, the Blum–Blum–Shub output-rate gap (Fischlin–Schnorr prove $O(\log w)$ bits per squaring; $w/2$ is the attack). The assumption of §4 lives in that gap.

### 2.5 What escapes Theorem 2

(a) *Two-stage assumptions*, whose own adversary has a bounded-output preprocessing stage. The natural candidate, single-instance preprocessing Rabin ("from $s'$ bits about $r$, and $y$, find $r$"), does not reach the scheme: $(R_1, R_2)$ can build a consistent $C$ around $(y^*, r^*)$ by programming $K_{j^*}$ around a chosen $c$ (Lemma 1's trick), but $A_1$ returns $sB$ bits and $R_1$ may forward $s'$; extracting one block's share needs a direct-product theorem for two-stage games, which is open (MW20 §5 conjecture counterexamples for Yao-type incompressibility). The usable two-stage assumption is therefore the multi-instance statement about RW–SMS itself (§4). (b) *Non-black-box use of $A_2$'s time bound*: no technique known to me. (c) *Idealising the decoder*: the completion theorem; its transfer to RW–SMS is (a). Idealising only the mixer while keeping Rabin standard is GLW20's setting, whose proof needs $B\lambda$ rounds (a pigeonhole over the adversary's state); at two rounds one is back to DGO19's refuted accounting. (d) *Enlarging fibres* to $2^{\Omega(w)}$ per block (hidden coins, rate loss) or a data-length CRS (memory $\times 2$): outside the budget, and the brief's Theorem 3 caps factoring-based twins near 25 %.

## 3. Attacks at the frontier

Two heuristics carry the section. **(H1)** From $y$ and $\ell$ bits of advice about a Rabin root $r$, recovering $r$ in time $T$ needs $\ell \ge w/2 - \log_2 T - O(1)$ (Coppersmith's $N^{1/2}$ plus brute force; likewise $c$ from $v$). **(H2)** For dense $K$ there is no polynomial relation over $\mathbb{Z}_N$ of degree $< 2^{\Omega(w)}$ between $r$ and $r \oplus K$ ($r \oplus K = r + K - 2(r \wedge K)$ has $\mathrm{popcount}(K) = 1025 \pm 22$ unknown bits at $w = 2048$, Exp. C), and squaring mod $N$ has no low-degree $\mathbb{F}_2$ form.

**Lemma 3 (two-layer accounting) [H under H1, H2].** The outer relation $a_2 c^2 = v$ can be used *forwards* (candidates for $c$, each checked by one decode, since H2 forbids batching the test $a_1 r^2 = y$ over a family of $c$-candidates) or *backwards* (from $v$, which needs $r$, which by H1 needs $\ge w/2 - \log_2 T'$ stored bits of $r$, after which $c$ needs $\ge w/2 - \log_2 T'$ stored bits of its own; $T'$ = affordable Coppersmith runs). Forwards saves $\log_2 T + 2$ (Jacobi of $c$ and of $y$). Backwards saves $2\log_2 T' - 2\delta - 3$, where $\delta$ is the distance from $w/2$ that a lattice costing $C_{LLL}(\delta)$ reaches, $T' = T/C_{LLL}(\delta)$. Because the two layers are verified independently ($r$ against $y$, then $c$ against $v$), the backwards route has **two** brute-force budgets: a real structural deviation from an ideal permutation, whose loss is one $\log_2 T$. It is priced by $\delta$: at $w = 2048$, dimension $n \approx w/\delta$ and entries $\approx nw/2$ bits give (L² cost $n^4 B^2$, one decode $\approx 2^{23}$ bit operations) $C_{LLL} \approx 2^{33}$ decodes at $\delta = 32$ ($n = 64$), $2^{21}$ at $\delta = 128$, $2^{7}$–$2^{12}$ at $\delta = 341$ (the 3-dim lattice); backwards beats forwards only when $\log_2 T > 2\log_2 C_{LLL} + 2\delta + 5$, whose minimum over $\delta$ is $\approx 111$ (`frontier.py`). Below $T \approx 2^{100}$ it saves nothing; at the online $T \le 2^{30}$ its saving is negative.

| # | attack | stored bits | saving at $T = 2^{30}$ | status |
|---|---|---|---|---|
| 1 | truncate $c$, brute force; $(c\mid N) = 1$, $(y \mid N)$ fixes half of $a_1$ | $w + 2 - \log_2 T$ | $32$ ($15$–$22$ at $T_\Delta$) | works [P]; optimal [C] |
| 2 | store $r_{hi}, c_{hi}$; Coppersmith twice (Exp. A) | $2w - t_r - t_c + 5$, $t \le w/2$ | $\le -1$; $-w/3$ with 3-dim lattices | works, no saving [H, toy] |
| 3 | #2 plus brute force on both layers (Lemma 3 backwards) | $w + 2\delta - 2\log_2 T' + 5$ | $< 0$ for $T < 2^{100}$; $2\log_2 T$ asymptotically | deviation, priced [H] |
| 4 | linearise the XOR (store $r \wedge K$), eliminate $r$, degree 4 in $c$ | $w/2 + w - t_c$, $t_c \le w/4$ | $\le -w/4$ | [H] |
| 5 | bivariate $a_2 c^2 - x_v = \mathrm{const}$, $(x_c, x_v)$ unknown | $x_v$ only from eq. 1, i.e. #2 | none | [H] |
| 6 | meet-in-the-middle on $v$ | $2w - t_r - t_c$, cost $2^{t_r} + 2^{t_c}$ | $\le 2\log_2 T - w$ | [P] |
| 7 | shift-and-kangaroo on $c$ (R3's RSA break) | needs the outer target $v$; recognising the shift is one decode per candidate | collapses to #1 | [P] |
| 8 | cross-block: unordered set, XOR of groups, factor base | $\log_2 g$ at $g$ queries; $\rho(152)$ | inside the ideal loss; 0 | [P]/[H] |
| 9 | public $K_j$: bitwise $r_{hi} \to z_{hi}$ transfer; long runs in $K_j$ | feeds #2; a run of length $t$ has probability $w 2^{-t}$ | 0 | [P] |
| 10 | distributional: F2's 2:1 bias on $v$; $r < N/2$ | | $< 1$ | [P] |

*Counterfactual (Exp. B) [toy].* With an **affine** mixer $v = r + K$ the record satisfies $a_1(a_2c^2 - K)^2 = y$, a degree-4 univariate in $c$ with $y, K$ public: storing $c_{hi}$ alone and running a 5-dimensional lattice recovers the low $w/10$ bits (60/60 at $t_c = 10, 14$ and 58/60 at $t_c = 16 = w/10$, $w = 160$), and Coppersmith's full method reaches $w/4 = 512$ bits, a decisive break at zero online cost. The same stored data and lattice against the XOR mixer: 0/60. The XOR is all that separates the frontier from rate 0.75, and H2 is the statement that it holds.

*Latency.* #1 is embarrassingly parallel: $2^{13}$ candidates × 200 blocks × two squarings is one GPU-millisecond. A 3-dimensional Coppersmith is microseconds; approaching $w/2 - \delta$ needs dimension $w/\delta$ and seconds to hours. No attack in the table is simultaneously useful and latency-limited.

Toy output (`python3 rwsms_toy.py`, 3 min, pure Python plus sympy for degree-4 roots), abridged:

~~~
[0] w=64,96: 120 blocks encode/decode/canonical OK; fibre size 16; canonical records per fibre 1
[A] w=128: drop 32+32 bits of r,c -> recovered 60/60; storage 197 bits = 1.54 w (baseline 132)
[A] w=128: drop 42+42 bits of r,c -> recovered 58/60; storage 177 bits = 1.38 w (baseline 132)
[B] w=160: store c>>14 only. affine mixing: recovered 60/60.  XOR mixing, same lattice: 0/60.
[C] w=2048: popcount(K) = 1025.1 +- 22.2 unknown bits to linearise r XOR K
~~~

**Result [H].** The best attack saves $\log_2 T + 2 \le 32$ bits ($s/w \ge 0.984$); the frontier $[0.90, 0.97]$ is 30–170 bits beyond every route tried, and every route reduces to beating H1 or H2. The one structural deviation from the ideal model (two verifiable layers, #3) is priced and irrelevant below $T \approx 2^{100}$.

## 4. The minimal clean assumption

By `template_bound` Lemma 3 and Theorem 2, nothing single-stage suffices; the weakest sufficient statement is the conclusion itself, stated for the whole encoding, with the two-layer term made explicit:

**Assumption RW-IC$(s, T)$ [C].** For $N \leftarrow \mathrm{Gen}(w)$, any $W$, uniform salt, every $(A_1, A_2)$ of Definition 1 with $|\sigma| \le sB$ and $A_2$ of time $T$: $|G(\sigma)| \le (sB + \lambda)/(w - L)$ except with probability $2^{-\lambda}$, where
$$L = \max\Bigl(\log_2 T + \log_2|G|,\; \max_{\delta}\bigl[2\log_2\bigl(T/C_{LLL}(\delta)\bigr) - 2\delta\bigr]\Bigr) + O(1),$$
the second term being Lemma 3's backwards route. For $T \le 2^{100}$ the first term dominates: "RW–SMS loses no more than a random permutation." It is two-stage, multi-instance and construction-specific, not falsifiable in Naor's sense, and the exact analogue of Assumption RSA-IC that R3 refuted for single-round RSA, except that the refuting attack (#7) is blocked by the XOR and the two-layer term is now stated rather than missed.

*Necessary consequences* — each implied by RW-IC$(0.95w, 2^{30})$, each closer to the literature, none sufficient alone:

- **PIR$_\gamma$ (half-leakage Rabin–Williams) [C].** For uniform $y$ with canonical root $r$, any leakage $\Lambda(N, y, r)$ of $(\tfrac12 - \gamma)w$ bits and any $T$-time $A$: $\Pr[A(N, y, \Lambda) = r] \le T\,2^{-\gamma w + O(1)}$. RW-IC $\Rightarrow$ PIR$_{0.05 - 30/w}$ via #2 (store $\Lambda(r)$ and $w/2$ bits of $c$). False at $\gamma \le 0$ (Coppersmith, verified). This is DGO19's $B$-leakage property at $B = 0.45w$ and the BBS gap of §2.4.
- **TO (truncation optimality) [C].** RW-IC restricted to advice "top bits of $c$ plus $O(1)$ bits": no algorithm recovers $c$ from $(y, K, a_1, a_2, h, c_{hi})$ in fewer than $2^{t_c - O(1)}$ decodes. Exp. B refutes TO for affine mixing; H2 is its content for XOR.
- **No public fibre bits beyond Jacobi**: no three bits of $\mathrm{rec}_j$ are computable from $(N, y_j, K_j)$; the only candidates are residuosity bits, i.e. the QR assumption.

*Evidence for.* Coppersmith-type methods have sat at $N^{1/d}$ for one unknown for thirty years, and beyond it a modular quadratic can have exponentially many small roots, so any improvement must use the structure of $x^2 - u$, i.e. be a partial-key-exposure break of Rabin and BBS; XOR against ring arithmetic is the mixed-domain barrier behind ARX ciphers and Sloth; every route in §3 collapses to Lemma 3's identity, which does not depend on lattice constants; toy checks agree.

*Evidence against.* The 2012 hourglass "near-incompressibility" conjecture, the same kind of statement for a simpler map, fell to an elementary attack; "arbitrary advice" is far larger than "low bits", and no direct-product or leakage theory supports the multi-instance quantifier; no intermediate model (generic ring with bit access, ideal mixer with standard Rabin) is known in which a proof goes through; the two-layer term shows the ideal-permutation loss is *not* an upper bound at large $T$, so the deviation list is only as complete as its last review; the map has had one afternoon of adversarial attention.

## 5. Verdict

(i) **A reduction to factoring for this exact map.** Fully-black-box, programmable ROM, to any single-stage assumption: excluded by Theorem 2 (probability 0 given factoring is hard). Via a non-black-box argument, or a two-stage single-instance assumption plus a new direct-product theorem: $\approx 0.03$. **Total $\le 0.05$.**

(ii) **Actually secure at $s/w = 0.95$, $T = 2^{30}$** (no attack saving 102 bits per block in $2^{30}$ decodes): **$\approx 0.75$.** The 70-bit margin over the best attack rests on H1 (well-tested folklore) and H2 (structurally clean, untested by dedicated cryptanalysis); the hourglass precedent and the unbounded-advice quantifier are the discount.

(iii) **Design changes.** Nothing with deterministic decoding and short parameters alters (i) (Theorem 2, remark ii). For (ii): a third RW round moves Lemma 3's floor from "$\ge w$ stored" to "$\ge 3w/2$" for every algebraic route (the two-layer term becomes three-layer, still irrelevant below $2^{100}$), a $w/2$ cushion against a partial failure of H1 at about $+50\,\%$ decode cost; a keyed ARX mixer removes the bitwise $r_{hi} \to z_{hi}$ transfer (#9) and gives H2 conventional footing at $\approx 1$ op/byte; randomising the root choice adds four hidden bits per block and changes nothing. Whether a *provable* variant exists (mixer idealised as an ideal cipher, with a compression argument that avoids GLW20's pigeonhole at two rounds) is the redesign track's question; I do not see the argument, and Theorem 2 says it cannot be a reduction.

## Summary (10 lines)

1. RW–SMS records are determined by public data; a trapdoor-free ROM simulator (Lemma 1) yields a perfect codeword for any $N$, so every reduction hands $A_1$ the very values $A_2$ must return.
2. Embedding a fresh factoring target is detected with probability 1 (one Jacobi symbol); without canonicalisation it is undetectable and still yields nothing.
3. Theorem 2 [proved]: no fully-black-box reduction from advice-aided completion to any single-stage assumption, even in the programmable ROM, for any deterministic publicly-decodable encoding with small fibres — RW–SMS and every redesign of its rounds or mixer.
4. Escapes: two-stage assumptions (necessarily multi-instance, i.e. the conclusion), non-black-box use of $A_2$'s time bound, or idealising the decoder.
5. Attacks: every algebraic route collapses to "store $\ge w/2$ bits of $r$ and $\ge w/2$ of $c$" (Lemma 3); best saving $\log_2 T + 2 \le 32$ bits, $s/w \ge 0.984$; the frontier is 30–170 bits beyond it.
6. One structural deviation from the ideal permutation: two independently verifiable layers give two brute-force budgets ($2\log_2 T$ asymptotically); priced by Coppersmith's cost, it saves nothing below $T \approx 2^{100}$.
7. Toy-verified: half-bits attack works but stores $\ge w$; affine mixing loses $w/4$ bits for free (decisive); XOR mixing loses nothing to the same lattice; linearising the XOR costs $w/2 \pm 22$ bits.
8. Minimal assumption RW-IC (RW–SMS loses no more than an ideal permutation, plus the two-layer term): two-stage, construction-specific; implies half-leakage Rabin hardness PIR$_{0.05}$ and truncation optimality — the BBS gap between $O(\log w)$ proved and $w/2$ attacked.
9. Probabilities: reduction to factoring $\le 0.05$; secure at $s/w = 0.95$, $T = 2^{30}$: $\approx 0.75$; a third round or an ARX mixer raises the latter toward 0.9 and leaves the former at 0.
10. Recommendation: file RW–SMS as "proved in the ideal-permutation model, secure under RW-IC, unprovable by reduction"; commission dedicated cryptanalysis of H2 (dense XOR between two modular squarings) before relying on the 5 % margin.
