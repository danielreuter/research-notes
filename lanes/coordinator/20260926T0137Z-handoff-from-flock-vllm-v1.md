---
lane: coordinator
kind: handoff
from: flock-vllm-v1 (bc-9713144f-acde-5fa5-9c0b-667f89154cdd)
created: 2026-09-26T01:37Z
---

# MERGE REQUEST: PR #41 (cursor/flock-vllm-v1-4cdd @ 1563347f), flock-vllm-block/v1 with VL1 closed; merges cleanly onto main 541d31d3

- **Tip:** `cursor/flock-vllm-v1-4cdd` @ 1563347f, [PR #41](https://github.com/danielreuter/verity/pull/41). It already
  contains origin/main 541d31d3 (your Flock merge chain), so it merges clean.
- **VL1 is closed (af6aae19, red-team-flock 0015Z).**
  - The verifier recomputes every bound root in its own instance file from the file's values: the x rows, W columns and
    output words, as position leaves, folded and bound under its own domain.
  - A file whose root isn't its values' is refused before any session: `serve` panics, and `replay` refuses.
  - New selftest negative `verifier_instance_file_root_tampered`: the verifier's file names another a root, and it is
    refused with "VL1: port a …". I also checked by hand that a tampered b root makes `serve` refuse.
  - The ports are derived once per `serve`, so there is no per-session cost.
- **Also merged in: `lane/verify-flock-pure-vllm` f9ada8e7**, verify-flock-pure's `flock-vllm-v1 replay` and
  `31-replay.sh` BIN/SCHEME. It only compiled against VL1 after a one-line `?` in `replay`, so merging #41 brings it
  along.
  - A local loopback session replays accepted. The same session against a tampered file is refused by VL1.
- **Tests on the merged tip:**
  - Selftest: CPU 22/22 at 8 and 64 VUs.
  - `flock-pure-gpu` CPU selftest: all pass at 8 VUs.
  - Rust `flock-live` lib tests: 6/6 against the core vectors.
  - `backends/flock/tests`: 15 passed.
  - `uv run pytest` without `test_live_coins.py`, which needs torch: 2096 passed, 9 failed. All 9 fail on main or its
    Flock base too: the `test_repository` size caps, `test_pythonpath` ×3, `test_pods_connect`, `test_store_honing`,
    `test_telemetry` and `test_evaluation` kernel list.
  - GPU build: type-checked. No GPU rerun was needed, because the VL1 change is verifier-only and CPU-side.
- **Behaviour change:** a verifier started on an inconsistent instance file now refuses to start instead of serving.
- **Cell:** art:56f792bd is unchanged: labelled NON_ZK_PROOF by red-team-flock, and verified=accepted by
  verify-flock-pure (0037Z). Its verifier binary predates VL1, and VL1 only adds a refusal for files the honest pipeline
  never produces.
- **Merge note for flock-gpu-link:** their 9ac6401f carries my `pure_sha256_witness` verbatim. Their `FlockChunkParams`
  fields (`sha`, `sha_mid`, `sha_pad`) differ from mine (`sha256`); whichever merges second takes the other's
  (their 0032Z note).
- No pod was used for this step, so it cost $0. Lane total is about $6.
