---
id: 20260930T2302Z-handoff-from-backend-sweep-2-final
campaign: verity
lane: proofs
kind: handoff
status: open
repo: danielreuter/verity
origin: backend-sweep-2 (bc-62b7c7a1)
---

# backend-sweep-2 → proofs, final: (b) stopped at 1,598 statements, prover +8.5% on the mean; (a) never reached its gate; lane stopped

The lane has been stopped since 3:51 PM PDT (`sweep2-feed/STOPPED.json`, after Daniel's 3:49 PM PDT "forget about the vLLM
deployments"). Nothing of it is queued or running on node 1, and its feeder (tmux `backend-sweep-2-feed`) is off.

**(b) whole row, K = 2,048 GEMM coordinate.** This is a measurement on the draft prover key `4d568a3cb558b005` (#554), for Llama-3.2-1B's
row, shape `f1e4d147…`, with 50,346 statements.
- **Where it stopped:** statement 1,598 of 50,346 (3.2%), by the proofs research owner at 3:33 PM PDT. It never reached 5%
  agreement on the mean.
- **Proved:** chunk r0 (statements 0-622, `r20260930-210621-2a46`), chunk r2500 (2500-3128, `r20260930-210627-d1e9`) and
  chunk r5000 (5000-5345, `r20260930-214647-a70b`). All accepted.
- **Measured against extrapolated.**

  | | Per statement | Whole row |
  |---|---|---|
  | Extrapolated (median of 3, `r20260930-180937-ab3f`) | 1.00736 s | 14.09 GPU-h |
  | Prover, mean (+8.5%) | 1.0927 s | 15.28 GPU-h |
  | Prover, median (+1.6%) | 1.023 s | 14.31 GPU-h |
  | GPU held, loopback verifier (6.85 s) in series | 8.34 s | 116.6 GPU-h |

  The mean is the cost figure. The gap from the median comes from each chunk's 3-4 s first run and a tail over 1.5 s (about 3% of
  runs).
- **GPU-hours used:** 3.70 held.
- **Evidence:** the three runs' records (live prove records, session index, logs, `summary.json`) are in
  `art:17e200ddeb15987449bfa58ec2be108580841386d302951a9c1a9a0c9fe5eb3c`. Their Jobs were deleted, so the runs never ended, and
  their Attempts had to be published with `--force`. Each run is labelled with its statement range and `custody waived` →
  that artifact.

**(a) sampled units.** There's no selftest or byte-identity result. The first deployment (Llama-3.2-1B g232) was staged
(`r20260930-210718-2f89`), and the job's draw reproduced the record's 460 units (58 Call Definitions). Its prove job, which
carried the GPU selftest (`gpu_proofs_match_cpu`), was deleted in the stop before it started. The staged data went with the
stage-cache cleanup.

**My slip:** at 4:00 PM PDT I restarted the feeder before I had read the stop. It wrote `a-llama32-1b-07b84a-g2-s` and
`llama32-1b-07b84a-sc312`, both CPU-only stages. I deleted both Jobs within 3 minutes, and no GPU was used. The restarted feeder is
killed.

**Disk:** the stage cache copied fresh stages instead of hardlinking them, which was the duplication infra flagged. The fix is
`87690f2a6`. A dedupe job freed 39.2 GB before the cleanup. `PRUNE=1` (delete a proved job's staged circuits) and a cap on
deployments on disk are on the branch (`57e4c5ef7`, `3ba58ca0a`), for whenever the stage/prove split is reused.

**Code:** branch `cursor/backend-sweep-2-2ced`, draft PR #601, head `3ba58ca0a`. It includes node 1's live feeder edits. proofs-rows'
`73-sweep-shape.sh` patch (`note:20260930T2257Z-handoff-from-proofs-rows-73-hardlink-prune`) is backlog, not applied.

**Node 1:** GPU-busy 2.7% (10 min) / 4.2% (60 min) before, at 2:10 PM PDT; 2.6% / 4.1% after, at 4:02 PM PDT. Util was 0.1% / 0.3%
before and 1.1% / 1.6% after.
