# Training security from bounded accumulation (v4: F/G policies, no input cap)

Status tags: **[proved]** (theorem with proof here or in code docstrings), **[measured]** (number produced by the
pipeline with a checked artifact), **[estimated]** (closed-form reference, no artifact), **[assumed]**.
Numbers marked **[estimated]** are placeholders until `results/REPORT.md` replaces them.

The previous version of this document (`THEORY_xcap_deadend.md`) analysed a policy with a per-RU runtime-input
cap `X`. That policy forced *both* inference and training into matmul-tile RUs and therefore measured inter-RU
traffic under a tile policy, not the object below; its "inference costs 2.4 MB/token" was an artifact. Nothing
from it is used here except the exposure-certificate theorem (§8), which is policy-agnostic.

## 1. Security goal

Let `T` be the class of actual circuits `C*` that implement a specified amount and kind of full-parameter
training work (§5, §11). Let `Legal(C*, Π)` mean that partition `Π` of `C*` satisfies the RU policies (§3), and
let `κ(C*, Π) = M(C*) / I(Π)` be the training work per byte of runtime input (§5).

**Training security (universal).** `∀ C* ∈ T, ∀ Π: Legal(C*, Π) ⇒ κ(C*, Π) ≤ κ_train`.
The adversary chooses both the implementation and the partition; the bound must survive both.

**Inference usefulness (existential).** For each representative inference circuit `C*_inf` we exhibit one
legal partition `Π_inf` with `κ(C*_inf, Π_inf) ≥ κ_inf`.

The wedge is `ρ = κ_train / κ_inf`: under one runtime-input budget, the adversary sustains at most a `ρ`
fraction of the useful work the demonstrated honest workload sustains. Training is a universal claim;
inference is an existential one.

## 2. Actual computation and claimed computation

`C*` is a low-level deterministic DAG (Verity IR, scalar MAC granularity; `accumulation/algorithms/registry`).
Its exogenous inputs are *fixed* inputs `x_fix` (role `fixed`: known in advance, free) and *external* inputs
`x_ext` (role `token`; `seed`, `accumulated`, `carried` roots are also runtime inputs when read).

A partition `Π = {R_1, …, R_n}` assigns every non-input gate to exactly one RU. The claimed computation is the
quotient DAG whose nodes are RUs. Each RU has two kinds of inputs: fixed inputs (free) and **runtime inputs**:
external inputs it reads, and non-fixed values produced by another RU and consumed by it.

**A value internal to `C*` becomes runtime input only if the chosen partition cuts between its producer and its
consumer.** Low-level gates are not RU boundaries; an RU may contain twenty layers or a whole chat session.

## 3. Policies on the claimed computation

Local RU policies (the baseline; `F, G` are placeholders for the policy family):

