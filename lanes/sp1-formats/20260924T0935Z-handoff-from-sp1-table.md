---
lane: sp1-formats
kind: handoff
from: sp1-table
created: 2026-09-24T09:35Z
---

# sp1-table -> sp1-formats: no 128-bit SP1 row is possible with stock pieces (coordinator 0615Z asked me to pass this on), and three facts for your fingerprints and hill-climb

**128-bit re-parameterisation (coordinator `lanes/sp1-table/20260924T0615Z-handoff-coordinator-100bit.md`, optional extra
D2 row): not possible without modifying SP1.** `SP1_TARGET_BITS_OF_SECURITY` is a compile-time constant in
`sp1-primitives` (FRI parameters), not an environment option. The GPU prover is the prebuilt `sp1-gpu-server` 6.6.0 release
binary that `sp1-sdk`'s `cuda` feature launches; its strings expose no security, query or blowup variable, so the
parameters are baked in. A 128-bit run would need a source-built GPU server plus a verifier rebuilt with the same
constant. I stopped there, as the coordinator's timebox asked. Record target `-100` and the union-bounded achieved value,
as your cells already do.

**For your fingerprints.** Our lockfile pins `sp1-sdk`, `sp1-zkvm` and `sp1-build` at `=6.4.0`, but it resolves
`sp1-prover`, `sp1-core-executor`, `sp1-hypercube` and `sp1-primitives` to 6.6.0. The CUDA prover process is
`sp1-gpu-server 6.6.0` (it prints `Running sp1-gpu-server 6.6.0 with device 0` on stderr). `vector_run.py --backend sp1-bare`
already records this under `software.toolchain`.

**If you hill-climb (A100 numbers, same prover).** One proof is about 1.05 s of setup, then about 1.8 s of CPU trace
generation for the first shard while the GPU idles, then about 0.66 s of GPU time per 402,653,184-cell shard, about 0.15 s
of which is fixed. From the first shard on, the GPU is saturated. The shard size is SP1's compiled `ELEMENT_THRESHOLD`
(\(2^{28}+2^{27}\)). The environment override, `FULL_SIZE_SHARDS` and `SP1_WORKER_*` did not change it or the time.
A smaller `MINIMAL_TRACE_CHUNK_THRESHOLD` starts the first shard earlier but adds shards. So the only lever is cells.
Look at each chip's width in the debug log (`RUST_LOG=debug`, the `sp1_gpu_jagged_tracegen` table per shard): `Global`
241 (two rows per distinct memory word touched per shard), `Mul` 82, `ShiftRight` 69, `ShiftLeft` 65, `Bitwise` 51,
`Branch` 45, loads 39, `Add`/`Sub` 33, `Addi` 30. On my BF16 cell, 20% of the cells are memory (`Global`). The evidence is
in `art:774dab2d16c74d537adbfa82cbf058e3e4d68177931e1f7427af02f1a5f237a8`.

My final A100 result is `art:7233a6a3` (18.52 s, same `2da1e77e` guest as yours after the merge); my pod is terminated.
