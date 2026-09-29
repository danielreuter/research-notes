---
id: 20260929T1738Z-handoff-from-pous-daniel-defers-decisions
campaign: verity
lane: verity-root
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# POUS -> root: Daniel deferred all pending decisions to our recommendations; closing out now; one ask on #364's merge path

At 17:32Z Daniel said he defers to our recommendations on every open decision, wants things closed out as soon as
possible, and wants something working end to end. We're applying these defaults now, each recorded as
"default, Daniel deferred, 2026-09-29":

- **Tier-3 pilot:** the one-stage audit is accepted as the pilot. #408/#412 are on `main`, #416/#418 are granted, and #414
  is filed. Please update your summary for Daniel accordingly.
- **POUS trusted-layer pins:** everything the red team GO'd is accepted. That's the nine band pins, the install and the
  grader hardening (§54–§57), the three P3 concrete-H finals (§51), and the dense deployment re-pinned from k = 107 to
  k = 111, which is proved (§56). One PR to `main` is coming, with a Lean-train merge request.
- **P2:** frozen at the memo's six defaults, including k = 105. The new assumption is not accepted yet, and the current
  prime stays without a Lean-checked proof.
- **PoUW FP8:**
  - binding B's integer mix is not credited, which stops B;
  - the H-1T scheme decisions are at their defaults;
  - the folded epilogue stays the fallback;
  - the cost-model and W1 decisions are at their defaults;
  - `tuple` is unchanged.
- **Also at their recommendations:** the resource ontology, the Lean-organization plan (items that differ from your Lean
  doc will come to you from that lane), the deployment-requirements audit, and the registry's public detail.

**Ask: #364's merge path.** To reach end to end sooner, may we file #364's merge request as soon as the circuit red team
GOs the final head (`7b1ba73f`), and let the train's recorded check stand in for our own? That train check would run with
custody on and the skip off, after RC's #420. Our last recorded check passed everything except the 8 store-backed
`verity-vllm` tests, which failed on the `check.py` `RESEARCH_*` filter (our 16:58Z finding). If you'd rather have our
own recorded check first, we'll relaunch as soon as #420 lands.
