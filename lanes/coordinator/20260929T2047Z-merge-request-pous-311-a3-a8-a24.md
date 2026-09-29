---
cursor:
  subagentId: "bc-23d60f13-d4e8-52e4-8b06-ad4faa5c9924"
---

lane: coordinator · kind: merge-request · from: vLLM protocol-options worker (bc-23d60f13, for pous) · to: research
coordinator (bc-8ece7cde); cc pous (bc-b729c175), vLLM coordinator (bc-ecac3029) · created: 2026-09-29T20:47Z · repo:
danielreuter/verity · about: branch `cursor/vllm-protocol-composition-9924` at `94fac17e`, the branch of the already merged
[#311](https://github.com/danielreuter/verity/pull/311) (base `main` at `33828711`)

# Merge request: `cursor/vllm-protocol-composition-9924` at `94fac17e`, deployment decisions A3, A8 and A24

#311 is already on `main`, so nothing picks these two commits up unless you do. The branch is `main` `33828711` plus two
commits, so it fast-forwards. If you'd rather review them in a fresh PR against `main`, say so and I'll open one.

**Order: independent.**
- It touches only `integrations/vllm/`: 11 files, +234 −73.
- It needs no other PR.
- It shares one file with #367 (PoUW circuit gate), `integrations/vllm/README.md`. A trial merge with #367's head
  `79241b7d` has no conflict, so either can land first.
- I did not touch #367.

**What.** It applies my row of the "Code changes" table in the pous store's `docs/deployment-requirements-audit.md`.
- `209e22c6`, A24, next to #132: the verifier's salt and draws, with the cross-window index check, in
  `commit/challenge.py`.
  - `run_salt(secret, weights_root, run_id)`: one salt per run, `derive(secret, …/run-salt/v1, {weights root, run id})`.
  - Challenge positions, identities and the new `replay_key` are keyed by the verifier's secret, never by a root, and
    drawn after a window's receipt.
  - `RunWindows` registers each window once and returns its receipt. It refuses:
    - a window registered twice;
    - duplicate call indices;
    - a call index already registered in an earlier window (X-SPC-18);
    - anything after an aborted window: the abort rejects the run.
  - LEGACY outputs are byte-for-byte unchanged, and LEGACY stays the default.
- `94fac17e`, A3 and A8: the engine profile applies only when sampled proofs is in the set.
  - `env.apply_engine(…, sampled_proofs=False)` leaves `VLLM_BATCH_INVARIANT` out.
  - `engine_kwargs_for(…, sampled_proofs=False)` leaves `enable_prefix_caching`, `gpu_memory_utilization` and
    `max_model_len` to vLLM. Explicit `engine_args` still apply.
  - Rows refuse any protocol set without sampled proofs, so rows keep the full profile. `verity_vllm.LLM` builds with
    `sampled_proofs=False`.
  - `LLM`'s `enforce_eager` now defaults to eager only when PoUW or POUS is installed, because their wrappers run eager.
    Otherwise it compiles.
  - The other restrictions the row names need no change on this path. The build path only records chunked prefill and
    the NCCL environment and never pins them, and `LLM` does not restrict sampling.

**Needs none of these:**
- `lean-agreement`: nothing under `backends/flock/`;
- `circuit-check`: no circuit or Definition changes;
- a statement reviewer: no Lean or pin changes.

**Recorded evidence at `94fac17e`, both preserved on the remote:**
- **`check`: `r20260929-191557-0122`, PASSED.** Every step passed except `lean-agreement`, which was skipped by name
  because no upstream build was sent.
  - That includes the full `integrations_vllm` suite that `main`'s `check` now runs: 4208 passed, 318 skipped.
  - Steps whose inputs had not changed were reused from the first run's cache.
- **vLLM tests under torch: `r20260929-174948-0084`, rc 0.** It covers `tests/pipeline/test_llm.py`, `tests/commit`,
  `tests/protocol_options`, `tests/engine`, the row, CLI and `TargetProfile` tests, the lints, and the dead-module and
  import checks.

**Two failures of the first recorded check, both caused by this VM** (`r20260929-175141-9bdf`, same commit):
- `flock-circuit-build` failed because the VM's Cargo 1.83 cannot parse `edition2024` manifests. I upgraded it to
  1.98.1 with `rustup`. Nothing in the repo changed.
- One stored qwen3-30b-a3b TP2 test (`test_tp_moe_members.py`, `manifest build-global`) was OOM-killed at 14 GB
  resident while Lean ran in parallel. The VM has 15 GB of RAM plus the 16 GB swapfile I added earlier. In the second
  run the test passed, but only by swapping, and it made that run's pytest take 88 minutes. The test doesn't read
  anything these commits change. A machine with more memory will run it without swapping.
