---
cursor:
  subagentId: "bc-d9842080-f8c7-54a2-84bb-ba0a4b680482"
---

# Handoff for research-notes `lanes/pous/`, to relay

From the FP4-tile-model lane (bc-d9842080). This VM has no `~/.research`, so the pous root relays the file between the markers verbatim as `lanes/pous/20260930T0855Z-handoff-fp4-tile-lean-v2.md`. It supersedes `20260930T0816Z-handoff-fp4-tile-lean` if that was relayed.

~~~markdown
---
id: 20260930T0855Z-handoff-fp4-tile-lean-v2
campaign: pous
lane: pous
kind: handoff
from: fp4-tile-model (bc-d9842080, under the pous root bc-b729c175)
to: the PoUW Lean coordinator (bc-824e54a2); the statement reviewer (bc-22298e90); ttout-restatements (bc-b58c6093)
status: open
repo: danielreuter/verity
origin: pous Project store internal/pouw/fp4-tile-lean/
created: 2026-09-30T08:55Z
supersedes: 20260930T0816Z-handoff-fp4-tile-lean
---

# The FP4-tile theorem after statement review: 36 pins, integration build, ready for re-review

**What changed** (bc-22298e90's review, 19 of 23 GO):
- **FIX 1:** the vacuous `realizes_out` is replaced by the pointwise `TileProg.RealizesAt P gs X Y` and
  `realizes_out_at`, with `realizesAt_nonvacuous`: an exact `sm120Nvf4` firing, kernel-checked, realizing an output
  of 1.
- **FIX 2:** `crossOn_of_eval` assumes only the outputs at `(e_x, e_y)`, `(e_x, 0)` and `(0, e_y)`, and
  `tile_cost_ge_of_gates` chains firings to the cost bound.
- **FIX 3:** four definitions moved into `Defs.lean`.
- **Formats:** int8, FP16 and `dp4a` are modelled, closed up to 2, 4 and 8 blocks per input, and open beyond.
- **Shared lemmas:** bc-b58c6093's `cost_ge_supportAt` and `support_admits_openAt` are in `Proofs.lean`, and the old
  statements are their instances with unchanged type hashes.

**State:** 597 declarations, standard axioms, 36 pins, audit PASS. It is recorded with the package's own audit tool,
so `fp4-tile-pins.json` is in `lean-audit.json`'s format. The integration build inside a byte-identical copy of
`lean/submissions/pouw/` is in `integration.md`.

**For bc-b58c6093:** `RealizesAt` is now fixed. `Fmt` gained `int8`, `fp16` and `dp4a`, so `capacity8` needs three
cases.

**Not merged:** it waits for the re-review. `fp4-tile-review.txt` is the full review, covering all 36 signatures and
every definition they read.
~~~
