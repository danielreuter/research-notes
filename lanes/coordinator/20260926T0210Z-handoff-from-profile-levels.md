---
cursor:
  subagentId: "bc-838af8af-1de1-5296-99cf-f9698efa4a67"
---

# Handoff from profile-levels: PR #46 is merge-ready (IntegrityProfile over partition levels; math unchanged)

lane: profile-levels · kind: handoff · from: profile-levels (agent bc-838af8af) · to: research coordinator (bc-8ece7cde) · created: 2026-09-26T02:10Z

**PR:** [#46](https://github.com/danielreuter/verity/pull/46), branch `cursor/profile-levels-4a67`. It already contains origin/main `4eaaa9ae` (#39, #40, #44). No force-push: `main` was merged in, not rebased.

**Merge order:** it merges cleanly with the terminology PR #43 either way. The only conflict in a trial merge of main + #43 was `backends/numerical/CHANGELOG.md`, which is #43's against main and not in this PR.

**Tests:** on the full suite the branch fails the same 9 tests as `main` (`test_repository` ×2, `test_pythonpath` ×3, the evaluation kernel list, `test_pods_connect`, `test_store_honing`, `test_telemetry`), and `test_live_coins` still needs torch. The branch adds 182 passing tests.

## What changed

- **`IntegrityProfile`** (`verity.proofs.profile`): its fields are now `levels`, `sizes`, `draws` (`Bernoulli(p)` or `Subset(k)`), `delta` and `drawn` (a count per level). They replace `n_r, n_v, p, k, replayed`. `accept` and the `worst_case` linear program are unchanged. `worst_case(utility, cap=)` adds the cap for consumers that read above the Bernoulli level, and `count(name, within)` returns member counts.
- **`verity.ir.partition`:**
  - `Level` and `Hierarchy`;
  - `validate_refinement` and `members_per_parent`, the refinement check and the public count per parent;
  - `validate_partition(..., within=S)`, the subset-cover mode, which adds an `"outside"` status that `vu_status` treats as a fail.
- **Sampled proofs:** `TwoStageLaw.profile` keeps its signature and builds levels `REPLAY: Bernoulli(p)` and `CHECK: Subset(k)`. `PROTOCOL.md` and `AGENTS.md` are updated to match.
- **vLLM:** no call sites needed changes. **Format bytes:** no frozen or digest-bearing format changed.

## Evidence for "results unchanged"

- A frozen copy of the old arithmetic in `tests/proofs/test_profile.py` must equal the new two-level profile exactly, as a `Fraction` for `accept` and a float for `worst_case`, over a grid of n_r, n_v, k, p, δ and four utilities.
- 26.6 and 16.0 hold, both directly and through `TwoStageLaw.profile`.
- The existing tests were ported only where the API names changed: constructors, three attribute reads in `test_law.py`, and the JSON shape. No expected value changed.

## Left for later (not blocking)

- **Classes for unequal sizes** (vLLM's strata) sharing one δ budget is a multi-constraint LP, so it stays one profile per class as before.
- **Draft PR #31 (PoUW):** it builds `IntegrityProfile(n_r=…)` and needs the level form when it rebases.
