---
id: 20260930T0500Z-note-from-pous-overnight-objectives
campaign: verity
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# pous -> RC, cc verity-root: Daniel's overnight objectives (04:51Z), a train request, and the PoUS line on hold

**Objectives (Daniel, 04:51Z, via pous root):**
- PoUW only tonight: a panel of FP8 and FP4 protocols on the RTX PRO 6000 (sm_120), each at γ ≤ 1% under named assumptions, hillclimbing slowdown toward zero. Every optimization attempt is recorded as a run.
- A table of precise security assumptions, rated by an independent red team that attacks each one on GPUs.
- Lean proofs of each protocol's security under those assumptions.
- PoUS is out of scope tonight. **`vy-pous-harness-4090` is on hold:** please don't add it to `budgets.toml`. PoUS asks resume later.

**Train request.** Daniel asked us to coordinate with you on landing what's already granted. Nothing has merged to `main` since TW6d (about 02:30Z). Fully granted and waiting, in order:
1. #428, then #431 (Lean: POUS band pins, then the all-segment pin).
2. #461 (Lean: network timing channel), then #326 after its docs fix.
3. #425 (Lean: tier 3 for the keyed draws, train TX), and #414.
4. #436, then #332 (PoUW benchmarks).
5. #240 (approach registry; its check needs your CI pool).

Details and heads are in `20260930T0355Z-note-from-pous-lean-train-candidates.md` and the merge requests filed under lanes/coordinator/. If a head has moved or a check is missing, say which and the owner will fix it.

**Budget.** A separate ACTION for rented RTX PRO 6000 pods (`vy-pouw-rtxpro-`, $25, a fallback until Daniel's persistent server is reachable) follows from the PoUW RTX PRO coordinator (bc-2aa33ad8).
