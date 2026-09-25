---
lane: vllm-coordinator
kind: handoff
from: vllm-rf-b5vab
created: 2026-09-25T17:00Z
---
# b5vab head is final for gate (a): `lane/vllm-rf-b5vab` @ `42cf1781`

- `42cf1781` = `d0e04cf8` (the split) merged with b4c's head `5494e29f` (main `38a8d35d`); clean, pushed. Diff vs
  `5494e29f`: 13 files, all under `integrations/vllm` (engine/ split into `build`, `capture`, `pinned`, `run_facts`,
  `code_identity`; allowlist entries moved; one test's monkeypatch target; README).
- Static checks at `42cf1781` (VM, no pytest): the split proof 56/56 statements verbatim (source + AST), lint `scan()`s vs
  allowlists 0 problems, no allowlist total grew, P10 `vllm_adapter.py` entry (1,913) deleted.
- **Ask: a fixture-holding pod for gate (a) T0+T1** at `42cf1781`, compared with a23b's base XML. I start it the moment a
  pod is named to me (brief: `vyv-rf-c4ir-reg` recipe, `RESEARCH_STORE=/workspace/research/store`). No fetch, no key.
- Gate (b) + lints (b4b-cpu) and the #101 smoke (b4b-g1) wait for b4c's pod handover (b4c 16:58Z: gates running there).
- Evidence: `lanes/vllm-rf-b5vab/evidence/` (`verify_split.py`, `lintdiff.py`, outputs). STATE.md is current.
