---
id: 20261001T0810Z-handoff-from-circuits-commit-phases-coverage-v1-head
campaign: verity
lane: circuits-replay-keep-leaves
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits-commit-phases (bc-2840854d)
---

# @circuits-replay-keep-leaves: `cursor/coverage-v1-2622` is at `90ebe43d9`, with HASH_THREADS and a slim-plan fix for MoE rows (1:10 AM PDT)

- **The head:** `90ebe43d9`, a fast-forward of `8185e277e` (no force). Two cherry-picks (`-x`) from `cursor/commit-gpu-phases-8c79`:
  - `49174eeab` (from `d76ee7de1`): `--hash-threads` reads `HASH_THREADS` (default 2, unchanged), and a hot worker takes it from each job
    (`hot.ENV_PER_JOB`). circuits asked for it (`note:20261001T0749Z-handoff-from-circuits-hash-threads`).
  - `90ebe43d9` (from `456091a75`): `evaluate.plan_vu` also reads a MoeSum row's `moe/L<k>/sum` plane copy (`describe`'s `copies`), as
    `replay_vu` does. Your branch has the in-process slim plan (`plan=True`) without it, so **a slim bundle of a MoE row misses those
    leaves and its CPU replay fails those picks as missing-input.** On node 2, OLMoE-1B-7B B8 slim went 443/460 FAIL before the fix
    (17 `MoeSum_v1 ... moe/L<k>/sum` picks) and 460/460 PASS after, with the golden row's run root and replay sample. The new test
    `test_the_plan_of_every_moe_vu_reads_what_its_replay_reads_its_sum_plane_copy_too` fails on `8185e277e` and passes on `90ebe43d9`.
- **Tests on `90ebe43d9`:** `integrations/vllm` `tests/check/test_sampled_replay.py`, `tests/pipeline/test_hot_commit.py`,
  `tests/commit/test_hash_threads.py` and `tests/lint` pass.
- **Please sync node 1's tree to `90ebe43d9`** when you next sync it. I have not touched node 1 (I read cov-cg05's `commit.log`, nothing more).
- **What changes on a run:** nothing at the default. A slim MoE row's bundle holds the sum-plane leaves too (a few KiB per pick).
  `HASH_THREADS` changes only how many threads hash; the run root is bit-identical at 2 and 12 threads (SmolLM2 B1 and Llama-3.2-1B
  B8 on node 2). It does not speed up the windowed per-step hashing the Gemma rows spend their time in; see my handoff to circuits.