- **Total work.** `Work(R) ≤ G`. An RU cannot contain unbounded parallel work / fan-out.
- **Upstream work.** For every gate `g ∈ R`: `Work(Up_R(g)) ≤ F`, where `Up_R(g)` is the set of gates *inside
  `R`* from which `g` is reachable (ancestor work, not path length; it stops at `R`'s inputs). An RU cannot
  reconstruct arbitrarily deep accumulated state internally.

Runtime input: `I(R) = Width(runtime inputs of R)` bytes, `I(Π) = Σ_R I(R)`. A global policy may require
`I(Π) ≤ B`.

**Calibration.** `F` and `G` are set relative to one honest inference session: `fwd(Q_inf)` = total MACs of
prefill on `Q_inf` tokens; `F = F̂·fwd`, `G = Ĝ·fwd`. `Ĝ` is the number of sessions (or independent branches)
an RU may batch; `F̂` how much longer a serial chain than one session an RU may contain. Defaults `Q_inf =
8192`, `F̂ = 1.5`, `Ĝ = 4`.

The two constraints play different roles (§9, §13): `G` bounds how many (token × layer) blocks a training RU
can span, which forces activation/gradient/weight traffic ∝ `G^{-1/2}` per MAC; `F` forbids fusing a whole
training step, or several steps, into one RU when `G` is large. Without `F`, a large-batch adversary at large
`Ĝ` collapses to the per-step weight-state floor (§13.4).

**`Up` is a statement about true gate dependencies, not about the RU's token count [measured, checker +
exact solver].** In a forward pass attention couples tokens only within a sequence and the residual stream is
per token, so a forward RU of `m` layers × any number of sequences has `Work = m` layers × all its tokens but
`Up(g) = m` layers × *one* sequence for every gate `g`. Consequences: (i) data-parallel batching never
raises `Up`, so `F` binds a forward RU only when a single sequence through `m` layers exceeds it
(`seq · m · w_layer > F`, never at `seq ≤ F̂ · Q_inf`); forward tiling is bounded by `G` alone; (ii) the honest
session is one RU for the same reason; (iii) in training, every RU that reduces a weight gradient over its
tokens has a gate whose ancestors span all of those tokens' forward and backward chains, so there `Up ≈
(1/2–2/3)·Work` and `F` *does* bind (§9). The coarse checker resolves `Up` from the kernels' real operand
reads (the plan supplies only the cut, never dependency claims); an independent gate-level BFS over the
flattened circuit agrees or is looser on 41/41 tiny cells (`results/up_independence.md`).

## 4. Running inference example **[measured constants, legality by construction]**

`inference-dense` (prefill of one `Q_inf = 8192`-token sequence; `inference-session` = prefill + teacher-forced
decode with the KV cache internal). Put the whole session in one RU. `Work(R) = fwd(Q_inf) ≤ G` for `Ĝ ≥ 1`
and every `Up_R(g) ≤ Work(R) ≤ F` for `F̂ ≥ 1`, so the RU is legal. Weights are fixed inputs; activations, KV
state, attention intermediates, logits are internal. Its runtime input is the token ids:

| model | `fwd(8192)` MACs (= `G` at `Ĝ = 1`) | useful MAC/token | runtime input | `κ_inf` MAC/B | fixed weights |
|---|---|---|---|---|---|
| Llama-3 1B | 1.45e13 | 1.77e9 | 4 B/token | 4.4e8 | 3.0 GB |
| Llama-3 8B | 7.91e13 | 9.65e9 | 4 B/token | 2.4e9 | 16.1 GB |
| Llama-3 70B | 6.57e14 | 8.02e10 | 4 B/token | 2.0e10 | 141 GB |
| Llama-3 405B | 3.59e15 | 4.38e11 | 4 B/token | 1.1e11 | 812 GB |

(`toks` is `V32`; 2 B/token if 17-bit ids are argued. 4 B is the conservative choice for the wedge.)

We do not pay for an activation because it exists; we pay only if the partition places its producer and
consumer in different RUs. A decode RU that imports a KV cache produced by an earlier RU (`inference-decode`,
2.1 MB/token at 8B) is a legitimate but unnecessary honest implementation; the session partition avoids it.

### 4b. Dynamic rollout generation **[measured]**

The intermediate workload between inference and training: the *same* forward graph and routing trace with
the weights declared a new (accumulated) model version (`forward-nonfixed`, MoE `forward-nonfixed-moe`).
Useful MACs per token are identical to inference, so its runtime input per token divided by 4 B is directly
the slowdown an RL-style loop pays for generating with weights it has not committed. `Q_roll` = 1M tokens,
default point (`Q_inf = 8192`, `F̂ = 1.5`, `Ĝ = 4`), lower hash `ac6c3bb0e3`, coarse hash `f4baa2d7be`
(`results/ROLLOUT_TABLES.md`):

| model | `P` (dynamic weights) | `L` MB/token | `U` MB/token | `U/L` | certified slowdown | best attack |
|---|---|---|---|---|---|---|
| Llama-3 1B | 3.0 GB | 0.0196 | 0.0382 | 2.0 | 4.9e3× | 9.6e3× |
| Llama-3 8B | 16.1 GB | 0.0847 | 0.125 | 1.5 | 2.1e4× | 3.1e4× |
| Llama-3 70B | 141 GB | 0.315 (MILP gap 32 %) | 0.525 | 1.7 | 7.9e4× | 1.3e5× |
| Llama-3 405B | 812 GB | 1.50 | 2.11 | 1.4 | 3.8e5× | 5.3e5× |
| Mixtral 8×7B | 93.4 GB | 0.134 | 0.226 | 1.7 | 3.3e4× | 5.6e4× |

Three facts the tables establish. (a) The exposure is *recurring*, not a one-time model read: the weight-only
floor `P/Q_roll` (0.0153 MB/token at 8B) is exceeded by both bounds at 1M and the certified and achieved
per-token rates converge as `Q_roll` grows (70B: `L/Q` 0.315 → 0.413 from 1M to 4M while `U/Q` stays at
0.52; the recurring share of `L` is 82 % at 8B/1M, 92 % at 70B/4M). (b) The mechanism is the forward block
model of §9b: with `Up` per sequence only `G` bounds a tile, the optimum is `m* ≈ 4` layers × ≈ 250K tokens at
8B, and the two-parameter analytic optimum reproduces the planner's `U` within 2–24 % across dense models
with no tuning; across `Q_inf` = 2K / 8K / 32K at 8B, `U` = 0.257 / 0.125 / 0.0595 MB/token, i.e. `∝ Q_inf^{-1/2}`
(ratios 2.06, 2.10 per 4× in `G`) exactly as the `A^{-1/2}` law predicts, and `L` = 0.192 / 0.0847 / 0.0291
follows. `F̂` = 3 or 10 leaves both bounds unchanged (0.0847 / 0.125): `F` is not a forward constraint.
(c) Policy relaxations move it but do not erase it: at `Ĝ = 1000` the whole 1M rollout is one legal RU and
`I* = P + tokens` exactly (`L = U = 0.0153` MB/token at 8B, still 3.8e3×); at `Ĝ = 10`, 0.0516 / 0.0794; at
`Q_inf = 128K` two RUs suffice (`U = 0.0306`, `L` on the floor). MoE: the planner's MoE block family (attention + router +
the experts a token chunk actually hits, per layer) gives Mixtral `U/L = 1.7`; Qwen3-235B-A22B and
DeepSeek-V3 at 1M are still being recomputed at these hashes (their 8K–128K rows are current).

## 5. Training resource

Full-parameter training circuits are multi-step: `local-sgd` with `local_steps = K` chains `K` SGD steps on
`Q_step` tokens each; `W_k` (`k ≥ 1`) is produced by step `k−1`'s update gates. `ℳ(C*)` = the scalar
multiplication gates of the products `W_k A` and their gradient counterparts (fwd, dgrad, wgrad) at steps
`k ≥ 1`, excluding recomputation (no credit), the layer-0 block and the embedding gather (§8: their charge would
depend on token diversity). Step-0 weights are baseline (free): `M(C*) = |ℳ|` is a steady-state quantity and
every headline is a per-step marginal, `b_train = (I(K=3) − I(K=2)) / Q_step` bytes per training token.
Per token at 8B: `M_train/Q_step = 3.0e10` (3.0–3.15× inference at every scale).

`κ(C*, Π) = M(C*) / I(Π)`. (Arithmetic efficiency `M / Work` is not central: the mechanism constrains `M / I`.)

## 6. Best partition for a fixed actual circuit

`I*(C*; F, G) = min_{Π legal} I(Π)`; `κ*(C*) = M(C*) / I*(C*)`: the narrowest total runtime interface through
which this computation can be implemented under the policies. For inference we need `I*(C*_inf) ≤ U_inf`
(§4 gives `U_inf = 4 B/token`). For training we need `I*(C*_train) ≥ L_train`, plus a checked `U_train` so
that `L ≤ I* ≤ U` brackets the truth.

## 7. Exact partitioning problem

With `𝓡(C*)` the legal candidate RUs, `I* = min Σ_R I(R) z_R` s.t. `Σ_{R ∋ g} z_R = 1 ∀ g`, `z_R ∈ {0,1}`.
There are no privileged layer or matmul boundaries. `accumulation/exact` solves this on micro circuits
(brute force + MILP, `X = ∞`), which is how the bounds below are validated (§12).

## 8. Exposure certificates **[proved]**

**Theorem (exposure certificate).** Let `p_g ≥ 0` be charges on non-input gates such that every legal RU
satisfies `Σ_{g ∈ R} p_g ≤ I(R)`. Then for every legal partition `Σ_g p_g ≤ I(Π)`, hence `L := Σ_g p_g ≤ I*`.
*Proof.* Sum the RU inequalities over the partition; each gate lies in exactly one RU. ∎
(The relaxed set-partitioning LP has exactly these charges as its dual; `L` is a dual feasible value.)

The certificate implemented in `lower_coarse` (`bounds/lower.py`) prices target MACs using four facts, each
verified on the operator graph rather than assumed:

1. **Token-row lemma.** In a dense-residual transformer block, producing any element of the block input row
   `x_l[q,·]` (`l ≥ 1`) requires the full residual row `h_l[q,·]` (rmsnorm), and producing any element of
   `h_l[q,·]` requires full rows of the previous block's stages for token `q` (`d`-wide contractions). So for
   each (step, token) with any produced forward activation at layers `≥ 1` inside `R`, the bottom of `q`'s
   produced chain is a full `d`-row that is *not* produced in `R`, i.e. `≥ 2d` bytes imported and attributable
   to that (step, token). Symmetrically a produced gradient element requires the full gradient row above; the
   top of a produced backward chain below the loss is an imported `2d`-row. Chains that bottom out at the
   embedding get no charge (embedding rows are shareable across same-id tokens), which is why layer 0 is
   excluded from `ℳ`.
2. **Weight presence.** An accumulated weight element `W_k[n,j]` read by a target MAC in `R` is imported
   (2 B) or produced in `R`; produced means `R` contains its update gate, so `dW_{k−1}[n,j]` is present:
   imported (≥ 2 B) or produced, which requires all `Q_step` wgrad MACs for `(n,j)` in `R` and hence
   `dY_{k−1}[q,n]`, `x_{k−1}[q,j]` present for every token of step `k−1` (each imported or itself charged by 1).
3. **Loomis–Whitney over tokens × weights.** Per (step, layer, matrix) the MACs in `R` satisfy
   `|S| ≤ sqrt(|A||W||O|)` with `|A|` the activation elements present (directly imported + `K` per charged
   token row), `|W|` the weight elements present, and `|S| ≤ Work(R) ≤ G`.
4. **`F` through `Up`.** If `R` produces `dW_{k−1}[n,j]` from produced operands, `Up_R(dW) ≥ Σ_q` (work of
   `q`'s produced chain below layer `l`) `≥ Q_step · depth · P_layer`, so `F` bounds the produced depth and
   forces token-row imports for all but the bottom `≈ F / (Q_step · P_layer)` layers; likewise a fwd MAC's `Up`
   includes its token's produced chain. This is what excludes "a whole step in one RU" when `F < 3·fwd(Q_step)`
   even if `G` is huge.

The price `λ` (per target MAC, per class) is the largest value with `λ·m(R) ≤ i(R)` over every RU shape the
parametrization admits; the theorem that the parametrization covers every legal RU is in the `lower_coarse`
docstring. A separate sound bound is the **per-step weight floor**: when `F` excludes computing any `dW`
element from scratch and `Q_step ≥ NK/(N+K)`, every accumulated weight element costs `≥ 2 B` per step,
`L_W = 2P(K−1)`. `L = max(L_block, L_W)`.

**8b. Weight-presence certificate as implemented (`bounds/lower_wp.py`) [proved given convexity; gate-checked; measured].**
The unconditional form of fact 2 that the sweeps use. Let `W_k` be a *chained* weight tensor: produced by the
step-`k` update op, consumed by step `k+1` (forward, recompute, backward) and by its own step-`(k+1)` update.
For an element `e` with producer gate `p_e` and update gate `u_e`, any RU containing both is convex (§0 of the
SPEC: RUs are replayed against committed inputs, so the quotient is acyclic) and therefore contains every gate
on a `p_e → u_e` path; those gates are ancestors of `u_e` inside the RU, so `Work(Up_R(u_e)) ≥ T_e :=`
work of that hull, and `Work(R) ≥ T_e` as well. If `T_e > F` or `T_e > G` the RU is illegal, `p_e` and `u_e`
lie in different RUs, and the value `W_k[e]` crosses an RU boundary: it is runtime input. Summing over
elements, `L_wp = Σ_{chained W_k : T > F or T > G} bytes(W_k)`. `T_e` is bounded below at op level by the
work of the ops topologically between the producer and the update op restricted to layers `≥ l+2` and the head
(`l` = the weight's layer): every gate of those ops lies on a `p_e → u_e` path for *every* element `e` because
the transformer mixes all coordinates (rmsnorm, down-projection transposes) and positions (attention) within two
layers, and the higher layers' weight-gradient ops -- which are not ancestors of `u_e` -- are excluded by the
op-level ancestor test. The `l+2` rule is what the exact gate-level check required: `redteam/wp_gatecheck.py`
flattens tiny 1-4 layer `local-sgd` circuits to gates and verifies `Up_lb ≤ min_e T_e` for every chained tensor
(0 violations; the `l+1` variant violated). The charge counts step-`k` weights (`k ≥ 1`), disjoint from the
step-0 roots and the tokens, so `L = max(L_coarse, root_read + tokens + L_wp)`; it is additive per step
boundary, which is what makes it a *steady-state* statement (below).

Measured at `F̂ = 1.5`: a weight at layer `l` is forced when the work of layers `≥ l+2` of one step's
forward+backward exceeds `F`, i.e. for all but the top `≈ F̂·L/(3·Q_step/Q_inf) + 2` layers. 8B, `Q_step =
8192`: 144 of 290 chained tensors, 6.98 GB = 0.43 P per step boundary → **852 KB per training token**
(`Ĝ ≥ 4`; at `Ĝ = 1` `G` also binds: 189 tensors, 9.16 GB). `Q_step = 32768`: 252/290, 12.2 GB = 0.76 P →
373 KB/token. `Q_step = 131072`: 13.5 GB = 0.84 P (embedding rows are gathers and are never charged) →
103 KB/token. 1B, `Q_step = 131072`: 270/292, 1.82 GB = 0.74 P → 13.9 KB/token. Against the constructive
partition's marginal (`U`: 3.09 MB/token at 8B, `Q_step = 8192`) the sandwich is `U/L = 3.6`; both are
`≥ 2e5×` the 4 B/token inference ingress. At `F̂ ≥ 3` and `Q_step = Q_inf` one step's whole hull (`≈ 2.8
fwd`) fits under `F` and the certificate forces nothing **[estimated; the F̂ axis of Table 2 measures it]**:
it is an `F` statement first and a `G` statement only at `Ĝ ≈ 1`. Its ceiling is the per-step weight floor:
the forced fraction of `P` grows with `Q_step` (0.43 → 0.76 → 0.84 P at 8B) but `b_L ≤ P/Q_step` per token,
whereas the constructive partition's per-token cost is dominated by activation-row traffic that does not fall
with `Q_step`; the sandwich therefore widens at large batches (`U/L` 3.6 at `Q_step = 8192`, larger at
`131072`), and closing it needs the token × layer block term, not a better weight argument.

*Steady-state semantics.* A difference of two lower bounds is not a bound on the marginal `I*(K) − I*(K−1)`
(the coarse MILP closed at `K = 2` and not at `K = 3` for 1B and the difference came out negative). What is
proved is `I*(K) ≥ root + K·tok_step + (K−1)·wp`, hence `lim_K I*(K)/(K·Q_step) ≥ (wp + tok_step)/Q_step`:
the certified steady-state rate `b_L`. On the other side the planner's partition repeats per step, so the slope
of `U(K)` is an achievable rate `b_U`. Tables report `b_L ≤ b* ≤ b_U` in this sense.

Reconstruction-width, separator, reach and communication-complexity arguments are all ways of constructing
valid charges; they are not separate security definitions.

## 9. Separator / reach intuition

A partition cuts `C*` along separators; a narrow separator is dangerous if a large amount of credited training
work lies behind it before a policy forces another boundary. Inference has spectacular reach — 4 B/token of
external input reaches an entire session — because the weights are fixed.

**`F` is an area cap for training.** Any RU that reduces a weight gradient over its tokens (a full `dW` or a
partial sum it exports) contains a gate whose ancestors include every one of its tokens' forward chain below
and backward chain above, so `Up ≈ (1/2–2/3)·Work(R)` for that gate (only sibling wgrads are non-ancestors).
Hence `Work(R) ≲ c_F·F` with `c_F ≈ 1.5`, and the effective cap on a training unit is `min(c_F·F, G)`;
forward-only units (inference, rollout) are not `F`-bound at all (§3: `Up` is per sequence), so their cap is
`G`. Whenever `Ĝ > c_F·F̂` the branching/batching allowance `G` is irrelevant to training security
**[estimated; planner: at 8B the 32 `bwd[1 layer × all tokens]` units are exactly F-bound, `Up = Work =
1.375 fwd`]**. Reducing outside the RU (exporting per-token outer products) costs `≈ 2/min(N,K)` B/MAC and is
never competitive.

**9b. Forward block model (rollout) [measured].** A forward RU covering `m` layers × `t` tokens imports its
layers' dynamic weights (`m·P_b/L` bytes, `P_b` = weight bytes, `L` = layers) and the residual stream entering
the chunk (`2d·t` bytes; the first layer's input is token ids). With `Q` tokens and `A = Ĝ·Q_inf·L` the
admissible area in token-layers (`G` alone, §3),

`cost(m,t)/token = P_b/t + 2d·(L/m − 1)`, `m·t ≤ A` → `m* = sqrt(2d·L·A/P_b)`, `cost* ≈ 2·sqrt(2d·L·P_b/A)`,

independent of `Q` once `Q ≫ t*`: the one-time model read amortises but the per-tile weight re-import does
not. 8B at the default point: `A = 1.05e6`, `m* = 4.1` layers, `t* = 2.5e5` tokens, `cost* = 0.119 MB/token`
vs measured `U = 0.125`; the planner's tiles are exactly this shape (`results/ROLLOUT_TABLES.md` P2/P3).
Relaxing `Ĝ` until `A ≥ L·Q` makes the whole rollout one RU and the cost drops to `P_b/Q + 4 B` (measured
`L = U` at `Ĝ = 1000`).

**Block model [estimated].** A training RU covering `m` layers × `u` tokens (`u = k'·Q_step` whole steps, or
`u < Q_step` part of a step) imports bottom activation rows and top gradient rows (`4·d·u`), its weights
(`2·m·P_layer`, once — with whole steps inside, the updates are internal), and, if `u < Q_step`, its partial
`dW` arrives at the reducer (`4·m·P_layer`). With `A = min(c_F·F, G)/w_tl` the admissible area in
token-layers (`w_tl` all-op work per token-layer) and `w_c` credited MACs per token-layer,

