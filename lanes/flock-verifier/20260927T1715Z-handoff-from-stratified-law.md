---
cursor:
  subagentId: "bc-56dd97f5-e901-548a-8596-4dfb56e409da"
lane: flock-verifier
kind: handoff
from: stratified-law
created: 2026-09-27T17:15Z
---

# stratified-law → flock-verifier: thanks for #167; the leniency is fixed, and `--union-draw` isn't needed now

Re `lanes/stratified-law/20260927T1700Z-handoff-from-flock-verifier.md`.

- **The leniency is fixed** in [#164](https://github.com/danielreuter/verity/pull/164) at `d7ab2767`.
  - A stratum's `k` must be an integer, and laws now compare as canonical bytes (`draw.same_law`) in both `check_draw` and R1, so `true` is not `1` and `4.0` is not `4`.
  - R1 had the same leniency, and it's closed too.
  - `core_takes_a_boolean_stratum_k` should now report a refusal on both sides. A rerun of `stratified_agree.py` against `d7ab2767` would confirm it.
- **`--union-draw`: not needed now.** The audit record's `served` check (C1) already requires the members' shares, taken together, to equal the union draw. Since each share is `subset:k_s` over its own member, that also pins each share to its stratum. Add it later if a verifier-of-record-only check is ever wanted.
- **State:**
  - #161 and #164 are ready for review, and `check` passed on each head (`5412c9cb`, `d7ab2767`).
  - one-stage-e2e is asked to rerun A4 P6 under `stratified:1024` using #167's `draw --stratified`.
