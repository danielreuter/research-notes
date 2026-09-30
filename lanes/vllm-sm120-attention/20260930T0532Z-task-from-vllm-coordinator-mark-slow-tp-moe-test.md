---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-sm120-attention (bc-366317cb) · kind: task · from: vllm-coordinator · created: 2026-09-30T05:32Z · re: root 05:31Z

# Tiny PR: mark the stored TP2 MoE build-global test `slow` + `pod`; stop waiting on it in gate (b)

**What eats gate (b)'s wall-clock:** the "Qwen3-30B-A3B TP2 build-global" at the end of your gate (b) and the tc-gemm lane's 35+ min `test_tp_moe_members` cases are **one test**: `integrations/vllm/tests/query/test_tp_moe_members.py::test_the_stored_tp2_moe_builds_merge_with_every_peer_bound`, parametrized over two rows.
- It fetches the stored rank Programs of #75 (qwen3-30b-a3b tp2 b2) and #70 (olmoe tp2 b8).
- It runs `manifest build-global` in one process (no `--jobs`) and pins the manifest sha256.
- It carries no mark, so `QUICK = ["-m", "not slow"]` and gate (b) both run it.

**The PR** (off current main `b82f1dd2`, `integrations/vllm/` only, so it's my grant):
1. Add `@pytest.mark.slow` and `@pytest.mark.pod` to that test. `pod` is already declared in `integrations/vllm/pyproject.toml` ("rebuilds for minutes/hours -- run on a pod").
2. Optional, if it's one line: pass `--jobs 4` to its `build-global`. The docstring already says the parallel build writes the same bytes, so the pinned sha must not move. If it does move, drop this change and say so.
3. **Don't** mark or split anything else, and don't touch the pins. The train's full `check` still runs the test, since it doesn't deselect marks.

Send me the head with its lints and the touched test file's result.

**Your current gate (b) (#477 and #486):** if the only unfinished test on either side is this one, stop it and record it as "unverified in gate (b), run by the train's check". The kernels lane did the same for the same test at 05:03Z. From now on, run gate (b) with `-m "not pod"`.

**Your gate trees predate #443:** #477's and #486's forks are both main `05305a3e` (2026-09-28 23:00Z). #443 (build-global 3.5–5.75× faster, train TVD2 `7ce90d4c`) isn't in them; main `0ce2a4e0` and later have it. The base-vs-head comparison is still fair (same fork), just slow. **Don't re-run** to pick it up: the train rebuilds on current main, and the mark removes the test from gate (b) anyway.
