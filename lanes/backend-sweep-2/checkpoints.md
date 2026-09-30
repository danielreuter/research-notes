---
cursor:
  subagentId: "bc-62b7c7a1-9d2c-5669-9b01-1d4d148b2ced"
---

# backend-sweep-2 checkpoints (postmortem action 1: the backend sweep as node 1's GPU backfill)

Branch `cursor/backend-sweep-2-2ced` (on #554's `ec49a99eb`, + `73-sweep-shape.sh`); tree `/workspace/research/trees/backend-sweep-2`; ready files `/workspace/jobs/ready/backend-sweep-2/`.

- 17:26Z: config `llama32-1b__bf16__rtxpro6000__tp1__b1__i1024__o128__mixed__greedy__bi-eager` (Commit PASS, `r20260930-170421-3244`); cut job queued. Shapes queued 0, done 0, failed 0.
- 17:25Z: broker: source=broker
- 18:01Z: cut done (`r20260930-172942-e0ce`, 28 min CPU): **2,578 shapes**, 1.87e9 row units, into `/workspace/jobs/sweep2/<row>/shapes.tsv`. First shape = the K=2048 GEMM coordinate (#1551, 4.1e8 row units): stage job running, prove job with GPU selftest after it. Shapes queued 1, done 0, failed 0.
- 18:35Z: first shape #1551 (K=2048 GEMM coordinate, 4x4 tile, k_log 26, B=512) `r20260930-180937-ab3f`: accepted; GPU selftest 43/43 pass incl. `gpu_proofs_match_cpu` (proofs+transcripts byte-equal to CPU's) and `gpu_paths_agree`. Prover key 4d568a3cb558b005 = M0's #554 runs. Feeder (tmux `backend-sweep-2-feed`, CPUs 96-127) now queues the rest: stage (CPU) then prove (1 GPU). Shapes queued 1, done 1, failed 0.
- 19:30Z: Llama-3.2-1B: shapes queued 62, done 42, failed 0 (of 2,578). From shape 12 on, jobs cover 10 shapes (`sc<i>` CPU stage, then `pc<i>` 1-GPU prove, commit `325aef22e`); first chunk pc12 done in about 5 min including a GPU selftest. Node 1 GPU-busy 6.0% (10 min) / 29.3% (60 min), util 0.6% / 4.6%, CPU 33%. The sweep is GPU-light (about 2 GPU-hours of real proving): handoff `note:20260930T1855Z-handoff-from-backend-sweep-2-sweep-is-gpu-light`.
