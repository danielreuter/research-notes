---
id: 20260930T2202Z-handoff-from-circuits-rerender-old-commits-t3-command
campaign: verity
lane: vllm-epoch-run
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa)
---

# @circuits: resubmit the 4 pending old-template Commits under the new template; the exact T3 Build command; TP2 crash routed

1. **The 4 old-template Commits pending at the head of `deployments-gpu`** (node1-fill, 2:48 PM PDT: 8 Commits rendered before
   2:15 PM still replay on their GPU, 4 running and 4 pending) will each hold a GPU through its replay. Cancel the 4 **pending** ones
   and resubmit them under the same keys, so they render with `config-run@c43dba74fa68` (three tasks, `REPLAY_DEFERRED=auto`). Leave
   the 4 running ones alone. Tell me the keys.
2. **T3 (`research run --queue`, 9–10 PM PDT):** cluster-build said yes, with these flags:
   `research run --queue --source <tree at cursor/queue-submit-path-0381 (27676a80c) or later> --project verity --kind vllm.build
   --phase cpu --cpus 4 --mem-gb 64 --max-min 15 -- <Build command>`. Please put the **exact Build command line**, the one the
   `config-run` build task runs for the SmolLM2-135M rtxpro6000 B1 256/32 greedy row, with its env, and the node-1 Build run id to
   compare against, in `/workspace/jobs/cov/t3-candidate/` on node 1, and tell me the path.
3. **`cov-p002-2`'s TP2 Commit crash** (rank 1, illegal memory access): `config-run-row.yaml` doesn't set `NCCL_P2P_DISABLE=1`, which
   TP2 without NVLink needs. I've sent it to the research owner and the GPU-less-Build lane. TP2 stays held (`TP2_MAX 0`).

Thanks for the times and for cancelling the 15; nothing left for node1-fill there.
