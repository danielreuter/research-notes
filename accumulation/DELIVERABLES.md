# Deliverables: the two tables every agent fills

Every row below estimates the same object, `I*(C; F, G)` = the minimum total runtime input over all legal RU
partitions of a fixed circuit `C` (SPEC.md §0), sandwiched by a certified lower bound `L` and a checked
partition `U`:

~~~
L  <=  I*  <=  U            (bytes, whole circuit)
~~~

Nothing goes into a table unless it carries `L/Q`, `U/Q`, `U/L`, `c_L`, `c_U`, the certified penalty and the
achieved-attack penalty (or an explicit `[ ]` / `pod` / `analytic` status). Do not broaden the algorithm set
until every available row reports these objects.

## 0. Definitions (fixed; do not redefine per table)

- `Q` = useful token positions processed by the circuit (training: `K * Q_step`; rollout / inference: tokens).
- `M/Q` = useful MACs per token (credited products; recompute excluded; step 0 of a training chain excluded).
- Runtime-input cost per useful MAC: `c_L = (L/Q) / (M/Q)`, `c_U = (U/Q) / (M/Q)`.
- Reference: the demonstrated fixed-weight inference implementation, one RU per session, `4 B/token`
  (V32 token ids; 2 B/token if 17-bit ids are argued -- 4 B is the conservative choice):
  `c_inf = 4 B / (M_inf/Q)`.
- **Certified penalty** `= c_L / c_inf` (how much less useful work per runtime byte the *best possible* legal
  partition of `C` can do, relative to honest inference). **Achieved-attack penalty** `= c_U / c_inf` (the best
  partition we actually found). Certified <= true <= achieved.
- For dynamic rollout (same forward graph as inference, weights dynamic) `M/Q` is identical to inference, so
  the penalty is simply `(L/Q) / 4 B` and `(U/Q) / 4 B`.
- Steady state for multi-step training: marginal `b = (I(K) - I(K-1)) / Q_step`, reported for `L` and `U`;
  also the fit `I(K) = I_0 + r K` over the K sweep, with `r_L`, `r_U` in bytes per training token.
- Default policy point: `F_hat = 1.5`, `G_hat = 4`, `Q_inf = 8192`, `F = F_hat * fwd(Q_inf)`,
  `G = G_hat * fwd(Q_inf)` with `fwd` = checker `Work` of `inference-dense` at `Q_inf`.
- Units: bytes/token in B / KB / MB / GB (decimal); always give the ratio to inference next to any byte figure.

## 1. Table 1: headline security results

Policy point: default unless stated. Status is one of `measured` (checked U / certified L from the checker),
`pod` (queued on the pod), `analytic` (closed form only; never quoted as a result), `[ ]` (not run).

| Model | Workload | Useful MAC/token | L/Q | U/Q | U/L | Certified penalty | Best-attack penalty | Status |
|---|---|---|---|---|---|---|---|---|
| 1B | fixed-weight inference (session) | 1.77e9 | -- | 4 B/tok | -- | reference | reference | measured |
| 8B | fixed-weight inference (session) | 9.65e9 | -- | 4 B/tok | -- | reference | reference | measured |
| 70B | fixed-weight inference (session) | 8.02e10 | -- | 4 B/tok | -- | reference | reference | measured |
| 405B | fixed-weight inference (session) | 4.38e11 | -- | 4 B/tok | -- | reference | reference | [ ] |
| 1B | dynamic rollout generation (steady, Q_roll -> 1M) | = inference | [ ] | [ ] | [ ] | [ ]x | [ ]x | pod |
| 8B | dynamic rollout generation (steady) | = inference | [ ] | [ ] | [ ] | [ ]x | [ ]x | pod |
| 70B | dynamic rollout generation (steady) | = inference | [ ] | [ ] | [ ] | [ ]x | [ ]x | pod |
| 405B | dynamic rollout generation (steady) | = inference | [ ] | [ ] | [ ] | [ ]x | [ ]x | pod |
| 1B | full pretraining, steady state (K marginal) | ~3.1x inf | [ ] | [ ] | [ ] | [ ]x | [ ]x | measured U |
| 8B | full pretraining, steady state | ~3.1x inf | **[critical]** | 0.5-0.6 MB/tok | [ ] | [ ]x | ~45,000x | measured U |
| 70B | full pretraining, steady state | ~3.1x inf | [ ] | [ ] | [ ] | [ ]x | [ ]x | pod |
| 405B | full pretraining, steady state | ~3.1x inf | [ ] | [ ] | [ ] | [ ]x | [ ]x | pod |
| MoE (Mixtral / Qwen3-MoE / DeepSeek-V3) | pretraining (single step) | -- | [ ] | [ ] | [ ] | [ ]x | [ ]x | pod |

