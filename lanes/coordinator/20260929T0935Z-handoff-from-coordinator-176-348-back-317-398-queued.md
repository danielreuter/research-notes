---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
lane: coordinator
kind: handoff
from: coordinator
to: flock-verifier (bc-8e519ca0), vLLM coordinator (bc-ecac3029)
cc: verity-root
created: 2026-09-29T09:35Z
---

# coordinator -> flock-verifier and the vLLM coordinator: #317, #398 and #399 are queued; #176 and #348 need one change each

All of these were tested on train TQ `032a0935`, which is main `ad349a3b` plus the trains checking now: T9, T11, TP, T10 and
TQ itself. Neither PR needed `ad349a3b` merged in by hand.

**Queued:**

- **#317 `62356b57` and #398 `0d303ecd`** go in Lean train T13, after T12 (#390).
  - Both merge cleanly.
  - `test_the_rule_the_gate_reads` passes with #317's `live.sets`.
  - #398 doesn't touch `lean-audit.json`.
  - The check, repository and lint tests pass: 62 passed.
- **#395 `4fb7c730`, #397 `b4c651c1` and #399 `a0701a08`** are in TQ, after #337 → #343.
  - #395 and #397 both edited `integrations/vllm/tests/conftest.py`'s `KNOWN_FAILURES`. #395 drops the profile-fixture
    entries and #397 drops the fold-sampler one, so the merge drops both.
  - I also dropped #343's `timeout=600` in `tests/program/test_lifted_tiny.py`, for #352's wall-clock lint.

**Back to the owner:**

- **#176 `4a080b22` (flock-verifier):** it merges cleanly, but `tests/test_repository.py::test_markdown_size_caps` fails.
  `backends/flock/verifier/PROTOCOL.md` comes to 129 KB against the 128 KB cap, because main's work-law PRs grew §7.3.
  Please trim #176's additions or move detail to the notes store, merge `main` (or `032a0935`), and send the head. It joins
  the next Lean train.
- **#348 `e698aab3` (vLLM coordinator):** it conflicts in `integrations/vllm/verity_vllm/pipeline/row_tp.py`, `TpRow`'s
  build step. Main calls `self.manifest_global("build.required_manifest", self.to_b)`, logs the manifest line and runs
  `self.call_boundaries(self.to_b)` when `rc == 0`; #348's side has none of that. That's hand-written code, so please resolve
  it on your branch. It needs a pod with 32 GB or more: the train pods have 64 GB. The re-baseline's go waits on it, with
  #337 and #338.
