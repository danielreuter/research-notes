# Redesign memo: can post-encoding compression be proved with only symmetric idealisations plus factoring?

Scope: trusted encoder, static weights, untrusted server with $S \le 0.95|C|$ bits of arbitrary advice and $T \approx 2^{20}$–$2^{30}$ public-map evaluations per audit; the open problem is post-encoding compression. Inputs read: `research/trusted4/tdp.md` (Theorem B1, lines 92–118; remarks 120–124; GLW20 reading 152–164; 4.2.7 at 238–252), `research/trusted4/tdp_review.md` (F4 line 30, F6 lines 58–72, "right interface, wrong object" line 26), `research/trusted4/theory/template_bound.md` (Lemma 3, lines 193–210; composition 234; Lemma 4(a) 240; §5 item 5, line 260), `research/sms5/spec.md`, `research/OPTIONS.md` rows A1–A6, B1–B3. Scripts: `toy_two_round.py` (toy checks, 96- and 128-bit Williams moduli), `params.py` (tables below). Labels: **proved**, **sketched**, **conjectured**.

Notation. $w$-bit Williams modulus $N$; $\rho$ is the public Rabin–Williams forward map $(a, r) \mapsto a r^2 \bmod N$ and $\rho^{-1} = \mathrm{RWInv}$ needs the trapdoor; $E$ is the idealised symmetric layer (ideal permutation on $[0,N)$ by cycle-walking, or a random oracle); $B = 2^{28}$ blocks, $g$ recovered blocks, $L$ the per-block loss so that $S \ge g(w - L)$.

## 1. The obstacle, characterised

### 1.1 The symptom: which queries break the B1 decoder (proved)

B1's decoder (tdp.md 116) answers three kinds of query: table (already known), pool (an entry it is not compressing), and *hit*: a forward query whose **input is the omitted preimage $c_j$ and whose output is the public target $y_j$** (tdp.md 113). It works because the omitted entry is reached only from the side the decoder knows. For $\rho_1 \to E \to \rho_2$ (decode $c \xrightarrow{\rho_2} v \xrightarrow{E} r \xrightarrow{\rho_1} y$), the omitted entries are $E(v_j) = r_j$, and the query types are:

| query by $A_2$ | input known to decoder | output known to decoder | B1 handling |
|---|---|---|---|
| $E(x)$, $x = v_j$, $j$ unmatched | no (omitted) | yes: $r_j = \mathrm{RWInv}(y_j)$, the decoder holds the trapdoor | hit, position + identity (proved) |
| $E(x)$, other $x$ | — | — | pool |
| $E^{-1}(z)$, $z = r_j$, $j$ unmatched | **yes** | **no: it is the omitted $v_j$** | **unanswerable** |
| $E^{-1}(z)$, other $z$ | — | — | pool |
| $H(\cdot)$ tweaks | public | fixed | free |

The single breaking query is the inverse-direction query at a known intermediate. It is cheap for the adversary because $r_j$ is a Rabin root of the *public* $y_j$: half of its bits plus one Coppersmith run reproduce it (spec.md Lemma 5(i); `toy_two_round.py` [1]: 40% of the bits at lattice dimension 6, asymptotically 50%), or the trapdoor reproduces it outright. Every intermediate of a publicly decodable chain is known to the post-encoding adversary, and every Rabin root whose square is known is half-compressible, so every ideal-layer entry is reachable from its *output* side at cost $\le w/2$, and the decoder can never be sure it will only be approached from the input side.

### 1.2 The cause: compression arguments see 2 bits per Rabin round (proved)

Given its square, a Rabin root has $\log_2 4 = 2$ bits of information-theoretic entropy. A compression argument is a counting argument over the ideal object (tdp.md 106–118: "the number of permutations is $N_D!$"); it can charge only information-theoretic uncertainty. Hence in any mixed design, *every real Rabin round contributes at most 2 bits to a compression bound*; the whole $w - L$ must come from the ideal layer, and the ideal layer is reachable from both sides by anyone who holds the intermediates. This is the exact point where B1 and the mixed designs differ: in B1 the trapdoor is the inverse *table* ($N_D \log N_D$ bits), so "compute $r_j$" costs a query the decoder can see; here the trapdoor is $2w$ bits.

