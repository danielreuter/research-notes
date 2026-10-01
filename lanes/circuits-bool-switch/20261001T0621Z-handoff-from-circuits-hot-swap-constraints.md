---
id: 20261001T0621Z-handoff-from-circuits-hot-swap-constraints
campaign: verity
lane: circuits-bool-switch
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa)
---

# @circuits: make the switch a pure hot-swap, so tonight's word-Program Commits can re-verify against Boolean on CPU without re-serving

Daniel (11:18 PM PDT) is weighing whether tonight's coverage-grid Commits re-verify against the Boolean Programs. Build the switch so they can:
1. **Same Call boundaries.** Boolean mode changes only Definition bodies below the committed Call boundaries. Every Call keeps its id
   position, its signature, and its committed outputs (op_path, output_member, invocation). New sub-Calls live strictly inside a Call.
2. **A pinned partition.** Don't re-cut the Boolean Program with `Q_word` from Boolean gate counts. The Boolean Program's population is the
   word Program's committed identity set (its required manifest), unchanged. Report gate counts per unit as a cost, and never let them
   move a unit.
3. **A recorded substitution.** Emit σ: word Definition id → Boolean Definition id, each with its circuit-check correspondence result, plus
   P' = σ(P), checked against P by `descriptor_equivalence`. A re-verification then cites the Commit's original Program digest, binding
   map and run root (the sample is seeded from the run root, so the 460 picks don't change), and evaluates each pick's Boolean body with
   `verity.evaluation.bits` on the committed inputs.
4. **Your 460-unit check is exactly this re-verification,** on an existing SmolLM2-135M B1 greedy Commit's kept leaves.
Tell circuits at once if any family's Boolean version can't keep a Call's boundary.
