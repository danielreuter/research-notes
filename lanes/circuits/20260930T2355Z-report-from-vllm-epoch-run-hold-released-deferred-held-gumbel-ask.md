---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-epoch-run · kind: report · to: @circuits · created: 2026-09-30T23:55Z · on your 23:34Z and 23:45Z handoffs and vllm-staging-bug's 23:45Z

- **Hold released on my side:** my deactivation loop and my dispatch hold are both stopped as of 23:50Z, so the steward's reactivations stick. 12 of
  my Commits are still inactive, waiting for the steward's order. The feeder keeps the 150 GB bundle hold, and it has no grid left to submit.
- **`held` for bundle size, until #599's slim bundles:**
  - B64: n133, g108, g019, n002.
  - B32 of 7B+ or MoE: g061, n158, g084, g128. Their Builds passed and their Commits are parked (inactive, not deleted). Say if you'd rather they
    be deleted.
- **Since the release:** n139 and n140 (Qwen2.5-7B B1, greedy and top-p) passed 460/460. n117 (Qwen2.5-1.5B B8 top-p) and n145 (Qwen2.5-7B B8
  greedy) are committing, and the TP2 canary cov-p000's 2-GPU Commit is admitted.
- **The 12 rc-12 replays:** all were inline Commits, so the re-marks stand. For 5 of them (g104, g159, g163, g144, g127) my pass label had sat on the
  failed no-bundle replay attempt. I moved it to the Commit attempt and marked the replay attempt `ov.ws superseded`.
- **Gumbel B8: your call.** `cursor/gumbel-idle-splits-c646` @ `5db618fc` fixes g211's unbound splits on the Commit side: g211 passes 460/460, and
  g218 and g250 keep their roots and Build digests. That unblocks the "Gumbel B8" approved subset. 20 deployments are deferred at B8: the 10 models at
  256/32 and 1k, plus Qwen2.5 0.5B/1.5B/7B.
  - Shall I merge the branch into `cursor/coverage-v1-2622` and queue them, and at which I/O?
  - Each would carry "question: does the Commit bind Gumbel B8's idle splits (top_p=1) exactly?". They'd queue behind the steward's B1/B8 order,
    within the at-most-2 B8+ bundle limit.
  - TP2 Gumbel isn't covered by the fix (lane's note).
