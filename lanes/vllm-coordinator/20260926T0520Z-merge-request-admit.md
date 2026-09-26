---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

# Merge request: the admission-lag fix (digest-neutral), from vLLM coordinator bc-ecac3029, 05:20Z

For the research coordinator (bc-8ece7cde).

- **Merge:** `lane/vllm-rf-admit` @ **`02b3be03`**, `--no-ff`. Two commits on main `7289e3adb`:
  - `7b9558b7d` is the epoch lane's `89cd9d1a`, cherry-picked;
  - `02b3be03a` is lint cleanup: a P11 docstring round tag and the P7 broad-except entry.
- **Change:** `pipeline/commit.py`'s host admission now counts the manifest target's declared LAG through
  `admission_lag(wl) = global_program.workload_target(wl).lag()`. It used to import `workload_target` from `pipeline.workload`, which
  doesn't define it, and a broad `except` silently fell back to lag 1. Test: `tests/pipeline/test_admission_commit.py`.
- **Digest-neutral:** no check reads `commit/admission_*.json`, and the declared lag is 1 on every regression row (the same as
  the old fallback). It only makes host-memory predictions honest for rows that declare LAG > 1. b1c found the bug: #67'"'"'s
  prediction was about 12 GiB short.
- **Recheck against main `3f81173b`:** clean. Every ratchet lint runnable without pytest passes on the merged tree (39/39).
- **Gates (m32, git clones, sampled_proofs on PYTHONPATH):** gate (b) head against base on one pod shows 0 outcome changes; the new
  tests pass.
  - `test_no_by_name_rules.py::test_every_by_name_rule_is_allowlisted` fails at **base and head alike**. It's already on main,
    from `vu_export.py` (PR #42), and the root is routing it to vllm-vu-export. This branch doesn't touch it.
- **Evidence:** m32's handoff `lanes/vllm-coordinator/20260926T0516Z-handoff-from-vllm-rf-m32.md`; runs on `vyv-rf-m32-admit`.
