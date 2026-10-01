---
id: 20261001T0950Z-handoff-from-proofs-verify-overlap-session-specs-k4096-k8192-k16384
campaign: overnight
lane: proofs
kind: handoff
status: open
repo: verity
origin: proofs-verify-overlap (bc-96b9bb72-2593-562d-97c6-7c9f8d32b77d)
---

# GPU sessions at K = 4096, 8192 and 16384, one preflight check each (specs; not submitted)

to: proofs (bc-8416bc72), for the owner's yes, per `note:proofs-verify-overlap/20261001T0803Z-reply-from-proofs-spec-posted-for-owner`.
K=2048 confirmed the session at 37.8 s per point (`note:proofs/20261001T0923Z-reply-from-proofs-verify-overlap-session-run-checkpoints`).

**Ask:** a yes to run these three sessions, one K at a time, each on one of proofs' floor GPUs. The total is about 0.8 GPU-h.
Nothing is submitted.

## What each K runs

- **The baseline at each K** is bf16-hill's most recent node-1 point with the setting common to all three K:
  `FC_VERIFY_AHEAD=4 FC_VERIFY_SERVERS=2`, the verifier in the GPU pod, structured lincheck, column-major fold, commit
  `f12fe3592`. The session uses the same settings and the same statement, plus `POINTS=10`. bf16-hill's newer, unconfirmed
  levers are left out: 8 MB device prefetch, pipeline depth 2, and the hsdma build `2156deb`.
- **Tree:** `/workspace/research/trees/proofs-verify-overlap-l` at `404aa0535`. That is the tree that ran K=2048, plus a
  merge of bf16-hill's flag rules (`a8a3661e2`). Its prover and verifier sources equal `f12fe3592`'s.
- **Two jobs per K:**
  - a staging job (0 GPU, 16 CPUs, 128G, `STAGE_ONLY=1`). My stage cache holds only K=2048: stage keys differ between
    trees for the same statement, so bf16-hill's entries can't be reused;
  - then the GPU session (1 GPU, 16 CPUs, 200G). It runs one preflight check, then the step's statement 10 times back to
    back (`RUNS=24`, 25 sessions per point).
- **The verifier stays in the GPU pod (2 processes),** as in the baselines, so there is no verifier-pod job. A CPU dry run
  of this mode passed on the tree: two points at K=64, 2 loopback processes, both accepted, keys equal to the check's.

| K | baseline (node 1) | its GPU-held s: preflight + sweep | expected per point (amortized) | session | step |
|---|---|---|---|---|---|
| 4096 | step 8, `r20261001-090355-df59` | 99.5: 44.1 + 53.4 | about 58 | about 580 s | 10 |
| 8192 | step 5, `r20261001-085540-cab4` | 167.3: 80.9 + 76.0 | about 85 | about 850 s | 10 |
| 16384 | step 4, `r20261001-090316-6c85` (confirm `r20261001-091637-a0e0`: 297.6) | 268.4: 149.5 + 117.0 | about 132–142 | about 1320–1420 s | 7 |

- **Expected per point** is the baseline's sweep plus a tenth of everything else it held. At K ≥ 4096 the preflight check
  runs its three GPU cases one at a time, which is why it is 44–170 s.
- **Steps:** each is the roll-up's next free step. If bf16-hill takes one first, I'll bump it at submit time; nothing else
  changes.

## Identity: every point should equal its baseline

| K | statement digest | proof bytes per rep | preflight digest | preflight bytes per rep |
|---|---|---|---|---|
| 4096 | `accf43c64453ae67…` | 963794 | `801a4254cce7042d…` | 572482 |
| 8192 | `46d84a0e1c724796…` | 963826 | `964f63d6639b3876…` | 628418 |
| 16384 | `bbb79d7042330283…` | 963858 | `5021e06ae78b40ba…` | 740162 |

## Order and limits

- **Order:** stage K=4096 first, then its GPU session. Each next K's staging runs while the current session holds the GPU;
  the K=16384 staging may take about 24 min, as bf16-hill's did. This lane holds at most one GPU at a time, each session is
  placed only while provers holds at most 1 GPU, and none is borrowed.
- **Window:** everything ends well before 5:05 AM PDT. Nothing goes in after 5:05 that could run past 5:35.
- **Records:** as at K=2048, with `hillclimb-session/v0` and per-point records citing the preflight check. On landing I
  append the points to each K's roll-up, relabelled under its `flags_rule`, and report the same numbers as for K=2048.
- **Specs** on node 1, under `/tmp/pvo-specs/`:
  - `pvo-k4096-stage-404aa05.json` and `pvo-k4096-s10-gpu-404aa05.json`;
  - `pvo-k8192-stage-404aa05.json` and `pvo-k8192-s10-gpu-404aa05.json`;
  - `pvo-k16384-stage-404aa05.json` and `pvo-k16384-s10-gpu-404aa05.json`.
- **Option:** the three staging jobs hold no GPU. If you'd rather, I can start the K=4096 staging now and have it ready
  when the yes comes. I'm waiting for your word.

While I wait I'll write the how-to for bf16-hill and flock-fp to run their points in sessions.
