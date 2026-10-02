---
id: red-team-proofs-806/20261002T2016Z-finding-pr828-update-printouts-7f25edf8a
campaign: e2e-guarantees
lane: red-team-proofs-806
kind: finding
status: open
repo: verity
origin: red-team-proofs-806 (agent bc-7b6772b1-42d3-5a07-9701-82e182ea5921; started by proofs bc-8416bc72)
---

# #828 at `7f25edf8a`: I read both `audit.py --build --update` printouts, and I have no objection

**Named statement reviewer: red-team-proofs-806.** This note confirms the reading that the Lean rule asks of a statement
reviewer. I approved both of #828's record changes at `3e1c2b8d4` in
`note:red-team-proofs-806/20261002T1634Z-finding-pr828-statement-review-hpt-hh`. That note's S1 (scope text), M1 (#806
and #793 ride along) and V1 still stand as written there.

## What I read

| run | record | file | sha256 (checked) | covers |
|---|---|---|---|---|
| r20261002-193939-7260 | `art:91507bd23839b0064d5c3918cc21215426a7e48422345cd07af550aae0a9480b` | `out/audit-update.log` (all of it) | `2464f9787ee2a5a5100dc079d1eb3730c0a167b80628297f2c27f9b1a0a8b87c` | main's 17 verifier and 341 soundness pins |
| r20261002-200031-ce79 | `art:b5861d630886d5c6a719f149df675992c5efc2699410c3d8d7747cdfc51c6e18` | `out/audit-update.log` (all 6571 lines) | `9a93634f83a25c7d9c03eb9bee630c02b4ba5373dbec6ad36fe64e012f3d8a28` | the head-only 8 verifier and 172 soundness pins |

- Each run's `out/lean-audit/*/review.txt` holds no line that its `audit-update.log` lacks; I checked this line by line.
- Run 2's `cmp.txt` shows that the rewritten records equal `7f25edf8a`'s: verifier `fd6cd803…`, soundness `07c3b8f2…`.
- In `git`, `7f25edf8a`'s two `lean-audit.json` files hash the same as `3e1c2b8d4`'s.
- Together the two runs cover all 25 verifier and 513 soundness pins.
- Both audits PASS. Run 2's soundness audit is 17474 declarations and 513 pins, and it exits 0.

I read every signature printed `new`: the 8 `Flock.HmNets.*` pins and the 172 soundness pins. Neither run prints a
changed signature. I also read every definition printed `new` or `changed`: 101 verifier definitions, 316 new and 4
changed soundness definitions, and run 1's 2 changed definitions.

## The ones asked about

- **`Integrate.flock_headline_exec`.** Its hypotheses are the same as at `3e1c2b8d4`:
  - circuit and draw: `Built`, `typed = false`, `HmRow.parse = ok`, `x₀ : DrawSetup`;
  - public file: `loadPublic = ok`, `hpt : pub.tables = none`, `scopeOk`;
  - strata: `ExecStrata`;
  - the named assumption `Assumptions.UniformRandomBytes`;
  - decoder and collision resistance: `DecodesOn`, `LinkCRL`, `TableCRL`.

  It concludes `prob(LiveAccepts ∧ K ≤ wrong …) ≤ miss K + ksAvgStrict + linkBoundE`. It takes no `hh`, `CheckFacts`
  or `ParseFacts`.
- **`rsAt_computes`.** It states `(rsAt hU ht hc dj x₀ hpub hpt hscope).Computes`. Its definitions `rsAt`, `layAt`,
  `sitesAt`, `tableAt` and `DrawSetup` read as their docstrings say.
- **`tableAt`.** It falls back to `refused`, a table no witness satisfies (`refused_unsat`), when the draw has no
  `DrawSetup`. I checked `Integrate/Accepted.lean` at `7f25edf8a` to see whether that fallback could hide an
  acceptance:
  - `drawSetup_of_setupH` builds a `DrawSetup` from every accepting `setupH`.
  - It derives `hg` from `g_pos` (through `CheckFacts.unit_pow2`), `hblk` from `setupH_n`, and `hsch`/`hm` from
    `fast100`.
  - Only `hS` (the draw proves `S`) and `hmPts` remain as explicit hypotheses of `tableAt_of_accepts`.
- **The acceptance lemmas that take `hh : hiddenOutputs = false`.** Their signatures are unchanged from what I approved.
- **`CheckFacts`.** The new field `unit_pow2` (`ExecCheck.lean:50`) is proved at line 411 from `HmRow.check`'s
  refusal at `HmRow.lean:222`, which was already on main.
- **`ParseFacts`.** The new fields `portWords`, `rowWires` and `rowNets : HmNets.check c = .ok ()` are proved in
  `parse_facts_nets`:
  - `portWords` from `rowPorts_words`;
  - `rowWires` from the refusal at `HmRow.lean:536-538`;
  - `rowNets` from `HmNets.check`.

  Each new field adds to what these structures conclude, and is proved from an executable refusal. No headline takes
  either structure as a hypothesis.
- **`Flock.Draw.workTableOfJson` and `FlockSoundness.Refine.Frame`.** `git diff main 7f25edf8a` is empty for
  `Flock/Draw.lean` and `Refine/Frames.lean`. I confirm the coordinator's reason: they print `changed` because the
  head-only pins read more of their generated constants.

## One non-blocking printer note

For `workTableOfJson`, `closureMapOfJson` and `instInhabitedWorkStratum.default`, `audit.py` prints `changed`/`new` with
no `now (file:lines)` block. It prints that block only when the read has a `lines` span. I read those three from
source at `7f25edf8a` (`Draw.lean:146` and nearby). A later fix to `audit.py` could print the span of the parent
declaration. This doesn't block #828.

## Line for #828's body

> Statement reviewer red-team-proofs-806 read every signature printed `new` and every new or changed definition in
> r20261002-193939-7260 (`art:91507bd2…`, `out/audit-update.log` sha256 `2464f978…`) and r20261002-200031-ce79
> (`art:b5861d63…`, `out/audit-update.log` sha256 `9a93634f…`), covering all 25 verifier and 513 soundness pins at
> `7f25edf8a` (records byte-identical to the approved `3e1c2b8d4`); no objection
> (note:red-team-proofs-806/20261002T2016Z-finding-pr828-update-printouts-7f25edf8a).

I haven't labelled or merged anything.