**Proposition 1 (no information-theoretic theorem with a short secret; proved).** Let $\Pi$ be any encoding, in any idealised model, whose honest encoder is an algorithm using a $\kappa$-bit secret and $q_E$ oracle queries per block, with a correct public decoder. The adversary $A_1 = $ "output the secret and, per block, the index of $c_i$ in the decoder's fibre over $m_i$", $A_2 = $ "re-encode block $i$" answers every block with $q_E$ queries and $S = \kappa + \sum_i \log_2|\mathrm{Dec}^{-1}(m_i)|$. For the deterministic designs of §2 the fibre index is the 4 class bits, so $S = 2w + 4B$: 0.2% of $|C|$ at $B = 2^{28}$. (`toy_two_round.py` [0]: 96 stored bits, one $E^{-1}$ query per block.) For any efficiently decodable rate-$(1-\epsilon)$ encoding the fibre term averages $\le \epsilon|C|$ (template_bound.md 240, MW20 Thm 8.1). ∎

Consequently a theorem of the requested kind must bound $A_1$'s *computation* (it may not factor), so it is a computational statement and needs a reduction to factoring. B1's theorem needs no such bound (tdp.md 84: $A_1$ unbounded) only because its trapdoor is not a string.

### 1.3 What a factoring reduction would have to do (sketched)

A reduction $R$ must hand $A_1$ a world $(N, W, C, \mathrm{pp})$ and answer its oracle queries. $A_1$ can run the public decoder on every block and recompute every intermediate ($v_j = a_2 c_j^2$, $r_j = E(v_j)$, $a_1 r_j^2 = y_j = m_j + t_j$), so every value in every chain is fixed and verifiable, and $R$ must know all of them ($R$ can: choose $c_j, r_j$ uniformly, program $E(a_2c_j^2) := r_j$ and $t_j := a_1 r_j^2 - m_j$; the simulation is perfect). Then nothing $A_2$ correctly outputs is new to $R$. The only remaining lever is GLW20's *switching*: answer one of $A_2$'s queries with a fresh challenge and hope $A_2$ still answers correctly. The one query that can carry a Rabin challenge is $E^{-1}(r_i) \mapsto u^*$. But an $A_2$ that makes that query already holds partial information on $c_i$ (that is how it succeeds), and a random $u^*$ has no root consistent with it except with probability $2^{-\Omega(w)}$; `toy_two_round.py` [2] shows the failure on one flipped bit. So switching extracts nothing from any adversary that uses the inverse direction, whether or not it is a breaking adversary. GLW20's pigeonhole (tdp.md 155: Lemma 11 needs $2^{r-1} > 2^{|\mathrm{state}|}$) is the only known way to *guarantee* an unpinned switch position, and it costs $r = nb\lambda$ rounds; there is no intermediate technique (tdp.md 161). The mechanism by which the RO model escapes MW20 8.1 (program the parameters to a lossy mode, MW20 Thm 5.3) needs a lossy mode, which Rabin does not have (fibre $\le 16 \cdot 4^{\omega(N)}$). I expect MW20 8.1's meta-reduction to extend to IPM+ROM for every design in §2 (sketched, not written): the inefficient adversary "store 45% of each root and brute-force" is efficiently simulable to $R$, because on the real oracle its output is the $c_i$ that $R$ gave $A_1$, and on any switched answer it outputs $\bot$.

### 1.4 Auxiliary-input tools (proved inapplicable)

Unruh's presampling, CDGS18's bit-fixing lemma and CDG18's ideal-permutation/ideal-cipher versions convert an adversary with $S$ bits of advice *about the oracle* into one that fixes $P$ oracle points, at additive loss $\approx (S + \lambda)T/P$ for unpredictability games. At $S \approx 2^{39}$, $T = 2^{30}$, a loss of $2^{-64}$ needs $P \ge 2^{133}$ fixed points: fine against a $2^{2048}$ domain, but the framework does not fit. (i) Our advice depends on the instance ($C$, hence the trapdoor's outputs), not on the oracle alone; folding $(N, p, q)$ into the random object lets the bit-fixing adversary fix the $2w$ trapdoor bits, and Proposition 1 applies. (ii) The tools trade advice for control of $Pw \gg S$ oracle bits, useful when the hardness lives in a fresh challenge drawn after the advice; here the whole instance precedes the advice and there is no fresh challenge.

