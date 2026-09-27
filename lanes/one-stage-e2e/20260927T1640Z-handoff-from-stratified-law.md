---
cursor:
  subagentId: "bc-56dd97f5-e901-548a-8596-4dfb56e409da"
lane: one-stage-e2e
kind: handoff
from: stratified-law
created: 2026-09-27T16:40Z
---

# stratified-law → one-stage-e2e: rerun A4 P6 under the stratified law (one draw per template at least), on your existing served files

Daniel adopted stratified sampling as the default law (Sep 27): one stratum per template, and inside each a uniform draw without replacement of $k_s = \max(1, \mathrm{round}(k\,n_s/n))$ units. That answers your open question from P6: every template is now exercised in every audit. **Please rerun A4 P6 under `stratified:1024`** on serving's existing P6 files (small files `art:df875b6a…`, member files `art:d2e35dd9…`; registration `0d1f8f84…`, partition `631d88f8…`). The root asked me to hand this to you once the pieces were in. They now are, on open PRs.

## The pieces, all open

| PR | What | State |
|---|---|---|
| [#161](https://github.com/danielreuter/verity/pull/161) | core `verity.proofs.profile.Stratified` (exact `count_bound`, `stratum_bound`) | ready for review; `check` passed on `5412c9cb` |
| [#164](https://github.com/danielreuter/verity/pull/164) | `verity_one_stage`: `draw.parse_law("stratified:K")`, `draw.derive`, stratified `check_draw`, R1 on the expanded law, `audit.wrong_units` from `count_bound` with `per_template` | stacked on #161; `check` running on `d7ab2767` |
| [#167](https://github.com/danielreuter/verity/pull/167) (flock-verifier) | Lean sampler of record: `flock-verify draw --program P --partition Q --stratified K`, and `draw-test` with U2 for stratified draws | open |
| [#165](https://github.com/danielreuter/verity/pull/165) (audit-lean) | `Law.stratified`, `stratified_escape`, the floor lemma | open; not needed to run |

The encoding (strata, $k_s$, the law and draw objects) is in #164's `protocols/one_stage/PROTOCOL.md`, "The stratified law". #167's `stratified_agree.py` checked it against #164 on A4's shape.

## What changes in `a4.py` (#143)

1. **The law.** `law = D.derive(program, query, D.parse_law("stratified:1024"))`, over the verifier's own P6 program and `Q_template_instances` query. Pass the same `law` to `R.record`, `R.check`, `D.check_draw` and `audit.audit_record`. It must be the expanded law: `check_draw` refuses the bare rule.

   Expected strata, in canonical order:

   | Template | Units | $k_s$ |
   |---|---|---|
   | RMSNorm Triton | `[0, 287)` | 1 |
   | GEMM K = 2048 | `[287, 6171935)` | 933 |
   | RoPE | `[6171935, 6183415)` | 2 |
   | RMSNorm fused | `[6183415, 6183702)` | 1 |
   | SiLU·mul | `[6183702, 6183989)` | 1 |
   | GEMM K = 8192 | `[6183989, 6771765)` | 89 |

   That is 1,027 units drawn.
2. **The registration: a re-audit of P6's commitment, not a new one.**
   - The new record must carry P6's roots, domains, scheme and leaf layer unchanged. Assert that they equal P6's record.
   - Set `previous` to P6's registration digest, and pass P6's record as `log` to `R.check`.
   - R6 refuses an identical `window`, so make it P6's window plus `"reaudit": "stratified-floor-1"`.
   - This is sound: the committed transcript has been fixed since P6's registration and the roots don't change. A fresh draw from the verifier's own randomness is independent of the wrong units, as the first was. `docs/audit-protocols.md` §2.8 covers re-auditing one registration.
3. **The draw.**
   - Use #167's `flock-verify draw --program P --partition Q --stratified 1024`, with `--program` and `--partition` set to the verifier's copies as in your `verify` calls. It prints `DRAW {law, population, k, strata, units}`.
   - Hold the draw with `D.check_draw(union_draw, rec, law)` and with Lean `draw-test` on the same flags.
   - **Fallback**, if you can't build #167: one existing `flock-verify draw --population n_s --k k_s` per template, each local index $j$ mapped to `lo + j` of its stratum, then the union sorted, with the `strata` list copied from `law`. It's the same law: independent uniform subsets per stratum from the verifier's own randomness. Record which path you used.
4. **Members: no change.** Your loop already serves each member `subset:len(local)` in its own indices, which is exactly its stratum's $k_s$-subset. All six members now get a session; P6 had four.
5. **The record.** `audit.audit_record` gives:
   - `wrong_units.bound = 91063`, which is fixed by the law, not the draw;
   - `wrong_units.per_template`, with 286 for each 287-unit template;
   - a core `profile` with `law: stratified` and the count drawn per stratum.

   In the summary, replace `expected_draws` with each member's $k_s$.
6. **New negatives**, beside your nine:
   - R1: the registered law with one stratum's `k` changed (`R1-law`);
   - the union draw with one GEMM K = 2048 unit swapped for a second RMSNorm Triton unit (`strata-count`), refused by `check_draw` and by Lean `draw-test`;
   - a stratum's `k` written as `true` (`law`, `strata`).

## Cost and expected result

- **Pod.** P6's attempt 3 ran 22.6 min on a cpu5m (32 vCPU, 256 GB, $2.08/h) and peaked at 86.6 GB. The rerun draws 933 K = 2048 units against P6's 923, so memory is the same. It adds two small-template sessions, RMSNorm Triton and fused: in P6 the one SiLU·mul unit took 327 s to prove and 297 s for Lean `verify`.
- **Estimate:** about 35–45 min wall on the same pod class, about **$1.5**, within your cap ($7.3 of $40 spent). The root asked for an estimate before any pod; this is it.
- **Expected:** accepted and complete, with 18 verdicts (6 members × M0, Lean U1–U3 and Lean `verify`), served shares equal to the Lean draw, at most 91,063 of 6,771,765 wrong at $2^{-20}$, and every template exercised.

Reply to `internal/lanes/stratified-law/`, and to the root when it's preserved.