Dynamic rollout generation is the `forward-nonfixed` circuit: the inference forward graph with the weights
as dynamic (accumulated) values instead of members of the fixed baseline. Same useful forward work, fixed vs
dynamic weights -- no backward pass, no 3.1x normalisation. Report the steady value (largest `Q_roll`) here and
the whole `Q_roll` curve in Table 2.

Inference rows: also report the prefill-only circuit (`inference-dense`) alongside `inference-session`, and the
one-RU sanity (`Work <= G`, `max Up <= F`) at every `(Q_inf, F_hat, G_hat)` used anywhere in Table 2.

## 2. Table 2: adversarial sweep / mechanism table

Both `L` and `U` at every point (8B, default point, one axis varied), plus the fitted exponent where the axis
is continuous. Bold rows are mandatory before anything else is broadened.

| Sweep | Values | Report | Security question | Expected signature |
|---|---|---|---|---|
| **Sequential training steps K** | 1, 2, 4, 8, 12, 16, 24, 32, 48, 96 (Q_step = 8192; 2-8 at 32768) | marginal L/Q, U/Q; fit r_L, r_U | Can accumulated state be amortised over arbitrarily many updates? | knee at K ~ 8-12, then a positive constant slope |
| **Rollout volume Q_roll** | 8K, 32K, 128K, 1M (1B / 8B / 70B / 405B) | L/Q, U/Q for forward-nonfixed | Can one dynamic model be amortised over arbitrarily many rollouts? | weight-loading transient (P/Q), then a positive steady floor |
| **Training batch Q_step** | 8K, 32K, 131K, 524K, 1M, 4M (G_hat in {1, 10, 100, 1000}) | steady L/Q, U/Q | Does giant-batch training kill the result? | no collapse; possibly worsening once partial-gradient cuts dominate |
| **Allowed inference context Q_inf** | 2K, 8K, 32K, 128K | inference U/Q; training and rollout L/Q, U/Q | How much security is lost by permitting longer chats? | inference stays 4 B/tok; dynamic cost falls as a power law (~Q_inf^-1/2 predicted) |
| **F_hat** | 1, 1.5, 3, 10, 30, 100, 300, 1000 | L/Q, U/Q | How permissive can ancestral work be? | main security knob; identify exponent / knees |
| G_hat | 1, 3, 4, 10, 30, 100, 1000 | L/Q, U/Q | Does parallel branching / batching defeat us? | flat once G exceeds the F-limited block size (measured: U identical for G_hat 4..1000) |
| Model width d | syn-* family + 1B / 8B / 70B / 405B | L/Q, U/Q, fitted exponent | Does security strengthen with scale? | strong positive width scaling (measured U ~ d^1.1 at fixed P) |
| Depth L | syn-deep | L/Q, U/Q | Is depth important? | weak |
| Heads / GQA / FFN ratio | syn-attn, syn-manyheads, syn-ffn | L/Q, U/Q | Do architecture details change the mechanism? | weak vs width |
| Optional local input cap X | inf, 100 MB, 20 MB, 5 MB, 1 MB | L/Q, U/Q | Extra wedge from forcing tier-2 matmul sharding? | potentially very large; keep separate from the core F, G result |