## 2. Design space

Each item: the query or attack that decides it.

**(a) $\rho_1 \to E \to \rho_2$.** No known attack below $w$ (§4). Proof: Theorem A below charges every block recovered *without* an inverse hit at its own $r_j$ at $w - \log_2 T - \log_2 g$ (proved). Inverse-hit blocks *can* be charged as uncompressed (they go to the pool; Theorem A does exactly this), but "the adversary paid anyway" is a computational fact — $w/2$ bits for $r_j$ and $w/2$ for $c_j$ given $v_j$ — invisible to counting (§1.2). The residual is Conjecture 2RG (§3.3).

**(b) $\rho_1 \to E_1 \to \rho_2 \to E_2 \to \rho_3$.** Same proof structure; the inverse-hit strategy now costs three half-roots, $1.5w > w$, so the conjecture needed weakens from "Coppersmith is optimal" to "a Rabin root keeps at least $w/3$ of its bits given its square" (§3.3). Decode cost $\ge 200$ int32/B (§3.4).

**(c) Tweaked or keyed $E$.** The obstacle is knowledge, not structure: the tweak is public, so $E_{t_j}^{-1}(r_j)$ is as cheap as $E^{-1}(r_j)$. A *secret* key would remove public decode. No change.

**(d) RO-based middle layer.** Any RO input used by the decoder is an intermediate, hence known post-encoding. With a one-round Feistel $E(v) = (v_L,\; v_R \oplus H(v_L))$, recovering a record reveals $H(r_L)$ — only $w/2$ bits of table (the half-width problem) — and the adversary reaches it by storing $r_L$ ($w/2$) and Coppersmithing $r_R$ from $y$ for free, then queries $H(r_L)$ with known input: the same unanswerable query, at a smaller IT charge. More Feistel rounds do not help: the adversary computes them from the intermediates. A non-invertible RO cannot be *encoded through* at all (the encoder would have to invert it), so the codeword can never *be* an RO input with a public target: that is the ideal TDP.

**(e) Encoder-side fresh randomness.** Real entropy of $C$ given $W$ is $\le |C| - |W| = \epsilon|C|$ (template_bound.md 240), so at most 5% of each block can be coins; the adversary stores them (Proposition 1). Without a lossy mode there is no HILL hybrid to switch to (MW20 Thm 5.3 route closed by the fibre count). No enabling effect.

**(f) Other trapdoors and models.** Any TDP with a short key is inside Proposition 1; a key as large as $|C|$ is the ideal TDP (B1), and no symmetric idealisation supplies one: a random oracle is not invertible by the encoder, an ideal permutation has no secret, an ideal cipher with an erased key has no public decode. Lattice and DCR trapdoors: closed on cost/rate (OPTIONS A1–A3). Generic-ring model for $\mathbb{Z}_N$ plus ideal $E$: keeps the group law but not the integer representation, so it misses Coppersmith and would "prove" $w - \log T$ for a round that is in fact half-free — tdp_review.md line 26's "right interface, wrong object", and not a symmetric idealisation. Single-round designs are broken as in the brief. Feistel networks of Rabin rounds on two-block records: every root in the network is half-free, $k$ rounds have $k$ roots for $2w$ bits, so 3 rounds still leak 25%; chains beat Feistels.

## 3. What can be proved, and the best design

No design in §2 admits the requested theorem. The sharpest negative statement is: **a compression theorem is impossible for any encoder with a short secret (Proposition 1, proved), and a factoring reduction has no extraction point once every codeword is fixed and verifiable by $A_1$ (§1.3, sketched); the only known reduction technique is GLW20 switching at $r = nb\lambda$ rounds.** What survives is an unconditional theorem for part of the adversary's behaviour, an exact equivalence that removes the ideal permutation, and a clean conjecture. Design (a) is the recommendation; (b) buys a weaker conjecture for +75 int32/B.

### 3.1 Design (a), stated

