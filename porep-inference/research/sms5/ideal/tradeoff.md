# Ideal-model completion bound for the RW–SMS raw-block audit

Theory memo, 2026-09-21. Package: this memo and `research/sms5/ideal/tradeoff.py` (stdlib; `python3 tradeoff.py --all` prints every number below). Builds on `research/trusted4/tdp.md` Theorem B1 (section 1.2, proof and Counting paragraph) with the R3 tightenings of `research/trusted4/tdp_review.md` (Findings 1, 2, 4, 5), and on `research/trusted4/theory/template_bound.md` Lemma 3 and section 3.5. Labels: **proved** (written out here or cited to a section), **sketched**, **conjectured**, **derived** (script).

## 0. Object, conventions, what is charged

**Block map.** $y_j = m_j + t_j \bmod N$; $(a_1, r_j) = \mathrm{RWInv}(y_j)$; $z_j = r_j \oplus K_j$; $h_j = \lfloor z_j/N \rfloor$; $v_j = z_j - h_j N$; $(a_2, c_j) = \mathrm{RWInv}(v_j)$. Record $(c_j, a_1, a_2, h_j)$, $w + 8$ bits. Decode: $v = a_2 c^2$, $z = v + hN$, $r = z \oplus K_j$, $y = a_1 r^2$, $m = y - t_j$.

**Incompressible width.** Let $D := \mathbb{Z}_N^*$, $M := |D| = \varphi(N)$, $w' := \log_2 M$. Encode is a bijection from $D$ onto the set of valid records, so a record is a $(w+8)$-bit *name* for one element of a set of size $M$. The theorems charge $w'$ bits per block; with the top 20 bits of $N$ set, $w' = w - \kappa$, $\kappa < 2^{-19}$, and I write $w$. The 5 flag bits and 3 padding bits are **not charged**: given $y_j$ the flags are recoverable from $(c, a_2)$ in at most six squarings, and the padding is constant. So a server holding $S = (1-\varepsilon)(w+8)B$ bits is measured against $wB$ incompressible bits and gets $8(1-\varepsilon)$ bits per block free. The *loss budget* (the $L$ at which the bound turns vacuous) is $\varepsilon w - 8(1-\varepsilon)$: **94.8 bits** at $(w, \varepsilon) = (2048, 0.05)$, not 102.4; 43.4 at $\varepsilon = 0.025$; 146.0 and 69.0 at $w = 3072$.

**Budget $T$.** Total modular squarings (RW forward evaluations) available to the online adversary over the whole audit window: about $10^9$ per second per H100 at $w = 2048$, so $2^{20}$ per GPU-millisecond; $2^{24}, 2^{28}, 2^{34}$ cover 16 to 16,000 GPU-milliseconds. The budget is *total for the audit* (R3 Finding 2), not per block. In model M1 one ideal query is two squarings; I charge one, conservative by one bit.

**Adversary.** $A_1$ unbounded, receives $W$, pp, $C$ and the entire oracle tables, outputs $\sigma$ with $|\sigma| = S$. $A_2(\sigma, \cdot)$ has forward-oracle access only, at most $T$ queries in total, and must return the exact records. No inverse oracle: an inverse is a canonical Rabin root, i.e. factoring; the transfer (section 5) needs that neither $A_1$ nor $A_2$ holds the factorisation.

**Sizes.** $70 \cdot 10^9$ payload bytes at $w - 16$ bits per block: $B = 2^{28.04}$ at $w = 2048$ ($|C| = 70.83$ GB), $B = 2^{27.45}$ at $w = 3072$; $\lambda' = 64$. Slow memory is out of scope except for section 1.5 and the allowance $\tau$.

## 1. Theorem 1: whole-file bound, sequential reveal

### 1.1 Models

**M1 (composite, independent).** $\Pi = (\Pi_1, \dots, \Pi_B)$ independent uniform permutations of $D$; $c_j := \Pi_j^{-1}(y_j)$; a query names $(j, x)$ and returns $\Pi_j(x)$.

