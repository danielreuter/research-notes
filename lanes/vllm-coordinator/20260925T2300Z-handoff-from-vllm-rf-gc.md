---
lane: vllm-coordinator
kind: handoff
from: vllm-rf-gc
created: 2026-09-25T23:00Z
---
# MERGE-READY gc3: lane/vllm-rf-gc3 @ 411c5cee (contains gc2 a0ec1083; base origin/main 5f8d8789)

- One test-file commit `411c5cee` (`tests/program/test_harden_guards.py`): G4c's bindings glob/relpath, EVIDENCE, DERIVE_STEP and G5's
  PYTHONPATH/cwd resolve from integrations/vllm instead of packages/verity/src. gc2 wasn't in main, so the branch is gc2 + main merge
  + this commit: merge gc2 first or merge gc3 for both.
- Gate r20260925-224928-36b7 (vyv-rf-gc3-cpu, git clones, sampled_proofs on PYTHONPATH): lints rc 0 both; test_harden_guards base
  2 P / 11 S, head 2 P / 11 S, same outcomes per test. G4c now scans 16 files (13 bindings) with 0 hits: passes for real; no product defect.
- Not fixable here: the R10 evidence (G1a-G4b, 10 skips) is not in the repo and veritor isn't reachable; migrate or retire. G5 needs a
  GPU pod with HARDEN_LIVE=1 to exercise (not run).
- Pod terminated; spend ~$0.03. Record: lanes/vllm-rf-gc/READY.md (gc3 section on top).
