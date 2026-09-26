---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

# Merge request: gc3, test_harden_guards resolves from integrations/vllm (test-only), from vLLM coordinator bc-ecac3029, 23:10Z

- **Merge:** `lane/vllm-rf-gc3` @ **`411c5cee`**, `--no-ff`, after m32. The branch holds gc2 (`a0ec1083`, already in main)
  plus a main merge plus one commit, `411c5cee`, touching `tests/program/test_harden_guards.py` only.
- **Recheck against main `22985ba9`:** clean. The shared files are gc2's own, with the same content on both sides. The
  ratchet lints pass on main plus m32 plus gc3 (39/39).
- **Change:** G4c's bindings glob and relpath, `EVIDENCE`, `DERIVE_STEP`, and G5's PYTHONPATH and cwd now resolve from
  `integrations/vllm` instead of `packages/verity/src`. This closes the gap noted in the gc2 request: G4c had become
  vacuous for the 13 `vllm_bindings/*.py` files after b5vc.
- **Gate** (`r20260925-224928-36b7`, vyv-rf-gc3-cpu, git clones, `sampled_proofs` on PYTHONPATH): lints rc 0 on both sides;
  `test_harden_guards` 2 passed / 11 skipped at base and head, with the same outcome per test. **G4c now scans 16 files
  (13 bindings) with 0 hits**: it passes for real, with no product defect.
- **Not fixable here:** the R10 evidence behind G1a–G4b (10 skips) isn't in the repo, and veritor isn't reachable (migrate
  or retire, an owner call). G5 needs a GPU pod with `HARDEN_LIVE=1` (not run).
- **Evidence:** `lanes/vllm-rf-gc/READY.md` (gc3 section); handoff `lanes/vllm-coordinator/20260925T2300Z-handoff-from-vllm-rf-gc.md`.
  About $0.03.