`cost(m,u) = 4d/(m·w_c) + c_W·P_layer/(u·w_c)`, `m·u ≤ A`, `c_W = 2 (u ≥ Q_step) or 6 (u < Q_step)`,

`m* = sqrt(4d·A/(c_W·P_layer))`, `cost* = 2·sqrt(4d·c_W·P_layer/A)/w_c`, `b_train = cost*·M_train/token`.
8B at `Q_inf = 8192`, `F̂ = 1.5`, `Ĝ = 4`: `A ≈ 1.5e5`, `m* ≈ 2.4` layers, `u* ≈ 6.4e4` tokens (≈ 8 steps
of 8192) → `b_train ≈ 0.44 MB/token`; with `Q_step = 131072 > u*`, `c_W = 6` → `0.75 MB/token` (a larger
batch is worse for the adversary here). The per-step weight floor `2P/Q_step` is the `m = L` case and applies
only when `L·Q_step ≤ A` (`Q_step ≲ 5e3` at 8B) — never for realistic batches under these policies.

*Acyclicity correction [measured].* RUs are replayed against committed inputs, so the RU quotient must be
acyclic: an RU is convex in the gate DAG. A unit holding both the forward and the backward of layers
`l..l+m` for some tokens is convex only if it also holds everything on the paths between them (all layers
above, the loss, and their backward), so the joint `fwd+bwd` tile assumed above is illegal unless it spans the
whole model. Forward tiles and backward tiles are therefore separate units; a backward tile imports the
checkpointed activation rows *and* the incoming gradient rows (`4d·u`) plus its weights, and is `F`-bound
through its `dW` reduction. This roughly doubles the row traffic relative to the joint model: the convex
planner at 8B (default point) finds `U = 0.81 MB/token` with 32 F-bound `bwd[1 layer × all tokens]` units
accounting for 83 of 106 GB per step, versus 0.44–0.75 for the (illegal) joint tiles.

