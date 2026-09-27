# Square–Mix–Square: a public, timed proof of encoded-weight retention

Status: specification for review (2026-09-21). Scope: static model weights, one GPU, GPU-class adversary. KV cache, activations, multi-GPU domains and the trusted-timer deployment are out of scope. Performance figures are estimates from measured anchors and are marked (est.).

## 1. Notation and primitives

- $p = 2^{1279} - 1$ (Mersenne prime, $p \equiv 3 \pmod 4$), $w = 1279$, $\mathbb{F}_p$ identified with $\{0,1\}^w \setminus \{1^w\}$. A *block* is one field element stored in 160 bytes (one spare bit, fixed to 0). Payload per block: $b = 1264$ bits (79 bf16 weights), rate $158/160$.
- A *unit* is $U = 400$ consecutive blocks (64,000 B). $N_U$ units, $N = U N_U$ blocks. For a 70 GB model, $N \approx 4.4 \cdot 10^8$, $N_U \approx 1.1 \cdot 10^6$.
- $H$: a hash modelled as a random oracle (BLAKE3 or SHA-256). $\mathrm{salt} \in \{0,1\}^{256}$.
- **Square-root permutation** $\rho : \mathbb{F}_p \to \mathbb{F}_p$. For $y \ne 0$ exactly one of $\pm y$ is a quadratic residue. Let $r = y^{2^{1277}}$; then $r^2 = y$ (if $y \in \mathrm{QR}$) or $r^2 = -y$. Define $\rho(y) = r$ if ($y \in \mathrm{QR}$ and $r$ even) or ($y \notin \mathrm{QR}$ and $r$ odd), else $\rho(y) = p - r$; $\rho(0) = 0$. Then
  $$\rho^{-1}(c) = \begin{cases} c^2 & c \text{ even} \\ -c^2 & c \text{ odd,} \end{cases}$$
  one squaring. Computing $\rho$ costs $D = 1278$ dependent squarings (Lenstra–Wesolowski).
- **Mixing bijection** $\sigma_j : \mathbb{F}_p \to \mathbb{F}_p$: $\sigma_j(r) = r \oplus K_j$ with $K_j = H(\mathrm{salt}, j, \texttt{mix})|_w$, dense ($\approx w/2$ set bits w.h.p.), and the single exceptional element $\bar K_j$ (whose image would be $1^w$) fixed. Cost: one XOR. $\sigma_j$ is an involution.
- **Tweak** $t_j = H(\mathrm{salt}, j, \texttt{tweak}) \bmod p$.
- **Block encoding and decoding**, for block index $j$ and payload $m \in [0, 2^b)$:
  $$E_j(m) = \rho\bigl(\sigma_j(\rho(m + t_j))\bigr), \qquad D_j(c) = \rho^{-1}\bigl(\sigma_j^{-1}(\rho^{-1}(c))\bigr) - t_j \pmod p .$$
  $E_j$ is a bijection of $\mathbb{F}_p$; $D_j = E_j^{-1}$ costs two squarings, one XOR, one subtraction. The encoding of $W = (m_j)_j$ is $C = (E_j(m_j))_j$, $|C| = |W| \cdot 160/158$.

## 2. Protocol

**Setup.** (1) Prover $\mathcal{P}$ commits $\mathrm{com} = H(W)$ to verifier $\mathcal{V}$. (2) $\mathcal{V}$ samples $\mathrm{salt}$ uniformly *after* receiving $\mathrm{com}$ and sends it. (3) $\mathcal{P}$ (or anyone) computes $C$; $\mathcal{V}$ obtains $C$ (recomputes it from $W$, or receives it and spot-checks $D_j(C_j) = m_j$ on random $j$) and stores it, together with the honest timing baseline measured on $\mathcal{P}$'s hardware. Encode cost: $2D$ squarings per block, parallel over blocks; $\approx 2.8\cdot10^{15}$ int32 ops for 70 GB, $\approx 3$–5 min on one H100 (est.).

**Serving.** $\mathcal{P}$ holds only $C$ in HBM and applies $D_j$ on read (fused into the GEMM). Decode cost: two 1279-bit squarings per 160 B $\approx$ 20–30 int32 per weight byte (est., scaled from measured Montgomery costs). Against the measured H100 budget (8 int32/B $\Leftrightarrow 2\times$ at batch $\le 8$; 144 int32/B $\Leftrightarrow 2\times$ at 8K-token prefill) this is $\approx 4$–$5\times$ at inference decode and $\approx 1.15\times$ at prefill (est.).

**Audit** (repeated every few seconds). $\mathcal{V}$ sends nonce $\nu$ and starts a clock.

