---
lane: share-logup-2
kind: report
created: 2026-09-23T21:00Z
status: superseded
---

CHECKPOINT 0b40ae8a (05:54Z) [superseded] closed by coordinator 2026-09-25 05:55Z for the cloud switch-over: no sign of life >24 h; branch lane/share-logup-2 pushed to origin; uncommitted work (if any) saved in evidence/uncommitted-0554Z*
CHECKPOINT cfdcf65 (21:14Z) pipelined pair committed; hint syncs removed (private_decode on device, pinned async fp statics). Same pod p4 (prof_p4.py, 5 passes, median): bare 0.155 s, Poseidon2-unshared 0.391 s, shared 0.293 s (1.89x; host busy 0.12-0.15 s, device ~52% busy: latency-bound on the G->H chain per job). Next: overlap H's commit with G (H's root is independent of rho/F), then extend +shared to the other 3 relations.
CHECKPOINT 1054caf+wip (21:0xZ) pipelined pair WORKS (uncommitted yet): `SharedHashedRunner.prove_vus_many` = one prove_many job per sub-batch (G stages, F_H vectorised, H stages, H witness gathered on device); also `HashedRelationRunner.prove_vus_many` (unshared Poseidon2 at --pipeline). Same pod, 4096 VUs, l=16384, interactive non-ZK local coins, p4: bare 0.158 s; Poseidon2-unshared 0.394 s (was 0.62 unpipelined); shared 0.39 s median of 3 but NOT converged (1.52/0.39/0.31: per-(stream,layout) graph captures in timed reps; H has 70/71-unit layouts) -> fixing warm-up, profiling tests phase next.
CHECKPOINT 1054caf (20:55Z) worktree ~/projects/verity-main-wt/share-logup-2 on lane/share-logup-2 @ 1054caf (predecessor tip); read brief §0/§1.1, leaf-campaign §0/§9, predecessor report + red-team handoff, open-fixes a0ff818; reusing pod vy-share-logup (kx69zewzhawgy1, 4090). Reading code: SharedHashedRunner + prove_many.

# share-logup-2 — pipelined tile64 row sharing (`fp8-ada+shared`) and the other relations

## Log
