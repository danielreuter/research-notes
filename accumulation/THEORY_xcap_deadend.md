# Training security from bounded accumulation: theory

Status of every claim is tagged **[proved]**, **[measured]** (computed on the Verity IR circuits in this
package), or **[assumed]**. Numbers are pulled from `results/RESULTS.md`; where a number is still pending it
is marked `TBD`. Code references: `SPEC.md` is the normative contract, `bounds/lower.py` the certificate,
`bounds/upper.py` the construction, `exact/` the reference solver, `redteam/` the adversarial tests.

## 0. Objects and notation

* **Circuit** `C`: a finite DAG of gates. Every gate `g` has prescribed work `w(g) >= 0` (MAC-equivalents;
  `Mac16 = 1`) and an output value of width `l(g)` bits. Exogenous inputs carry a *role*:
  `fixed` (registered ahead of time, free everywhere), `token` (data), `seed`, `accumulated` (state that the
  step reads and rewrites), `carried` (state read by the step and produced by an earlier step of the same
  circuit). Non-`fixed` inputs are *runtime inputs*.
* `Up(S)`: the backward closure of a set of gates `S` (including `S`). `Work(S) = sum w`, `Width(S) = sum l`.
* **Replay unit (RU)**: a part `R` of a partition `Pi` of the non-input gates. `In(R)` = distinct
  non-fixed values entering `R` (runtime-input leaves read in `R`, plus values produced outside `R` and read
  inside). `Up_R(g)` = backward closure of `g` following only wires that stay inside `R`. `Pi` is
  **legal** for `(F, G, X)` iff for every `R`: `Width(In(R)) <= X` (runtime input), `Work(R) <= G` (total
  work; `G = None` = unbounded, the `(F, X)` policy of earlier sections), and `Work(Up_R(g)) <= F` for every
  gate `g` in `R` (serial upstream work).
* **Resource**: `I*(C; F, G, X) = min over legal Pi of sum_R Width(In(R))` (bytes). This is *the* primary
  object of the whole program (§0.1); every other quantity is a bound on it or a ratio of such bounds.
