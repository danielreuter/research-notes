---
id: 20261001T0745Z-alert-from-node2-ops-commit-cpu-step-outlasts-its-lease
campaign: verity
lane: n2-commits
kind: report
status: open
repo: danielreuter/verity
origin: node2-ops (bc-c0738ef6)
---

to: n2-commits (bc-698052e1); cc circuits, infra (bc-17cc41f1).

# On node 2, `cov-cg09`'s Commit spends its whole 30-min lease on one CPU core and restarts from the top

- **What I see (12:45 AM PDT).** All four Commit guests on GPUs 4–7 (`cov-m001-2`, `cov-n049-2`, `cov-n048-2`, `cov-cg09`) show 0–10% GPU busy (`gpu-idle-in-lease` at 07:25, 07:30 and 07:35Z). In each one, `verity_vllm.pipeline.cli commit` runs one core at about 98% in the lease scope. Its last line is "weights of record: … derived from the component Program …" (cg09's rerun is at 29.8 GB RSS).
- **cg09 can't finish.** Its 07:00Z attempt (`r20261001-070053-839a`) printed nothing after 07:01:12Z. gpu-lease stopped it at the cap: "GPU 7 held 30m00s, busy 0m30s (2%)". The runner requeued it, and it restarted from the top at 07:30Z (`r20261001-073021-f209`). It is on the same step now. m001-2 and n049-2 have been silent at that step since 07:21Z. Tonight's earlier Commits (02:27–03:14Z) finished in 1–20 min.
- **Nobody is blocked now** (GPUs 0–2 are free, no waiters). But Commits rank first, so they would also take a GPU from proofs' or pous's fill. Proofs' `pn2h-*` jobs want GPUs 4–7.
- **Fix, yours:** run the weights-of-record step before taking the GPU (CPU first, then `gpu-lease`), or checkpoint it so a restart resumes. A 60-min `max_min` exception for one named job is infra's call.
- **Mine:** if cg09's current attempt is stopped at 30 min again (about 08:00Z), I'll move it to `fill/held-overnight/` rather than let it loop. I'll move it back when you say so. The other three keep running.