**Transient.** While `K·Q_step·m·w_tl ≤ c_F·F` the whole run fits in `L/m` chunk units and only rows cross:
`4d·(L/m)` per token (0.26 MB/token at 8B, `m = 2`) — this is what small-`K` measurements show; the steady
state is the slope of `I(K)` past the knee `K ≈ c_F·F/(m·Q_step·w_tl)`.

Training cannot obtain inference-like reach from narrow separators because every block bottom re-enters a
`d`-row per token and every block re-imports its weights (or re-exports its gradients).

## 10. Fixed-circuit theorem **[proved given §8]**

For a fixed training circuit with certificate `L_train`, every legal partition has `I(Π) ≥ L_train`, so
`κ(C*, Π) ≤ M_train / L_train`. An exhibited inference partition gives `κ_inf ≥ M_inf / U_inf`. Therefore

`ρ_cert = (M_train / L_train) / (M_inf / U_inf)`, `ρ_ach = (M_train / U_train) / (M_inf / U_inf)`,

and `ρ_cert = 1e-5` means: under the runtime-input budget that sustains the demonstrated inference workload,
the specified training work runs at most `1e-5` as fast. With `b_inf = 4 B/token` and `M_train/M_inf ≈ 3.1`,
`1/ρ_cert ≈ b_train[bytes/token] / 12.4`.

