---
id: 20260928T1945Z-handoff-from-pous-merge-eta
campaign: verity
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# Request: #208 and #218 in D3 rather than the Lean train, and the vLLM protocol-options stack right after

Daniel wants the POUS and PoUW prototypes, with their vLLM integration, on `main` as soon as practical, to send to a colleague. He asked for an ETA.

- **#208 `85912edd` and #218 `c726f7e4`:** both are green, non-Lean and clean on `main`. Together they conflict only in the `pyproject.toml` union you noted. If D3 isn't already sealed, could they ride in D3 instead of waiting for the Lean train?
- **Next, the vLLM stack:** #311 (the composable `protocol_options` scaffold), then #312 (POUS adapter) and #315 (PoUW adapter), both stacked on #311.
  - #311's owner is finishing its recorded `check`. The vLLM tests pass under torch as `r20260928-190833-ed72`. It will post its own handoff and ask the vLLM coordinator for a verdict.
  - The two adapters will merge in #311's final head, re-run `check` and post their handoffs, so all three can go in one train once the vLLM coordinator approves.
- **Please reply in `lanes/pous/`** with the train you expect each group in and a rough time, so I can give Daniel an ETA.
