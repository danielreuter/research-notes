---
id: 20260928T1630Z-handoff-from-pous-land-protocols
campaign: verity
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# Please merge the POUS and PoUW protocol packages once they're green (#208, #218)

Daniel (16:28Z) wants both generic protocol packages on `main`, with their vLLM options.

- **#208 (`protocols/pous`):** based on `main` and mergeable. Its owner is re-running the recorded check and will mark it ready.
- **#218 (`protocols/pouw`):** conflicts with `main`. Its owner is merging `main` in, re-checking and marking it ready.
- **Separate PRs, not in this handoff:** the vLLM `protocol_options` scaffold and its POUS and PoUW adapters come next, and the vLLM coordinator is asked to review them.

Each owner will post a follow-up here with its recorded check run id when its PR is ready.
