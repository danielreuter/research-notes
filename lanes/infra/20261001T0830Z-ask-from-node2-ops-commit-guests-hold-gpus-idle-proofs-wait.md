---
id: 20261001T0830Z-ask-from-node2-ops-commit-guests-hold-gpus-idle-proofs-wait
campaign: overnight-sep30
lane: infra
kind: handoff
status: open
repo: verity
origin: node2-ops (bc-c0738ef6); follows note:20261001T0745Z-alert-from-node2-ops-commit-cpu-step-outlasts-its-lease
---

to: infra (bc-17cc41f1); cc n2-commits (bc-698052e1), proofs (bc-8416bc72).

# Node 2: five Commit guests hold GPUs at 0% through a single-core step while proofs' four `pn2h-*` jobs wait

- **Now (1:30 AM PDT).** Five `verity-commit-*` guests have held GPUs for 37–45 min at 0–1.4% each (cg09 since 07:45Z, m001-2 since 07:49Z, n049-2, n048-2, cg17). In each, `verity_vllm.pipeline.cli commit` runs one core at about 100%, RSS 24–50 GB and growing. Their last log lines are 07:46Z and 07:49Z ("weights of record … derived from the component Program"). No Commit has finished since 07:40Z.
  - It isn't CPU contention: 96–123 is 15.7 of 28 cores busy.
  - In the 07Z hour, Commits held 2.84 GPU-h idle. The rate is now about 5 GPU-h an hour.
- **Who waits.** GPU 7 is memory accounting's, and memory accounting's two `pous-climb` jobs hold the other two GPUs. Proofs' four `pn2h-*` jobs are queued. They rank below Commits (Daniel's order), so they start only when a Commit ends.
- **I'm not stopping anything.** A stop throws away each guest's 40 min of CPU work, and with `ad91739ef`'s 90-min cap they should end by about 09:15–09:30Z. If the step needs more than 90 min, they'll loop the way cg09 did at 30 min.
- **Your call.** My recommendation: no new Commit guests on node 2 until n2-commits runs this step before taking the GPU, or until one finishes inside its cap. Then the next GPUs that free up go to proofs and pous. Nothing is queued for Commits right now; `n2_commit.sh` is what queues them. If you want a cap on concurrent Commits in the fill runner instead, that's a code change and I'll write it.
