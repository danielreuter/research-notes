---
lane: vllm-retire-v1
from: integrator
kind: handoff
---
# Staging moved: 815b837c → 38122d1f (origin/main merged); two vllm facts for your census

- `origin/lane/vllm-cleanup-2` = `38122d1f`:
  - `d46c681f` merges `origin/main` `b761c3a9`, the proof-system work.
  - `38122d1f` adds a comment to `fixtures.toml` (#70's FAIL cause).
- Main's only vllm change is 88e4f7ae (relocatable Builds):
  - It adds `verity_vllm/build_paths.py`. Its one production importer is `verity_capture/experimental/cb_a/global_program.py`, so if your pruning drops global_program, build_paths goes dead with it.
  - It adds `verity_capture/experimental/cb_a/tests/test_build_relocation.py`, which imports `test_global_program_regress`.
  - `lifting/record.py` and `test_lifted_workload_record_real_padrev.py` stay deleted: dead-code-2 wins the modify/delete.
- Gates on the merge match `815b837c`'s failure sets. vllm is 25 F / 11 E, and lints pass 7/7.
- You don't need to merge staging yourself: I'll merge your tip onto `38122d1f`. If you do merge it, expect no conflicts in `integrations/vllm` outside those files.
