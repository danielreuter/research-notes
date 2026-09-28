---
cursor:
  subagentId: "bc-ff572e70-b0e7-5094-85be-13ff9ddc4d6a"
lane: coordinator
kind: handoff
from: flock-netlist / M0 (bc-ff572e70)
to: the backend sweep lane (pods vyb-sweep-l40s-3, vyb-sweep-101-rd; results in internal/backend-sweep/live), via the coordinator
created: 2026-09-28T14:50Z
---

# One GPU validation run of PR #289 (GEMM options 2 and 3) on the sweep's L40S, inside its budget

Please route this to the lane running the m = 34 GEMM diagnosis: its owner isn't on file under `internal/lanes/`. I create no pods.

**What it validates.** [PR #289](https://github.com/danielreuter/verity/pull/289), branch `cursor/flock-gemm-witness-4d6a` at `85117061`, is a prover-only change:
- **Deep units on the host.** A unit of at least 2048 AND-levels, such as the flattened GEMM coordinate, is evaluated on the host, and the device skips its per-level unit kernel.
- **Rep 1 reuses rep 0.** Rep 1 proves from rep 0's device witness and level-0 commitment.

Proofs should be byte-identical. That's what the run checks, alongside the timing.

**Run A: byte identity**, a small batch so that reuse keeps. Your `DEFS` and a `SHAPES` file with the two GEMM shapes: K = 2048 (`bc8cf592…`) and K = 8192.

~~~text
research run --on vyb-sweep-l40s-3 --project verity --source <branch at 85117061> --cwd source --tool flock_class_sweep --campaign <yours> -- \
  bash backends/flock/pod/70-class-sweep.sh DEFS=<defs> SHAPES=<shapes> BATCH=16 SELFTEST=1 SELFTEST_GPU=1 WARM=0 RUNS=1
~~~

Pass criteria:
- Every shape's `selftest.all_pass` is true, with `selftest.gpu` true.
- `gpu_paths_agree`: `proofs_equal` and `transcripts_equal` are true, `host_units` is `[true, true]` and `rep_reused` is `[false, true]`. It compares device units with a rebuilt rep 1 against host units with reuse.
- `gpu_proofs_match_cpu`: `proofs_equal` and `transcripts_equal` are true (GPU against CPU).

The per-case lines are in each shape's selftest output. If a shape's cases aren't in the record, `selftest --gpu --only gpu_paths_agree` on the staged directory prints them.

**Run B: speed.** Your m = 34 diagnosis exactly as it runs on `main`, with `--source` set to the branch. The record's `live.buckets` are now kept (per rep: `t.witness`, `t.witness_units`, `t.encoding_commitment`, …, `host_units`, `rep_reused`). Compare them and `prove_total_s` against the `main` run.

What I expect:
- `t.witness_units` is about 0.
- Rep 1's `t.witness` and `t.encoding_commitment` are about 0, where `rep_reused` is true.
- `witness_s` (host) grows by the host's unit evaluation, about 0.1–0.5 s per session.

At m = 34, reuse needs three witness-sized buffers more than the arena, about 6 GB, plus 4 GiB free. If the device lacks that, `rep_reused` stays false and rep 1 proves in full. The proof is unchanged either way. Please report which happened.

**Reply** with a handoff to `flock-netlist` naming the two run ids. I'll hand #289 to the research coordinator once `check` passes; run A's verdict goes into that merge request.
