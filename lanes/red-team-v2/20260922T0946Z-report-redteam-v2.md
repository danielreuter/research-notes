---
id: r20-proof/red-team-v2/20260922T0946Z-report-redteam-v2
campaign: r20-proof
lane: red-team-v2
kind: report
status: closed
repo: verity-main@f96fc53
origin: verity-main@f96fc53:backends/numerical/reports/redteam_v2.md
---

# red-team-v2 — adversary report against the checker-v2 provers

Lane `red-team-v2`, pod `vy-cpu2`, `main`=4ddb170. Targets: **A** = `verity-gkr run-vu --variant v2` (Goldilocks
GKR); **B** = `direct-unit --v2` (Plonky3 LogUp AIR, BabyBear). Every verdict below is from the **real verifier
binary** on the pod (runs cited), not from a re-implementation. z3 is used for the gadget-level claims.

## Attack table (target · class · verdict)

| # | id | target | class | verdict | note |
|---|----|--------|-------|---------|------|
| 1 | one-column zero | A | 6 | **REJECTED** | `depth2 phase-1 round 0 sum mismatch`; `one` is effectively pinned |
| 2 | unit-0 non-initial state | A | 3 | **REJECTED** | chain init link (col 2) |
| 3 | epilogue reads non-final unit | A | 3 | **REJECTED** | epilogue input (col 1) ≠ last unit |
| 4 | ovf flip into epilogue | A | 3 | **REJECTED** | epilogue input (col 5) ≠ last unit |
| 5 | swapped VU epilogues (B=2) | A | 3 | **REJECTED** | epilogue input (col 1) ≠ last unit |
| 6 | B=1 wrong public word | A | 6 | **REJECTED** | output word ≠ public word |
| 7 | B=1 honest (control) | A | 3 | **ACCEPTED** | positive control |
| 8 | honest B=2 (control) | A | – | **ACCEPTED** | positive control |
| 9 | **chain.txt stripped** | A | 3 | **ACCEPTED (forgery)** | epilogue reads unit-0 state; word=cast(unit-0); see URGENT |
| 10 | zero_swap −0 vs +0 | B | 5 | **VACUOUS confirmed** | 0/6000 divergences + all-zero corner |
| 11 | shipped negatives + battery | B | 1–6 | **REJECTED (all)** | 52/52 vu-neg; battery all classes; extras 6/6 |

The single accepted forgery (#9) is reported in `note:r20-proof/red-team-v2/20260922T0958Z-finding-redteam-v2-urgent` and ledgered. It is a **verifier-API /
deployment trust-boundary** break, not a break of the GKR sumcheck or the checker-v2 arithmetization: `load_vu` reads
the state/`ovf`/`sgn` links and `steps`/`B` from the **untrusted proof bundle** (`chain.txt` + witness header); only
the public-word link `epi_y16 == public_y16` is hardcoded. Ship an empty `chain.txt` and the epilogue may read any
unit's state while the published word (which the attacker sets equal to `epi.y16`) still satisfies the hardcoded link.
Owning lane a-gkr / a-verifier; fix = verifier-owned linkage (as already done for `epi_y16`) or transcript-absorb +
equality-assert the spec.

Cases 2–6 confirm that **when the chain spec is honest**, the v2 linkage is sound: initial state, per-unit state
carry, `ovf`-forced-zero-on-non-final, and public-word binding all reject their respective forgeries with precise
errors. Case 1 shows the implicit constant-1 column cannot be zeroed: the depth-1 input-wire gate multiplies every
column by the one-wire, so `one=0` zeroes all wires (collapsing the lookups) and the committed wire table
(literal constants) contradicts the one-wire arithmetization the sumcheck checks.

## z3 verdicts (gadget level)

- **Shipped, re-confirmed as the reference envelope:** B v2 AIR `notes-asset:campaigns/r20-proof/assets/b-air-v2/reports/b_air_v2_z3.json` 7/7 UNSAT over Z and wrap-free
  BabyBear; checker-v2 `note:r20-proof/checker-min/20260922T0727Z-report-checker-min` 10/10 UNSAT over Z and Goldilocks. These cover the 15 hints, the chunked
  shift / floor-lemma relation, product-form `attained`, `normalise_chunked`, `state_decode`/`epilogue` limb splits.
- **red-team-v2 additions:** the two gadget-level holes I conjectured — an unranged one-column constant (A) and a
  sign-of-zero divergence (B) — are **not** SAT. The one-column is pinned by the wire/one-wire consistency (empirical,
  case 1); the sign-of-zero is masked by `z` (empirical scan, case 10; the reference gives identical words for ±0
  across 6000 units and the all-zero corner). No new gadget SAT was found. Hint ranges (`E`, `l`, `koff`, `v0`,
  `dsp`) are each bound by a lookup key column or an identity that the shipped z3 already proves UNSAT to violate.

## Open items / not done

1. **A chain spec is caller-supplied** (#9). The principled fix is verifier-owned linkage; a one-line harness guard
   (`assert!(!limbs.is_empty() && limbs == expected)`) would close the demonstrated instance. Reported, not fixed.
2. **B operands unbound without `--bind-operands`.** The v2 gate binds the statement = claimed words (verified: a
   `words[0]^=1` statement is rejected), but operands are only bound with `--bind-operands`. By-design per the brief
   (the words are the statement); any tie to externally committed operands needs `--bind-operands`. Label accordingly.
3. **Not exercised on the real A binary this run:** implicit-table (`itable`) out-of-range materialisation (class 4)
   and the a-logup-union tag/γ cross-table query (the union Rust had not landed). Left as follow-ups.

## Fixtures

`fixtures/redteam-v2/gkr/` (generator `python -m verity_numerical.redteam.v2_forge gkr-chain --out …`) with a
`manifest.json` recording expected accept/reject; loader test `backends/numerical/python/tests/test_redteam_v2_fixtures.py`.
The zero_swap scan is `python -m verity_numerical.redteam.v2_forge zero-swap`.