## 11. From one training circuit to the security claim **[assumed; the main conceptual gap]**

The fixed-circuit theorem quantifies over partitions, not over implementations. The universal claim needs a
class `T` such that (i) every computation accomplishing the specified training objective lies in `T`, and (ii)
every `C* ∈ T` admits the certificate. Where architecture enters: the token-row lemma relies on the transformer
block's full-row dependencies (rmsnorm, `d`-wide residual mixing), and the weight-presence fact relies on the
update being an element-wise function of `W_{k−1}` and a `Q_step`-token reduction. Hence the honest statement
of `T` today is **dense-residual transformer training circuits with full-parameter element-wise updates**,
covering: dense pretraining, local-SGD / DiLoCo (the block term is unchanged; only the weight floor is divided
by the sync interval), RL policy gradient, ES / forward-only perturbation training (fwd only: ≈ 1/3 the
block traffic). Outside `T`: low-rank / compressed / sparse updates (different objective class), architectures
without full-row mixing (would need a different row lemma). Also outside the current analysis: alternative
matrix-multiplication algorithms (the IR fixes the schoolbook product; Strassen-type reuse would change the
Loomis–Whitney constants, not the token-row or weight-presence facts).

## 12. Empirical program

Inference: build `C*_inf` (prefill; session), exhibit the one-RU partition through the coarse checker
(`bounds/coarse.py`), report `U_inf`. Training: build multi-step `C*_train`, compute `L_train`
(`lower_coarse`), `U_train` (`upper_coarse` block families), and `I*` exactly on tiny multi-step circuits
(`accumulation/exact`, `L ≤ I* ≤ U` on every cell → `results/validation.{md,json}`). Policy calibration: sweep
`Q_inf`, `F̂`, `Ĝ`, `Q_step`, `K`, model scale and architecture (`results/REPORT.md`, figures A–E).

