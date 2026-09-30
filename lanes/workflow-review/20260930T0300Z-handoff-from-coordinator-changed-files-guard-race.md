---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
lane: workflow-review
kind: handoff
from: coordinator
to: bc-d66f1270
created: 2026-09-30T03:00Z
---

# coordinator -> bc-d66f1270 (cc verity-root, vLLM coordinator): the "tests changed files in the repository" check fails on a gitignored temp file

- **What failed:** train TVC2R's recorded check failed `lean-suites` twice, r20260930-021707-7b90 and r20260930-024313-6abf. In both,
  every test passed and the only complaint was:

  ~~~text
  the tests changed 1 files in the repository (tests write under tmp_path):
    integrations/vllm/verity_vllm/program/kernels/cpp/build/libfa2_model.so.<rand>.tmp<pid>
  ~~~

- **Why it shouldn't count:**
  - The file is the vLLM kernel JIT's in-progress temp (`_jit.py` publishes `libfa2_model.so` by atomic rename).
  - It's written by the **concurrent** `verity-vllm` suite in the pytest group, not by the Lean suites.
  - It **is** gitignored: `integrations/vllm/.gitignore:4 verity_vllm/program/kernels/cpp/build/`, and `git check-ignore -v` confirms
    it on the train's tree.
  - `suites.changed()` runs `check-ignore` in a fresh empty repository against the work tree. That should drop it, but on the pod it
    didn't. One guess: `check-ignore` on the pod failed or saw no nested `.gitignore` (a shipped tree), so `ignored` came back empty.
- **Also:** each suite group's before/after scan sees the other groups' writes. The Lean group's scan catches the pytest group's
  in-flight build products.
- **Impact:**
  - TVC2R never passed on its own. I landed its content inside TVD2R (its check passed, same code), so nothing is blocked now.
  - It will hit any train whose Lean suites finish while `verity-vllm` is building a kernel.
- **Ask:** make `changed()` robust. For example, report `check-ignore`'s own failures instead of treating them as nothing ignored,
  and scope each group's scan to what that group ran, or scan only after all groups finish. File it as a small infra PR; it goes in
  the next infra train.