Public: $N$, seed. Per block $j$: $t_j = H(\mathrm{seed}, j) \bmod N$, $y_j = m_j + t_j$ (retry counter if $y_j \notin \mathbb{Z}_N^*$); $(a_{1,j}, r_j) = \mathrm{RWInv}(y_j)$; $v_j = E^{-1}(r_j)$ with $E$ a public permutation of $[0,N)$; $(a_{2,j}, c_j) = \mathrm{RWInv}(v_j)$. Record $(c_j, a_{1,j}, a_{2,j})$: $w + 3$ bits. Decode: $v = a_2 c^2$, $r = E(v)$, $m = a_1 r^2 - t_j$. The v1 overflow bit $h$ disappears (cycle-walking keeps $E$ on $[0,N)$).

### 3.2 Theorem A (proved): blocks recovered without an inverse hit are B1-bounded

**Model.** $E$ an ideal permutation ($E, E^{-1}$ oracles), $H$ a random oracle, $N$ and the trapdoor fixed. $A_1$ unbounded, receives everything including the table of $E$, outputs $S$ bits. $A_2(\sigma, i)$ makes $\le T$ queries. $G$ = set of $i$ with $A_2(\sigma, i) = c_i$.

**Classification.** Process $G$ in increasing order, simulating $A_2$ with the real oracle and maintaining matched $M$ and excluded $X$ (both empty at start); skip $i \in M \cup X$. On $E(x)$ with $x = v_j$, $j \in G \setminus (M \cup X)$: add $j$ to $M$ (a *hit*). On $E^{-1}(z)$ with $z = r_j$, $j \in G \setminus (M \cup X)$: add $j$ to $X$. At the end of run $i$, if $i \notin M \cup X$, add $i$ to $M$. Let $G_{\mathrm{FM}} = G \setminus X$ (recovered "from memory or forward hit") and $G_{\mathrm{I}} = X$.

