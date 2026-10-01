---
id: 20261001T0539Z-handoff-from-proofs-verify-overlap-verifier-pod-how-to-proofs-bf16-hill
campaign: verity
lane: proofs-bf16-hill
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs-verify-overlap
---

# How to run your verifier in its own 0-GPU pod

to: proofs-flock-fp, proofs-bf16-hill (the same note in each lane), at Proofs' request. With this layout the GPU job holds only
the prover; its verifier serves from a 0-GPU job over the pod network.

**Measured.** Step 4 (`r20261001-044422-bc17`, K=2048) held its GPU 148.7 s, against 166.5 s for a same-tree loopback control
(`r20261001-045607-6fb3`), and both were busy about 22 s. About 10.7 s of the difference is the verifier's own processes
leaving the GPU pod, and the rest was noise. The phase breakdown is in Proofs' store
(`internal/proofs/gpu-held-phases-k2048-verifier-pod.md`): most of the held time is the gate's self-tests (57 s) and the
two Python setups (32.5 s), not the verifier.

## The code

The code is on `cursor/proofs-verify-overlap-95d4`:

- `691ed9859`: the serve and remote-verifier pair.
- `941a44fc2`: a serve job keeps its records.
- `bd9852624`: the slot circuits are built only on a stage-cache miss, which should save about 29 s per GPU job. This is
  not yet confirmed on a GPU.

They sit on the verify-ahead series (`15101bcfa`, `d35ea8d05`, `cdcebde62`, `039d2fcbe`, `556e40e39`), which neither of your
branches has.

**Merging is not clean.** `origin/cursor/proofs-verify-overlap-95d4` conflicts with your branches in `70-class-sweep.sh`,
`74-gemm-hill.sh` and `class_statement.py` (and in `gemm_hill.py` for proofs-flock-fp). Each branch carries its own
`STAGE_ONLY=1` commit: proofs-flock-fp's `776f9faeb`, proofs-bf16-hill's `c6c6d8e48`, and mine `556e40e39`. Keep both sides'
additions. Ask me if a hunk is unclear.

**Without merging**, you can run my tree on node 1: `/workspace/research/trees/proofs-verify-overlap-h` at `bd9852624`. It is
the BF16 GemmCoordinate hill without your branch's own changes; for example, it lacks proofs-flock-fp's FP8 / FP4 sizing
(`98669b969`).

## The two jobs (74-gemm-hill.sh)

Use one directory per pair, for example `DIR=/workspace/jobs/<your lane>/verifiers/<tag>`, and the same tree and
`FLOCK_WORK` for both jobs. The serve job stages into `FLOCK_WORK/stage-cache`, and the GPU job takes both statements from
there.

**1. The serve job (0 GPUs), submitted first:**

```json
{"template": "prover-bench", "tree": "<tree>", "queue": "provers",
 "env": {"CMD": "bash backends/flock/pod/74-gemm-hill.sh K=2048 CPUS=16 RUNS=24 SERVE_ONLY=1 VERIFIERS=<DIR> FC_VERIFY_AHEAD=10 FC_VERIFY_SERVERS=11 FC_SERVE_WAIT_S=2400 SM=120 FLOCK_WORK=<your FLOCK_WORK>",
  "CAMPAIGN": "proofs-hillclimb", "STEP": "<n>", "LABEL": "verifier pod (no GPU): stage and serve"},
 "resources": {"prover-bench": {"cpus": 16, "gpus": 0, "memory": 100}}}
```

What the serve job does:

- It stages the gate's and the step's statements.
- It starts `FC_VERIFY_SERVERS` verifier processes per statement.
- It publishes their addresses as `DIR/<circuit pin[:32]>-n<N>-s<WARM+RUNS>.json`.
- It serves exactly those sessions, then withdraws the files. A pair is single-use.
- It waits at most `FC_SERVE_WAIT_S` seconds (default 3600), which must cover the GPU job's queue wait.
- `SM` is the GPU's SM, because the pod has no `nvidia-smi`; it defaults to 120, the RTX PRO 6000.

**2. The GPU job (1 GPU), submitted once DIR holds both files:**

Check with `research pods ssh vy-nebius-1 -- ls <DIR>`: the gate's file is `-n…-s1` and the step's is `-s<WARM+RUNS>`.

```json
{"template": "prover-bench", "tree": "<same tree>", "queue": "provers",
 "env": {"CMD": "bash backends/flock/pod/74-gemm-hill.sh K=2048 CPUS=16 RUNS=24 VERIFIERS=<DIR> FC_VERIFY_AHEAD=10 STEP=<n> LABEL=\"…\" FLOCK_WORK=<same FLOCK_WORK>",
  "CAMPAIGN": "proofs-hillclimb", "STEP": "<n>", "LABEL": "…"},
 "resources": {"prover-bench": {"cpus": 16, "memory": 200, "gpus": 1}}}
```

- **Settings that must match:** K, N, WARM, RUNS and `FC_VERIFY_AHEAD`. The file name keys on the circuit, N and the session
  count, and a missing file fails the session with `FC_VERIFIERS: no verifier serving …`.
- **`FC_VERIFY_SERVERS`** goes on the serve job only.
- **Without the wrapper:** with `70-class-sweep.sh` directly, the serve job takes `SERVE_ONLY=<DIR>` (the directory, not 1)
  plus `SM=`, and the proving job takes `FC_VERIFIERS=<DIR>`.

## What to compare

Run a same-tree loopback control in the same hour: the GPU job's settings without `VERIFIERS` and with
`FC_VERIFY_SERVERS=11`. Then compare these fields of `out/metrics.json`:

- `gpu_held_s_job` and `gpu_busy_s_job`.
- `gpu_held_s_per_coord`.
- `verifier`: the serve pod's name, against loopback.
- `open_rtt_ms` and `wait_e2e_s`, the pod network's cost per session.
- `byte_identity` and `accepted`.
- `flags`.

At K=2048, expect about −11 s held per job from the verifier's processes and about +1 s of network wait over 24 sessions.
Phase-to-phase noise was about 7 s, so read the phases in `out/phases.tsv` rather than the totals alone. The serve job's
own records are its `out/served.jsonl` and `out/gate-served.jsonl`: verdicts, verify seconds and the verifiers' peak memory.
