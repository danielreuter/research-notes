---
lane: flock-backend
kind: handoff
from: coordinator (bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628)
created: 2026-09-26T02:40Z
---

# Integrate your tip and flock-gpu-link's with main tonight, then hand me the merge request

The root wants the code behind the published Flock cells on main tonight: the bf16-ampere, fp8-hopper, NVFP4-unit and
bf16-hopper-wgmma pins, the SHA-256 GPU witness, and `register --lane`. bench-spine's PR #47 wires `stage()` against it.
I tried the merge, and neither tip merges cleanly into main `c79005af`.

## What conflicts

- **`cursor/flock-backend-4983` @ a9d13f68** conflicts in 8 files, mostly against PR #41 (Flock over vllm-v1, merged at
  1563347f).
  - `live/src/gpu.rs` and `cuda/prove_chunk.cuh` have two `ChunkParams` layouts:
    - main: `sha256: i32` with `*const u64` host pointers, used by `prove_vllm`;
    - yours: `sha`, `sha_mid` and `sha_pad` with `*const F128`.
    `statics_with` versus `statics_for` also conflicts.
  - `live/src/lib.rs`: main's `Prime` message sits beside your `Ping`. Keep both.
  - `python/verity_flock/instances.py` and `bench.py` have two `--scheme` axes:
    - main: `frame-v3 | vllm-v1`, which picks the statement;
    - yours: the row-leaf schema, `blake3 | sha256`.
    Both are needed. Keep `--scheme` as main's and add yours under another name, for example `--leaf blake3|sha256`, or
    fold both into one choice list. Just make sure `30-cell` / `40-vllm-v1` and `31-replay` pass the right one.
  - `backend.py`: your branch predates the `verity.verification` → `verity.proofs` rename (#29). Use
    `verity.proofs.target`.
  - `register.py`: yours, `a.lane` as a required flag.
  - `tests/test_backend.py`: keep both sides' tests.
- **`cursor/flock-gpu-link-797a` @ 758a8edf** (Chunk(n)) conflicts with main in the same `gpu.rs` and `prove_chunk.cuh`.
  red-team-flock is reviewing Chunk(n) now. Merging its code is fine; its cells still need the grant before they render.

## The ask

1. Merge `origin/main` (c79005af or later) into `cursor/flock-backend-4983`. Merge `cursor/flock-gpu-link-797a` @ 758a8edf
   too, or tell me to take it separately after flock-gpu-link does the same. Use one `ChunkParams` for every layout: the
   note said the branch that merges second takes the other's names, so use main's `sha256` for the flag and keep your
   `sha_mid` / `sha_pad`.
2. Gate on the merged tip. Use a GPU pod, because the CUDA struct changed under both provers, and keep it short (about $2):
   - CPU selftests at 8 and 64 VUs for pure bf16-hopper, fp8-ada, fp8-hopper and bf16-ampere (BLAKE3 and SHA leaves),
     plus `flock-vllm-v1` 22/22;
   - GPU selftests at 8 and 64 VUs for one BLAKE3 layout, one SHA-256 layout and `flock-vllm-v1`;
   - `backends/flock/tests` and `backends/numerical/tests/bench`;
   - a `31-replay.sh` of one published cell, to show the replay path still accepts.
3. Push, then send a merge request to `lanes/coordinator/` with the tip, the gate run ids and anything behavioural. I gate
   and merge `--no-ff`.

Checkpoint WAITING on the pod run and end the turn; don't wait in-turn.
