# Bounded accumulation: definitions, bound family, module contracts

This file is the shared contract for everything under `accumulation/`. Code in `bounds/`, `exact/`,
`sweeps/` must use these definitions verbatim; if a definition has to change, change it here first.

## 0. Policy v4 (corrected model) -- supersedes every use of `X` below

**Legality.** An RU `R` is legal iff `work(R) <= G` and `work(Up_R(gate)) <= F` for every gate in `R`.
A **partition** is legal iff every RU is legal **and the RU quotient graph is acyclic** (the protocol's
contract, `docs/PROTOCOL.md`: every RU is replayed against its committed inputs, so its inputs must exist
before it runs; a 2-cycle `R1 -> R2 -> R1` is not executable as two units). Equivalently every RU is
**convex** in the gate DAG: a gate on a path between two gates of `R` belongs to `R`. Consequences (2026-09-15):
a `joint` fwd+bwd unit of a layer chunk is legal only if it also contains everything between -- the layers
above it and the head; fusing steps `k, k+1` of a layer chunk into one RU is illegal unless the RU contains
the whole of step `k` (all layers, all `Q_step` tokens, the head); `U` witnesses that violate this are not
attacks and must not be reported. Acyclicity removes partitions, so every certificate `L` proved without it
stays valid and `I*` can only rise. Forward-only circuits (inference, `forward-nonfixed`) are unaffected:
layer-chunk x token-chunk units are ordered lexicographically.
*How the coarse checker evaluates `Up` (2026-09-16).* `bounds/coarse.py::check_coarse_plan` takes from the
plan only the **cut** -- which `(op, slice)` members exist and which unit holds them. The dependency edges
are **not** the planner's: each member's operand windows are resolved through the program to the producing
`(op, instance, rows)` (attention's within-sequence coupling, the residual stream, router/expert gathers are
the kernels' real reads), and every member producing part of a read window is an ancestor. `Up(u)` = work of
`u` plus all its ancestors inside the unit; the unit's `Up` is the max over members. This dominates the
gate-level `work(Up_R(g))` for every gate (any in-RU gate upstream of `g` lies in a member reached by one of
those wires, and the whole member is counted); the cut only fixes the granularity, and a finer (per-sequence)
cut is tighter but no less sound than whole-op members. Independent path: `gate_level_up` expands a unit to
gates and BFSes the flattened circuit's real wires (`exact/solve.py::up_set`); `results/up_independence.md`
records checker `Up >=` gate-level `Up` on every tiny2 / tiny-moe rollout and local-sgd cell (1.3-40x
conservative; `Work` equal up to the checker's accumulator inits for cut `red` chains). **When `F` binds:** a
forward RU of `m` layers x `s` sequences has `Up = m` layers x one sequence, so `F` binds iff
`seq * m * w_layer > F`, i.e. `m/L > F_hat * Q_inf / seq` -- never at `seq <= F_hat * Q_inf`; `G` alone sizes
forward tiles. A training RU containing a `dW` reduction over its tokens couples all its sequences (the
reduction gate's `Up` is the whole unit's upstream), so `F` binds a bwd/top unit once its tokens x layers of
backward work exceed `F`; cutting the reduction by sequence moves the coupling into the running accumulator
the next unit imports -- the structural cost of training under `F`.
There is **no per-RU runtime-input cap**: `X` is gone (treat `X = None/inf` everywhere; §2-§3 are retained
as the documented dead end -- they measured inter-RU traffic under a matmul-tile policy, not `I*`).

**Runtime input** is unchanged: `in(R)` = non-fixed root leaves read by `R` (`token | seed | accumulated |
carried`) plus outputs of gates outside `R` read inside `R`, in bytes. `fixed` is free. Cross-RU activations
count -- the point is that the optimal *inference* partition never cuts them.

**Calibration.** `fwd(cfg, Q_inf)` := the coarse checker's `Work` of the whole `inference-dense` circuit at
`Workload(tokens=Q_inf, seq=Q_inf)` (all ops, the same units the F/G checks use; `= adw(...).all_work`,
0.4-1.6% above `all_macs` -- calibrating in `all_macs` made the honest session fail the one-RU check at
`F_hat = 1` / `G_hat = 1`). `results/calibration.md` reports both. Policy points are `F = F_hat * fwd`,
`G = G_hat * fwd`; defaults `Q_inf = 8192`,
`F_hat = 1.5`, `G_hat = 4`; sweeps `Q_inf in {4096, 8192, 32768}`, `F_hat in {1, 1.5, 2}`, `G_hat in {1, 4,
16, 100}` (`G_hat` = honest sessions batched per RU). Absolute values at `Q_inf = 8192` (`results/calibration.md`):
1B 1.45e13, 8B 7.91e13, 70B 6.57e14, 405B 3.59e15 MACs.

**Sanity condition (must hold at every calibrated point).** `inference-dense` / `inference-session` at
`Q_inf` is one legal RU (`work = fwd <= G`, every `Up <= work <= F`) whose input is `toks` only:
`b_inf = 4 B/token` (`toks` is `V32`; footnote the 2 B/token 17-bit figure).

**Training circuits are multi-step.** `local-sgd` with `Workload(tokens=K*Q_step, seq=..., local_steps=K)`
chains `K` SGD steps; `W_k` (`k >= 1`) is produced by step `k-1`'s `sgdupdate` gates. Headline per-token
quantity: the steady-state marginal `b_train = (I(K=3) - I(K=2)) / Q_step` for each of `L`, `U`, `I*`.
Step-0 weights are baseline (free) for the lower bound; target work `ℳ` = matmul MACs at steps `k >= 1`
excluding recompute, the layer-0 block and the embedding gather (data-independence: embedding rows can be
shared across same-id tokens). `M_inf` = `all_macs` of the inference circuit.

**Reported quantities.** `kappa = M / I`; `rho_cert = (M_tr / L_tr) / (M_inf / U_inf)`; `rho_ach = (M_tr /
U_tr) / (M_inf / U_inf)`; penalty `= 1 / rho`; per-token `b_inf`, `b_train_L`, `b_train_U`.

**Module contracts (v4).**
- `bounds/coarse.py`: `upper_coarse(g, F, G, *, program=None) -> Plan` and `check_coarse_plan(g, plan, F,
  G)`. Units are sets of `(op, slice)` (slice = whole or a sequence-aligned token-row range) spanning many
  ops; imports recomputed from `Edge.ranges` (half-open) / `leaves_per_copy`; inexact edges import the whole
  source; `Up` bounded by the sum of ancestor unit members' work (conservative). Families: whole-session
  inference; training blocks (layer chunk `m` x sequence chunk `s` x fwd+bwd per step) with wgrad/update
  placement variants. `Plan.ru_stats()` as before.
- `bounds/lower.py::lower_coarse(g, F, G, *, program=None) -> LowerBound`: certificate `sum_{g in R} p_g <=
  in(R)` for every legal `R`, built from (i) the token-row lemma (a produced activation of token `q` at layers
  `>= 1` inside `R` forces a full `d`-row import at the bottom of its produced chain; symmetric for gradient
  rows at the top), (ii) weight presence (an accumulated weight element read in `R` is imported, or produced
  in `R` which requires its `dW` imported or all `Q_step` wgrad operands present), (iii) Loomis-Whitney over
  tokens x weights per (step, layer, matrix), (iv) `F` bounding the depth of produced chains through `Up`;
  plus the separate per-step weight floor `2 P (K - 1)` when `F` excludes computing any `dW` element from
  scratch and `Q_step >= N K / (N + K)`. Returns `max` of the components with each reported, `worst_ru` = the
  minimising RU shape.
- `exact/`: `X = None`, `F, G` finite; multi-step micro circuits (`local-sgd` tiny2 `local_steps in {1, 2, 3}`,
  tiny inference) -- the arbiter: `L <= I* <= U` on every cell → `results/validation.{md,json}`.

## 1. Objects

**Circuit.** A Verity IR program `P` (from `accumulation.algorithms.registry.build(name, cfg, wl)`), i.e. a
DAG of primitive gates. Every root parameter has a *role* (`BuiltProgram.roles`):
`fixed | accumulated | carried | token | seed`. `fixed` values are free everywhere. Everything else is
*non-fixed*.

**Operator graph** `g = accumulation.graph.extract(bp)` is an exact operator-granularity quotient of the
circuit (validated gate-for-gate by `accumulation.graph.validate.check_against_flat` on tiny configs).
`g.ops[i]` has `kind` (`matmul`, `rmsnorm`, `add`, ..., `prim:<name>`), `statics` (`M, N, K, CH` for matmuls:
`M` = rows of the activation operand per copy, `N` = rows of the weight operand per copy, `K` = contraction),
`copies`, `work_per_copy` (MAC-equivalents), `out` (tensor id), `inputs: list[Edge(src, leaves_per_copy, exact,
ranges)]` where `ranges` are merged bounding leaf intervals of the source read by one canonical instance of
the op (over-approximate). `g.share(t)` = max per-element consumer multiplicity derived from them.
`g.tensors[t]` has `kind` (`param|op`), `leaves`, `width` (bits), `role` (params), `producer`.
For a matmul the input edge order is **(A, B)**: `A` is the `M x K` operand (activations, or the incoming
gradient), `B` is the `N x K` operand (weights in forward/activation-gradient products; activations in weight
gradient products and attention). Element widths are 16 bit unless stated (`Tensor.width`).

**Replay unit (RU).** A part of a partition `Pi` of the gate set. `in(R)` = distinct non-fixed values entering
`R` (non-fixed root leaves read by gates of `R`, plus outputs of gates outside `R` read by gates inside `R`),
weighted by width in bytes. Outputs are free. `Up_R(gate)` = the gate plus everything reachable backwards from it
along wires that stay inside `R`. Legal for `(F, G, X)` iff for every `R`: `in(R) <= X`, `work(R) <= G`
(total work of the RU; `G = None` means no cap and recovers the `(F, X)` policy), and `work(Up_R(gate)) <= F`
for every gate. Work is the primitive `.work` (MAC-equivalents: `Mac16` = 1).

**Resource.** `I*(P; F, G, X) = min over legal Pi of sum_R in(R)` (bytes) -- the primary object (THEORY
§0.1). Everything reported is `I*` divided by tokens (`Workload.tokens`) or by `|ℳ|`. Every bound must take
`G` (`None` = unbounded): a certificate valid for `(F, X)` stays valid for `(F, G, X)` (fewer legal RUs), and
a partition legal for `(F, G, X)` is legal for `(F, X)`; `G` only ever *tightens* `L` and *raises* `U`.

**ADW (accumulation-dependent work).** `ADW(P)` = total work of ops that *depend on non-fixed state*:
an op contributes if any root parameter in the transitive closure of its inputs has role
`accumulated | carried` (activations downstream of an adapter count; the frozen base of a LoRA forward
*before* the first adapter does not). `ADW_matmul` restricts to `kind == 'matmul'`. Both are reported; the
bound family below charges matmuls only (other kinds contribute 0, which is sound).

## 2. Lower bound family (must be sound for every legal partition)

`L(P; F, X) = max(L_source, L_source_min + L_cap)` where

* `L_source` = bytes of every non-fixed root parameter that is read by at least one gate (each must enter at
  least one RU). Computed from `g` as the sum over param tensors with role != fixed that appear as an edge
  source. (`accumulated + carried` bytes = the state floor `P`; `token + seed` bytes are added too.)
* `L_cap = sum over matmul ops o of L_o(X)` where `L_o` is the **Loomis-Whitney import charge** of §2.1 with the
  operand cost model of §2.2. `L_source_min` = the part of `L_source` that is *not* already implied by the per-op
  charges (token/seed bytes; see `bounds/lower.py` for the exact non-double-counting rule -- when in doubt use
  `L = max(L_source, L_cap)`).

### 2.1 Per-op Loomis-Whitney charge

Fix a matmul op `o` (all copies) with `Q_o = M*copies` activation rows, `N` weight rows, contraction `K`,
operand byte costs `alpha` (per A element), `beta` (per B element) and partial-sum charge `gamma` from §2.2
(`gamma = theta_gamma * 4`; the MatmulT accumulator is 32-bit). For an RU `R` let `a, b, c` be the numbers of distinct
A elements, B elements and output (partial-sum) elements touched by gates of `o` inside `R`, and `w` the
MACs of `o` in `R`. Loomis-Whitney: `w <= sqrt(a*b*c)`. Charging rule (proved in `bounds/lower.py`):

    input attributable to o  >=  sum_R (alpha*a_R + beta*b_R + gamma*c_R) - gamma*Q_o*N

(each output element touched by `r` RUs forces `r-1` partial sums to be imported somewhere; the final sum is
not charged). Subject to `alpha*a_R + beta*b_R <= X` (by the validity condition of §2.2 the charges claimed
inside one RU total at most its imports `<= X`, whether the touched elements were imported or generated
there) and `sum_R w_R = Q_o*N*K`, the right-hand side is at least `Q_o*N*K * m_o - gamma*Q_o*N` with

    m_o = min over REALS a, b, c > 0,  alpha*a + beta*b <= X,  a <= Q_o*K,  b <= N*K,  c <= Q_o*N
          of (alpha*a + beta*b + gamma*c) / sqrt(a*b*c)

Substituting `a = a_rows*k, b = b_rows*k, c = a_rows*b_rows` (a bijection on positive reals) this is

    cost/MAC = alpha/b_rows + beta/a_rows + gamma/k      s.t.  k*(alpha*a_rows + beta*b_rows) <= X,
                                                              a_rows <= Q_o, b_rows <= N, k <= K   (reals)
    L_o = Q_o*N*K * (min cost/MAC - gamma/K)        (and L_o = 0 when alpha == beta == 0)

**The minimum must be taken over real-valued shapes** (closed form or a continuous optimiser), never over
integer tiles only: an RU's `(a, b, c)` need not be a rectangular integer tile, and restricting the
minimisation to integers can only *raise* `m_o`, which is the unsound direction. A fine integer grid may be
used as a *starting point* but the reported value must be a certified lower bound of the continuous minimum
(e.g. evaluate the KKT candidates / boundary faces analytically).

**Tightenings (v2.1, all sound; implement after the plain version passes the exact-solver sandwich):**

* *True weight width in the constraint.* When `B_o` is a runtime-input root parameter (accumulated /
  carried), its elements cannot be generated inside an RU: every touched element is imported at its full
  width `w_B` (2 bytes), and (§2.2) nothing is ever inherited from a weight's budget, so the `alpha` claims on
  A elements are paid entirely by *other* imported bytes. Hence the RU constraint may use
  `k*(alpha*a_rows + w_B*b_rows) <= X` (with `w_B`, not `beta`) while the objective keeps `beta = w_B/share`.
  This is typically a 4x tighter constraint on the weight side.
* *Fusion of ops sharing an A operand.* Ops `o_1..o_m` whose A operand is the same tensor over the same row
  range (e.g. the `Wq, Wk, Wv` projections of one layer, or `Wg, Wu`) may be treated as ONE matmul with
  `N = sum N_i` for the purpose of §2.1: the RU's gates form a subset of the fused index set, so
  Loomis-Whitney holds for the union. `share(A)` is then computed with the fused op counting as one consumer.
  Sound; removes the `1/share` division on the shared operand.
* *`theta` per tensor.* Choose `theta_t` (and `theta_gamma`) to maximise `L` (coordinate ascent from 0.5);
  any values in `[0, 1]` are sound.

When `alpha == 0` (A free) the optimum sends `a_rows -> Q_o` and the charge is `Q_o*N*K*(beta/Q_o + ...)`,
i.e. one load of the weights amortised over all rows -- do not special-case it, the formula does it.

### 2.2 Operand cost model (`alpha_eff`) -- v2 (closure-budget model)

**Why v1 was wrong.** v1 bounded the cost of *generating* an operand element inside an RU one producer at a
time, giving every producer along the chain its *own* budget `X` for its weight slice, and it bottomed out
at `0` because the chain ends at the free token input. But an RU has one budget: the weights needed along the
whole generation chain compete for the same `X`. Once the chain crosses one full transformer layer
(`>> X`), regeneration from free inputs is impossible and the element -- or some non-free ancestor of it --
must be *imported*. v1 therefore collapsed to `L = L_source` (state floor only, no growth with `Q`). v2 makes
the cumulative closure explicit. Notation: `w_t = width(t)/8` bytes per element; `theta in (0,1)` a split
factor (default `1/2`; may be optimised per tensor, see below); `rowlen(t)` = leaves per row of `t` (token
position for transformer activations; `M`-row for matmul outputs); `beta_p = w(B_p)` (full width, not shared)
whenever `beta` appears inside a *budget constraint* rather than a charge.

**Sharing.** `share(t) = g.share(t)` = the maximum, over elements of `t`, of the number of distinct ops that
read the element (`OpGraph.share`, from the per-edge leaf ranges the extractor records; it is an upper bound on
the true multiplicity, which is the safe direction). *Not* the consumer count: a stacked `Wq` for 32 layers has
128 consumers but every element is read by 4 ops. Every per-element charge is divided by `share(t)` so that an
element imported once and used by several ops in the same RU is charged at most once in total.

**Row closure `Wfree(t)`** = the set of `(non-free root param, leaf range)` pairs any RU must hold as input to
produce *one full row* of `t` from free (`fixed|token|seed`) inputs alone -- union semantics (a shared ancestor
counts once), `|Wfree|` its byte total. It is a *lower bound* on what such an RU needs (every listed item is
necessary), which is the safe direction for the "cannot generate" verdicts below:

* token/seed params, and tensors whose closure roots are all free: `Wfree = {}`.
* `t = out(p)`, `p` a matmul whose `B_p` is a non-free root param: `Wfree(A_p) U {(B_p, slice read by p)}`
  -- the **whole** slice, since one output row needs all `N_p` rows of `B_p`. If `B_p` is an activation:
  `Wfree(A_p) U Wfree(B_p)` (at least one row of `B_p` is needed).
* `t = out(p)`, `p` a gather from a non-free table (embedding): `{(table, one row)}`.
* element-wise / row-wise / scan producers: union over **all** inputs (row-aligned inputs contribute their
  row closure; broadcast non-free params such as norm gains contribute the slice read).
* reductions over rows, gathers/scatters of rows: union over inputs of their row closure.

**Element closure `Welt(t)`** = closure of *one element* of `t`: as `Wfree(t)` except that a matmul with a
non-free root `B_p` contributes only **one row** of `B_p` (`K_p * beta_p` bytes) on top of `Wfree(A_p)`;
element-wise producers use `Welt` of their row-aligned inputs; row-normalising producers (`rmsnorm, softmax,
lossgrad, mean/sum over the row`) use `Wfree` of their inputs. `Welt(t) <= Wfree(t)` always.

**`gen(t)`** := `|Welt(t)| <= X`. Then some RU can hold the entire closure of an element of `t` and make it
from free inputs, so no per-element charge is sound: `kappa(t) = alpha_eff(t) = 0`. This is where the free
token input enters, and it is the *only* place. (Consequence: layer-0 `Q/K/V/W1/W3` outputs of pretraining are
free -- one table row plus one weight row fit -- and repeated token ids need no special treatment: their
sharing of a table row only matters for tensors that are already free.) `F` is still ignored here; §2.3.

**Credit `kappa(t)`** (bytes of non-free input attributable to one element of `t` present in an RU, when
`gen(t)` is false). An element of `t` in `R` was either imported (`w_t` bytes) or produced by `p`'s gates in
`R` from operands present in `R`, which by `not gen(t)` rest on some imported non-free element. Each imported
byte is split: a fraction `theta_u` of an element's credit goes to the ops that read the element directly
(the `alpha`/`beta` charges of §2.1), the rest `(1 - theta_u)` is *inherited* by the elements generated from
it. Writing `inh(u) = (1 - theta_u) * kappa(u) / share(u)` for the credit one consumer of `u` inherits per
`u` element:

    kappa(t) = 0                                              if gen(t)
    kappa(t) = min(w_t, kappa_gen(t) [, (1 - theta_gamma) * gamma  for matmul outputs])   otherwise

with `kappa_gen(t)` by the kind of `t`'s producer `p`:

* matmul, `B_p` a non-free root param (contraction `K_p`): one output element needs a **full** `A_p` row
  (`K_p` elements) and one `B_p` row (`K_p * w_B` bytes of mandatory input at the weight's full width, since
  root-parameter rows cannot be generated). An RU holding `b_p` rows of `B_p` has `b_p * K_p * w_B <= X`, so
  one `A_p` row yields at most `X / (K_p * w_B)` complete output elements:
  `kappa_gen = inh(A_p) * K_p^2 * w_B / X`   (using `beta_p <= w_B` in place of `w_B` is also sound, weaker).
* matmul, `B_p` an activation (attention, weight gradients): one output element needs a full `A_p` row and a
  full `B_p` row; a row of `A_p` serves at most `N_p` outputs and a row of `B_p` at most `M_p`:
  `kappa_gen = K_p * (inh(A_p) / N_p + inh(B_p) / M_p)`.
* element-wise (`add, mul, swiglu, scale, gain, mask, perturb, combine, ...`): one output element needs one
  element of each row-aligned input: `kappa_gen = sum over row-aligned inputs of inh(in)` (broadcast inputs
  contribute 0).
* row ops (`rmsnorm, softmax, lossgrad, row sums/means`): one output element needs the full input row, whose
  credit is spread over the `rowlen(t)` outputs of that row: `kappa_gen = sum_in rowlen(in) * inh(in) / rowlen(t)`.
* reductions over rows (`colsum, sum, mean` over tokens): at least one input element per output:
  `kappa_gen = inh(in)`.
* gathers / scatters / routing (`embed`, `gather rows`, `scatter add`, `topk`): `0` unless the map is known to
  be injective on elements (MoE dispatch feeds each token row to `TOPK` slots: `inh(in) / TOPK` is sound; the
  embedding gather is not injective).
* `scan:*` and unknown kinds: `0`.
* The optional third term handles elements of a matmul output that exist in `R` as the *completed sum of
  imported partials*: they carry `>= (r-1) * gamma >= gamma` bytes of partial-sum imports, of which §2.1
  claims `theta_gamma * gamma`; the rest is credit. Choose `theta_gamma in [1/2, 3/4]` per op (both sound;
  larger `theta_gamma` strengthens the partial term and weakens `kappa`).

**Charges used in §2.1.**

    alpha (A operand)                     = theta_A * kappa(A) / share(A)         (0 if gen(A))
    beta  (B a non-free root param)       = theta_B * w_B / share(B)              (default theta_B = 1: weights are
                                                                                    always imported and their credit is
                                                                                    claimed directly by their matmul
                                                                                    readers; see note below)
    beta  (B an activation)               = theta_B * kappa(B) / share(B)
    gamma (partial sums)                  = theta_gamma * 4

*Inheritance from root-param weights.* With `theta_W = 1` nothing is inherited from a weight and its matmul
readers claim all of it. A root param may instead take `theta_W < 1`, in which case `inh(W) = (1 - theta_W)
* w_W / share(W)` flows to the outputs of its **non-matmul** consumers exactly as for activations (each `W`
element is imported wherever it is read, so its budget is `w_W` in every RU that holds it). This matters
when the weights that matmuls actually read are *produced* tensors: ES (`W' = W + sigma * noise`, `perturb`),
local-SGD steps `>= 2` (`W' = W - lr * G`, `sgdupdate`), hidden adapters. With `theta_W = 1` those `W'` get
`kappa = 0` and the whole forward is uncharged; with `theta_W = 0` for a weight whose only matmul readers
are downstream of the elementwise op, `kappa(W') = min(w, w_W / share(W))`. Optimise `theta_W` per param
like any other `theta`. The §2.1 v2.1 "true weight width in the constraint" tightening applies only to
operands that are root params themselves (an RU can hold `W'` rows it generated from `W` rows, but it
must then hold the `W` rows: the constraint may use `w_W` for the *root* rows behind each `W'` row read).
That tightening rests on `alpha` claims being paid only by activation imports; it therefore requires that
credit inherited from a root-param weight never reaches a tensor used as an `A` operand (check: the
non-matmul consumers' outputs that inherit from `W` are read only as `B` operands; otherwise fall back to
`beta` in the constraint for those ops). (Note also that the `theta_B * w_B` form keeps `beta <= w_B`.)

`theta_t` may be chosen per tensor (grid over `(0,1)`; default `1/2`) -- soundness is per element of `t`:
direct claims total `<= theta_t * kappa(t)`, inherited claims total `<= (1 - theta_t) * kappa(t)` by
induction over the generation DAG, and `kappa(t) <= w_t` for imported elements. In dense models `kappa_gen`
exceeds `w_t` by a factor `~ (1-theta) * K^2 * beta / (X * share)` (6.7 at 8B, 27 at 70B for X = 5 MB), so
`kappa = w_t` and the optimum pushes `theta` up; for LoRA-like chains it stays near `1/2`.

The recursion is well-founded (it follows producer edges of a DAG) and memoised per tensor; `Wfree/Welt` are
sets of `(tensor id, lo, hi)` (use `Edge.ranges`), memoised per tensor.

**Sanity expectations** (8B, `X = 5 MB`, `Q = seq = 4096`): every activation from layer-0 `Wo` onward has
`|Welt| >> X` and `kappa = w_t = 2`; `alpha ~ 1 / share`, `beta = 2 / share_elem(W)`, giving
`cost/MAC ~ 8 * sqrt(alpha * beta / X) ~ 2e-3 .. 7e-3 B/MAC`, i.e. `L/token` of order tens of MB (vs the state
floor `16 GB / Q = 4 MB/token`) and within a small factor of the constructive `U = 218 MB/token`. Layer-0's
first projections are the only matmuls charged 0. If `L` still equals `L_source`, the model is mis-implemented.

Everything above holds for **any** legal partition, including ones that recompute values, because
Loomis-Whitney counts distinct elements touched per RU and the charges are per RU.

### 2.3 F term (optional, add only if certified)

Rows of a tensor whose *own* generation work from free inputs exceeds `F` (e.g. late positions of a long
sequence under causal attention on fixed weights: the prefix must be recomputed inside the RU) cannot be
generated inside any RU and must be imported: for those rows `alpha_eff = width/8` regardless of `gen(t)`.
Per-row generation work must be computed per row (position `i` needs the work of positions `<= i` in every
earlier layer), never as an average -- a wrong "must import" verdict would make the bound unsound, a wrong
"can generate" verdict only weakens it.

## 3. Upper bound (constructive)

`U(P; F, G, X)` = the input cost of an explicit legal partition. `bounds/upper.py` builds one from rectangular
tiles per op (the same `(a_rows, b_rows, k)` family, with the *actual* import cost: A tile rows at their real
width, B tile rows, partial-sum reduction RUs), verifies `in(R) <= X`, the `F` constraint and `work(R) <= G`
at tile granularity (`check_plan` re-derives every unit), and sums. Reduction row ops whose one row exceeds `X`
(`colsum` over `Q` at large `Q`) are split into 32-bit partial sums plus a reduce unit (recompute=True only). `U` must be >= `L` on every graph; on tiny graphs both bracket the exact `I*`.

**Adversary freedom (headline reading).** The adversary may evaluate any circuit *equivalent* to `P`
(recompute values, split reductions into free 32-bit partial outputs plus separate reduction RUs,
regenerate free-closure operands in place). Headline `U` numbers use `recompute=True`; `recompute=False`
(a literal partition of `P`'s gates, chain reductions only) is reported alongside and is the object the exact
solver of §4 matches. `L` is sound for both readings.

## 4. Exact reference (`accumulation/exact`)

For micro circuits (<= ~40 gates) `I*` is computed exactly by an integer program over gate->RU assignments
(scipy HiGHS `milp`) with the literal definition of §1 (per-RU input `<= X`, `Up` work `<= F`, total RU work
`<= G` when given). Used only to
test soundness (`L <= I*`) and tightness (`I* <= U`) of the bounds on the flattened Verity circuits.

## 5. Module contracts

    accumulation.bounds.lower.lower_bound(g: OpGraph, roles_ok, F: int, X: int, *, G: int | None = None, adw=None) -> LowerBound
        LowerBound: dataclass(total: int, source: int, cap: int, per_op: dict[op_id, int], alpha_eff: dict[tid, float],
                              notes: list[str], worst_ru: dict)   # worst_ru: THEORY §0.1 diagnostic (see below)
    accumulation.bounds.upper.upper_bound(g: OpGraph, F: int, X: int, *, G: int | None = None, ...) -> UpperBound
        UpperBound: dataclass(total: int, n_units: int, per_op: dict[op_id, int], plan: Plan, notes: list[str],
                              by_kind, by_class);  Plan.ru_stats() -> {n_ru, input_mean, input_max, work_mean, work_max, up_max}
    accumulation.bounds.upper.check_plan(plan, g, F, X, G=None)   # re-derives every unit; asserts X, F and G legality
    accumulation.bounds.adw.adw(g: OpGraph) -> ADW
        ADW: dataclass(total, matmul, matmul_macs, all_work, all_macs, credited_macs, recompute_macs, by_kind, per_op)
    accumulation.exact.solve.exact_min_input(program, roles, F, X, G=None, limit=40) -> ExactResult(total, assignment)

All byte quantities are `int`. `F` and `G` are in MAC-equivalents, `X` in bytes. `G=None` = no total-work cap.

`worst_ru` (lower bound): the legal RU (or real-valued tile shape) that attains the minimum exposure per
target MAC among the constraints that bind the certificate: `{op_id, kind/class, shape (a, b, k), input_bytes,
work, up_work, target_macs, bytes_per_mac, operands: [(tid, name, role, bytes)], binding: "X" | "G" | "F"}`.

## 6. Reporting units and the deliverable tables

Target work `M(C)`: `credited_macs` for training circuits (distinct target products, recompute excluded);
`all_macs` for inference circuits (fixed-weight products are the useful work there). `kappa = M / I` MAC per
runtime-input byte. Both sides of any `rho` are computed at the same `(F, G, X)` and model.

* **Main circuit table** (one policy point): model | circuit | `M`/token | `L` MB/token | `U` MB/token |
  `U/L` | `kappa_low = M/U` | `kappa_high = M/L` | `n_RU`/token | mean, max RU work | mean RU input.
  Circuits: inference prefill, inference decode (when in the registry), full-parameter training; dense
  1B/8B/70B/405B and MoE Mixtral / DeepSeek-V3 / Qwen3-235B-A22B. Inference gets `L` too (is `U_inf` near
  optimal?).
* **Derived security table** (matched training/inference pairs): inference exposure `U_inf` | `L_train` |
  `U_train` | `rho_cert = (M_tr/L_tr)/(M_inf/U_inf)` | penalty `1/rho_cert` | `rho_ach = (M_tr/U_tr)/(M_inf/U_inf)`.
* **Policy frontier** (8B first, `X = 5 MB`): sweep `(F, G)`; per point the main-table columns for inference and
  training plus `rho_cert`, `1/rho_cert`; the Pareto frontier of honest inference cost (`U_inf`/token, `n_RU`)
  against `1/rho_cert`; pick permissive / balanced / aggressive operating points and run the scale table at
  exactly those. Then sweep `X`.
* **`Q` scaling**: fit `L(Q) = P_L + r_L Q` and `U(Q) = P_U + r_U Q` per circuit and operating point; report
  `P_L, r_L, P_U, r_U` (bytes and bytes/token). `r` is the anti-amortisation result.
* **Validation table** (exact solver): tiny circuit | `I*` | `L` | `U` | `L/I*` | `U/I*` across dense
  inference/training, several `(F, G, X)`, sharing-heavy and torture cases; fuzz aggregate: `0/N` soundness
  violations, median and 5th-percentile `L/I*`. Plus the `worst_ru` of every headline certificate.
* Always also report `ADW`, `ADW_matmul`, `P` (state floor), `L_source`, token count, and whether `U` used
  `recompute=True`.
