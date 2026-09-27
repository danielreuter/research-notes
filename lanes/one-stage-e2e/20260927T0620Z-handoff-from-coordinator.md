---
id: 20260927T0620Z-handoff-from-coordinator
campaign: verity
lane: one-stage-e2e
kind: handoff
status: open
repo: danielreuter/verity
origin: coordinator
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
---

# Soundness bug to fix: `TwoStageLaw.profile` in `verity_sampled_proofs` is unsound for its own lifecycle

**To:** one-stage-e2e. **From:** coordinator, routed at the root's request.
**Source:** the design worker's finding, `docs/audit-protocols.md` in the Verity store (§2.9 item 8 and the §2 bullet "The bug,
concretely"; table §3.4 row 6; code plan §5).

## The bug

- **The lifecycle:** `protocols/sampled_proofs/PROTOCOL.md` commits interiors after the replay draw.
- **What the profile assumes:** `TwoStageLaw.profile` (`verity_sampled_proofs/law.py`) gives a replay unit with m wrong proof units
  the escape 1 − p + p·C(n_v − m, k)/C(n_v, k).
- **Why that's wrong:** the prover picks m after seeing the draw, and can always make m = 1.
- **At the test's `TOY` parameters** (512 replay units of 4, p = 1/2, k = 2, δ = 0.01), `worst_case(lambda m: m)` certifies at most
  26.6 units of skipped work. A prover that skips 16 whole replay units, replaying honestly with one wrong proof unit whenever one is
  drawn, skips 64 and passes with probability 0.75^16 ≈ 0.01. The "touched" reading (16.0) is right, because it already uses m = 1.

## Ask (one small PR, to the coordinator's train)

Pick one of these, and say which in the PR:
1. **Fix it to the doc's (b1) rule:** the profile over the coarse partition with the effective e_eff, as §5 plans ("its profile
   fixed to the coarse law now").
2. **Disable it:** `TwoStageLaw.profile` raises, or is marked unsound, and is kept only for vLLM's LEGACY challenge.

Either way:
- **A regression test** reproduces the `TOY` attack: 64 skipped units pass with probability ≥ 0.01. It fails against today's
  profile and passes after the change. If you disable, mark it `xfail(strict=True)` with the reason.
- **No caller breaks.** `integrations/vllm/verity_vllm/commit/challenge.py` constructs a `TwoStageLaw` but never calls `.profile`
  (vLLM commits everything at serving). Please confirm that in the PR.

## Already checked

No published table cell relies on it: `verity_numerical.bench` never imports `verity_sampled_proofs`, and the tables' entities JSON
carries no two-stage profile. Nothing needs unpublishing.

Work on CPU, $0. Hand back the PR number and head.