**M2 (two shared oracles).** $\pi_1, \pi_2$ independent uniform permutations of $D$; public bijections $\sigma_j$ (XOR with $K_j$ plus the $h$, $a$ bookkeeping); $r_j := \pi_1^{-1}(y_j)$, $v_j := \sigma_j(r_j)$, $c_j := \pi_2^{-1}(v_j)$; queries to $\pi_1$ or $\pi_2$. **M3**: $\pi_1 = \pi_2$, the faithful model (one squaring function); same bound as M2 (2.3).

M1 needs no distinctness; in M2/M3 the $y_j$ and the $v_j$ must be distinct, which holds except with probability $B^2 2^{-w}$ over the tweaks and masks. All $B$ oracles are treated jointly, so the theorem is a whole-encoding statement and needs no composition lemma (template_bound.md 3.5, last bullet).

### 1.2 Single-history lemma

**Lemma A (proved).** Fix deterministic $(A_1, A_2)$ where $A_2(\sigma, i)$ is a *replay* of at most $T_r$ queries independent of $i$ followed by at most $T_f$ fresh queries, $T_r + T_f \le T$, $T \ge 4$. Let $G := \{ i : A_2(\sigma, i) = c_i \}$. For every $1 \le g \le B$,
$$\text{M1:}\ \ \Pr_\Pi\bigl[|G| \ge g\bigr] \le 2^{S} \tbinom{B}{g}\, e\,(1 + 2/T)\,(eT)^g\, M^{-g},\qquad
\text{M2:}\ \ \Pr\bigl[|G| \ge g\bigr] \le 2^{S} \tbinom{B}{g}\, e\,(1 + 2/T)\,(gT)^g\, (M - g)^{-g}.$$

*Proof (M1).* An injective encoding of the tuples $\Pi$ with $|G| \ge g$, following tdp.md 1.2 with one oracle per block. Let $G'$ be the $g$ smallest elements of $G$. Write (1) $\sigma$; (2) $G'$; (3) the hit list; (4) the pool. The decoder simulates the replay, then $A_2(\sigma, i)$ for $i \in G'$ in increasing order, skipping matched blocks. A *hit* is a query $(j, x)$ with $j \in G'$ unmatched and $\Pi_j(x) = y_j$; at most one per block, so $h \le g$ hits at positions among at most $T_r + g T_f \le (g+1)T$ simulated queries; item (3) is the set of hit positions, $\sum_{h \le g} \binom{(g+1)T}{h}$ possibilities. **No identity is written: the matched block is the oracle index $j$ named in the query.** Item (4): for $j \in G'$, $\Pi_j$ on $D \setminus \{c_j\}$ as a bijection onto $D \setminus \{y_j\}$ ($(M-1)!$); for $j \notin G'$, all of $\Pi_j$ ($M!$); mixed-radix in decoder order. Decoder, on query $(j, x)$: table if known; if the position is flagged, answer $y_j$, set $c_j := x$, mark $j$; else read $\Pi_j$'s next pool entry. At the end of the run for an unmatched $i$, set $c_i :=$ output. Every answer is right: an unflagged new query $(j, x)$, $j \in G'$, has $x \ne c_j$, so $\Pi_j(x) \in D \setminus \{y_j\}$ is a pool value. *Counting.* Consecutive terms of the sum have ratio $((g+1)T - h + 1)/h \ge T - 1$ (R3 Finding 1), so the sum is at most $(1 + 2/T)\binom{(g+1)T}{g} \le (1+2/T)\,(e(g+1)T/g)^g \le e\,(1 + 2/T)\,(eT)^g$. Divide by $(M!)^B$. $\square$

