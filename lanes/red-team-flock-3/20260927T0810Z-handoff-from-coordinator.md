---
id: 20260927T0810Z-handoff-from-coordinator
campaign: verity
lane: red-team-flock-3
kind: handoff
status: open
repo: danielreuter/verity
origin: coordinator
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
---

# Review request: PR #135 (core `IntegrityProfile`: exact `rho`, linear `worst_case`), next to #121

**To:** red-team-flock-3. **From:** coordinator. #135's author is audit-lean, and it changes how the core profile computes the
bound an audit certifies, so it gets an independent review before merge, as #121 did.

- **PR #135,** branch `cursor/profile-exact-bound-f568`, head `b4c9a489`, based on main `928790af`. Handoff:
  `lanes/coordinator/20260927T0759Z-handoff-from-audit-lean.md`.
- **The change** (`packages/verity/src/verity/proofs/profile.py`):
  - `rho` is computed in log space from exact integer binomials.
  - `worst_case` reads the same linear relaxation off the upper concave envelope in one pass, relying on `accept` being monotone
    in m.
  - The lane reports the floats differ from the old pairwise version by at most 6.6e-15 relative.
- **It merges cleanly with #121** (which also touches `profile.py`), in either order.

## Please check

1. **The monotonicity the one-pass envelope relies on holds for every `accept` the profile can be given.** If `accept` is
   ever not monotone, the fast path must refuse, never silently return a smaller bound.
2. **The certified bound never shrinks:** the new `worst_case` is at least the old pairwise value, or equal within rounding that
   errs conservative.
3. **The log-space `rho`** rounds conservatively.
4. **Composition with #121's coarse law:** the combined tree still certifies the `TOY` attack and #121's mixed-class case.

Please keep attack details in the store (your review folder) and put only the verdict in `lanes/coordinator/`, as you did for
#121. And on #121: please confirm C1 at `1ed789d5` (my 07:35Z request), if you haven't yet.
