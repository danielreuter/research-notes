---
id: 20261001T0759Z-handoff-from-proofs-verify-overlap-session-preflight-run-spec
campaign: overnight
lane: proofs
kind: handoff
status: open
repo: verity
origin: proofs-verify-overlap (bc-96b9bb72-2593-562d-97c6-7c9f8d32b77d)
---

# The confirming run for one preflight check per GPU session: K=2048, 10 points, tree `4ea79db79` (not submitted)

This is the spec for the research owner's yes (your Slack thread `1790833483.081999`). Nothing is submitted; the two job specs
are staged on node 1 and go into `/workspace/jobs/ready/proofs-verify-overlap/` only when you relay the yes.

## The run

- **Question:** does running the K=2048 BF16 point as one GPU session of 10 identical points under one preflight check
  bring its GPU-held seconds per point from 82.8 s (step 5, `r20261001-064454-9419`) to about 45 s (47 s counting the
  custody tail), with every point's statement digest and proof bytes equal to step 5's?
- **N = 10, K = 2048, hillclimb step 8** (the K=2048 roll-up already holds steps 0–7).
- **Tree:** `/workspace/research/trees/proofs-verify-overlap-k` at `4ea79db79` (branch `cursor/proofs-verify-overlap-95d4`,
  clean). The build is `6322ab823`, `b2c049ddf` and `4ea79db79` on top of the rename (`07f06b6b5`).
- **Two jobs, as in step 5:**
  - The verifier pod (0 GPUs, 16 CPUs, 100G): it builds the binaries, stages the preflight check's and the step's statements,
    and serves every session. Its 11 processes are bounded for all 10 points (250 sessions) and the preflight check's one.
  - The GPU job (1 GPU, 16 CPUs, 200G), placed once both address files exist and `provers` reads cpu ≤ 32. It runs one
    preflight check, then the step's statement 10 times back to back.
- **Settings:** step 5's, plus `POINTS=10` on both jobs:
  - both: `K=2048 CPUS=16 WARM=1 RUNS=24` (25 sessions per point) and `FC_VERIFY_AHEAD=10`;
  - the verifier pod also: `FC_VERIFY_SERVERS=11 FC_SERVE_WAIT_S=2400`;
  - `VERIFIERS=/workspace/jobs/proofs-verify-overlap/verifiers/s10-4ea79db`.

  I kept 11 verifier processes so the per-point term compares with step 5. proofs-arch's sub-second verifier
  (`note:20261001T0741Z-handoff-from-proofs-arch-verifier-now-sub-second`) suggests one or two would do, but that is a
  separate question.
- **Specs:** `/tmp/pvo-specs/pvo-k2048-s10-serve-4ea79db.json` and `/tmp/pvo-specs/pvo-k2048-s10-gpu-4ea79db.json` on node 1.

## Expected

| GPU-held seconds | per point | the session (10 points) |
|---|---|---|
| to the last point's metrics | 44.7 (40.5 + 42.3/10) | 447 |
| with the custody tail (infra's DCGM view) | 47.1 (40.5 + 66/10) | 471 |

- **Where the numbers come from:**
  - 40.5 s is step 5's per-point sweep (P6–P13 in the phase report).
  - 42.3 s is its pod start and preflight check (P1–P5).
  - 66 s adds step 4's 24 s custody tail, which the session pays once.
- **Not counted:** the faster verifier now in the tree could shorten the warm and last verdict waits. Those were 6.1 s of
  each point in step 5 (P9 + P11).
- **GPU:** about 0.13 GPU-h.
- **Verifier memory:** the processes serve the points one after another, so the peak stays at one prover's sessions (step
  5's 11 processes: about 43 GiB in the cgroup, against 100G).
- **Identity:**
  - Every point's statement digest should equal step 5's (`7f39853935e48dec…`), with 963794 proof bytes per rep.
  - The preflight check should pass all three cases, and every point's key should equal the check's.
  - Since step 5, the code changed only on the verifier's side (its lincheck, the C0 check, the fold, its timers) and in the
    records. A digest or proof-byte difference would be a finding.
- **Node 1's window:** submitted on the yes, both jobs end long before 5:05 AM PDT; nothing goes in after 5:05 that could
  run past 5:35.

## What it records

The GPU job's Attempt declares these outputs, in order:

- `preflight` (`preflight-record/v0`), the session's one preflight check;
- per point, `result-<i>` (`bench-point/v1`, its contract result; the tables read `bench-result/v1` only), then
  `hillclimb-<i>` (`hillclimb-point/v0`). Both cite `refs.preflight`, which resolves at publish to the preflight output's
  `art:` id, and the hillclimb record also cites its own result.

The Attempt's `result.json` is the session's (`hillclimb-session/v0`):

- It passes only if the preflight check and all 10 points passed.
- Its measurements are `hill.points_passed`, `hill.gpu_held_s_session`, and the medians over the points of
  `gpu_held_s_amortized`, `gpu_held_s_point`, `t_session_s_per_vu`, `overhead` and `gpu_util`.

Each point's record holds:

- `point {index, of}`;
- `preflight {output, record_sha256, status, key, key_matches}`, where the key is the binaries' sha256, the `FC_*` settings
  and the GPU;
- `gpu_held_s_point`, `gpu_held_s_session` and `gpu_held_s_amortized`. The last is its sweep plus an equal share of the
  seconds outside every point, and the shares sum to the session's;
- `gpu_held_s_job: null`.

A point whose key differs from the check's fails itself, and with it the session. After it lands I'd append the 10 points
to the K=2048 roll-up as step 8; `rollup` now keeps one point per run and index. For the overnight file's
`gpu-held-per-job` row I'd suggest the median `gpu_held_s_amortized`; that row is your call. The console's reader change
is in `note:20261001T0805Z-handoff-from-proofs-verify-overlap-session-points`.

## Checked locally (CPU only)

A two-point session ran at K=64 (`N=32 WARM=1 RUNS=3 FC_VERIFY_AHEAD=2 FC_VERIFY_SERVERS=3`), a verifier-pod job beside a
prover job:

- **The verifier pod** served 8 sessions (2 points × 4) on its 3 processes. All were accepted, none timed out, and it
  withdrew its address files.
- **Both points** had keys equal to the check's and cited the same preflight record. Their amortized held seconds,
  77.53 + 77.18, equal the session's 154.71.
- **The result failed, as it must on a CPU:** a CPU run has no GPU cases, so its preflight check fails.
- **Replayed with a record whose GPU cases pass,** both points and the session passed, both points' contract results
  conformed, and the outputs published into a scratch store with `refs.preflight` resolving to the preflight artifact.

The dry run found one bug, now fixed (`4ea79db79`): the key mapped binaries by name, and a prover build and a selftest build
can share one.

**Tests:** new tests cover the session, the key refusal and the roll-up (`backends/flock/tests/test_gemm_hill.py`), and the
verifier pod's bounds (`test_class_statement.py`: 11 processes, 25 sessions, 8 points). `suites.py flock --quick` gave 258
passed and 118 skipped; the numerical and repository suites pass.

## After this one

- **The other K:** sessions at K = 4096, 8192 and 16384, one preflight check each, each its own pair of jobs. I'll write
  their specs from the latest bf16-hill records at those K once K=2048 confirms the per-point term.
- **Then the how-to for bf16-hill and flock-fp.** `origin/cursor/proofs-flock-fp-95d4` also edits `74-gemm-hill.sh` and
  `gemm_hill.py`, so its merge with this branch will conflict there.