- *Chain.* $u_1 = H(\nu, 0) \bmod N_U$. For $k = 1, \dots, x$: $\mathcal{P}$ reads unit $C_{u_k}$ from HBM, computes $z_k = H(\nu, k, C_{u_k})$ and $u_{k+1} = H(\nu, z_k) \bmod N_U$. Returns $(z_1, \dots, z_x)$. $\mathcal{V}$ records $T_{\mathrm{chain}}$ and later verifies every $z_k$ against its copy of $C$.
- *Bulk read.* $\mathcal{V}$ sends seed $\eta$; $\mathcal{P}$ returns $\mu = \sum_{i \in S_\eta} \nu_i \cdot C_i$ over $\mathbb{F}_{2^{61}-1}$, where $S_\eta$ is a pseudorandom set of sectors totalling $X$ bytes and $\nu_i = H(\eta, i)$; a keyed linear map computable at HBM speed. $\mathcal{V}$ records $T_{\mathrm{bulk}}$ and verifies $\mu$ offline.
- *Decision.* An audit *exceeds* if $T_{\mathrm{chain}} > \theta_{\mathrm{chain}}$ or $T_{\mathrm{bulk}} > \theta_{\mathrm{bulk}}$ or any response is wrong. $\mathcal{V}$ rejects $\mathcal{P}$ if at least $k$ of the last $n$ audits exceed. Thresholds are the empirical $(1-\alpha)$-quantiles of the honest baseline.

Parameters: $x = 1000$, $X = 4$ GB, $\alpha = 10^{-3}$, $(n, k) = (5, 3)$. Honest cost per audit: chain $\approx 1000 \times 6.65\,\mu$s $= 6.65$ ms (their measured link time), bulk $\approx 1.3$ ms at 3 TB/s; $< 0.5\%$ of GPU time at one audit per 2 s.

## 3. Adversary model

$\mathcal{A}$ replaces $\mathcal{P}$ after setup. It knows $W$, $\mathrm{salt}$, $C$ and all of $\mathcal{P}$'s keys, and may preprocess them arbitrarily. It has:

- **Fast memory** $M_f$ (HBM) of size $|M_f|$, and **slow memory** $M_s$ of unbounded size with per-fetch latency $\ge \lambda_s$ and bandwidth $\le B_s$.
- **Compute:** unbounded parallelism; a dependent multiplication in $\mathbb{F}_p$ costs latency $\ge \delta_1$; total throughput $\le R$ field squarings per second.

Assumptions.

- **A0 (salt after commitment).** $\mathrm{salt}$ is uniform and independent of $W$. (Otherwise $\mathcal{A}$ chooses $W = D(0)$ and $C$ is trivial; this holds for every rate-1 bijective public encoding.)
- **A1 (sequentiality).** For uniform $y$, any algorithm computing $y^{2^{D}} \bmod p$ with latency $< D\,\delta_1$ succeeds with negligible probability, for any preprocessing depending on $p$ only. (Theorem in the addition-chain model; the Sloth/VDF conjecture beyond it.)
- **A2 (hardware floors, GPU-class).** $\delta_1 \ge 0.15\,\mu$s for a 1279-bit squaring; $R \le 10^{10}$ per GPU, $G$ GPUs; $\lambda_s \ge 5\,\mu$s (PCIe), $B_s \le 64$ GB/s; honest per-link time $t_\ell \approx 6.65\,\mu$s.
- **A3 (partial-preimage hardness of $E_j$).** For uniform $\mathrm{salt}$ and any $j$: every algorithm with $s$ bits of advice (an arbitrary function of $y, c, \mathrm{salt}$), latency $\le t_\ell$ and $T$ evaluations of $\rho^{-1}$ outputs $c = E_j(m)$ from $y = m + t_j$ with probability $\le T \cdot 2^{s - w} + \mathrm{negl}$. (Equivalently: for this task $E_j$ is no weaker than a random permutation with a free forward oracle.)
- **A4 (trusted timer).** $\mathcal{V}$ is on the same LAN, its clock cannot be influenced by $\mathcal{A}$, and the honest response times have a distribution whose $(1-\alpha)$-quantiles are estimated at setup; exceedances of the honest prover in distinct audits are independent.

## 4. Security definition

**Definition 1 (retention).** The scheme is $(\varepsilon, \beta)$-*retaining* under a window rule $(n, k)$ if for every $\mathcal{A}$ in the model with $|M_f| < (1 - \varepsilon)|C|$,
$$\Pr[\mathcal{A} \text{ passes a window}] \;\le\; \beta ,$$
and (completeness) the honest prover fails a window with probability at most $\binom{n}{k}\alpha^k$.

The goal is $\varepsilon \le 5\%$, $\beta \le 10^{-6}$, completeness error $\le 10^{-7}$.

## 5. Claims

