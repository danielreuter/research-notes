---
cursor:
  subagentId: "bc-a0c5a22f-172a-5651-8a9b-eb333fdcf568"
---

lane: coordinator · kind: handoff · from: audit-lean (bc-a0c5a22f) · to: research coordinator · created: 2026-09-28T07:00Z ·
repo: danielreuter/verity · about: 1d step 1 is up as [#249](https://github.com/danielreuter/verity/pull/249)

# 1d step 1: `Rows.compose` from the rows the verifier derives

**The PR.** [#249](https://github.com/danielreuter/verity/pull/249), draft: branch `cursor/audit-compose-rows-f568` at
`ec52ce38`, on #205 (`cursor/flock-compose-sound-8569`, `b9dea1f7`). One new file,
`soundness/FlockSoundness/Compose.lean`:
- `Rows.compose`, the audit's rows in the constant-first logical order;
- `placement_of_realizes`, at the matrix level;
- for flat types, `compose_ordered` and `Rows.compose_eval`.

**Checks.**
- `lake build` passes, and `Check.lean` shows standard axioms only.
- `audit.py` with replay: PASS, 4,941 declarations, 13 pins (2 new).
- The duplicate-constant check is clean.
- The flock tests that can run here pass. The failures are missing Python modules (`blake3`, `circuit_check`), which this
  PR doesn't touch.

**Merge order.** After #205. The two pins need the red team's statement review first.

**The documents I created** (all under `internal/lanes/`):
- `red-team-flock-3/20260928T0700Z-handoff-from-audit-lean-249-pin-review.md`: the statement review for the two pins;
- `flock-soundness/20260928T0700Z-handoff-from-audit-lean-1d-step2-on-247.md`: step 2 as an adapter over #247's
  `blockRow`, with four asks about S3's order facts;
- `flock-verifier/20260928T0700Z-handoff-from-audit-lean-1e-placement-hypotheses.md`: the matrix facts 1e discharges.

**Waiting on others.**
- Step 2 waits on the soundness lane's answer to those asks. It builds on #247.
- The #204 `parse_facts` extension waits on #204, as planned.
