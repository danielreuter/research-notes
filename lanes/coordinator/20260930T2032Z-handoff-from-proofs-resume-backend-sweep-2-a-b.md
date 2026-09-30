---
id: 20260930T2032Z-handoff-from-proofs-resume-backend-sweep-2-a-b
campaign: verity
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs (bc-8416bc72, Slack @proofs)
---

# @old-circuits-and-proofs: resume backend-sweep-2 (bc-62b7c7a1) for root's (a) and (b) now, in parallel on node 1's free GPUs

Re `note:20260930T2032Z-handoff-from-coordinator-backend-sweep-2-result-and-open-approvals`. It already has the build, the
ready-file path and the feeder, so it starts soonest. This is approved, in-flight work, and it fills idle GPUs (Daniel's
priority 1).

Please relay this to it:
1. **Run (a) and (b) at once, on separate GPUs.** (a) is the 460 sampled units of each passing deployment (58). (b) is
   K=2048 whole-row proving, about 14 GPU-h, stopping at 5% agreement with the extrapolation. Split (b) across as many free
   node-1 GPUs as its units allow, so it finishes in hours of wall time, not 14. Keep the same launch path as today: Kueue
   ready files / `research run` at priority `dev`. `provers` (M0) stays ahead. Infra will say when the one queue accepts
   1-GPU prover jobs, and it moves then.
2. **Batch to beat start-up cost.** Each shape's proof is 0.08–1.0 s of GPU, but a job holds its GPU for minutes. Pack enough
   units per job that proving, not start-up, dominates. Report GPU-busy and real utilization before and after.
3. **Feeder:** keep the Llama / next-model feeder as the lowest priority behind (a) and (b). It already yields to `provers`.
4. **Label the results as measurements on #554's draft prover key** (`4d568a3cb558b005`). The 4×4 tile's statement and pins
   aren't reviewed yet (M0's Daniel decision 1), so they aren't verified table rows.
5. **Evidence:** publish each result with `research data put … --preserve` or through the run's custody, and cite its
   `art:` / run ids.
6. **Report** to `lanes/proofs/` (through you) when (a) finishes, when (b) reaches its 5% stop or its first 4 GPU-h, and on
   any failure. Include the cost against the extrapolation and the GPU-hours used.
7. **Branch `cursor/backend-sweep-2-2ced` @ `18ceb459`:** open it as a draft PR now so the code isn't only on a branch. File
   no merge request until infra settles the queue (Daniel holds new merges as backlog).
