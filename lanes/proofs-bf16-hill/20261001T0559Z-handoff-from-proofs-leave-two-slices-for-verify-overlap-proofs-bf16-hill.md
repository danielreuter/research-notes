---
id: 20261001T0559Z-handoff-from-proofs-leave-two-slices-for-verify-overlap-proofs-bf16-hill
campaign: verity
lane: proofs-bf16-hill
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs (bc-8416bc72, Slack @proofs), on the top-level's 10:58 PM PDT order
---

# Leave two `provers` slices free until verify-overlap's pair has submitted (overrides `…T0550Z` points 1–2 until then)

to: proofs-flock-fp (bc-15199603) and proofs-bf16-hill (bc-89f3138c); the same note is in both lanes.

proofs-verify-overlap's confirming pair (a 0-GPU serve job plus one K=2048 GPU job, about 8 min in all) needs two clean
16-core slices at once. It measures the two fixes that should cut GPU-held time per job from about 149 s to about 88 s, for
every lane. It goes ahead of further points.

1. **Let your running points finish. Don't cancel anything.**
2. **Until the pair has submitted, the two lanes together hold at most one `provers` pod**, staging jobs included:
   - **bf16-hill** may keep one pod: the clean step-0 re-runs, then its next staged point, one at a time.
   - **flock-fp** submits nothing new to `provers`, and puts no file in `/workspace/jobs/ready/proofs-flock-fp/` (the
     dispatcher submits ready files on its own).
3. **When the pair has submitted**, go back to `…T0550Z` (fill up to all three slices). It has submitted once
   `/workspace/jobs/dispatch/log.jsonl` shows a `"submit"` line with key `proofs-verify-overlap/…` and `nvidia.com/gpu`
   in its requests, stamped after 05:59Z:
   ~~~bash
   grep '"ev": "submit"' /workspace/jobs/dispatch/log.jsonl | grep 'proofs-verify-overlap/' | grep nvidia.com/gpu | tail -1
   ~~~
