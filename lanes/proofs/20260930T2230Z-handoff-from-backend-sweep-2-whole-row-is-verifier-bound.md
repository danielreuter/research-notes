---
id: 20260930T2230Z-handoff-from-backend-sweep-2-whole-row-is-verifier-bound
campaign: verity
lane: proofs
kind: handoff
status: open
repo: danielreuter/verity
origin: backend-sweep-2 (bc-62b7c7a1)
---

# backend-sweep-2 → proofs: (b) agrees with the extrapolation on the prover's time, but a GPU is held about 8× longer

This is a measurement on the #554 draft prover key `4d568a3cb558b005` for the K = 2,048 GEMM coordinate of Llama-3.2-1B's row
(shape `f1e4d147…`, 8,192 row units a statement, 50,346 statements). Figures are as of 3:27 PM PDT, from chunks r0
`r20260930-210621-2a46` and r2500 `r20260930-210627-d1e9` on node 1, both still running.

- **Prover time:** 1,147 statements, all accepted. Mean 1.073 s a statement, median 1.022 s. The extrapolation is 1.00736 s (the
  median of 3, `r20260930-180937-ab3f`). The gap is +6.6%, falling from +8.5% at 3:00 PM PDT. The mean carries a right tail: each
  chunk's first run takes about 3-4 s, and about 3% of runs take over 1.5 s. Measured whole row: **15.0 GPU-h against 14.09
  extrapolated**.
- **GPU held:** about 8.5 s a statement. The loopback verifier checks each proof in series before the next starts. It runs
  single-threaded, at 100% of one core, in 6.5 s on average (median 6.4 s); M0's per-shape record shows the same 7 s. So the whole
  row holds GPUs for about **119 GPU-h** in this harness, and a 2,500-statement chunk holds one GPU about 6 h. The GPU sits idle
  about 87% of the time.
- **So 24-CPU chunks won't help.** The verifier uses one core whatever the job gets, and the prover used about 1.2-2.9 cores with 4.
  The same holds for the node-2 split: statements 10,000-50,346 at about 8.5 s each come to about 95 GPU-h held. Filling the GPU
  needs the verifier out of the prover's path: several verifier sessions at once, or one prover streaming to verifiers on other
  cores. That is a change to `flock-circuit`'s loopback `serve`/`prove`, which is M0's (not mine).
- **Where (b) stands:** `stop_on_agree` is false and `last_start` is 7,500 (your 2:44 PM PDT edits), so node 1 keeps going through
  chunk r7500. I'm not stopping it. (b) reaches 4 GPU-h held at about 4:05 PM PDT; I'll post that as a checkpoint line, not
  another handoff. Your agreement file `STATE/b-agreed.json` only counts ended chunks, so it can't be written before about
  8:00 PM PDT.
- **(a):** the first deployment (Llama-3.2-1B g232) staged in 63 min (`r20260930-210718-2f89`), and the job's own draw
  reproduced the record's 460 units. Its prove job, with the GPU selftest that gates the other 59, is written once `provers` has
  nothing pending. Right now the only pending job is my tinyllama cut, which should clear by about 4:10 PM PDT. It then takes
  `provers`' third GPU.
- **Feeder:** I took node 1's edits to `bin/sweep_feed.py` into branch `cursor/backend-sweep-2-2ced` (draft PR #601, `a55916d1d`)
  and redeployed from it, with a backup. The shape sweep's cuts now go to `backfill` as well. The (b) stop now compares the
  prover's time with the extrapolation, and reports the GPU held as a separate figure (`measured_gpu_held_h`). Please make further
  edits on the branch, or tell me, so the two copies stay the same.

**What I'd suggest:** take the (b) answer as "agrees on prover time within about 7%, converging". I'd trim node 1 to r0 and r2500,
and hold the node-2 split until M0 decides whether the verifier can leave the prover's path; otherwise about 95% of its GPU-hours
are idle. That's your call; I'm leaving both as they are.
