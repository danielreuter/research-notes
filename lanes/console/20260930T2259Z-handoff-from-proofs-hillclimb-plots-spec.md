---
id: 20260930T2259Z-handoff-from-proofs-hillclimb-plots-spec
campaign: verity
lane: console
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs (bc-8416bc72, Slack @proofs)
---

# Proofs plots: replace every existing proofs / prover-overhead plot with per-subcircuit hillclimb plots (Daniel, 3:59 PM PDT: supersedes; the old plots weren't useful)

**Replace:** the M0 prover-overhead / Progress charts and any other proofs or C-Flock plots on the console. Daniel says the new
plots supersede them. Remove the old ones rather than keeping them beside the new.

## What gets plotted
- **One plot page per subcircuit**, where a subcircuit is `(datatype, Definition, K)`. Now there are four:
  - `bf16/GemmCoordinate_v2/K=2048`
  - `…/K=4096`
  - `…/K=8192`
  - `…/K=16384`

  All are `GemmCoordinate_v2{K, DOT=HopperBF16WgmmaDot16_v1}` on the RTX PRO 6000 Blackwell Server Edition (sm_120).
  NVFP4, MXFP4 and FP8 pages follow once their Definitions land; make the page list data-driven.
- **The x-axis is the optimization step:** 0, 1, 2… Each step is one recorded run on one commit.
- **Three stacked panels:**
  1. **Overhead against native (the target):** a log y-axis, lower is better. Draw a best-so-far line; the headline number is
     the latest best.
  2. **Throughput:** verification units (coordinates) proved per second.
  3. **GPU utilization:** the SM-active fraction over the job's GPU-held time, 0–1. Show a second series, GPU-held seconds per
     VU, on its own axis.
- **Hover or tooltip:** the step label (what changed), commit, run id, time (show PT), the byte-identity verdict and flags.
- **Points that fail the byte-identity gate:** draw them hollow, and leave them out of the best-so-far line.
- **Flags** (for example `tile-statement-unreviewed`): show a small badge.

## Definitions (fixed; the old research coordinator's formula, which follows the campaign contract `verity_numerical.bench.contract`)
- **1 VU** = one `GemmCoordinate_v2{K, DOT}` = K MACs = 2K FLOP.
- **overhead** = peak ÷ R_proved, where R_proved = 2·K·VUs ÷ t_prove.
  - t_prove covers every prover bucket (witness, commit, arithmetic, lookup, serialization) in steady state, per accepted
    VU. Setup (staging, circuit build) is reported beside it, not in it. **The verifier is excluded.**
  - peak is the datasheet dense tensor-core peak for the datatype at FP32 accumulate, no sparsity, from `census/hardware.json`
    (a new entry `rtx-pro-6000-bse/bf16`, being added).
- **throughput** = VUs ÷ t_prove.
- **gpu_util** = the mean SM-active fraction over the job's whole GPU-held wall time, *including* the in-job verifier.
  **gpu_held_s_per_vu** = GPU-held seconds ÷ VUs. Only this series shows a verifier fix: tonight a K=2048 statement proved in
  1.02 s but held its GPU about 8.3 s.

## Data: one record per run
Each run publishes a declared output **`hillclimb.json`** to the evidence store, next to its contract `result.json`. The run
carries the labels `campaign=proofs-hillclimb`, `subcircuit=<id>` and `question=<text>`. The record:

~~~json
{
  "schema": "verity/hillclimb-point/v0",
  "subcircuit": {"id": "bf16/GemmCoordinate_v2/K=2048", "dtype": "bf16", "definition": "GemmCoordinate_v2",
                 "K": 2048, "dot": "HopperBF16WgmmaDot16_v1"},
  "step": 0, "label": "baseline (M0 #20 tree)", "commit": "<sha>", "run_id": "r2026…", "time_utc": "2026-10-01T…Z",
  "hardware": {"gpu": "RTX PRO 6000 Blackwell Server Edition", "sm": "sm_120", "node": "vy-nebius-1", "vcpu": 48},
  "peak_flop_per_s": 0.0, "peak_census_id": "rtx-pro-6000-bse/bf16",
  "vus": 8192, "t_prove_s_per_vu": 0.0, "setup_s": 0.0,
  "overhead": 0.0, "throughput_vu_per_s": 0.0,
  "gpu_util": 0.0, "gpu_held_s_per_vu": 0.0, "verify_s_per_statement": 0.0,
  "byte_identical": true, "flags": [], "question": "…"
}
~~~

Read the records however suits the console: through its store API, or by `research data` over `campaign=proofs-hillclimb`.
If you'd rather have a single rolled-up JSON per subcircuit, tell me and a proofs worker will publish it.

## Timing
BF16 baselines at the four K values are being built now (worker `proofs-bf16-hill`, branch `cursor/proofs-bf16-hill-95d4`).
The first records should land tonight, after which there's one point per optimization step. Until data exists, show an
empty state per page.
