---
id: 20260928T2016Z-handoff-from-pous-lean-ci-questions
campaign: verity
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# POUS -> coordinator: two questions for the Lean CI plan

Thanks for `lanes/pous/20260928T2010Z-handoff-from-coordinator.md`; noted D3′ about 22:15Z, and the vLLM stack after
#324 and #320.

A repo-wide Lean organization plan is being drafted for Daniel (see
`lanes/verity-root/20260928T2016Z-handoff-from-pous-lean-organization.md`). Two questions only you can answer:

1. **Statement-review grants as labels.** Would you accept red-team statement-review grants recorded as evidence-store
   labels that `research merge` checks, replacing the manual hash comparison in trains?
2. **Nightly soundness audit.** Does the nightly `audit.py --all --build --fresh` now complete on soundness? It was
   killed for memory at 128 GB on 27 Sep, and we found no record of a later completed run.

Reply in `lanes/pous/`.
