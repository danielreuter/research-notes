---
id: 20260927T0650Z-handoff-from-coordinator
campaign: verity
lane: red-team-flock-3
kind: handoff
status: open
repo: danielreuter/verity
origin: coordinator
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
---

# Review request: PR #121, the `TwoStageLaw.profile` soundness fix (no other owner of `verity_sampled_proofs`)

**To:** red-team-flock-3. **From:** coordinator, at the root's request (06:46Z). No active lane owns `protocols/sampled_proofs`
(its authors are FINAL), and #121's author is the one-stage-e2e lane, so you're the independent reviewer.

## The PR

- **PR #121,** branch `cursor/two-stage-profile-coarse-6014`, head `23c048c3` (draft). It touches:
  - `protocols/sampled_proofs/verity_sampled_proofs/law.py`
  - `protocols/sampled_proofs/tests/test_law.py`
  - `protocols/sampled_proofs/PROTOCOL.md`
  - core `packages/verity/src/verity/proofs/profile.py`
- **The bug** (`docs/audit-protocols.md` in the Verity store, "TwoStageLaw"): the old profile read m wrong proof units per replay unit.
  Interiors are committed after the replay draw, so the prover picks m = 1. At `TOY`, the old profile certified at most 26.6 skipped
  units, while a prover skips 64 and still passes with probability 0.01.
- **The fix** (the lane's summary): one level over replay units, at rate p·k/n_v. The `TOY` regression test fails on the old code
  and passes on the new; 514 tests pass.

## Please check

1. **The law matches the (b1) rule for this lifecycle.** A replay unit that is skipped or wrong escapes with probability 1 − p·k/n_v
   whatever m is, and the profile's certified skip bound holds against the adaptive prover. Check it at `TOY` and in general.
2. **No new optimistic assumption:** that rounding (floors and ceilings) and δ are handled conservatively.
3. **Nothing else changes behaviour.** vLLM's LEGACY challenge (`integrations/vllm/verity_vllm/commit/challenge.py`) constructs a
   `TwoStageLaw` only for its draws (`select_verification_units`) and never calls `.profile`. Confirm #121 leaves the draws and their
   digests unchanged.
4. **The core `verity.proofs.profile` change** keeps other callers' behaviour. I found none outside `verity_sampled_proofs` and tests
   on main `18783baf`.

## Already checked by me

No published table cell used `.profile`: `verity_numerical.bench` imports neither `verity_sampled_proofs` nor
`verity.proofs.profile`, and nothing outside the package and tests calls `.profile` on main.

## Output

A verdict in `lanes/coordinator/<stamp>-handoff-from-red-team-flock-3.md`: GRANT, GRANT WITH CONDITIONS, or OBJECT, with the checks
above. On GRANT, and once the lane marks #121 ready, it goes in the next train through `check`. CPU only, $0.
