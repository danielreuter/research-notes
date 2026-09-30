---
id: 20260930T1053Z-handoff-from-pous-infra-to-pouw-gpu-queue-dry-runner-fixed
campaign: verity
lane: nebius-infra
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# pous infra (bc-efe47341) -> pouw (bc-2aa33ad8), cc GPU 3 (bc-0f3f8a2f) and GPU 6 (bc-0de2d624): the GPU queue is dry, the fill runner is fixed, one of your jobs needs a one-line fix

**1. Node 2's GPU fill queue is empty.** At 10:53Z, 4 of 8 GPUs were free and 0 GPU jobs were queued (6 CPU jobs were queued).
- The last hour met the target: the status page read 80% busy over 09:37–10:37Z. The next hour misses it unless GPU-heavy chunks arrive.
- No ready GPU-heavy row is left in `fill-candidates.md`. The ones that would supply hours are still being built by their owners:
  - GPU 0's capture fill, split into GPU and CPU jobs (`workers/0-fp8-capture.md`, its 10:33Z next step);
  - GPU 3's aligned-exact-regions census (`fill-candidate-aligned-exact-regions.md`, 10:40Z): the GPU stage is 4 units per family at about 2 GiB of flags each.
- Could you ask those two owners to queue their GPU stages as chunks of 8 minutes or less with `prio=10`?
- This is engineering supply, not theory.

**2. Your 10:18Z note (GPU 3): both fixes are live since 10:51Z** (`/workspace/pouw/infra/bin/fill_runner.py`; the runner restarted and adopted its running jobs).
- **Start order**, for GPU and CPU jobs alike:
  - `prio` first;
  - within a prio, owners take turns: the owner with the fewest jobs of that kind running goes next;
  - then the longest-queued job. A job requeued after exit 99 queues afresh (its file's mtime is touched), so a 5-minute chunker no longer jumps back to the front.
- **`max_min` stops while a job is paused** for a timed window. The runner doesn't enforce the cap while a job is paused, and each exit event now records `paused_min`. A job adopted while stopped is adopted as paused, so it is resumed when the window ends.
- At 10:53Z, four of GPU 3's jobs held all 4 CPU slots (`gpu3-fp8-llama70b-v2-L08`, `L16`, `L24`, `gpu3-fp8-llama70b-quality`).

**3. `coord-fp4-v3-real-qwen7b.sh` failed twice at 10:48Z** and is in `/workspace/pouw/fill/failed/`.
- The error is in `fill-out/fp4-v3-real/qwen2.5-7b/capture.log`: `ModuleNotFoundError: No module named 'verity'`. `fp4_emulation.py` imports `verity.ml.tc.models`, and `uv run --no-project` installs none of the workspace.
- **Fix:** add `PYTHONPATH=$T/packages/verity/src` to its `export` line (core needs only numpy, which the job already adds), or `--with-editable "$T/packages/verity"` to `$PY`. Then move it back to `queue/`.
- I didn't edit it, because it's your job file.

**4. The per-die baseline spread (for GPU 6's candidate) is done:** all 16 jobs, 8 dies × 2 runs. It used tree `7be37429`, the headline bench at the headline run's quality, and `locked-2100`.
- These were fill runs with neighbours busy, not quiet windows, so nothing here goes on the panel.
- The numbers are best-kernel graph medians, Measured; the spreads are Derived.

| Shape | Die range (fastest–slowest) | Largest run-to-run difference on one die |
|---|---|---|
| 8,192³ BF16 | 0.27% (GPU 3 2.8363 ms, GPU 1 2.8440 ms) | 0.11% |
| 8,192³ FP8 E4M3 | 0.71% (GPU 3 1.4390 ms, GPU 1 1.4492 ms) | 0.25% |
| 8,192³ FP8 blk128, MXFP8, INT8 | 0.26%, 0.29%, 0.12% | ≤ 0.11% |
| 8,192³ NVFP4, MXFP4 | 0.37%, 0.56% (GPU 1 slowest in both) | ≤ 0.15% |
| m = 32 decode, FP8, FP4 and MXFP8 | 0.47–1.64% | up to 3.0% (noise at 30–75 µs) |
| m = 32 decode BF16 | 3.04% (GPU 6 0.0994 ms; every other die 0.1022–0.1025 ms) | 0.67% |

- At 8,192³ the dies are ordered consistently: GPUs 3 and 5 fastest, GPU 1 slowest. Timed windows use GPU 0, which sits mid-pack. So a headline measured on another die carries up to about 0.7% of die bias, larger than the run-to-run noise.
- GPU 6's 3% lead on decode BF16 shows in both of its runs. It is probably a different winning kernel on that die. That's for GPU 6 to read; I haven't checked it.
- Outputs: `/workspace/pouw/fill-out/harness/baseline-spread/gpu{0..7}-rep{1,2}/out/bench.json`, fill outputs with no run id.
