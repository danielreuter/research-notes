---
lane: v3-scout
kind: report
created: 2026-09-23T21:00Z
status: superseded
---

CHECKPOINT none (00:03Z) [superseded] by v3-scout-2 (coordinator)
CHECKPOINT 5e6b3e3 (21:11Z) H100 l=16384 p4 done, all Rust-accepted + pinned: bf16-hopper-v3 0.2406 s vs v1 0.2955 (v3 −19 %); fp8-hopper-v3 0.1444 vs v1 0.1152 (v3 +25 %: v3 hints 0.050 s of the wall); p8 + l=32768 running; A100 chain running (bf16-ampere-v3 vs bf16-ampere, then vu.py control); pod-side custody works (art:4fb1ce07 PRESERVED, laptop catalog remote=1).
CHECKPOINT 5e6b3e3 (21:03Z) worktree ~/projects/verity-main-wt/v3-scout on lane/v3-scout @ 5e6b3e3 (= lane/open-fixes tip, no commits yet); H100 vy-v3-scout-h100 (x2b0ahxr8g7k0s, 81559 MiB reference, EPYC 9554) bootstrapped 20:58Z, 16-run chain started 21:00Z; A100 vy-v3-scout-a100 (u3nsufkequsg76, A100-SXM4-80GB reference, EPYC 7742) bootstrapping.

# v3-scout — tonight's private-safe headline configs (v3 vs v1, H100 + A100)

## Setup

* Base `lane/open-fixes` @ 5e6b3e3 (a0ff818: per-stream hint CUDA graphs for `privsel/hints.py` / `pubsel/hints.py`).
* Pods (created with `research pods create ... --require-reference-part`, qol tooling):
  * `vy-v3-scout-h100` = RunPod x2b0ahxr8g7k0s, NVIDIA H100 80GB HBM3 81559 MiB (reference), driver 570.211.01, host AMD EPYC 9554
    (nproc 256 visible), created 20:55Z. Bootstrap = `lane/qol` `pod_bootstrap.sh` (RELS=bf16-hopper,fp8-hopper,bf16-hopper-v3,
    fp8-hopper-v3, NS=4096): torch 2.6.0+cu124, GPU Merkle blake3, `ligero-verify` sha256 ba724c69…, BOOTSTRAP_OK 20:58Z.
  * `vy-v3-scout-a100` = RunPod u3nsufkequsg76, NVIDIA A100-SXM4-80GB 81920 MiB (reference), host AMD EPYC 7742, created ~21:00Z.
* Env on every run: `LIGERO_GPU_STRICT=1 LIGERO_GRAPH_STRICT=1 OMP_NUM_THREADS=4`. Scripts: `evidence/chain.sh`.
* Bench line (every cell): `run.py --relation <rel> bench-vu --zk --mode interactive --batch <l> --pipeline <N> --total-vus 4096
  --reps 3 --device cuda --instances-cache /workspace/instances-cache --dump-dir <d> --dump-reps 1 --out <r>.json`; then
  `ligero-verify batch --system <d>/system.bin --dir <d>/rep1 --target-bits 128 --threads 8 --json …`. Local coins
  (`mode=local-coins`), drill-downs.

## Which runner supports v3 + pipelining (A100 question)

`vu.py` (`--relation bf16`, the current A100 bare cell 0.781 s) proves only the v1 Ampere unit and is sequential (`--pipeline` is
a no-op there). The v3 relations exist only on the generic chain runner (`relchain.bench_vu_rel`, `--relation bf16-ampere-v3`),
which is also the only one with `--pipeline N`. The like-for-like v1 on that runner is `--relation bf16-ampere --root <bench-instances/v1>`
(the same Ampere unit on the frozen `vu-k1536` set). Caveat for Table 2: `bf16-ampere-v3` (like every v2/v3 relation) proves a
SYNTHETIC instance set (`instances_digest` = sha256 of "<rel.name> synthetic|seed=…|n=…|K=…"), so its
`instances.manifest_sha256` differs from the frozen set's; see the results below.
