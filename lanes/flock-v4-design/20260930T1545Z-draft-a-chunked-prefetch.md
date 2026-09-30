---
id: 20260930T1545Z-draft-a-chunked-prefetch
campaign: overnight-sep30
lane: flock-v4-design
kind: draft
status: open
repo: danielreuter/verity
origin: cursor/ov-gemm-slowdown-4d6a@ac08812e
cursor:
  subagentId: "bc-8a7dff1c-37ef-5954-b12e-caa928daeb58"
---

# Attempt A: measure the chunked device prefetch (`FC_DEV_PREFETCH=1`, `FC_COPY_PIECE_MB=8`), already on M0's tip

For M0 (bc-ff572e70). No code to write: M0's `b85a8c7c` (14:10Z) implements flock-v2-design's backlog design, and its tip
`ac08812e` carries it. Nothing I can find (notes, handoffs, the notes repo at 15:34Z) records a measurement of it.

**What it does.** A witness built ahead of its session copies its a, b host slots and compression rows to pooled device
buffers (`DevBuf`, at most `FC_DEV_PREFETCH_GB`, default 16). `flock_cuda_copy` issues the copy in 8 MB pieces, each synced
before the next. The session's rep 0 then finds the words on the device (`fc_on_device`), so `fc_host_slots` reads device
memory instead of doing mapped PCIe reads.

**Why the unchunked prefetch was neutral or worse** (#5, #6, v1#6). The prove waits on the whole device often: M0's Nsight
run has 29 `cudaDeviceSynchronize` and 78 `cudaFree` calls per process of two statements (Ligerito's `lf_observe_msg`,
`lf_cuda_release`). The first such wait after a 1.2 GB copy starts sat out the rest of it (25–45 ms), which repaid the
saving. With 8 MB pieces a wait covers at most one piece (about 0.2–0.3 ms).

## Predicted gain

- Rep 0's `t.witness`: −23 ms at K=2,048 and −28 ms at K=8,192 per statement. These are #5's same-job savings; at m=35 the
  host-slot span is 26 / 44 ms (M0's Nsight table), so the saving could reach −26 / −44 ms there.
- Cost: the copy runs about 5% of a statement's wall time, so of about 107 device-wide waits some 5 land on a piece:
  about 1 ms per statement. The copy itself counts as build time, which has slack at depth 2 (#6's control: K=8,192 builds
  in 0.43 s beside a 0.59 s prove).
- **Metric: −5% to −7% in both prefill and decode** against the same-job control. On #9's proves (0.342 s at K=2,048,
  0.518 s at K=8,192) the m=34 saving is −6.7% and −5.4%; M0's ring-switch commits (`8f80915a`, `959839ae`) shorten the
  proves, which makes the same milliseconds a larger share.
- **Kill criterion.** If, against the control, the other phases (Ligerito, the zerocheck, the reused rep 1) rise by more
  than 5 ms per statement, the sync explanation is wrong or incomplete. Then one retry at `FC_COPY_PIECE_MB=2`, and if that
  doesn't help either, stop the line and switch to attempt B.

## Byte-identity gate

Nothing changes in the statement, pins, circuits or protocol; only where the device reads the same words from.

1. 71's gate runs with `FC_DEV_PREFETCH=1` exported (72 exports its KEY=VALUE arguments before calling 71):
   `gpu_paths_agree` on the `device-ab` layout against the pageable path, and `gpu_proofs_match_cpu` (proofs and transcripts
   equal the CPU prover's), on both GEMM coordinates.
2. The gate's statement digests equal those of your last v3 attempt at the same m (at m=34: `86b48502…`, `72ba2879…`
   untiled, `4998fffc…` for the 4×4 tile).
3. `CHECK=1`: `FC_UNIT_CHECK=1` reads each device copy back (`DevBuf::holds`) and compares it; every check statement
   is accepted.

A failure of any of the three stops the attempt; don't report its metric.

## The bench

The steady state, as #6: depth 2 and RUNS=8, so most timed proves run beside the next build and its copies. That is where
the unchunked copy lost.

~~~bash
# on ac08812e (or your later tip, if it changes no prove path), from your v3 checkout
tools/research/src/research/pods/nebius/sky/submit.sh prover-bench m0-v3-a<N>-chunked \
  --env CMD='research run <your v3 flags: --tool, --campaign overnight-sep30, --cwd source> -- \
    bash backends/flock/pod/72-host-unit-eval.sh <your v3 knobs: FLOCK_GEMM_TILE=4x4 FC_HOST_PREPIN=1, m, BATCH_ANDS, MAX_STATEMENT_BITS> \
      FC_DEV_PREFETCH=1 FC_COPY_PIECE_MB=8 FC_PIPELINE_DEPTH=2 WARM=1 RUNS=8 \
      BASE=1 BASE_ENV=FC_DEV_PREFETCH=0 NOPIPE=0 CHECK=1'
~~~

Keep the `research run` flags, the vCPU count and your v3 knobs exactly as in your last v3 submission; only the arguments on
the last two lines are new. At 18 vCPU (the template default) two such benches fit in `provers` side by side. The same-job
control makes the delta independent of the vCPU basis.

- **Read:** `out/result.json` (prefetch) against `out/base/result.json` (control), and per phase from each sweep's
  `classes/*/prove.err` (rep 0 `t.witness`, Ligerito, the reused rep). `out/unitprof.tsv` has the `upload` part's
  `wall_s` per witness.
- **Labels:** `ov.line flock-m0-v3`, your next `ov.attempt`, `ov.noisy true`, and
  `ov.note "chunked device prefetch, 8 MB pieces (b85a8c7c); same-job control FC_DEV_PREFETCH=0"`.
- **Success:** gate pass, and the metric at least 3% below the control in both prefill and decode, with rep 0's `t.witness`
  down 20 ms or more at both K. Then `FC_DEV_PREFETCH=1` becomes v3's default and attempt B is moot.
