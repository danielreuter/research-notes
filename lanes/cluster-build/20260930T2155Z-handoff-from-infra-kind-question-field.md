---
id: 20260930T2155Z-handoff-from-infra-kind-question-field
campaign: verity
lane: cluster-build
kind: handoff
status: open
repo: danielreuter/verity
origin: infra coordinator (bc-17cc41f1)
---

# cluster-build: add a `question` to every kind, and record the research question on every queued job

**New standing rule (Daniel, 2:52 PM PDT):** every overnight queue needs an explicit yes from its lane's research owner, and every job names the research question it answers. Idle beats padded.
- **In the registry,** every kind in `kinds*.toml` gets `question = "..."`: the research question it answers.
- **On submit,** `research run --queue` takes `--question`, defaulting to the kind's, and records it in the ledger and the run record.
  An `adhoc` job with no question gets a warning tonight, per the lighter design. It isn't refused.
- **Accounting:** `cluster usage --by question` sits beside `--by kind` and `--by lane`.
- **Seeds:** `lean-audit` (proofs) gets its question from proofs; ask in `lanes/proofs/`.
