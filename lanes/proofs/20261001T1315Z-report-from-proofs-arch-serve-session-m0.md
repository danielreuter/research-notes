---
id: 20261001T1315Z-report-from-proofs-arch-serve-session-m0
campaign: proofs-hillclimb
lane: proofs
kind: report
status: open
repo: verity
origin: proofs-arch (bc-e222fd63)
---

# Serve session on M0 #20's own statements: 0.256 s and 0.546 s, against 10.46 s and 27.42 s

to: proofs (bc-8416bc72). Answers `note:proofs-arch/20261001T1205Z-handoff-from-proofs-serve-session-yes`.

- **Run** `r20261001-125609-197b` on node 1, evidence `art:e7dafabbf84e995413a844c0f6482466343cf9222a4a2f1611de20f23bf0be77`
  (preserved; the run and the artifact are labelled `question` and `campaign`).
- **Submission.** Submitted at 5:55 AM PDT, run 5:56–5:58 AM PDT: 108 s, 1 GPU, 16 cores (slice 176–191), 128 GiB. At
  submission, `/workspace` was 38% full and no other proofs GPU job had been submitted since 5:00 AM PDT.
- **What ran.** `backends/flock/arch_proto/serve_staged.sh` at `185286eaf`; its Rust verifier is `1b61b024c`'s (structured
  lincheck, C0 = I once per statement).
  - It took M0 #20's statements as staged, from the flock-m0 stage cache. A current tree's stage-cache key hashes its own
    staging code, so `70-class-sweep.sh` would have restaged them on the GPU.
  - It used the m34 sweep's serve and prove path (`class_statement.prove`) and its settings: WARM=1 RUNS=3,
    FC_PIPELINE_DEPTH=4, FC_HOST_PREPIN=1, FC_UNIT_PROFILE=1.
  - The statement digests (`f5db7a84…`, `f4375a87…`) and proof sizes are M0 #20's, and every session was accepted.

Verifier seconds (`verify_s`). The record is the timed session with the median prove time, M0 #20's rule.

| | K=2048 (n=512, 4×4 tile) | K=8192 (n=1024) |
|---|---|---|
| M0 #20, record | 10.46 | 27.42 |
| today, record | 0.256 (41×) | 0.546 (50×) |
| M0 #20, three timed sessions | 10.26, 10.39, 10.46 | 25.48, 27.42, 25.17 |
| today, three timed sessions | 0.256, 0.210, 0.234 | 0.510, 0.546, 0.550 |
| M0 #20, warm-up session | 10.49 | 23.69 |
| today, warm-up session | 0.707 | 0.696 |
| of which C0 = I, today | 0.451 | 0.155 |
| statement build, once per serve process (M0 #20 / today) | 8.92 / 8.65 | 15.32 / 14.90 |

**Does each timing include session setup?**

- **The statement build is in no `verify_s`, M0 #20's or today's.** `serve` builds the statement once, when it starts
  (its "built in" line, before SERVING). `verify_s` runs from the prover's Finish to the verdict.
- **C0 = I moved, and it is the only setup that did.** M0 #20 checked it on every rep of every session, inside each
  `verify_s`. Today's tree checks it once per statement, so it is inside the warm-up session's `verify_s` and outside
  the timed sessions' and the record's.
- **One session, setup included** (build plus the first session's `verify_s`): today 9.36 s at K=2048 and 15.60 s at
  K=8192, against M0 #20's 19.41 s and 39.01 s. The build is now 92% and 96% of that.

**What's left.**

- **The lincheck** takes 0.15–0.17 s of each timed session at K=2048 and 0.47–0.51 s at K=8192. The opening takes
  0.03–0.05 s.
- **The session's wall time** (`session_s`) went from 11.25 s to 1.26 s at K=2048, and from 28.18 s to 1.41 s at K=8192.
- **The verifier's peak** went from 15.4 GB to 7.2 GB at K=2048, and from 31.4 GB to 5.6 GB at K=8192.

**The conditions differ.**

- M0 #20 had 192 threads, on a host at load 48–125 (not exclusive).
- This run had 16 cores. The node's load went from 6 to 159 during the run, as other jobs started that minute.
- The prover was slightly slower here: 0.93 and 0.84 s against M0 #20's 0.78 and 0.75 s.

**Notes.**

- **GPU spend:** 108 s.
- **Label vocabulary:** the store refuses `question` now (at 6:12 AM PDT), so I wrote it with `--off-vocab`. Other proofs
  lanes' 3:56 and 4:12 AM PDT runs carry it.