*M2 differences.* The $\pi_1$ pool is written as the $g$ preimages $r_j$ ($j \in G'$) followed by the bijection $D \setminus \{r_j\} \to D \setminus \{y_j\}$: $M!$ in total, no saving. The $\pi_2$ pool is $D \setminus \{c_j\} \to D \setminus \{v_j\}$, $(M-g)!$. The decoder computes $v_j = \sigma_j(r_j)$ before simulating, answers $\pi_1(r_j) = y_j$ from the table, and a $\pi_2$-hit (query $x = c_j$) needs the **identity** of the matched block, because $\pi_2$ names no block: item (3) is $\sum_h \binom{(g+1)T}{h}\, g!/(g-h)! \le (1 + 2/T)((g+1)T)^g \le e(1+2/T)(gT)^g$ (tdp.md 1.2, Counting).

*Constants.* In tdp.md the $\log_2 e$ vanished because $\binom{gT}{g}\, g! \le (gT)^g$: the identity factor absorbs the $1/g!$ of the unordered position set (R3 Finding 1). M1 has no identity factor, so $\binom{gT}{g} \le (eT)^g$ leaves $\log_2 e$. The trade is $\log_2 g \to \log_2 e$: 26.6 bits per block saved at $g \approx 2^{28}$.

### 1.3 Whole-file threshold and the sequential audit

Per-block losses $L_{\mathrm{M1}} := \log_2 T + \log_2 e$, $L_{\mathrm{M2}}(g) := \log_2 T + \log_2 g$, and
$$g^* := \min\Bigl\{ g : g\,\bigl(w - L(g)\bigr) \ \ge\ S + \log_2 \tbinom{B}{g} + \lambda' + k \log_2 B + 2.5 \Bigr\}.$$
The 2.5 absorbs $\log_2 e + \log_2(1 + 2/T) + 1$; $\log_2\binom{B}{g} \le B\,H_2(g/B) \approx 0.16$–$0.22\,B$; $\lambda' + k\log_2 B$ is below $10^{-4}$ bits per block.

**Theorem 1 (proved; M1 and M2/M3).** Sequential game: for $j = 1, \dots, k$ the verifier draws $i_j \leftarrow [B]$, sends it, receives $\hat c_j$; $A_2$ is stateful with at most $T$ queries in total. For every $(A_1, A_2)$,
$$\Pr\bigl[\hat c_j = c_{i_j}\ \forall j\bigr] \ \le\ (g^*/B)^k + 2^{-\lambda'} .$$
*Proof.* For a history $h = (i_1, \dots, i_{j-1})$ the round-$j$ computation is a single-block algorithm $A_{2,h}(\sigma, \cdot)$: the replay of rounds $< j$ (the same queries for every input) then the fresh queries. Lemma A applies with $T_r + T_f \le T$, the replay executed once (R3 Finding 2). At $g = g^*$ the exponent is at most $-\lambda' - k \log_2 B$; a union bound over the fewer than $2B^{k-1}$ histories gives $\Pr_\Pi[\exists h : |G_h| \ge g^*] \le 2^{-\lambda'}$. On the complement $i_j$ is uniform and independent of $(\Pi, h_j)$, so round $j$ passes with probability below $g^*/B$; multiply. $\square$

*Whole file, not challenged population.* $G_h$ ranges over all $B$ blocks and $S$ is the state for the whole file. spec.md's Theorem 1 wrote $s \ge g(w - \dots)$ for the $g$ *challenged* blocks, vacuous at $s \approx 0.95\,Bw \gg kw$; the right object is the recoverable fraction $g^*/B$, multiplied $k$ times by the audit.

*Closed form (derived).* $g^*/B \approx \bigl[(1-\varepsilon_c)(w+8) + H_2(g^*/B)\bigr]/(w - L)$; $u := 1 - g^*/B$; $k_\beta = \lceil \ln \beta / \ln(1-u) \rceil$.

### 1.4 Simultaneous reveal, and why sequential wins

**Theorem 2 (proved; template_bound.md Lemma 3(iii), tdp.md 1.4 as corrected by R3 Finding 5).** All $k$ indices revealed at once, at most $T$ queries in total. For $\eta \in (0, 1)$ let $R := \lceil (\lambda' + \log_2 B) \ln 2 / \eta \rceil$ and let $g^*_{\mathrm{joint}}$ be $g^*$ with $L + \log_2 R$ in place of $L$. Then
$$\Pr[\text{pass}] \le (g^*_{\mathrm{joint}}/B)^k + k\eta + 2k\,2^{-\lambda'} .$$
*What changes.* For position $j$ let $f_j(i)$ be the probability over the other coordinates that output $j$ equals $c_i$, and $L_j(\eta) := \{ i : f_j(i) \ge \eta \}$. The encoder is randomised (shared $\rho$): $R$ sampled tuples with coordinate $j$ open; for each $i \in G' \subseteq L_j(\eta)$ it writes the position of a sample on which $A_2$ is right ($\log_2 R$ bits; every block of $L_j$ is hit by some sample except with probability $2^{-\lambda'}$). The decoder regenerates the named tuple and runs $A_2$ once per recovered block, hits flagged as in Lemma A. Then $\Pr_I[\text{pass}] \le \prod_j |L_j|/B + k\eta$ because the coordinates of $I$ are independent and uniform. $\square$

At $\beta = 10^{-6}$ the optimum is $\eta \approx 2^{-31}$, $\log_2 R = 37$: those bits turn $k = 376$ into 777 (M1, $w = 2048$, $T = 2^{20}$) and make M2 at $w = 2048$, $T = 2^{34}$ vacuous. **Sequential reveal is the variant to use**: a fixed history makes the per-block algorithm deterministic, so no sample position is paid and the replay is executed once. The price is operational: verifier-driven reveal costs $k$ LAN round trips, and $T$ must be taken over the wall-clock window $\Delta + k\,\mathrm{RTT}$ (2–3 bits at $k = 400$, $\mathrm{RTT} = 5$–$10\ \mu$s). **Hash-chained reveal (sketched).** $i_{j+1} := H(\nu, j, c_{i_j})$, $H$ a random oracle, removes the round trips. Take the round boundary to be the adversary's first $H$-query at the true $c_{i_j}$: before it the computation is independent of $i_{j+1}$ (a fresh uniform value of $H$); after it, it is $A_{2,h}(\sigma, i_{j+1})$ with $\nu$ in the history. Lemma A applies per history with $H$ fixed; the union bound grows by $256 + k\log_2 B$ bits, still below $10^{-3}$ bits per block. Routine, not written out.

### 1.5 Budget convention and slow memory

*Total versus per block.* Theorem 1 charges $\log_2 T$ with $T$ the total budget, because after any fixed history the whole remaining budget can go to the next block. The truncation attack that must complete all $k$ blocks realises only $\log_2(T/k)$ (column `att`), so the bound is loose by $\log_2 k + \log_2 e \approx 10$ bits at $k \approx 300$. A per-history compression cannot see $\sum_j q_j \le T$; recorded as slack.

*Slow copy (extension, stated, not tabulated).* Give $A_2$ read access to an arbitrary string $\Sigma$ fixed by $A_1$, at most $8 b_s$ bits read per audit. The bits read during a run are unknown to the decoder, so the encoder writes them, at most $8 b_s$ per executed run: Lemma A holds with $S$ replaced by $S + 8 b_s g$, i.e. per-block state $S/B + 8 b_s$. This is tight in the only sense that matters: $b_s = 257$ bytes per challenged block fetches the record. No completion theorem absorbs slow fetches beyond a few bytes per block; tiering belongs to the bulk-bandwidth audit and enters here only as the allowance $\tau$, with Theorem 1 applied at $\varepsilon_c = \varepsilon - \tau$.

## 2. Two-round structure

**What M1 hides.** The real decode is $\mathrm{RW} \circ \sigma_j^{-1} \circ \mathrm{RW}$ with **one** squaring function shared by all blocks. M1 asserts that the $B$ block maps are independent random permutations, hiding (i) that the first decode squaring $a_2 c^2$ is block-independent, so one real squaring is a $\pi_2$-query for every block at once, and (ii) the intermediates $r_j$, $v_j$, all known to $A_1$. M2/M3 expose both.

**Hit structure in M2/M3.** $\pi_1(x)$ at $x = r_j$: the decoder holds every $r_j$ from the start (first segment of the $\pi_1$ pool, at full price), a free table lookup. $\pi_2(x)$ at $x = c_j$: a hit whose answer is one of the $g$ known $v_j$; *which one* costs $\log_2(\#\text{unmatched})$ because a $\pi_2$-query names no block. Everything else is a pool read. Hence the proved loss is $\log_2 T + \log_2 g$, as in tdp.md, against $\log_2 T + 1.44$ in M1; the identity term is the only difference and is charged only on other-hits (R3 Finding 4). Attack side: truncation costs two queries per candidate, realising $\log_2 T - 1$; storing partial intermediates does not help, since verifying a candidate needs the full chain to $y_j$ (an $\ell$-bit filter on $v_j$ saves $\pi_1$-queries, no $\pi_2$-queries, and costs $\ell$ bits), and spec.md Lemma 5(iv)'s half-bits accounting says the same for the concrete map; meet-in-the-middle needs an inverse oracle. The truth in M2 is believed to be $\log_2 T + O(1)$.

**Answer.** Idealising the composite (M1) suffices for a proof and gives the tighter constant, but it asserts more about the real scheme than one squaring function can deliver: that cross-block reuse of the shared squaring gains nothing, which is Conjecture B1' in disguise. The right model is M2, or M3 (one pool on $D \setminus (\{r_j\} \cup \{c_j\})$; identical bound up to the probability $2g^2/M$ that some $r_j$ equals some $c_{j'}$ or some $y_j$ some $v_{j'}$). The two-oracle model changes the proved loss by exactly $\log_2 g - \log_2 e \approx 26.6$ bits at $w = 2048$, 1.3 points of $u$. *Storing* intermediates is covered by both theorems ($\sigma$ is never interpreted); *exploiting their algebra* is outside both (section 5).

## 3. The $\log_2 g$ term

(a) **In M1 it is gone, proved**: the identity of a hit block is the oracle index in the query. This proves Conjecture B1' for independent per-block permutations and shows the term in tdp.md is entirely a consequence of oracle sharing (tdp.md 1.3's per-group-moduli knob is the $g \to 64$ instance).

(b) **In M2/M3 it stays for other-hits, and the raw-block audit gives no leverage.** The compression runs over the whole recoverable set $G'$ ($\approx 0.977B$ blocks); the $k$ challenged indices never enter it. Charging an other-hit by its position among *all* simulated queries is $\log_2(gT)$, the same $\log_2 g$ written differently; charging it to the pool costs $w$ bits (R3 Finding 4). Simulating only the $k$ challenged blocks would save $kw \ll S$ bits and prove nothing, which is spec.md's error.

**Conjecture B1'-M2 (conjectured).** In M2/M3, Theorem 1 holds with $L = \log_2 T + c_0$ for an absolute $c_0$; the tables take $c_0 = \log_2 e$, i.e. the M1 column. Evidence: R3 Finding 4's refined encoding shows the excess is $a \log_2 g$ with $a$ the other-hit fraction; the only known other-hitting strategy (unordered set) saves $\log_2 g - 1.44$ bits at $g$ queries and, combined with truncation, $\log_2 T - 2.4$; nothing above $\log_2 T + O(1)$ is known. Both bounds are tabulated.

## 4. Numbers

Derived, `tradeoff.py`. `M2` = proved with the shared squaring oracle(s); `M1` = proved in M1 = Conjecture B1'-M2; `att` = truncation floor with the total budget split over $k$ blocks; `u` = unanswerable fraction $1 - g^*/B$; `k6`, `k2` = $k$ for $\beta = 10^{-6}$, $10^{-2}$ per audit; `-` = vacuous. Rows with $\tau = 0.025$ apply Theorem 1 at $\varepsilon_c = \varepsilon - 0.025$. Moving $\Delta$ from 0.25 to 1 ms shifts $\log_2 T$ by 2 bits, within a row's neighbours.

~~~
    w  S/|C|   tau  eps_c log2T |   L_M2    u_M2  k6_M2  k2_M2 |   L_M1    u_M1  k6_M1  k2_M1 |  L_att   u_att k6_att
---------------------------------------------------------------------------------------------------------------------
 2048   0.95   0.0 0.0500    20 |   48.0  0.0233    586    196 |   21.4  0.0361    376    126 |   11.6  0.0408    332
 2048   0.95   0.0 0.0500    24 |   52.0  0.0214    640    214 |   25.4  0.0342    398    133 |   15.6  0.0390    348
 2048   0.95   0.0 0.0500    28 |   56.0  0.0194    706    236 |   29.4  0.0323    422    141 |   19.5  0.0371    366
 2048   0.95   0.0 0.0500    34 |   62.0  0.0164    834    278 |   35.4  0.0294    463    155 |   25.4  0.0343    396
 2048   0.95 0.025 0.0250    20 |   48.0 -0.0023      -      - |   21.4  0.0108   1274    425 |   10.3  0.0163    844
 2048   0.95 0.025 0.0250    24 |   52.0 -0.0043      -      - |   25.4  0.0088   1556    519 |   14.1  0.0144    953
 2048   0.95 0.025 0.0250    28 |   56.0 -0.0063      -      - |   29.4  0.0069   2000    667 |   17.9  0.0126   1094
 2048   0.95 0.025 0.0250    34 |   62.1 -0.0094      -      - |   35.4  0.0039   3504   1168 |   23.5  0.0098   1402

 2048  18/19   0.0 0.0526    20 |   48.0  0.0260    525    175 |   21.4  0.0388    350    117 |   11.7  0.0435    311
 2048  18/19   0.0 0.0526    24 |   52.0  0.0241    568    190 |   25.4  0.0369    368    123 |   15.7  0.0416    326
 2048  18/19   0.0 0.0526    28 |   56.0  0.0221    618    206 |   29.4  0.0350    389    130 |   19.6  0.0397    341
 2048  18/19   0.0 0.0526    34 |   62.0  0.0192    714    238 |   35.4  0.0321    424    142 |   25.5  0.0369    367
 2048  18/19 0.025 0.0276    20 |   48.0  0.0004  36133  12006 |   21.4  0.0135   1020    340 |   10.5  0.0188    728
 2048  18/19 0.025 0.0276    24 |   52.0 -0.0016      -      - |   25.4  0.0115   1194    398 |   14.3  0.0169    809
 2048  18/19 0.025 0.0276    28 |   56.0 -0.0036      -      - |   29.4  0.0096   1439    480 |   18.2  0.0151    909
 2048  18/19 0.025 0.0276    34 |   62.0 -0.0067      -      - |   35.4  0.0066   2083    695 |   23.9  0.0123   1115

 3072   0.95   0.0 0.0500    20 |   47.4  0.0325    418    140 |   21.4  0.0408    333    111 |   11.7  0.0439    308
 3072   0.95   0.0 0.0500    24 |   51.4  0.0313    436    146 |   25.4  0.0395    343    115 |   15.7  0.0426    318
 3072   0.95   0.0 0.0500    28 |   55.4  0.0300    455    152 |   29.4  0.0382    355    119 |   19.6  0.0414    327
 3072   0.95   0.0 0.0500    34 |   61.4  0.0280    486    162 |   35.4  0.0363    374    125 |   25.6  0.0395    343
 3072   0.95 0.025 0.0250    20 |   47.4  0.0071   1937    646 |   21.4  0.0156    882    294 |   10.5  0.0191    717
 3072   0.95 0.025 0.0250    24 |   51.4  0.0058   2377    793 |   25.4  0.0143    962    321 |   14.4  0.0179    767
 3072   0.95 0.025 0.0250    28 |   55.4  0.0045   3077   1026 |   29.4  0.0130   1059    353 |   18.3  0.0166    826
 3072   0.95 0.025 0.0250    34 |   61.4  0.0025   5518   1840 |   35.4  0.0110   1247    416 |   24.1  0.0147    932

 3072  18/19   0.0 0.0526    20 |   47.4  0.0352    386    129 |   21.4  0.0434    312    104 |   11.8  0.0465    291
 3072  18/19   0.0 0.0526    24 |   51.4  0.0339    401    134 |   25.4  0.0421    321    107 |   15.8  0.0453    299
 3072  18/19   0.0 0.0526    28 |   55.4  0.0327    417    139 |   29.4  0.0409    331    111 |   19.7  0.0440    307
 3072  18/19   0.0 0.0526    34 |   61.4  0.0307    443    148 |   35.4  0.0390    348    116 |   25.7  0.0422    321
 3072  18/19 0.025 0.0276    20 |   47.4  0.0098   1406    469 |   21.4  0.0182    753    251 |   10.7  0.0217    630
 3072  18/19 0.025 0.0276    24 |   51.4  0.0085   1624    542 |   25.4  0.0169    810    270 |   14.6  0.0204    669
 3072  18/19 0.025 0.0276    28 |   55.4  0.0072   1923    641 |   29.4  0.0156    878    293 |   18.5  0.0192    714
 3072  18/19 0.025 0.0276    34 |   61.4  0.0052   2657    886 |   35.4  0.0137   1003    335 |   24.4  0.0173    792
~~~

Simultaneous reveal (Theorem 2, $\varepsilon = 0.05$, $\tau = 0$, $\beta = 10^{-6}$): $w = 2048$, $T = 2^{20}$: M2 $k = 3467$ ($\log_2 R = 38$), M1 $777$; $w = 3072$: M2 $684$, M1 $479$; M2 at $w = 2048$, $T = 2^{34}$ vacuous. Between $1.4\times$ and $6\times$ the sequential $k$.

## 5. What the ideal theorem needs from the concrete map

Let $g^*_{\mathrm{M2}}(S, T, \lambda_{\mathrm{dev}})$ be the threshold of 1.3 with $L = \log_2 T + \log_2 g + \lambda_{\mathrm{dev}}$.

**Assumption RW-IC$(w, T, \lambda_{\mathrm{dev}})$ (transfer; not proved here).** $N$ a $w$-bit Williams modulus sampled by the encoder; salt uniform and drawn after $W$ is fixed; $s := S/B$ with $s/w \in [0.90, 0.98]$. For every preprocessing $A_1$ of work below the cost of factoring $N$ ($\approx 2^{112}$ at $w = 2048$, $2^{128}$ at $3072$) outputting $|\sigma| = S$, every online $A_2$ whose total work in the audit window is at most $T$ squaring-equivalents on its hardware (all operations counted), and every history $h$ of the sequential audit: the real recoverable set satisfies $|G_h| \le g^*_{\mathrm{M2}}(S, T, \lambda_{\mathrm{dev}})$ except with probability $2^{-\lambda'}$ over $(N, \mathrm{salt})$.

In words: no advice-aided completion algorithm for RW–SMS does more than $\lambda_{\mathrm{dev}}$ bits per block better than the two-oracle ideal-permutation bound, at states between 90% and 98% of $w$ (the $\tau = 0.025$ rows sit at $s/w = 0.979$) and budgets up to $2^{34}$. The tables are at $\lambda_{\mathrm{dev}} = 0$; each bit of deviation costs $\partial u/\partial L \approx 1/w$, so 20 bits at $w = 2048$ is one point of $u$, the same order as the $\log_2 g$ question. The M1 transfer is the stronger assumption: it adds that cross-block reuse of the shared squaring gains $O(1)$ bits, i.e. B1' for the concrete map.

What the assumption must survive, by name: (i) single-round Coppersmith on $c^2 = a_2^{-1} v$ (spec.md Lemma 5(i); needs $v_j$, which costs $w$ bits or a root of $y_j$); (ii) homomorphism attacks such as shift-and-kangaroo (tdp.md 4.2.7), which need a group relation between stored value and target that the XOR $\sigma_j$ destroys (spec.md Lemma 5, closing remark); (iii) bivariate small-root attacks on partial $(c, v)$ or $(r, c)$ (Lemma 5(iii)–(iv)); (iv) Jacobi and quarter information, already inside the $w'$ accounting; (v) anything combining the integer representation of $K_j$-masked values with the ring structure of squaring. By template_bound.md Lemma 3(i)–(ii) the assumption is equivalent to the audit statement up to the margin, so it is a bespoke "assume the conclusion up to the ideal constant" statement of the kind tdp.md 4.2.6 discusses; the ideal theorem fixes the constant and certifies that no *structure-free* attack exists.

## 6. Verdict

**Viable at $\varepsilon = 5\%$ without a tiering allowance; not viable with the 2.5% allowance at $w = 2048$ under the proved M2 bound.**

- At $(w, \varepsilon, \tau) = (2048, 0.05, 0)$ the proved M2 bound needs $k = 586$–$834$ for $\beta = 10^{-6}$ ($196$–$278$ for $10^{-2}$) over $T = 2^{20}$–$2^{34}$; M1/B1' needs $376$–$463$; the attack floor is $332$–$396$. Honest cost: $k \times 257$ bytes and a lookup per audit. If $k \le 400$ is a hard limit, the proved bound gives $\beta = 10^{-2}$ per audit, hence $10^{-6}$ only via a window rule ($\binom{5}{3} 10^{-6} \approx 10^{-5}$ for 3-of-5) or under B1'.
- With $\tau = 0.025$ the budget halves (43 bits at $w = 2048$), the proved M2 loss (48–62 bits) exceeds it, and the bound is **vacuous**; M1/B1' needs $k \ge 1274$. At $w = 3072$ (budget 69 bits) M2 needs $k = 1900$–$5500$, M1 $880$–$1250$. The allowance, not the hardware multiplier, is the expensive item: $T \times 2^{14}$ costs 14 bits, $\tau = 0.025$ costs 51.
- $w = 3072$ buys $1.5\times$ the budget, 128-bit factoring for the no-inverse leg (2048-bit is 112-bit, marginal for a multi-year hostage) and $k = 418$–$486$ proved at $\varepsilon = 0.05$, at $2.25\times$ the squaring cost.
- $\Delta$ barely matters here (2 bits from 0.25 to 1 ms); its work is on the regeneration and tiering side.

Looseness, in bits per block at $w = 2048$: the $\log_2 g$ identity term, 26.6 (proved absent in M1, conjectured absent in M2; the largest item, 1.3 points of $u$); total-versus-per-block convention, $\approx 10$ (section 1.5); uncharged flag and padding bits, 8 (fix: pack eight records into $8 \cdot 2053$ bits or keep flags in a separate dense array; recovers 0.4 points of $u$, script `--all`); one bit for counting a two-squaring query as one. Everything else is below 0.2 bits. Outside the theorem: Assumption RW-IC, whose tolerance $\lambda_{\mathrm{dev}}$ is the dominant unknown.

## 7. Summary (ten lines)

1. Theorem 1 (proved): with independent per-block ideal permutations (M1), an $S$-bit adversary with $T$ total online squarings passes the sequential $k$-record audit with probability $\le (g^*/B)^k + 2^{-\lambda'}$, where $g^*(w - \log_2 T - 1.44) \approx S + 0.2B$.
2. With the shared squaring oracle (M2/M3, the faithful model) the loss is $\log_2 T + \log_2 g^*$, tdp.md's Theorem B1 constant; the difference is 26.6 bits per block at $w = 2048$.
3. The $\log_2 g$ term is proved to be an artefact of oracle sharing: it vanishes when queries name their block. In M2 it remains Conjecture B1'; the audit's named challenges give no leverage.
4. Charged per block: $w' = \log_2\varphi(N) \approx w$. The 8 flag and padding bits per record are free to the adversary, so the loss budget at $\varepsilon = 5\%$ is 94.8 bits, not 102.4.
5. Sequential reveal beats simultaneous by $\log_2 R = 37$ bits per block at $\beta = 10^{-6}$; use verifier-driven or hash-chained sequential reveal.
6. $T$ is the total audit budget; the bound charges $\log_2 T$, the truncation attack realises $\log_2(T/k)$: about 10 bits of slack.
7. At $(2048, 5\%, \tau = 0)$: proved $k = 586$–$834$ for $\beta = 10^{-6}$ over $T = 2^{20}$–$2^{34}$; B1' $376$–$463$; attack floor $332$–$396$. At $w = 3072$: $418$–$486$ proved.
8. With the 2.5% tiering allowance the proved M2 bound is vacuous at $w = 2048$ and needs $k \ge 1900$ at 3072; B1' needs $k \ge 1274$ and $882$. The allowance costs 51 of 95 budget bits.
9. Transfer is Assumption RW-IC: no advice-aided completion beats the M2 ideal bound by more than $\lambda_{\mathrm{dev}}$ bits per block for $s/w \in [0.90, 0.98]$, $T \le 2^{34}$, $A_1$ unable to factor; equivalent to the audit statement (template_bound.md Lemma 3), unproved.
10. Verdict: strong enough at $\varepsilon = 5\%$ with $k$ in the several hundreds if RW-IC holds; the 2.5% tiering allowance, not the deadline or the hardware multiplier, is what breaks it at $w = 2048$.
