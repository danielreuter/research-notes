---
id: 20261001T1513Z-report-from-proofs-flock-fp-packed-nvf4-k16384-nsys-profile
campaign: proofs-hillclimb
lane: proofs
kind: report
status: open
repo: verity
origin: proofs-flock-fp (bc-15199603)
---

# Where the 0.7 s packed statement spends its time (NVF4 K=16384 nsys profile)

to: proofs (bc-8416bc72). This is item 1 of your 7:53 AM PDT message. It is one node-1 GPU job, through `provers`, with 128 GiB.
No code changed.

## Summary

- **The packed statement spends its time the way BF16's m = 35 statements do.** Nothing in it is specific to FP4 or to
  packing. The packed frame's gain is all in n per statement: 4 times the coordinates in the same 0.75 s.
- **Where the time goes,** as a share of the prover's timers (both reps, per session):

  | Phase | ms | Share | Detail |
  |---|---|---|---|
  | zerocheck | 232 | 31% | the first round alone is 126 ms over its 2 launches |
  | Ligerito | 206 | 27% | 193 untraced; 67 ms of GPU idle, 52 of it host code between coin rounds |
  | witness | 94 | 12% | |
  | encoding commitment | 93 | 12% | |
  | ring switch | 75 | 10% | |
  | lincheck | 36 | 5% | |

  Only 19 ms per session falls outside the timers. The GPU is 84% busy.
- **Against BF16 at the same m, untraced,** four phases match within 11 ms: zerocheck, Ligerito, encoding commitment and ring
  switch. The two that differ follow the units' row counts:
  - lincheck is 34 ms, against 72 at BF16 K=16384 and 28 at K=2048;
  - the witness is 94 ms, against 97 and 70.
- **The prover changes bf16-hill proposed apply here unchanged, with the same shares.** Those are 1a (zerocheck round 1 on the
  ALU), live-coin latency, the Ligerito fusions, and 5 (no `cudaMalloc` in steady sessions). They are in
  `note:proofs/20261001T1415Z-report-from-proofs-bf16-hill-ncu-zc-round1-and-k16384-nsys`.
- **6e9b's 15% gap between overhead and prove-only comes from two sessions,** not from the statement:
  - Sessions 7 and 8 each spent 0.66 s and 0.96 s inside the prove call but outside the phase timers. That is bf16-hill's
    allocator-stall signature at K=16384. Every other session spent 7–61 ms there.
  - The traced run had no such stall: its two `cudaMalloc` calls over 20 ms took 23 and 39 ms. Its overhead (2.28e7) is within
    2% of its prove-only (2.25e7).
  - Item 5 is the fix for this.

## Why this cell

I chose NVF4 K=16384 for three reasons:
1. **It has the closest comparison.** bf16-hill's BF16 K=16384 profile (`r20261001-135122-b18a`) has the same m = 35 and the
   same K, so each phase can be read against a BF16 statement of the same size.
2. **It packs the most.** NVF4 packs four codes a leaf plus the scale rows, so n rises 4 times, more than in any other format.
   It is also the format of item 2's core rows.
3. **Its untraced point had the widest unexplained gap.** In node 1's 6e9b, overhead was 2.51e7 against 2.18e7 prove-only. The
   profile could show whether that gap is inside the statement. It isn't.

## Run and evidence

- **Run:** `r20261001-150409-cdcc`.
  - Node 1, 16 cores, 128 GiB.
  - Tree `proofs-flock-fp-pk` = `a30bc8e5b`, unchanged.
  - Placed at 15:03:11Z, done 15:05Z, rc 0.
- **Same statement as 6e9b.** It has digest `93709f569c8a58d2…`, 2,048 instances, m = 35 and k_log 24.
- **It passes the accept rule:** 1 warm and 24 timed LIVE records, none rejected, prove exit 0.
- **How it was traced.** `a30bc8e5b`'s harness predates `NSYS=1`, so a wrapper outside the tree did the tracing:
  - The wrapper is `/workspace/jobs/proofs-flock-fp/bin/nsys-pk.sh`, also copied into the artifact.
  - It ran the item's `74-gemm-hill.sh` command under `nsys profile -t cuda,nvtx --sample=none --cpuctxsw=none`, bf16-hill's
    trace.
  - `GATE=0 N=2048` (the gate's own fill for this cell) kept the gate's selftest processes out. Only the prove process made
    CUDA calls.
  - The run's `hillclimb.json` and `result.json` were moved to `out/nsys/*-traced.json`, so no roll-up takes it as a point.
- **Tracing cost:** e2e median 0.759 s traced against 0.738 s untraced. Most of the difference is in Ligerito, where the coin
  wait is 47 ms traced against 32 untraced.
- **Evidence:** `art:8c4e9ab378f82244c8a37fc84eba1085b0a21468cb7c765d0bef1acfb7767c55`, preserved. It holds:
  - the report, its SQLite export and the `nsys stats` CSVs;
  - the run's stamps and metrics;
  - bf16-hill's analysis scripts, unchanged, with their outputs on this trace, plus a `runs_cmp.py`.
- **Labels on the run:** `campaign`, `question`, `subcircuit` and `nsys.profile`, all on the remote.

## Phase timers against BF16 at m = 35

All values are ms per session, medians over the timed sessions. The gap rows are means.

| | NVF4 K=16384 packed, traced (`cdcc`) | the same, untraced (`6e9b`) | BF16 K=16384, untraced (`f010`) | BF16 K=2048, untraced (`9094`) |
|---|---|---|---|---|
| units × rows per unit | 2,048 × 2.05 M | 2,048 × 2.05 M | 512 × 8.95 M | 2,048 × 1.12 M |
| e2e | 759 | 738 | 847 | 704 |
| zerocheck | 232 | 228 | 230 | 221 |
| Ligerito | 206 | 193 | 182 | 197 |
| witness | 94 | 94 | 97 | 70 |
| encoding commitment | 93 | 93 | 93 | 93 |
| ring switch | 75 | 75 | 73 | 70 |
| lincheck | 36 | 34 | 72 | 28 |
| e2e − prove_total_s | 9 | 7 | 42 | 6 |
| prove_total_s − timers | 10 | 79 (sessions 7 and 8) | 30 | 13 |
| coin wait | 47 | 32 | 28 | 53 |

**Kernels in the trace,** ms per session:
- **zerocheck:** first round 126 (2 launches, 63 each; BF16's are 58), second round 47, tail 43.
- **encoding commitment:** additive NTT 67, `hm96_finish_leaves` 33, `sha512_staged_merkle_leaves` 14.
- **witness:** `fc_sha_tape3` 38, `fc_host_slots` 31, `fc_sha_rows` 25.
- **Ligerito:** `lf_fold_ext_pair` 34, `lf_fold_base_pair` 24, `lf_msg_partial` 23, over 1,121 launches.
- **ring switch:** fold rows 26, combine basis 21, zlin transpose 17, and one 4.3 GB device-to-device copy.
- **lincheck:** the compressed column fold is 12 ms (30.5 at BF16 K=16384).

**GPU idle** is 117 ms per session:
- Ligerito 67 ms (52 of it host code);
- ring switch 17;
- zerocheck 14;
- lincheck 8.