## 13. Headline tables and expectations

**Table 1 — inference feasibility** (§4): measured constants; `U_inf = 4 B/token` in one checked RU at every
calibrated point, dense and MoE (all seven models, `results/ROLLOUT_TABLES.md` acceptance section).

**Table 1b — dynamic rollout** (§4b): `L`, `U` at 1M tokens for 1B/8B/70B/405B and Mixtral at the frozen
hashes, `U/L` 1.4–2.0, certified slowdown 4.9e3×–3.8e5×; `Q_roll`, `Q_inf`, `F̂`, `Ĝ` sweeps and the
optimal-adversary anatomy in `results/ROLLOUT_TABLES.md` (P1–P4). **[measured]**

**Table 2 — training exposure** (per model at the default point): `M_train/token`, `L`, `U`, `U/L`,
certified `κ`. **[pending: all training rows are being recomputed at the frozen planner (acyclic convex family,
per-sequence `Up`) and certificate; the K = 3 certificate did not close at a 180 s MILP budget and is being
re-run at 600 s]**

**Table 3 — security wedge**: `κ_inf`, `M_train/L_train`, `ρ_cert`, penalty `1/ρ_cert`; `ρ_ach` alongside.
**[pending]**

Analytic expectations (§9 block model, steady state) **[estimated]**: 8B at the default point ≈ 0.44 MB/token
(penalty ≈ 3.5e4); the earlier single-step figure (1.2 MB/token at `Ĝ = 1`) ignored whole-step units and is
superseded. Expected dependences: `b_train ∝ A^{-1/2}` with `A ∝ min(c_F·F̂, Ĝ)·Q_inf` (so `∝ Q_inf^{-1/2}`;
`∝ F̂^{-1/2}` while `Ĝ > c_F·F̂`, and flat in `Ĝ` there — branching allowance is free); rising ≈ `sqrt(3)×`
in `Q_step` once `Q_step > u*` (partial-step units) and otherwise flat; `2P/Q_step` never governs at realistic
batches; `∝ P·sqrt(d/(L·Q_inf))` in model size (the wedge widens with scale); `I(K) = I_0 + rK` linear past
the transient knee (any flattening beyond it is an amortisation attack). Precision scales all charged widths
together and leaves token ingress unchanged (a 16→8-bit move is ≈ 2×, not orders of magnitude).