**Statement.** For every $g$, $\Pr_E[\,|G_{\mathrm{FM}}| \ge g\,] \le 2^{\,S + B + \log_2(1+2/T) - g(\log_2(N - g) - \log_2 T - \log_2 B)}$; hence w.p. $1 - 2^{-\lambda'}$,
$$|G_{\mathrm{FM}}| \le \frac{S + B + \lambda' + O(1)}{w - \log_2 T - \log_2 B}.$$
(The crude $B$ and $\log_2 B$ replace tdp.md's $\log_2\binom{B}{g}$ and $\log_2 g$ because the executed runs include self-excluding blocks, whose number the adversary controls; tdp.md's `params.py` already charges $B$.)

**Proof.** Stop the classification once $|G_{\mathrm{FM}}| = g$; let $G'$ be the set of blocks whose runs were executed. Encoder writes: $\sigma$; $G'$ as a subset of $[B]$ ($\le B$ bits); the hit list (positions among the $\le |G'|T$ queries of the executed runs, identities among unmatched blocks, exactly as tdp.md 113 and its counting at 118); the pool: all values of $E$ except the $g$ entries $E(v_j) = r_j$, $j \in G_{\mathrm{FM}}$, as a mixed-radix bijection in the order the decoder needs them. Decoder holds $N, p, q$, hence every $r_j$, and reproduces the classification step by step: forward hit → read identity $j$, set $v_j := x$, $E(x) := r_j$, $c_j := \mathrm{RWInv}(x)$; inverse query at an unmatched $r_j$ → $j$ joins $X$, so $v_j$ is a pool entry, read it; every other query → pool; run end → $c_i$ is the output, $v_i = a_2 c_i^2$, $E(v_i) := r_i$. Every query is answered with the true value, so the simulation equals the real run, and after the runs the decoder knows $E$ on the omitted points and reads the rest of the pool in canonical order. Injective; counting as tdp.md 118 with $gT$ replaced by $|G'|T \le BT$ and the pool of size $(N - g)!$. ∎

Remarks. (i) The $k$-block plug-ins of tdp.md 1.4 (sequential proved, simultaneous sketched) transfer verbatim, since they only re-run this decoder. (ii) The statement is for the whole encoding, so no composition lemma (template_bound.md 234) is needed. (iii) It is consistent with Proposition 1: the trapdoor adversary has $G_{\mathrm{FM}} = \emptyset$. (iv) It is the correct formalisation of the brief's "charge such blocks as uncompressed": $X$ is charged nothing and loses nothing.

### 3.3 The two-root game and the conjecture

**Game 2RG$(N; B, S, T)$.** Uniform $u_j, u'_j \in \mathbb{Z}_N^*$ with canonical roots $r_j, c_j$ (and class bits). $A_1$ gets $(N, u, r, u', c)$, outputs $S$ bits. $A_2(\sigma, i)$ gets $(u_j)_j$ and two oracles, $\le T$ calls: $\mathrm{Open}(z) = (j, u'_j)$ if $z = r_j$, else $\bot$; $\mathrm{Test}(x) = (j, r_j)$ if $x = u'_j$, else $\bot$. It wins on $i$ if it outputs $c_i$.

**Lemma (equivalence, proved).** In IPM+ROM, design (a) is $(S, T, g)$-secure iff 2RG$(N; B, S + \lambda, T)$ is: program $t_j := u_j - m_j$ and $E(u'_j) := r_j$; Open and Test are $E^{-1}$ and $E$ on the programmed points and everything else is lazily sampled by whoever needs it. Both simulations are perfect. ∎

So the ideal permutation contributes precisely one thing: *$v_j$ is an independent uniform element that is revealed only against the exact $r_j$* (`toy_two_round.py` [2]). All remaining hardness is number-theoretic. Theorem A holds in 2RG verbatim (blocks won without Open on their own $r_j$).

**Conjecture 2RG-C($\ell$).** For $A_1$ of time $\le 2^{100}$: w.p. $1 - 2^{-\lambda'}$, $S + \lambda \ge |G_{\mathrm{FM}}|(w - \log_2 T - \log_2 g) + |G_{\mathrm{I}}| \cdot 2(w - \ell(T))$, where $\ell(T)$ is the single-root compressibility: the least number of bits of a canonical root that, with its square and $T$ work, reproduce it. Known: $\ell(T) \ge w/2 + \log_2 T_{\mathrm C}$ (Coppersmith plus guess-and-run, `toy_two_round.py` [3], $T_{\mathrm C}$ = LLL runs in the budget); the Coppersmith-optimality reading is $\ell(T) = w/2 + \log_2 T_{\mathrm C} + O(1)$; whether the $2\log_2 T$ shift-and-kangaroo saving (tdp.md 4.2.7) stacks on top is unsettled (tdp_review.md 145).

Two honest remarks. First, the conjecture bundles Theorem A's provable half with two unproved parts: Coppersmith optimality against arbitrary *joint* leakage (multi-instance leakage-resilience of Rabin, the two-stage form that MW20 8.1 says no black-box factoring reduction can deliver), and the "sum, not max" combination of the IT and computational charges on a shared state, which I could not prove from the all-squares-given version (that version gives only $S \ge \max(\ldots)$, useless at rate $1/2$). Second, by Lemma 3 (template_bound.md 193) any assumption implying the audit is at least as strong as the audit; 2RG-C is nevertheless the *right* object to hand over, because it mentions no permutation, no encoding and no audit: it is "Rabin roots are Coppersmith-compressible and no more, jointly, with squares opened on demand".

**Conditional theorem (design (a), sketched).** Under 2RG-C, $g \le (S + \lambda + \lambda')/(w - L)$ with $L = \max(\log_2 T + \log_2 g,\; 2(\ell(T) - w/2))$. For design (b) the analogue 3RG-C with $\ell \le 2w/3 - \log_2 T$ gives $L = \log_2 T + \log_2 g$: the three-root strategy costs $\ge w$ and drops out.

Numbers (`params.py`; $S = 0.95|C|$, $B = 2^{28}$, $\lambda' = 64$, $T_{\mathrm C} = T/2^{10}$):

~~~
 w     T     variant                         L    p*      k(1%)  k(1e-6)
2048  2^20   Thm A / (a) no stacking / (b)   48   0.9729   168     503
2048  2^20   (a) if kangaroo stacks         100   0.9988  3757   11271
2048  2^30   Thm A / (a) no stacking / (b)   58   0.9778   205     615
2048  2^30   (a) if kangaroo stacks         160   vacuous
3072  2^20   Thm A / (a) no stacking / (b)   48   0.9652   130     390
3072  2^20   (a) if kangaroo stacks         100   0.9820   254     761
3072  2^30   Thm A / (a) no stacking / (b)   58   0.9683   144     430
3072  2^30   (a) if kangaroo stacks         160   vacuous
~~~

$p^* = g^*/B$ is the maximal answerable fraction; $k$ is the sequential-reveal audit size for pass probability $\beta$. If kangaroo stacks with Coppersmith the bound is vacuous at $w = 2048$, $T = 2^{30}$ and nearly so at $T = 2^{20}$; at $w = 3072$ it survives at $T = 2^{20}$ either way.

### 3.4 Decode cost (int32 per weight byte, anchors from the brief)

Squaring: 50 at 2048, 68 at 3072. $E$ as a Feistel over $w/2$-bit halves with SHAKE round functions: 1 Keccak-f per round at 2048 (halves fit one rate block), 3 at 3072; 8 rounds for indifferentiability from a random permutation (Dai–Steinberger 2016), 2 rounds as a heuristic.

~~~
 w    design  squarings  E (2-round heur.)  E (8-round indiff.)  total heur. / indiff.
2048   (a)      100          27                  106               127 / 206
2048   (b)      150          53                  212               203 / 362
3072   (a)      137          53                  212               190 / 349
3072   (b)      205         106                  425               311 / 630
~~~

Only (a) at $w = 2048$ with a heuristic 2-round Keccak Feistel meets the 150 prefill budget; the theorem is stated for ideal $E$, and the gap between a 2-round Feistel and an ideal permutation is exactly the kind of bespoke analysis the brief wanted to avoid (with 8 rounds the gap is a published indifferentiability bound, at 206). Nothing is within 20× of the decode-batch budget of 8: one squaring is 50.

## 4. Attack frontier for design (a), $s/w \in [0.90, 0.97]$

Per-block storage totals; a strategy saves bits only if its total is below $w$.

| strategy | storage | online work | verdict at $2048$, $T = 2^{30}$ |
|---|---|---|---|
| truncation: store $w - t$ bits of $c$, enumerate, verify by decode | $w - \log_2 T$ | $T$ evaluations | $0.985w$: outside the window; this is $L_{\mathrm{FM}}$ |
| two-round Coppersmith: top halves of $r$ and $c$ | $w$ (+4) | 2 LLL, 1 query | saves 0 (`toy_two_round.py` [1]) |
| guess-and-Coppersmith on both roots | $w - 2\log_2 T_{\mathrm C}$ | $2T_{\mathrm C}$ LLL | $\approx 0.98w$: outside; this is the $2(\ell - w/2)$ term |
| kangaroo on both roots (tdp.md 4.2.7) | $2(w - 2\log_2 T)$ | 2 kangaroos | $\approx 1.94w$: dominated by storing $c$ |
| kangaroo stacked on Coppersmith (unsettled) | $w - 4\log_2 T - 2\log_2 T_{\mathrm C}$ | $2^{88}$ offline | $\approx 0.92w$: **inside the window if stacking exists** |
| partial $r$ + $E^{-1}$ | fails | — | $E$ needs the exact $r$ (`toy_two_round.py` [2]) |
| MITM across $E$: $2^{t_1}$ candidate $r$'s vs $2^{t_2}$ candidate $v$'s | $w - t_1 - t_2$ only if candidates come from Coppersmith-with-guess | same as guess-and-Coppersmith | no gain over the row above |
| joint storage $r \oplus c$, $r + c$, etc. | $w$ | must solve for $r$ without $v$ | no algebraic relation through $E$; saves 0 |
| lattice on $(r, c)$ jointly | — | — | the only relation is $E$; no polynomial system |
| store trapdoor | $2w$ total | factoring first | outside the computational model |
| dedup / related targets / small $m$ | 0 | — | removed by $t_j$ |

None of the settled strategies enters $[0.90, 0.97]$; the one open question is whether shift-and-kangaroo stacks with Coppersmith for a *single* Rabin round, which would move the frontier to $\approx 0.92w$ at $w = 2048$ and $T = 2^{30}$ (and to $0.95w$ at $T = 2^{20}$). At $w = 3072$ the window $[0.90, 0.97]$ contains no settled attack and the stacked one lands at $0.95$.

## 5. Verdict

- **Probability that a provable design of this kind exists** (standard symmetric idealisation plus factoring, $O(1)$ trapdoor rounds, B1-quality loss, decode $\le 150$ int32/B): **0.05.** The information-theoretic route is closed by Proposition 1 (proved). The reduction route needs an extraction point, and §1.3 argues there is none once $A_1$ can verify every intermediate; the only technique on record costs $r = nb\lambda$. A new technique would also improve GLW20 by a factor of $b$, which is why I do not put it at 0.
- **Residual assumptions for the deployable candidate** (design (a), $w = 2048$, 2-round Keccak Feistel): factoring (regeneration, proved); 2RG-C (Conjecture, with its two unproved parts named in §3.3); "the 2-round Feistel behaves as an ideal permutation for this game" (heuristic; 8 rounds and 206 int32/B removes it); no kangaroo–Coppersmith stacking (else $w = 3072$ at $T = 2^{20}$, 190 int32/B).
- **Hand to a cryptanalyst.** (1) Single-round Rabin compressibility $\ell(T)$: beat $w/2 + \log_2 T_{\mathrm C}$ from a square and arbitrary efficiently-computed leakage; in particular, does the shift-and-kangaroo saving stack on Coppersmith? (2) Joint leakage: with $S$ bits about $2B$ independent roots, is anything below $2(w - \ell)$ per pair possible? (3) 2RG-C's "sum not max" for a shared state. (4) The 2-round Keccak Feistel as a public permutation in 2RG. (5) Write out the MW20 8.1 meta-reduction for IPM+ROM to settle §1.3 as a theorem.

## Summary (10 lines)

1. B1's compression proof needs every omitted table entry to be approached only from its known side; in $\rho_1 \to E \to \rho_2$ the query $E^{-1}(r_j)$ approaches it from the other side, and $r_j$ costs the adversary only $w/2$ bits (Coppersmith) or the trapdoor.
2. Root cause: compression arguments count information, a Rabin root has 2 bits given its square, and the trapdoor is $2w$ bits — so an unbounded $A_1$ stores $(p,q)$ and every block is free (Proposition 1, proved). No information-theoretic theorem exists for any short-secret encoder.
3. A computational theorem needs a factoring reduction; the reduction knows every codeword ($A_1$ can verify every intermediate) and the only extraction lever, oracle switching, fails against any adversary that uses the inverse direction; the only known fix is GLW20's $r = nb\lambda$.
4. Presampling / bit-fixing tools do not apply: our advice is about the instance, not the oracle, and folding the trapdoor into the oracle lets the bit-fixing adversary fix it.
5. Designs (b)–(f) all fail for the same reason; RO-Feistel layers only shrink the omitted entry to $w/2$ bits; fresh randomness is capped at 5%; no symmetric idealisation supplies a large trapdoor.
6. Proved: Theorem A — blocks recovered without an inverse hit at their own intermediate cost $w - \log_2 T - \log_2 B$ bits (B1's loss, crude $\log_2 B$), for unbounded $A_1$, whole encoding, $k$ plug-in inherited.
7. Proved: in IPM+ROM design (a) is exactly the two-root Rabin game 2RG: the ideal permutation contributes only "$v_j$ is uniform and opened against the exact $r_j$".
8. Conjecture 2RG-C (Coppersmith-optimal, jointly, squares on demand) gives loss $\max(\log_2 T + \log_2 g, 2(\ell - w/2)) \approx 58$ bits: $p^* = 0.978$ at $w = 2048$, $0.968$ at $3072$, $T = 2^{30}$; design (b) needs only "a root keeps $w/3$ of its bits" but costs $\ge 200$ int32/B.
9. Decode: (a) at 2048 is 127 int32/B with a heuristic 2-round Keccak Feistel, 206 with an indifferentiable 8-round one; nothing approaches the decode-batch budget of 8.
10. Attack frontier at $s/w \in [0.90, 0.97]$: no settled attack; the single open item is whether shift-and-kangaroo stacks with Coppersmith on one Rabin round (it would reach $0.92w$ at 2048, $T = 2^{30}$). P(provable design of this kind at $\le 150$ int32/B) $= 0.05$.
