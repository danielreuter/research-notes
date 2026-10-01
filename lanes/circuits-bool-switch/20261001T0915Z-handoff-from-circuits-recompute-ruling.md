---
id: 20261001T0915Z-handoff-from-circuits-recompute-ruling
campaign: verity
lane: circuits-bool-switch
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa)
---

# @circuits: proofs ruled (2:16 AM PDT). Recompute across Boolean Calls is allowed, as `Q_word` v2. Add a `known.py` entry per family in the PR

- **The ruling** (Slack 1790846049.444779, thread 1790835087.087079): a value recomputed in another unit is never committed, and each unit
  proves it from its own committed inputs.
  - `gate-not-certified-once` and committed cross-unit reads still hold. `gate-recomputed` buys economy, not soundness.
  - `Q_word` v2 is v1's algorithm exactly (same Calls, cut, units, committed set, width rule), except that cross-unit recompute is reported
    in `detail`, not refused. A Boolean Program's partition object names v2.
  - proofs-ir builds v2: Python reference, vectors, PROTOCOL.md, Lean partition check, lean-agreement. Target: a passing PR by 5:30 AM,
    landing by 7:50.
- **For your PR(s) now:** add one circuit-check `known.py` entry per family for `partition/gate-recomputed` on the Boolean composites as
  Calls (RoPE, GEMM coordinates sharing x, attention, norms, and any other family that hits it). Cite the ruling's Slack link. The precedent is
  `partition/gate-recomputed ScaledMmFp8Block_v1`.
  - Keep one unit per output element, as now. Don't use the opaque-Call form.
  - The entries come out when v2 lands.
- Put the per-Call recomputed-gate counts (for example, a RoPE pair has 280 of 5,932, about 5%) in the PR body's circuit-check table.
