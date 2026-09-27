---
cursor:
  subagentId: "bc-56dd97f5-e901-548a-8596-4dfb56e409da"
lane: flock-verifier
kind: handoff
from: stratified-law
created: 2026-09-27T15:50Z
---

# stratified-law → flock-verifier (and audit-lean): the stratified law's exact encoding, for your sampler and U2

Daniel adopted stratified sampling as the default law (Sep 27): strata per template, and a fixed-size uniform draw without replacement inside each, with $k_s = \max(1, \mathrm{round}(k\,n_s/n))$. I own the integration: core `Stratified` ([#161](https://github.com/danielreuter/verity/pull/161)), the registration's `law: stratified` checked in R1, and `verity_one_stage.draw` and the audit bound. The root asked you for the Lean sampler and its U2 checks. **This is the encoding I propose. Please confirm or amend by a reply in `internal/lanes/stratified-law/`.** The Python side is being written to it now, and I'll hold it there until 17:00Z (10 AM PT). The same text went to audit-lean. Background is in `docs/sampling-strategies.md`.

## 1. Strata, derived by each verifier from its own $C$ and $Q$

- Apply $Q$ to $C$. For each root node that computes units, take its template descriptor id, its first unit index `lo` and its unit count `c`, in canonical order. This is `verity_one_stage.partition.ranges`, and the same derivation your `--partition`/`--program` path already does for `Q_template_instances`.
- **There is one stratum per distinct template id.** Its units are the union of its nodes' `[lo, lo + c)`, written as ascending, disjoint, non-empty half-open ranges, with adjacent ranges merged.
- **Strata are ordered by their first unit.**
- This is defined for `Q_template_instance` v0 and `Q_template_instances` v0 only. Any other query refuses `stratified` until it defines its stratum key.

## 2. Sizes

Given $1 \le k \le n$: $n_s = \sum (hi - lo)$ and $n = \sum_s n_s$ (the population). Then, in integers, rounding half up:
$$k_s = \max\Big(1, \Big\lfloor \frac{2 k n_s + n}{2n} \Big\rfloor\Big)$$
- Always $1 \le k_s \le n_s$.
- The total drawn is $\sum_s k_s$, which can differ from $k$.

## 3. The law object

This is the registration's `law` and the integrity profile's `law`:

```json
{"law": "stratified", "k": 1024,
 "strata": [{"template": "{descriptor id}", "units": [[0, 287]], "k": 1}, ...]}
```

- R1 requires the registered law to equal the verifier's own derivation from $(C, Q, k)$.
- `parse_law("stratified:1024")` is the agreement's side.

## 4. The draw object (the union draw's `unit_draw`)

It carries the law's keys plus `population` and `units`:

```json
{"law": "stratified", "population": 6771765, "k": 1024, "strata": [...], "units": [ascending global indices]}
```

U2 for `stratified`:
- the keys are exactly `law, population, k, strata, units`;
- each stratum's keys are exactly `template, units, k`;
- the strata's ranges are ascending, disjoint and non-empty, and together they tile `[0, population)` exactly;
- template ids are distinct;
- each stratum's `k` is the rule's, from the draw's `k`, its $n_s$ and the population;
- `units` are ascending, distinct and inside the population;
- exactly $k_s$ of them fall inside each stratum's ranges.

## 5. The sampler of record (`flock-verify draw`)

- For each stratum, in order, run `subset k_s n_s` on **its own segment** of operating-system bytes. The segment is $2 k_s \cdot \mathrm{width}(n_s) + 64$ bytes, extended and rerun as `drawOS` does when it runs out.
- Map local index $j$ to the $j$-th unit of the stratum's ranges.
- The draw is the union, ascending.
- Suggested CLI: `flock-verify draw --program P --partition Q --stratified K`, which derives the strata itself. That's the strongest form, since the verifier never takes strata from anyone. `--law-file law.json`, checked against its own derivation, would also do. The draw prints `DRAW {json}` as now.

## 6. Per-member sessions: no change

In A4's shape, each template member serves its share of the union draw. Under stratification a member's share is exactly its stratum's uniform $k_s$-subset: `{"law": "subset", "population": n_s, "k": k_s, "units": [member-local]}`. So the member statements' U1–U3 checks don't change. The audit record keeps the union draw.

## 7. The abstract law (audit-lean's part)

`Law.stratified (σ : Fin n → Fin m) (k : Fin m → ℕ) (hk : ∀ s, k s ≤ (univ.filter (σ · = s)).card)`:
- $\Omega$ is the product over strata of the $k_s$-subsets of $\sigma^{-1}(s)$, and the draw is their union.
- The concrete law has $\sigma(u)$ = the stratum whose ranges hold $u$. Stratum order doesn't matter to the abstract law.
- **Statements:**
  - `stratified_escape`: $e(B) = \prod_s \binom{n_s - \lvert B \cap \sigma^{-1}(s) \rvert}{k_s} / \binom{n_s}{k_s}$;
  - `stratified_escape_floor`: $1 \le k_s$ and $\sigma^{-1}(s) \subseteq B$ imply $e(B) = 0$.
- The count bound is computed exactly in core (`Stratified.count_bound`), so Lean needs only the escape. Optionally, add a numbers theorem for A4's law below, in the style of `demo_count_590`.

## A4 P6 under the rule, $k = 1{,}024$ (for your tests)

| Stratum (canonical order) | units | $k_s$ |
|---|---|---|
| RMSNorm Triton | `[0, 287)` | 1 |
| GEMM K = 2048 | `[287, 6171935)` | 933 |
| RoPE | `[6171935, 6183415)` | 2 |
| RMSNorm fused | `[6183415, 6183702)` | 1 |
| SiLU·mul | `[6183702, 6183989)` | 1 |
| GEMM K = 8192 | `[6183989, 6771765)` | 89 |

- $\sum_s k_s = 1{,}027$.
- `count_bound` gives 45,686, 91,063 and 180,898 wrong units at $2^{-10}$, $2^{-20}$ and $2^{-40}$, against 45,679, 91,051 and 180,879 for `subset:1024`.
- Each 287-unit stratum's own bound at $2^{-20}$ is 286, and a wholly wrong template escapes with probability 0.
