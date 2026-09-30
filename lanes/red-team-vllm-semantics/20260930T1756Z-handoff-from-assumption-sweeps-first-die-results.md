---
id: 20260930T1756Z-handoff-from-assumption-sweeps-first-die-results
campaign: overnight-sep30
lane: red-team-vllm-semantics
kind: handoff
status: open
repo: danielreuter/verity
origin: assumption-sweeps (bc-5be66fb3)
---

# assumption-sweeps -> red-team-vllm-semantics: 8-die results so far: MUFU and the bf16 mma step are bit-identical on every die; your edges counts identical on 7 of 8 dies

Everything ran on vy-nebius-1 under `research run`, campaign `overnight-sep30`. Each passed Attempt carries labels `assumption-sweep=<edges|digest|tc-probe>` and `die=<GPU UUID>`, `--by assumption-sweeps`. The rating stays yours.

- **Your `edges_job.sh`, unchanged, passed on 7 of 8 dies:** 0, 1, 2, 3, 5, 6 and 7 (die 3 is your own `r20260930-082720-fca5`). All 38 measurements are identical on all 7: floor −133 has 0 mismatches, and the RoPE, SiLU and block128 counts match. MUFU is exact: 0 of 2^32 mismatches on `ex2` and `rcp`, device sha256 `fb25d530…` / `e5c9fc6a…` on every die. Die 4 was preempted in `backfill` before its router step; 3 more jobs are queued. Examples: `r20260930-153732-3772` (die 0), `r20260930-154114-a37a` (die 6), `r20260930-164644-5fb0` (die 2).
- **New: `as_digest.py`, GPU-only, 1 vCPU** (`lanes/assumption-sweeps/tools/as_digest.py`), on all 8 dies. It found one sha256 per output across all 8 dies:
  - all 2^32 inputs of `ex2`, `rcp`, `lg2`, `rsqrt`, `sqrt`, `sin`, `cos` and `tanh.approx`. The `ex2`/`rcp` digests equal `mufu_attack.py`'s, which checks them against the model, so the other dies are model-exact too. The other 6 ops have no model; this shows only that every die gives the same words.
  - bf16 `tl.dot` 16×16×16 with a random f32 accumulator, on uniform random bits, seeds 1–4 (2^18 tiles each). The words are stable across 2 repeats on the default stream and a concurrent second stream.
  - Examples: `r20260930-155954-84bf` (die 6), `r20260930-170433-3ed0` (die 4), `r20260930-170547-cc9d` (die 0).
- **`tc_probe` sm120 bf16 seeds 1–8:** the first pass crashed at `zero_acc_tiny_cancellation`, because I left `verity_numerical` off `PYTHONPATH`. Every family before it had 0 mismatches against `hopper_bf16_m16n8k16`. It is requeued as `tcp2-s1..8`.
- **Two things for you to check** (not mine to rate):
  - **block128:** every candidate order mismatches almost every coordinate (4059/4096, 32622/32768, 130857/131072), with layout `a_scales_mn_major`. Your 09:20Z rating says the promotion order is exact, so this looks like the probe's layout choice in `edges_probe.py`.
  - **Router harness:** `ROUTER-TAP-EXACTNESS FAIL` on every die. `errors: 1`, "layer 3 launched topk_softmax … renormalize=True; the manifest's router is … renormalize=False", while `outputs_equal` and `words_equal` are true.
- **Still open:** the jobs you want next, which is cuBLAS workspace, streams and split-k at new seeds (your `cublas_attack.py`?). Put the CMD in `lanes/assumption-sweeps/`, and I queue it as ready files in `backfill`.
