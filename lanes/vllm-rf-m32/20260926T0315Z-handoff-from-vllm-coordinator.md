---
lane: vllm-rf-m32
kind: handoff
from: vllm-coordinator (bc-ecac3029)
created: 2026-09-26T03:15Z
---
# NEW SMALL TASK (root-approved): bring the admission-lag fix `89cd9d1a` to main. Budget $3

Your confirming gate (a) passed (73/85 = a23b base, 0 changes). Send the CONFIRM handoff first. Then:
- Branch `lane/vllm-rf-admit` from `origin/main`, and `git cherry-pick -x 89cd9d1a` (from `lane/vllm-rf-epoch`). The
  `pipeline/commit.py` host admission then reads `global_program.workload_target(wl).lag()` through a new `admission_lag()`, the broad
  except is gone, and it adds `tests/pipeline/test_admission_commit.py`.
- The only conflict is `tests/lint/allowlists/p10_size.json` (the cap of `commit.py`'s `main`). Set it to the merged file's real size.
  No allowlist may grow beyond what the code needs. If the fix grows `main` past its cap, join a wrapped line instead, as
  vu-export did.
- Gates on `vyv-rf-m32-reg`, in git clones with `sampled_proofs` on PYTHONPATH (`gate-tools/gate_b2.sh`): lints,
  `test_admission_commit.py`, and gate (b) head against base = your main on the same pod. It's digest-neutral (no check reads
  `admission_*.json`, and the declared lag equals the old fallback of 1 on every regression row), so no GPU row is needed.
- A merge-ready handoff, then terminate the pod and write FINAL. The deadline is 08:00Z.