* **Target multiplications** `ℳ`: for a designated product `W A` (`W` an `N x K` array of accumulated or
  carried values, `A` a `Q x K` array of activation values) the set of scalar products `W_ik A_jk`.
  `ℳ(C)` = the number of distinct target products `C` performs (recomputation earns nothing). In this package
  the target is the union over all matmuls whose closure contains accumulated/carried state:
  `ADW_matmul` (SPEC §1) counts every such MAC in the declared circuit; `credited_macs` (`bounds/adw.py`)
  excludes the ops annotated `recompute` (the activation-checkpoint re-evaluations in every `*Bwd` block)
  and is the `|ℳ(C)|` used in efficiencies. At 8B pretraining: `ADW_matmul = 3.2e10`, `|ℳ| = 2.6e10`
  MAC/token, `Work(C)/|ℳ| = 1.24` (the honest circuit's own `eta` is 0.81). `ADW` adds the non-matmul work
  with the same property.
  The bound charges the declared circuit, which *completes* every product (partial sums crossing an RU are
  charged `gamma`); this is the "completed `WA`" resource, which is what a training step requires.
* **Efficiency** of an executor with total work `W_tot` and runtime-input allowance `B`:
  `eta = ℳ(C) / W_tot`. The security statement is an upper bound `eta_max` (§4).

### 0.1 The direct formulation: exposure of the multiplication gates **[proved]**

Everything in §§2-4 (reconstruction width, closure budgets, Loomis-Whitney) is machinery for *bounding* one
exact combinatorial quantity. Stated directly, for a fixed circuit `C` and policy `(F, G, X)`:

* **Exposure** of an RU: `i(R) = Width(In(R))`; of a partition: `I(Pi) = sum_R i(R)`. The adversary's
  optimum is `I*(C) = min_{Pi legal} I(Pi)`, and its best possible runtime-input efficiency on this circuit is
  `kappa*(C) = |ℳ(C)| / I*(C)` MAC/byte. No tiling assumption, no operand-sharing assumption, no tier-1/tier-2
  distinction enters: all of it is inside the minimisation.
* **Exposure certificate (dual).** Assign a price `p_g >= 0` to every gate such that
  `sum_{g in R} p_g <= i(R)` for **every legal RU** `R`. Then for every legal partition
  `sum_g p_g = sum_R sum_{g in R} p_g <= sum_R i(R) = I(Pi)`, hence `L := sum_g p_g <= I*(C)`.
  *This is the whole lower-bound theorem.* It is exactly the LP dual of the set-partitioning formulation of
  `I*` (variables `z_R` per legal RU, `min sum_R i(R) z_R` s.t. every gate covered once), and the
  "`sum claims <= I(R)` for every RU" condition of §3 is this certificate with the closure-budget prices.
  Simplest instance: `p_g = lambda` on target multiplication gates, `0` elsewhere, valid iff
  `lambda <= min_{R legal, m(R) > 0} i(R) / m(R)` where `m(R) = |ℳ ∩ R|`; then `kappa*(C) <= 1/lambda`. The
  question "how exposed are the multiplication gates to the runtime-input frontier in the best legal RU" is
  literally the bound. The full certificate also prices reductions, activation- and weight-generation gates,
  which lets communication paid in target-free RUs (partial sums, regenerated operands) count.
* **Two-sided exposure.** Outgoing values `o(R) = Width(Out(R))` (produced in `R`, consumed outside; final
  outputs excluded) satisfy `sum_R o(R) <= I(Pi)` (each is imported by at least one consumer). So for any
  `t in [0, 1]`, `E_t(R) = t i(R) + (1 - t) o(R)` also satisfies `sum_R E_t(R) <= I(Pi)`, and a certificate
  may charge partial sums on the producing side. `gamma` in §3.1 is this device.
* **Role of `G`.** Without `G`, the legal set contains RUs that take a modest frontier and fan it out over
  arbitrarily much parallel multiplication (bounded only by `X` through Loomis-Whitney: `m(R) <=
  ((X/3)^3 / (alpha beta gamma))^{1/2}`, about `5e8` MAC at `X = 5 MB`). `Work(R) <= G` removes them from
  the feasible set, so for a matmul tile with operand costs `alpha, beta` and partial-sum cost `gamma`
  the exposure per MAC obeys `(alpha a b + beta b c + gamma a c)/(a b c) >= 3 (alpha beta gamma / G)^{1/3}`
  (AM-GM at `a b c = G`) in addition to the `X`-limited form of §3.1; the certificate uses the larger. `G`
  also caps honest inference (attention query blocks sharing one K/V import, rows sharing one weight block),
  so it is a *policy frontier*, not a free knob: `rho(G)` is measured, not argued.
* **Sandwich and the security ratios.** A checked legal partition gives `U >= I*`; a certificate gives
  `L <= I*`; so `|ℳ|/U <= kappa* <= |ℳ|/L`. Against a *checked* honest inference implementation with
  `kappa_inf = M_inf / U_inf` (total matmul MACs over a legal partition's input, same `(F, G, X)`, same model):
  `rho_cert = (M_train / L_train) / (M_inf / U_inf)` (certified: the adversary gets the best training
  efficiency compatible with `L`, honest inference only what has been demonstrated), and
  `rho_ach = (M_train / U_train) / (M_inf / U_inf)` (best attack actually constructed). The **training
  penalty** is `1 / rho_cert`. With a runtime-input budget `B` per horizon, credited training MACs are at most
  `kappa* B <= (|ℳ| / L) B`, i.e. at most a `rho_cert` fraction of the inference work the same `B` supports.
* **Worst-RU diagnostic.** Every headline `L` must come with the most constraining legal RU the certificate
  found (its total and serial work, input bytes, target MACs, MAC/byte, ops and entering runtime values): it
  is *the attack that prevents a stronger bound*, and the thing to inspect when deciding whether another
  policy constraint should exclude it.
* **Scope caveat [assumed].** The minimisation ranges over every legal partition of the *fixed* `C`
  (plus the regeneration/partial-sum rewrites listed in SPEC §3). It does not quantify over mathematically
  equivalent training circuits (other matmul algorithms, layouts, optimisers, parameterisations); §6 tracks
  what is assumed there.

Operator-level view. `extract` quotients `C` into an **operator graph** (validated gate-for-gate on small
circuits): ops with kinds (`matmul`, `add`, `rmsnorm`, ...), each matmul with `Q_o` activation rows, `N_o`
weight rows, contraction `K_o`, operand arrays `A_o` (rows = activation rows) and `B_o` (rows = weight rows;
an activation array in weight-gradient and attention products). Everything below is stated at this level; the
operator graph is an exact partition of the gate set, so statements about "elements touched by `o` in `R`"
are statements about gates.

## 1. Training requires accumulation-dependent work **[measured]**

For every training circuit in the registry (`pretrain-dense`, `local-sgd`, `rl-policy-gradient`, `es`,
`lora`, `hidden-adapter`, `pretrain-moe`) the fraction of total work that depends on accumulated or carried
state is 99.7-100% (`results/characterization.md`). For inference with registered weights it is 0. The
per-token `ADW_matmul` is `3.2e10` MAC at 8B pretraining (`1.26 x` the textbook `6 P_active` because the IR
recomputes the block forward in the backward pass and attends over the full `S x S`), `2.7e10` for LoRA
(the frozen base products after the first adapter count, because their activations depend on the adapters),
`8.6e9` for ES (one forward per population member), `5.6e10` for Mixtral-8x7B MoE pretraining (`4.0 x` its
inference MACs) and `0` for inference. The *state* `P` ranges from
`208 KB` (LoRA r=1 on q,v at 1B) to `1.2 TB` (DeepSeek-V3 pretraining); `ADW/P` spans five orders of magnitude.
So "training" is not one regime: the accumulated state can be tiny while the accumulation-dependent work is
the whole computation.

## 2. The simple bound and the amortisation problem

**Proposition 2.1 (state floor) [proved].** `I*(C; F, X) >= L_source := Width(non-fixed runtime inputs read
by at least one gate) >= P`. *Proof.* Each such value is in `In(R)` for the RU of some gate that reads it.

For one step this is `P` plus the token bytes and never grows with the number of tokens `Q`. It is the bound
of the earlier calculator and it is weak for exactly the reason one expects: an RU that holds `X` bytes of
weight rows and receives activation rows for free can perform `Q_o * (X / (2 K_o))` target products for one
weight load, and `Q_o` is the adversary's to choose. Whether the recurring cost per token is large therefore
hinges on one question: **are the activation rows free?** They are exogenous-free only for inference on
registered weights. For training they are produced by earlier ops of the same circuit from accumulated
weights, so an RU that wants them must either import them or import enough of their provenance to regenerate
them. §3 quantifies the second option and shows that under `X = 5 MB` it is never cheaper than the first
beyond the first projections of the first layer.

Two mechanisms can make activations expensive; both are captured by one definition. Following the
formalisation in the design notes, for a set of values `S` let `kappa_F(S)` be the minimum width of a set
`D` of non-fixed values such that every `s in S` is either in `D` or has `Work(Up_D(s) \ (theta u D)) <= F`
(the narrowest interface from which `S` can be reconstructed with at most `F` work behind each requested
value). **Lemma 2.2 [proved, design notes].** If an RU makes `S` available then `Width(In(R)) >= kappa_F(S)`;
hence `kappa_F(S) > X` means no legal RU makes all of `S` available. The bound of §3 is a certificate that
lower-bounds `kappa_X`-type quantities for the operand sets of every matmul *simultaneously and without
double counting*; it uses the budget `X` (the interface must fit) rather than `F` (which is ignored -- a
sound relaxation, SPEC §2.2). The `F` mechanism (SPEC §2.3) is the only one that bites in the compact-state
regime (§5) and is not part of the headline bound.

## 3. The certificate lower bound

### 3.1 Loomis-Whitney per op **[proved]**

Fix a matmul op `o` with `Q_o` rows of `A_o`, `N_o` rows of `B_o`, contraction `K_o`, and an RU `R`. Let
`S_R` be the set of index triples `(j, i, k)` of `o`'s scalar products performed in `R`, `w_R = |S_R|`, and
`a_R, b_R, c_R` the numbers of distinct `A_o` elements `(j,k)`, `B_o` elements `(i,k)` and outputs `(j,i)`
they touch. Loomis-Whitney: `w_R <= sqrt(a_R b_R c_R)`.

**Charging rule.** Suppose non-negative *charges* `alpha_o` (per distinct `A_o` element touched),
`beta_o` (per distinct `B_o` element), `gamma_o` (per imported partial sum of an `o` output) satisfy the
validity condition of §3.2. Then

    sum_R Width(In(R))  >=  sum_o [ sum_R (alpha_o a_R + beta_o b_R + gamma_o c_R) - gamma_o Q_o N_o ]

because an output touched by `r` RUs forces `r - 1` partial sums to be imported somewhere, and validity says
the charges of all ops inside one RU total at most that RU's imports. For each `o`, the inner sum is at
least `Q_o N_o K_o * m_o - gamma_o Q_o N_o` where

    m_o = min over reals a, b, c > 0 with alpha_o a + beta_o b <= X, a <= Q_o K_o, b <= N_o K_o, c <= Q_o N_o
          of (alpha_o a + beta_o b + gamma_o c) / sqrt(a b c).

The constraint `alpha_o a_R + beta_o b_R <= X` holds for every real RU because, by the validity condition
(Theorem 3.1 applied to `R` with only `o`'s claims counted), these charges total at most `Width(In(R)) <= X`
whether the touched elements were imported or generated inside `R`. Minimising over reals rather than
integer tile shapes is required for soundness (an RU's `(a, b, c)` need not be a rectangular integer tile).

Two sound tightenings (SPEC §2.1 v2.1). (i) When `B_o` is a root parameter its touched elements are all
imported at full width `w_B` and their budget is only ever claimed by `beta` charges, so the `alpha` claims
are paid by other imports and the constraint can be `alpha_o a + w_B b <= X`. (ii) Ops with the same `A`
operand (the `Wq, Wk, Wv` projections of one layer) can be treated as one matmul with `N = sum N_i`:
Loomis-Whitney holds for the union of index sets, and the fused op counts once in `share(A)`. Substituting
`a = a_rows k, b = b_rows k, c = a_rows b_rows` (a bijection on positive reals) gives the familiar
`cost/MAC = alpha/b_rows + beta/a_rows + gamma/k`, which is SPEC §2.1 with the `- gamma/K` correction.
`L_cap = sum_o L_o`, `L = max(L_source, L_cap)`.

### 3.2 Validity of the closure-budget charges **[proved]**

Definitions (SPEC §2.2): per activation array `t` with element width `w_t`: `share(t)` = max over elements
of the number of distinct ops reading the element; `Welt(t)` = the set of non-free runtime-input leaves that
any RU producing one element of `t` from free inputs alone must hold (union over the producer chain: one
row of `B_p` and a full row of every row-aligned input for a matmul, whole weight slices for the full rows
upstream, one table row for an embedding gather; a lower bound on the true requirement by construction);
`gen(t) := |Welt(t)| <= X`; the credit `kappa(t)` with `kappa(t) = 0` if `gen(t)` and otherwise
`kappa(t) = min(w_t, kappa_gen(t), (1 - theta_gamma) * 4)` where `kappa_gen` is the producer rule
(matmul with a runtime-input weight: `inh(A_p) K_p^2 beta_p / X`; element-wise: sum of `inh` over row-aligned
inputs; row ops, reductions, gathers as listed), `inh(u) = (1 - theta_u) kappa(u) / share(u)`. Charges:
`alpha_o = theta_A kappa(A_o) / share(A_o)`; `beta_o = w_B / share(B_o)` for a runtime-input weight array,
`theta_B kappa(B_o) / share(B_o)` for an activation; `gamma_o = theta_gamma * 4`.

**Theorem 3.1.** For every legal RU `R`, the total of the charges claimed by all ops for elements they touch
in `R`, plus `gamma` per imported partial sum, is at most `Width(In(R))`.

*Proof.* Give every non-free element `x` present in `R` (imported, or produced by a gate of `R`) a *budget*
`b(x)`: `b(x) = w_x` if `x` is imported; if `x` is produced in `R` by an op `p` from operands present in `R`,
`b(x)` is the sum of the *inherited portions* of those operands assigned to `x` (defined next). Budgets of
imported elements sum to `Width(In(R))`, and budgets of produced elements are carved out of operand budgets
without creating new budget, so it suffices to show that the claims on each element `x` -- the charges of the
ops reading `x` directly plus everything inherited by elements produced from `x` -- total at most `b(x)`.

*Step 1: produced elements have budget at least `kappa`.* Let `x` be an element of `t` produced in `R`.
(i) If `gen(t)` is false, some operand of `x`'s producer in `R` is non-free: otherwise all runtime-input
leaves in `x`'s closure would be inputs of `R`, so `Welt(t) subset In(R)` and `|Welt(t)| <= X`, contradicting
`not gen(t)`. Hence `x` is produced from operands with budgets. (ii) Each operand element `u` of array `s`
reserves `(1 - theta_s) b(u)` of its budget for inheritance and splits it equally among the consumers of `u`
present in `R`, at most `share(s)` of them, so `p` receives at least `inh(u) = (1 - theta_s) kappa(u) /
share(s)` per operand element by induction (`b(u) >= kappa(s)`, shown below). (iii) `p` divides what it
receives among the elements it produces from that operand in `R`. For a matmul with a runtime-input weight
array `B_p`, the complete outputs produced from one full `A_p` row in `R` correspond to distinct `B_p` rows
present in `R`; root-parameter rows cannot be generated, so each is imported at `K_p w_B` bytes and there are
at most `X / (K_p w_B)` of them; each output receives at least `K_p inh(A_p) / (X / (K_p w_B)) =
inh(A_p) K_p^2 w_B / X = kappa_gen(t)`. For a matmul with an activation `B_p`, one output needs a full `A_p` row and a full `B_p` row;
a row of `A_p` serves at most `N_p` outputs and a row of `B_p` at most `M_p`, giving `K_p (inh(A_p)/N_p +
inh(B_p)/M_p)`. For element-wise ops each output takes one element of each row-aligned input, receiving
`sum inh(in)`; for row ops the row's inheritance is split over the `rowlen(t)` outputs of that row; for
reductions at least one input element contributes; for gathers with unknown multiplicity nothing is claimed.
(iv) An element completed in `R` from `r - 1 >= 1` imported partial sums (4 bytes each) has budget at least
`(1 - theta_gamma) * 4 (r - 1)` after §3.1 claims `theta_gamma * 4` per partial. In every case
`b(x) >= kappa(t)` since `kappa(t)` is the minimum of the applicable expressions and `w_t` (imported case).

*Step 2: claims on `x` are at most `b(x)`.* Direct claims: at most `share(t)` ops read `x`, each claiming
`theta_t kappa(t) / share(t)` (an `A` or activation-`B` charge), total `<= theta_t kappa(t) <= theta_t b(x)`.
For a runtime-input weight array the `theta` is 1 and the claim `w_B / share(B)` per reader totals `<= w_B =
b(x)`; nothing is inherited from weights. Inherited claims: `x` passes `(1 - theta_t) b(x)` to elements
produced from it, and by induction over the DAG of `R` (from the last produced element backwards) their total
claims are at most their budgets, which are exactly these inherited portions. Total `<= b(x)`. Elements of
free arrays (`gen`) have `kappa = 0` and claim nothing; their budget is irrelevant. Recomputed elements are
distinct elements of `R` with their own budgets. □

**Corollary 3.2 [proved].** `L = max(L_source, sum_o L_o) <= I*(C; F, X)` for every `F`, with the `theta`s
chosen arbitrarily per array in `(0, 1)`. The bound also holds for the *regeneration-extended* adversary
that evaluates a gate in more than one RU (the constructive `U` with `recompute=True` uses this freedom):
validity is per RU and the Loomis-Whitney sum only needs `sum_R w_R >= Q_o N_o K_o`. The exact solver
(`exact/`) minimises over strict partitions, so the sandwich test is `L <= I* <= U(recompute=False)`; on
the 32 micro programs x 15 `(F, X)` cells it holds with `L` v1, and the single `U(recompute=True) < I*`
case (`fixacc_2x2x1`, `F = inf`, `X = 8 B`: 20 vs 24 bytes) is regeneration of a fixed-weight product, i.e.
a legal execution outside the strict-partition model, not a defect.

What the theorem does *not* assume: how the adversary tiles, whether it recomputes, whether it splits
reductions, which values it chooses to import versus regenerate, or anything about the data (token ids enter
only through `gen`, which only ever *removes* charges). What it does assume is listed in §6.

### 3.3 Where the charges land in a transformer **[measured, TBD until v2 numbers land]**

At `X = 5 MB` on Llama-3 8B: `|Welt|` exceeds `X` for every activation from the layer-0 `Wo` product onward
(a full attention row needs all of `Wq, Wk, Wv` = 48 MB), so `kappa = w_t = 2` for all of them and
`alpha ~ 1/share` with `share in {1, 2, 3}`; stacked weights have per-element `share = 4` (forward, recompute,
activation gradient, update) so `beta = 0.5`. The layer-0 `Q/K/V/W1/W3` products (one table row plus one
weight row fit in `X`) are charged zero: ~3% of the work. Expected `cost/MAC ~ 8 sqrt(alpha beta / X) ~
2e-3 .. 7e-3 B/MAC`, i.e. `L/token` in the tens of MB against `U/token = 218 MB` (`bounds/upper.py`,
`recompute=True`) and a state floor of `4 MB/token` at `Q = 4096`. Exact numbers: `results/RESULTS.md`.

## 4. From bytes to the security statement **[proved given §3]**

Let `kappa_L(C; X, F) := |ℳ(C)| / L(C; F, X)` (credited MACs per certified input byte): no legal
execution of `C` performs more than `kappa_L` target MACs per byte of runtime input. Asymptotically in `Q`,
`L(Q) ~ P + r Q` and `kappa_L -> |ℳ|/token / r`. (Using `ADW_matmul` in the numerator instead gives a
larger, adversary-favourable `kappa`; RESULTS.md reports both.)

**Theorem 4.1.** An executor with total work `W_tot` and total runtime-input allowance `B` that runs any
circuit whose accumulation-dependent matmuls are those of `C` (or a subset) satisfies
`eta = ℳ / W_tot <= kappa_L * B / W_tot`.
*Proof.* `ℳ <= ADW_matmul(C') <= kappa_L(C') * L(C') <= kappa_L * B` for the executed `C'`, using that the
charges of §3 are per performed product and monotone under removing products. □

The policy sets `B / W_tot`. Calibrating it so that *honest inference* on registered weights at the same
`(X, F)` runs at full efficiency means `B / W_tot = 1 / kappa_U(inference)` where `kappa_U(inference)` =
matmul MACs per byte achieved by the constructive partition of the inference circuit. Then

    rho_max = kappa_L(train) / kappa_U(inference)         (certified relative runtime-input efficiency)
    rho_ach = kappa_U(train) / kappa_U(inference)         (achieved by our best legal partition; the adversary can do at least this)

and the truth lies in `[rho_ach, rho_max]`. `rho` is *relative runtime-input efficiency*: under a runtime-input
allowance that supports `W` MACs of honest inference, at most `rho W` certified target MACs can be performed.
It equals the efficiency bound `eta_max` of Theorem 4.1 exactly when the adversary's total work is the `W`
the budget was calibrated for; we keep `eta` for `|ℳ|/Work(C)` and `rho` for the ratio of MAC-per-byte
rates. Both sides of `rho` must be recomputed at each `(X, F, model)` -- inference's byte cost also depends
on `X` through attention K/V imports. Comparing with native HBM traffic is *not* a security statement --
the protocol's resource is runtime input into RUs, not memory bandwidth -- and is not used here.
Numbers: `results/RESULTS.md` (P3).

**Where the recurring cost comes from (two tiers).** Sharding *between* whole matmuls (tier 1) costs about
one activation-sized value per boundary: for the 8B training circuit roughly `7` products x `8 KB` x `32`
layers x `~3` (forward, dgrad, wgrad) ~ `5-6 MB/token`, the same order as honest inference's `2.7 MB/token`.
Sharding *inside* a matmul (tier 2) is forced purely by geometry whenever the non-free weight array exceeds
`X`: every 8B matrix is `32-112 MB` against `X = 5 MB`, so `b_rows k w_B <= X` makes each activation row
enter `~N K w_B / X` RUs and (if `k < K`) partial sums cross RUs -- these are the `alpha/b_rows` and
`gamma/k` terms, and they are what makes `cost/MAC ~ 4 sqrt(alpha beta gamma / X)` scale as `X^{-1/2}`.
The closure theorem's job is different from forcing the split: it makes the *activation side* of the split
chargeable (`alpha > 0`). Without it a weight block amortises over unboundedly many free activation rows
(`a_rows -> infinity`, cost `-> 0`); without the split (`X >= |W|`) activations are charged only at tier-1
rates `alpha / N` and `rho -> ~1`. The ratio tier-2 / tier-1 is `~ 4 N sqrt(beta gamma / (alpha X))`, which is
why `rho` improves with model width and with smaller `X`. LoRA sits in tier 1 because its non-free arrays
(`r x d`) fit in `X` and the large products use fixed weights: the discriminating variable is not the total
accumulated state `P` but whether the non-free array each token must be multiplied by exceeds `X`.

## 5. Regimes **[measured, provisional]**

* **Dense training (pretrain, RL, local-SGD, ES on the full model, LoRA with `r * (#adapted) * d` per layer
  summing past `X` within a few layers).** `|Welt| >> X`, the charges of §3 apply to essentially all
  target products, `L` grows linearly in `Q` with slope `r` of order tens of MB/token at 8B. `eta_max` is
  set by `kappa_L(train) / kappa_U(inf)`; inference pays only activation imports (`~2.7 MB/token` at 8B) so
  `kappa_U(inf) ~ 3e3` and `eta_max ~ 0.05 - 0.2` at `X = 5 MB` (TBD).
* **Compact state (LoRA r=1 on q,v: `P = 208 KB` at 1B, few MB at 8B; hidden adapters; any PEFT whose whole
  adapter set fits in `X`).** `gen` is true for every activation: `L = L_source`. **X gives no protection**;
  the adversary imports the adapters once and regenerates everything from token ids. The only remaining
  mechanism is `F`: a gate at layer `l`, position `i` has `Up` work `~ l * (i+1) * 2 P_active` under causal
  attention (the IR's full attention makes it `l * S * 2 P_active`), which exceeds `F = 1e12` beyond
  `~120` token-layers at 8B, forcing imports of late activations (SPEC §2.3, not yet certified). Expect
  `eta_max` near 1 in this regime unless `F` is small; this is the honest answer, and it is the regime where
  the earlier "activation cut" argument was needed.
* **MoE.** The training circuit now has the full expert backward (`MoeBlockBwd`: expert dgrad/wgrad with
  recompute, combine and softmax-router backward, shared experts; validated gate-for-gate on `tiny-moe`);
  training is `4.0-4.1 x` the inference MACs on Mixtral / DeepSeek-V3 / Qwen3-235B, matching the dense
  convention. Expert weights are read by `TOPK Q / E` rows each, so `Q_o` per expert product is smaller and
  the weight term `beta / a_rows` is larger: per MAC the bound should be *stronger* than dense, while the
  state `P` per active parameter is `E / TOPK` times larger. Numbers: `results/RESULTS.md`.

## 6. Assumptions, prioritised **[assumed]**

1. **Accumulated/carried values are runtime inputs at full width** (`kappa_F(W) = Width(W)`): the circuit
   has no compact precursor of the current weights. In the theory-model's terms this is the incompressibility
   assumption for `W`. It is *false* if the adversary may register the current weights as `fixed` every step
   and carry only the update: then `Welt = {}` for every activation, `gen` is true everywhere, `L = token
   bytes`, and the entire protection moves to the **registration channel** (bytes of `fixed` state registered
   per unit time). The policy must throttle registration to `<< P / step`; the bound here then applies to
   whatever remains non-registered. This is the single most important external assumption.
2. **Widths are information.** Values have their prescribed widths; the adversary may not quantise, entropy-code
   or otherwise re-encode values crossing RU boundaries (that would be a different, non-equivalent circuit).
   A protocol that hashes replayed values at the declared width enforces this.
3. **The adversary's circuit is a training circuit we can see**: recompute, reassociation, partial sums and
   regeneration are allowed (and are what `U` uses); a *different algorithm* with less accumulation-dependent
   work is a different `C` and must be analysed on its own (LoRA/PEFT are the empirical proxies for this).
4. **Layer 0 is dropped** rather than assuming anything about token repetition (costs ~3% of the work).
5. **Attention is full `S x S`** in the IR (adversary-unfavourable for `F`-closures and for attention MACs;
   irrelevant for the `X`-driven headline). Causal masking is the natural next IR refinement.
6. **`F` is ignored** in the headline bound (sound; loses the compact-state regime).
7. **Operator-graph fidelity**: validated gate-for-gate on tiny configs only; the large graphs are trusted by
   construction of the same factories. `extract` records over-approximate leaf ranges; `share` is therefore
   an upper bound (safe).
8. **Per-op `X`**: each op's tile is given the whole budget; an RU hosting several ops shares one `X`. Sound,
   and part of the `U/L` gap.

## 7. Red team: "at least 50% of matmul MACs must use fixed weights" **[proved by construction]**

The policy is defeated by linearity at a 2x overhead and is orthogonal to what makes training expensive:

* **Split weights.** Write the trained weight as `W + Delta` with `W` registered (`fixed`) and `Delta`
  accumulated. `x (W + Delta)^T = x W^T + x Delta^T`: two products of equal size, one on fixed weights.
  Full-rank `Delta` is full fine-tuning; the fixed fraction is exactly 50%, and `Delta` absorbs any amount
  of learning. With the gradient products handled the same way the fraction stays at 50%. Under §3 nothing
  changes: `x` at layer `l >= 1` depends on `Delta`s of earlier layers, so it is charged; the `x W^T`
  product pays its `alpha` term at `b_rows -> N` (weights free), the `x Delta^T` product pays in full.
* **Padding.** Run any fixed-weight product of matching size alongside (a second forward, distillation
  against a frozen teacher, RL with a frozen reference model): the fraction is met and the training work is
  untouched. Such computations are also legitimately common, so the policy cannot flag them.
* **Frozen-base PEFT.** LoRA at `r = 16` on all projections has >90% of its MACs on fixed base weights and
  adapts the model; the policy passes it while §5 shows its actual protection is set by whether the adapter
  closure exceeds `X`, which the fraction does not measure.
* **What the fraction gets right, by accident.** It correlates with `gen`: products on fixed weights whose
  activations are also free are cheap for everyone. But the security-relevant quantity is `|Welt|` of the
  *activations*, not the role of the *weights*, and the two decouple completely in the constructions above.

## 8. What would change the conclusions

* A counterexample `L > I*` from `redteam/` (none expected after v2; the fuzzer is the test).
* `U/L` staying above ~5 at 8B after v2: then the empirical claim is only "between", and the constructive
  side must be tightened before quoting `eta_max`.
* A demonstration that real trained weights admit a compact precursor within the circuit (assumption 1).
* MoE with expert backward behaving differently from §5's expectation.
