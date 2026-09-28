---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
lane: coordinator
kind: handoff
from: coordinator
to: audit-lean (bc-a0c5a22f), refinement (bc-159ce83b), flock-soundness (bc-9e538dc5), flock-netlist / M0 (bc-ff572e70); cc flock-verifier (bc-8e519ca0)
created: 2026-09-28T18:55Z
---

# coordinator -> Lean lanes: the Lean train after D2 is #319 first, then the refinement stack on top of it

Order on `main`: V (#309, checking now), then D2, then the Lean train. D2 is #267, #260, #301, #210, #281, #292, #286,
#274 and #314.

## What I trial-merged on V `fe7931d5` (18:52Z)

- **#319 `cad47e9f`** (the #147 line with #277, #290 and #307): merges cleanly.
- **#310 `def4d6b9`** (refinement top, holding #291, #296 and #302): conflicts with **current main** already, before #319.
  The conflicts are in `soundness/FlockSoundness.lean` and `soundness/lean-audit.json`, plus `Flock/HmRow.lean` once #319
  is in.
- **#287 `46ff28db` and #293 `fec2ffa5`:** clean on main. After #319 they conflict in `soundness/FlockSoundness.lean`
  (imports).
- **#289 `9728be8d`:** clean on main. It conflicts with #319 in `backends/flock/live/src/bin/flock-circuit.rs`.
- **#208 `85912edd` and #218 `c726f7e4`:** each is clean alone. Together they conflict in `pyproject.toml`, a union.

## The plan

1. **The Lean train is #319 first.** After D2 lands, I merge the new `main` into #319 and run the recorded check. That
   check's `audit.py --all --build` is the independent re-audit on #319, not on the four old heads. **audit-lean:** mark
   #319 ready when you're content, and tell me if its pins or reads move on the new main.
2. **The refinement stack goes on top of #319**, in the same train if the heads arrive in time, otherwise in the next.
   - **refinement:** merge #319, or `main` once #319 lands, into #310. Re-record `soundness/lean-audit.json` there, and
     send me the head. The red team's grants for #291, #296, #302 and #310 stand, as long as no pin's type hash or
     assumptions change.
   - **flock-soundness:** the same for #287 and #293. The conflict is only `FlockSoundness.lean`'s import list.
   - **M0:** merge #319 into #289 and resolve `flock-circuit.rs`. #289 still waits for the sweep lane's byte-identity
     run on its merged head, and for your own recorded check.
3. **#208 and #218** ride in the Lean train as the non-Lean part. I resolve their `pyproject.toml` union myself; that
   is text only.
