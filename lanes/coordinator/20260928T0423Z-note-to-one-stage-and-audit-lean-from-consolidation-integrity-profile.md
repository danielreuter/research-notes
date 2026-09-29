---
cursor:
  subagentId: "bc-da04890f-cab6-50c0-a1ab-b1bc00adcec1"
lane: coordinator
kind: note
from: consolidation (bc-e373566b)
to: one-stage audit (bc-c520c11b), audit-lean (bc-a0c5a22f)
created: 2026-09-28T04:23Z
---

# The integrity profile is its own object: what `cursor/integrity-profile-object-ac68` changes in your files

**Daniel's decision (Sep 28, 04:04Z):** the integrity profile is the audit's output: per-stratum bounds on faulty (wrong) proof units, with δ. Applications consume it, for example exfiltration security (wrong units weighted by output bits) and compute security (weighted by work). The profile is neither of them.

## Where the code or docs mix the profile with an application (survey on `main` @ `6746f408`)

- **Core `verity/proofs/profile.py`:** `Stratified.harm_bound` describes itself as "output bits for prover freedom, native work for compute transparency", which puts application meaning in the profile's own API. `tests/proofs/test_profile.py` pins A4's exfiltration numbers (9.40, 8.81 and 1.50 MiB) as tests of the profile.
- **One-stage `audit.py`:** the audit returns two different core types depending on the law: `IntegrityProfile` for `subset` and `bernoulli`, `Stratified` for `stratified`. The stratified profile is also a JSON dict built inline in `audit_record`. There is no application weighting anywhere in the audit or its record. `wrong_units` is already counts only.
- **Sampled proofs:** `PROTOCOL.md` step 6 and the docstring of `TwoStageLaw.profile` describe the compute reading ("work in VUs charges `n_v` per wrong RU") inside the profile's own description.
- **Lean `Audit/*`, `ASSUMPTIONS.md`, `DESIGN.md` §12:** clean. Every statement is over wrong-unit families `𝓑`, with no weighting.

## What the branch changes (no digest, vector, Lean or `lean-audit.json` change)

- **Core:** `IntegrityProfile` also takes a `Stratified` draw of its checked level, so it is the one profile type for every law. It gains `strata()`, `bound()` and `stratum_bounds()`, the per-stratum bounds on wrong units at δ, plus `harm_bound(weights)`, the generic weighted bound that dispatches to `Stratified.harm_bound` or `worst_case`. The docstrings describe the profile only.
- **One-stage, in files that PR #168's GitHub file list shows** (its own diff against `main` is `benchmarks/one_stage` only, so there is no overlap in content):
  - `audit.profile()` returns an `IntegrityProfile` for all three laws, and `wrong_units` and `audit_record` read it.
  - `audit.wrong_units_bound` is removed; `IntegrityProfile.bound()` replaces it.
  - **The audit record's bytes are unchanged**, and a test holds the new path to the old one on subset, Bernoulli, stratified and A4 fixtures. In particular, a stratified record's `profile` field keeps its v0 form (the law's JSON with `delta` and the count drawn per template), because the recorded A4 run `r20260927-170424-8360` (`art:39e89a007c9e`) holds those bytes.
  - `PROTOCOL.md` step 6 and the module docstring now describe one profile.
- **New `verity_one_stage/consumers.py`:** `exfiltration_bound(profile, output_bits)` and `compute_bound(profile, work)`, placed beside the protocol, since consumer readers stay out of core. Their tests assert equality with the old expressions: A4's `harm_bound`s, and the two-stage `TOY`'s `worst_case(4m) = 64`. A4's MiB numbers move there from the core tests.
- **Sampled proofs:** step 6 and the `profile` docstring describe the profile only; a new "Consumers" section names the compute reading. PR #132 already conflicts with `main` in `law.py`, and my edits are to lines it doesn't touch.
- **README:** unchanged here. `cursor/repo-docs-glossary-ac68` (`ce58cf83`) already carries the "Integrity profile" Glossary entry in Daniel's wording, and a second copy would conflict with it.

## Left for you

- **One-stage lane:**
  - Unifying the record's JSON, so that `profile` is `IntegrityProfile.to_json()` for every law and there is one field instead of `profile`, `wrong_units` and `integrity_profile` side by side. That changes recorded bytes, so it needs an audit-record format bump (`verity/one-stage/audit/v0` → v1), which is your call.
  - `benchmarks/one_stage` reads only `wrong_units` and `integrity_profile`, so nothing changes there.
- **Audit-lean lane:** nothing conflates today. If the optional harm-weighted escape of `docs/sampling-strategies.md` §4 is written, state and name it as a consumer corollary of `audit_profile`, not as part of the profile's statements. Any change to a pinned statement goes through the red team (bc-f0bc7e75).

## Status (04:37Z)

Pushed at `39c9ebb8`: five commits. Main's code (`6746f408`) and the branch give byte-identical JSON for every record and bound above. Tests: core proofs, protocols, the boundary and repository tests, and flock's `test_audit_profile`.
