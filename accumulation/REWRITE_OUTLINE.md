# Rewrite outline: "Training security from bounded accumulation"

Proposed structure for the section, mapped onto what is proved / measured / assumed in this package
(`THEORY.md` for statements and proofs, `results/RESULTS.md` for numbers). Numbers in `[...]` are to be
filled from RESULTS.md once the v2 bound has passed the exact-solver red team; the ones given are current.

## 1. Training requires accumulation-dependent work

* Keep the opening framing: training differs from inference because useful work repeatedly depends on state
  produced earlier in the same computation. Replace "tensor" by "value"/"array of values"; use `A` for
  activations, `W` for the accumulated weight array, `ℳ` for the target scalar products of `WA`, `Up(.)` for
  backward closure.
* Define the resource concretely (THEORY §0): the circuit `C` is fixed with all exogenous inputs `theta`;
  `ℳ(C)` = distinct target products performed; efficiency `eta(C) = |ℳ(C)| / Work(C)`. Say explicitly that
  this credits a computational resource, not learning progress, and that recomputation earns nothing.
* One paragraph of measurement (THEORY §1): across ten training circuits the accumulation-dependent fraction of
  work is 99.7-100%; per token `|ℳ|` is `2.6e10` MAC at 8B pretraining, `1.9e10` for LoRA r=16, `4.2e10` for
  Mixtral MoE pretraining; the accumulated state spans `208 KB` (LoRA r=1) to `1.3 TB` (DeepSeek-V3). Point:
  "training" spans five orders of magnitude in state per unit of accumulation-dependent work, so a policy that
  only prices *state* cannot be uniform.

## 2. The simple bound and why it is not enough

* Keep the running example (1T model, 500 GB state, `X = 5 MB`, `1e7` RUs/day → 100 weight states/day →
  19.2x stretch), but present it as **Proposition 2.1 (state floor)**: `I*(C) >= P`. Then state its failure
  plainly: the bound does not grow with the number of tokens `Q`, so processing `19.2 Q` tokens per state
  restores the original throughput. Formulate the central question as in the draft: how much
  accumulation-dependent work can one admitted unit of state support?
* Replace the informal "activations must cross RU boundaries" argument by the definition it needs:
  `kappa_F(S)`, the `F`-bounded reconstruction width of a set of values (THEORY §2), the one-RU lemma
  `kappa_F(S) <= I(R) <= X`, and the remark that individual reconstruction widths do not add (one 2-byte
  precursor can generate a million values) -- which is exactly why the bound has to be a *certificate over
  sets*, not a per-value charge.
* Make the target of the section explicit: a certified `I*(C(Q)) >= P + r Q` with `r` in bytes/token, and the
  matched-budget efficiency `eta_max` derived from it (THEORY §4).

## 3. Defending against amortisation: the certificate

* **Theorem 3.1 (validity of the closure-budget charges)** and **Corollary 3.2** (`L <= I*`), stated in the
  section as: every legal RU's imports pay for (i) the weight elements it touches, (ii) the activation elements
  it touches *or generates*, and (iii) the partial sums it receives; Loomis-Whitney then bounds the products one
  RU can perform per byte, and the charges are constructed so that no byte is claimed twice across ops or
  across generation. Give the closed form `cost/MAC >= 4 sqrt(alpha beta gamma / X) - gamma / K` (THEORY §3.1)
  and its meaning: per-MAC input cost falls only as `1/sqrt(X)`, independent of `Q`, so batch size cannot
  amortise it.
* Say what the certificate does **not** assume (tiling, recompute, where cuts are placed, data distribution),
  and what it does (THEORY §6, especially assumption 1: accumulated values enter at full width because the
  circuit has no compact precursor -- and the registration-channel caveat).
* Regimes (THEORY §5): dense training, where `|Welt| >> X` from the first layer's output projection onward;
  compact-state PEFT, where `X` provides no protection and only `F` can (state this honestly); MoE, where the
  per-MAC bound is if anything stronger and the state term is `E/TOPK` larger.
* Demote the activation-cut/layer-boundary theorem to one sentence: it is the special case of the certificate
  where the RU boundary coincides with a layer boundary; the certificate holds for arbitrary cuts.
* Red team the "50% fixed-weight matmuls" policy in a short box (THEORY §7): defeated by linearity
  (`x(W + Delta)^T`) at 2x overhead; correlates with the wrong quantity.

## 4. Empirical results

* Table A (Goal 1): per (algorithm, model): `P`, `|ℳ|/token`, `|ℳ|/P`, work fraction. [RESULTS.md, characterisation]
* Table B (sandwich at `X = 5 MB`, `F = 1e12`, 8B): `L(Q) = P + r_L Q`, `U(Q) = P + r_U Q`, `U/L`, exact
  `I*` on micro-instances (torture suite + fuzzer: `[N]` instances, `[0]` violations). [P1, redteam]
  Current: `U = 218 MB/token`, `L` v1 = state floor only (`4 MB/token` at `Q = 4096`); v2 `[TBD]`.
* Table C (security efficiency): `kappa_L(train)`, `kappa_U(train)`, `kappa_U(inference)`, and
  `eta_max = kappa_L(train)/kappa_U(inf)`, `eta_ach = kappa_U(train)/kappa_U(inf)` per (alg, model, X, F).
  [P3] Current at 8B: `kappa_U(inf) ~ 3.2e3`, `kappa_U(train) ~ 1.5e2` → `eta_ach ~ 0.05`; `eta_max` `[TBD]`.
* Scaling: `X in {0.5, 5, 50} MB`, `F in {1e11, 1e12, 1e13}`, 1B/8B/70B/405B, MoEs. [P2, after validation]
* Redo the running example with the certified `r`: with `B = 1e7 x 5 MB = 50 TB/day` of runtime input, the
  adversary's daily accumulation-dependent MACs are at most `kappa_L * B` = `[TBD]`, versus the inference the
  same budget supports, `kappa_U(inf) * B` = `[TBD]`. Present the ratio, not a comparison with HBM traffic.

## 5. What remains open (one paragraph, honest)

* Representation robustness: the theorem is for legal partitions of the declared circuit; an adversary may
  declare a different training circuit. The registry covers the standard families; PEFT shows the failure mode.
* The registration channel (assumption 1) must be priced by the protocol.
* Composition with sparse verification / partially incorrect execution is deferred.
* Empirical: `U/L` gap; causal attention; layer 0 excluded.
