---
cursor:
  subagentId: "bc-2a9978cc-cafd-5d88-a4de-888a71d85659"
lane: coordinator
kind: handoff
from: flock-zk (bc-2a9978cc)
to: research coordinator (bc-8ece7cde)
created: 2026-09-28T08:15Z
---

# Merge request: #229 (M1/M2's zero knowledge on M0's GPU prover), then #252 (the region-word check)

Daniel's go: hand #229, then #252, to you now that #192 and #193 have landed. Both are marked ready. Merge #229 first:
#252 is stacked on it.

## (a) #229

- **The PR:** [#229](https://github.com/danielreuter/verity/pull/229), branch `cursor/flock-zk-gpu-5659`, head
  **`19720b14e907d829ff2a675be7bd8da055b85d92`**, into `main`. Its base was retargeted from #193's branch to `main`.
- **It merges cleanly with `main` at `3ba4d8b3`.** It carries M1 (#123 `fe35d67d`) and M2 (#138 `2798c21a`), both granted,
  through #150's merge of M2 with M0, on M0's #192 and #193 (in `main`). #123, #138 and #150 need no separate merge.
- **No statement or pin change.** The device prover's proofs and transcripts are byte-identical to the CPU prover's
  (`gpu_proofs_match_cpu`), so the red team's grants and the public-circuit ZK proof cover it (`docs/zk-proof-public.md`
  gap 4). The red team was told and asked for no review.
- **Evidence:**
  - RTX 4090 pods under `vy-fzk-gpu-` (guarded, $1.13 in all, terminated): `selftest --zk --gpu` 32/32 on RoPE m = 25 and
    34/34 on GEMM m = 26, with `gpu_proofs_match_cpu` passing on both, and `zkaudit --gpu` clean.
  - Overhead against M0, after the host overlap: +41% at RoPE m = 25, +49% at GEMM m = 26, +31% at RoPE m = 27. Details are
    in `private/flock-zk-gpu-results.md`.
  - On `main` merged with #229 (CPU): RoPE and GEMM `selftest --zk` all pass with unchanged pins. `pytest
    backends/flock/tests tools/research/tests/test_repo_replicas.py tests/test_repository.py`: 214 passed, 18 skipped.
    The full `check` hasn't been run; please use the pipeline's.
- **Compile fixes for #138 and #150, noted here since #229 supersedes both:**
  - M2's `coin_tree.rs` didn't compile without the `sha512` feature, which M0's older GPU binaries build with
    (`20-gpu-link.sh`). #138 and #150 carry the break, since neither was built on a pod. #229 fixes it, with the SHA-512
    build unchanged.
  - The GPU selftest's case processes dropped `--zk`. #229 fixes it; it only matters with the port.

## (b) #252, after #229

- **The PR:** [#252](https://github.com/danielreuter/verity/pull/252), branch `cursor/flock-zk-statement-v2-5659`, head
  **`2198c19c1a3cdc1771aa31f7bb3832208a3e366c`**, stacked on #229. Retarget it to `main` once #229 is in.
- **The red team granted it at `2198c19c`.** Please merge exactly that head.
- **Contents:** the region-word check in the Rust `Stmt::new` (the red team's C3; `docs/region-word-check.md`), and coin-tree
  v2's v1 regression test. It only refuses statements, and no digest changes.

## What comes next, not for merging yet

[#258](https://github.com/danielreuter/verity/pull/258) is stacked on #252. It is coin-tree v2's prover side and Rust server
(the spec is granted; the implementation goes to the red team). It is still a draft.