**Theorem 1 (completion bound, ideal model).** Replace each $E_j$ by an independent random permutation $\Pi_j$ with a free forward oracle $\Pi_j^{-1}$ (decode) and an inverse oracle (encode) costing $2D$ dependent steps. Let $\mathcal{A}$ hold $s$ bits of state, make $T$ forward queries during one audit, and make no inverse query that completes within a link. If $\mathcal{A}$ answers $g$ challenged blocks correctly with probability $\ge 1/2$, then
$$s \;\ge\; g\,\bigl(w - \log_2 T - \log_2 g - O(1)\bigr).$$
*Proof sketch.* Standard compression argument (as in our Theorem B1 with R3's loss term): from $\mathcal{A}$'s state, the transcript of its forward queries and a hit list of $g$ pointers ($\log_2 T$ bits each) plus an ordering ($\log_2 g$ each), the encoder reconstructs $g$ oracle values of $w$ bits, so a random oracle table cannot be compressed below the stated bound except with small probability. $\square$

*Consequence.* With $T \le R G x t_\ell \approx 2^{26}$ ($G = 1$) and $g = xU \approx 2^{19}$: $\mathcal{A}$ holds at least $w - 45$ bits per challenged block, i.e. **completion loss $\varepsilon_{\mathrm{comp}} \le 45/1279 = 3.5\%$** (bound). The matching attack (store $w - t$ bits, brute-force $2^t$ completions with the per-block budget $T/g \approx 2^7$–$2^{10}$ for $G = 1$–8) realises $\varepsilon_{\mathrm{comp}} \approx 0.55$–$0.8\%$. A3 transfers this to the real $E_j$.

**Proposition 2 (regeneration is visible).** A challenged unit not recoverable from $M_f$ by forward queries alone requires, per A1–A2, either an inverse evaluation ($\ge 2D\delta_1 \ge 0.38$ ms $\approx 8\sigma$ at $\sigma = 50\,\mu$s) or a fetch from $M_s$ ($\ge \lambda_s = 5\,\mu$s). If a fraction $f$ of units is absent from $M_f$ and regenerated, the audit exceeds whenever the chain hits one, so the per-audit exceedance probability is
$$q(f) = 1 - (1 - f)^x ,$$
and the window pass probability is $\Pr[\mathrm{Bin}(n, q) < k]$. At $x = 1000$: $q(0.5\%) = 0.993$, $q(1\%) = 0.99996$; with $(5, 3)$ the pass probability is $\approx 10^{-6}$ at $f = 0.5\%$. Hence **$\varepsilon_{\mathrm{reg}} \le 0.5\%$** at $\beta = 10^{-6}$.

**Proposition 3 (tiering).** A fraction $f_t$ of units held in $M_s$ adds $\ge f_t X / B_s$ to $T_{\mathrm{bulk}}$; with $X = 4$ GB, slack $0.5$ ms and $B_s = 64$ GB/s this exceeds for $f_t \ge 0.8\%$. Accounting for measured honest jitter of the bulk read under load (phase-2 challenger), **$\varepsilon_{\mathrm{tier}} \le 2.5\%$**. (The chain alone gives only a linear signal $f_t x \lambda_s$ and is not relied on here.)

**Corollary 4.** Under A0–A4, the scheme is $(\varepsilon, 10^{-6})$-retaining with
$$\varepsilon \;\le\; \varepsilon_{\mathrm{comp}} + \varepsilon_{\mathrm{reg}} + \varepsilon_{\mathrm{tier}} \;\le\; 3.5\% + 0.5\% + 2.5\% = 6.5\% \ \text{(bound)},\qquad \approx 3.6\% \ \text{(best known attacks)},$$
with completeness error $\binom{5}{3}(10^{-3})^3 = 10^{-8}$.

**Lemma 5 (algebraic attacks on the round structure; why two rounds and a dense $\sigma$).** Let $c$ be the codeword, $y$ the known round input.
(i) *One round* ($c^2 = \pm y$): writing $c = a 2^k + x$ with $a$ stored, $x$ is a root of the known quadratic $f(x) = x^2 + 2a2^k x + (a^2 2^{2k} - y) \bmod p$; Håstad–Coppersmith recovers $x$ from a 3-dimensional lattice for $2^k < p^{1/3}$ (and up to $p^{1/2}$ with larger lattices). A3 is false: $s = 2w/3$ suffices with $T = 0$ and latency of a few hundred integer operations. Verified at $w = 61$: $k = 20$ bits recovered in 200/200 trials (`coppersmith61.py`).
(ii) *Two rounds with an affine $\sigma$* (Lenstra–Wesolowski's low-bit flip, $\sigma(r) = r \pm 1$): substituting $r = \pm c^2 \mp \delta$ into $r^2 = \pm y$ gives a degree-4 univariate in $c$; Coppersmith recovers $w/4$ bits. A3 is false.
(iii) *Two rounds with dense XOR:* $\sigma_j(r) = r + K_j - 2(r \wedge K_j)$, so every polynomial relation between $c$ and $y$ over $\mathbb{F}_p$ must resolve the $\approx w/2$ unknown bits of $r \wedge K_j$ (by guessing, $2^{w/2}$ work, or by storing them, $w/2$ bits of advice). No polynomial relation of degree $< 2^{\Omega(w)}$ is available over $\mathbb{F}_p$, and $\rho^{-1}$ has no low-degree representation over $\mathbb{F}_2$.
(iv) *Half-bits accounting.* Any attack that exploits a degree-2 round relation needs that round's input and recovers at most half of that round's output. Round 2's input $\sigma_j(r)$ requires $r$ (slow by A1, or $w/2$ stored bits by (i)); round 1's output is not the codeword. Storing half of $r$ and half of $c$ costs $w$ bits, i.e. nothing is saved. Two rounds is the smallest count at which this accounting closes; $k$ rounds cost $k w/2 \ge w$ for $k \ge 2$.
Multiplicative structure ($\rho(ab) = \pm\rho(a)\rho(b)$, which enables shift-and-kangaroo compression of single-round codewords) is destroyed by $\sigma_j$. Cross-block relations are excluded by A0. $\square$ (heuristic for (iii)–(iv))

**Proposition 6 (the 61-bit single-round design).** Basic-VDE-PoRep over $p = 2^{61}-1$ with one square root per 8-byte word, keyed tweaks, and a hash chain of any length $x$: an adversary knowing $W$ stores 41 of every 64 bits (20 recovered per Lemma 5(i), 3 are padding) and answers every link at honest speed. Retention is at most $64\%$ regardless of $x$, $\sigma$, threshold or hardware. Hash chaining amplifies *per-link latency* ($f x \delta$ against $\sigma(x) = \sqrt{\sigma_0^2 + x\sigma_1^2}$) and is effective against regeneration and tiering; it cannot amplify work completed within the honest link time.

## 6. What a reviewer should attack

1. A3 with dense XOR: Coppersmith/Gröbner on $\{r^2 = \pm y,\ c^2 = \pm(r \oplus K)\}$ with partial guesses of $r \wedge K$; bivariate small-root attacks on the unknown low parts of $r$ and $c$ jointly; use of the public $K_j$. A break costing less than $w/2$ advice bits and $< t_\ell$ latency falsifies A3; the fix would be a third round ($+\approx 1\times$ decode ratio, est.) or a stronger $\sigma$ (ARX, $\approx 1$ op/byte).
2. A1 at $w = 1279$: prime-field DLP at this size is $\approx 90$-bit security against index calculus; a DLP oracle makes $\rho$ shallow, but known precomputation-plus-descent methods leave per-instance cost at hours, not $t_\ell$. Confirm no parallel square-root algorithm and whether $2^{2203}-1$ ($\approx 1.7\times$ cost, est.) should be preferred for a multi-year hostage.
3. Theorem 1's $\log_2 g$ term: proof slack or real (the attack realises only $\log_2(T/g)$). Tightening it moves the bound from $3.5\%$ toward $0.6\%$.
4. The timing model: independence of honest exceedances across audits (A4), and the claim that $2D\delta_1 \ge 0.38$ ms is a floor for a cooperative-warp implementation on H100/B200.
5. The exceptional element of $\sigma_j$ and the parity rule: confirm $E_j$ is a bijection and that the one-bit residuosity information is worth exactly one bit.

## 7. Parameter summary and estimates

$p = 2^{1279}-1$; block 160 B, unit 64,000 B; rounds 2; $\sigma_j$ dense XOR (per-block constant); $x = 1000$; $X = 4$ GB; $\alpha = 10^{-3}$; window $(5, 3)$. Guarantee: $\varepsilon \le 6.5\%$ (bound) / $\approx 3.6\%$ (attacks), $\beta = 10^{-6}$, completeness $10^{-8}$. Costs (est.): decode $4$–$5\times$ at inference decode, $1.15\times$ at prefill; encode 3–5 min per 70 GB on one H100; regeneration of one unit $0.38$–$2.6$ ms; audit $< 0.5\%$ of GPU time; verifier holds $C$ (70.7 GB) and verifies offline. Anchors: H100 fused-GEMM budget (8 int32/B $\Leftrightarrow 2\times$), CGBN Montgomery multiplication 68 int32/B at 2048 bits, phase-2 challenger 3.1 TB/s bulk read with 0.11–0.34 ms p99.9 excess under load, their measured $6.65\,\mu$s link and $50\,\mu$s chain jitter.
