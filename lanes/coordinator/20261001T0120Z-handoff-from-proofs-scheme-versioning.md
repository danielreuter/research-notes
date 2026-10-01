---
id: 20261001T0120Z-handoff-from-proofs-scheme-versioning
campaign: verity
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs (bc-8416bc72, Slack @proofs)
---

# Advisor question (no rush, by 9 PM PDT): how should we name and version C-Flock's variants?

Daniel (6:13 PM PDT) wants a scheme for keeping proof-system variants organized. We'll run several side by side
(slots, live coins, single 128-bit repetition), with experimental ones separate from locked-in "live" ones, a promotion
path, and the variants shown on the overhead plots. The version changes on a security or design change, not on kernel or
implementation changes.

My draft: `/cursor/stores/bc-7f347b4b-6175-4b6e-84c6-731add2f8589/docs/protocol-schemes.md`.
- Ids like `flock-i-v1`. Experiments are named as deltas from a parent (`flock-i-v1+slots`), and promotion assigns the
  next live number.
- A registry in `verity_flock/schemes.py` modelled on PoUW's `schemes.get`.
- The scheme id goes into the statement digest's domain tag, and pinned vectors enforce the bump rule.
- Promotion reuses the existing gates: Lean pin, red-team grant, lean-agreement, vectors, merge.

Three questions:
1. How were the frame-v3, `verity/flock-pure-block/v2` and `flock-tables` statement tags versioned and retired? Is
   there a convention, or history, I'm missing?
2. Will anything in the train, `check` or lean-agreement break if the domain tag carries a scheme id?
3. Would you do it differently?

Reply in `lanes/proofs/`.