First measured 8B points **[measured, upper bound only; pre-acyclic planner, superseded]**: inference-session
and inference-dense are exactly one RU at 4 B/token (1B/8B/70B, `Q_inf` 1K–128K, `F̂ = 1.5`, `Ĝ ≥ 3`);
local-sgd `Q_step = 8192`: `U(K=2) = 1.09`, `U(K=4) = 0.68` MB/token, marginal 0.27 MB/token — the transient
regime (all steps fit under `F` per 2-layer chunk), matching `4d·L/2 = 0.26 MB/token`. Those plans used cyclic
(joint fwd+bwd, multi-step fused) units and are not legal under the acyclic RU quotient (SPEC §0); the convex
planner at the same point gives `U ≈ 0.81 MB/token` per step at `K = 2, 3` (marginal exact), with the cost
sitting in 32 F-bound `bwd[1 layer × all tokens]` units that re-import checkpoints, gradients and weights
(83 of 106 GB per step). The certified `L` at the default point is 0.137 MB/token at `K = 2` (dual bound);
`K = 3` is pending (§13, Table 2).

**Validation at the frozen hashes [measured]**: exact micro panel `N = 1729`, `U < I*` = 0, `L > I*` = 0;
95 registry rollout cells (dense tiny2, MoE tiny-moe) bracket `L ≤ I* ≤ U` with `L = I*` on all 14 exactly
solvable cells; 51 block-term cells (tiny2 local-sgd `K = 2, 3`) 0 violations (`results/validation*.md`,
`results/REDTEAM_STATUS.md`).

## 14. What would change the conclusions

- A legal RU shape outside the certificate's parametrization (the exact solver finding `I* < L` on a micro
  circuit) — soundness bug, fix before quoting anything.
- A block family cheaper than `5.66·sqrt(d/G)` that the planner finds (`U ≪` estimate) — then the certificate
  must be tightened toward it or the estimate is wrong.
- An architecture or update rule in the intended `T` that breaks the token-row or weight-presence facts.
- Policy needs (long sessions, heavy branching) pushing `G` to where whole steps fit; then everything rests on
  `F` and the weight floor `2P/Q_step`, which large batches erode.