### 2b. Policy table (derived from the Q_inf and F_hat rows)

| Allowed session Q_inf | Inference U/Q | Certified rollout penalty | Certified pretraining penalty | Achieved rollout | Achieved pretraining |
|---|---|---|---|---|---|
| 2K | 4 B/tok | [ ] | [ ] | [ ] | [ ] |
| 8K | 4 B/tok | [ ] | [ ] | [ ] | [ ] |
| 32K | 4 B/tok | [ ] | [ ] | [ ] | [ ] |
| 128K | 4 B/tok | [ ] | [ ] | [ ] | [ ] |

## 3. The seven questions the tables must answer (priority order)

1. **Is the lower bound tight?** 8B default point: `L/Q` vs `U/Q = 0.5-0.6 MB/tok`. Decides whether the result
   is 40,000x, 4,000x, 400x or 40x. Everything else is secondary until this lands.
2. **Does the steady-state slope stay positive?** `U(K) = U_0 + r_U K` and `L(K) >= L_0 + r_L K`; report
   `r_L, r_U` in bytes per training token. `r_L > 0` is the direct anti-amortisation result.
3. **Can huge batches evade F?** `Q_step = 131K, 524K, 1M, 4M`: `b_train(Q_step)` must not fall toward 0.
4. **Dynamic rollout generation.** Same forward graph, fixed vs dynamic weights, swept in `Q_roll`, all four
   dense models. Probably the cleanest headline statement in the project.
5. **Does width strengthen the result as predicted?** Real-model rows 1B / 8B / 70B / 405B.
6. **Sensitivity to the inference-service policy.** Table 2b.
7. **Is G unnecessary?** If `L` agrees with `U` that `G_hat = 4..1000` are identical: once `G` admits the
   desired parallel inference workload, security is governed by `F` alone.

## 4. Validation panel (mandatory in every report)

Exact micro-solver (`X = inf`, multi-step `local-sgd` tiny circuits + torture cases), `lower_coarse` and
`upper_coarse` on the same cells:

- `N` cells solved exactly; `0` soundness violations for `U` (`U < I*` never) and for `L` (`L > I*` never) --
  any nonzero count blocks the report.
- distribution of `U/I*` (median, max) and `L/I*` (median, 10th percentile, minimum).
- for the worst `L/I*` cells: the exact optimal partition (the attack the certificate is missing).

Current: 264 micro cells red-teamed; 0 upper-bound violations; `U = I*` in 132/155 exactly solved cells;
worst `U/I* = 2.4`. `L/I*` pending `lower_coarse`.

## 5. Worst-RU diagnostic (for every headline L)

For each headline lower bound emit the most constraining legal RU / cut the certificate found: total work,
max `Up`, input bytes by class (tokens / weights / activations / gradients / partial dW), credited MACs, MAC per
input byte, which ops it contains, which runtime values enter. When `L` is disappointing this says whether we
found a real attack or a loose certificate.

## 6. Where the numbers live

- rows: `accumulation/results/coarse.jsonl` (one row per `(model, circuit, Q_inf, F_hat, G_hat, Q_step, K, seq)`;
  fields `U`, `U_per_token`, `U_by_class`, `U_n_ru`, `L`, `L_per_token`, `L_by_class`, `L_worst_ru`, `credited_macs`,
  `fwd_units`, `P`, `token_bytes`, `status`, `stage_versions`). Pod rows merge in via `pod.py pull`.
- tables: `accumulation/results/TABLE1.md`, `TABLE2.md` (generated by `sweeps/final_report.py`; never hand-edited).
- figures A-E: `accumulation/results/plots/`.
- validation: `accumulation/results/validation*.{json,md}` (red team).
- report: `accumulation/results/REPORT.md`, structured after `REWRITE_OUTLINE.md`.
