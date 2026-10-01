---
id: 20261001T0901Z-report-from-circuits-grid-models-counts-0205
campaign: verity
lane: circuits
kind: report
status: open
repo: danielreuter/verity
origin: circuits-grid-models
---

# circuits-grid-models -> @circuits: 2:05 AM PDT counts: 25 submitted, 13 ended, 12 pass, 1 fail (SiluMul_v1 replay mismatch)

Re note:20261001T0821Z-handoff-from-circuits-go. As of 2:01 AM PDT (09:01Z):

- Submitted 25 (cov-gm001 to cov-gm025), all from tree `cursor/grid-models-8c79` @ b9880ac17 (coverage-v1 @ 90ebe43d9 plus the 20
  checkpoints and their workloads). So far these are TP1 B1 and B8 rows at 256/32 and 1024/128, greedy, on the models under 7B,
  smallest first.
- Ended 13: 12 pass (state succeeded, replay 460/460 equal) and 1 fail. Each one is labelled `ov.ws`, `ov.config`, `ov.gate` and
  `ov.note`, which carries the tree, its question and, for a failure, its cause. Labels are by `circuits-grid-models`, written to R2.
- In flight 12: 6 Builds, 3 Commits, 2 replays, and 1 Commit on node 2 (cov-gm014, moved there by `n2_commit.sh offload`).
  cov-gm018's Build ran on node 2 (`n2_build.sh offload`), and its Commit is back on node 1.
- Models with a deployment run: 10, from 6 families (falcon3, llama3, qwen25, qwen3, smollm2, yi). Every model is under 7B so far.
- Walls on node 1: Builds 176–435 s, Commits 262–516 s, replays 119–275 s. No Commit has come near 30 min.

Failure by cause (1):

- **cov-gm001**, `qwen3-06b__bf16__rtxpro6000__tp1__b1__i256__o32__mixed__greedy__bi-eager`. The cause is a replay mismatch in
  `SiluMul_v1{I=3072}` at `model.layers.27.mlp.act_fn/out`, request r0, prefill step 0, row 15. F_V applied to the committed
  `model.layers.27.mlp.gate_up_proj` words [92160, 98304] differs from the committed output in 1 of 3072 elements (index 107).
  - 459 of the 460 sampled VUs are equal.
  - It is the first SiluMul_v1 mismatch in any node-1 row's `stages.txt`. The only other F_V mismatch there is qwen25-05b's
    `GemmBiasF32Epilogue_v1` on 30 Sep (13:48Z, 51 VUs, an older tree).
  - Layer 27 is Qwen3-0.6B's last layer, so a large-activation edge case in SiLU is a guess, not a finding.
  - Undiagnosed. The 27 MB slim keep is at `/workspace/jobs/cov/cov-gm001/<row>/commit/replay_slim_p0`; the record is in
    `commit/sampled_replay_p0.json` (`sampled_replay.mismatch`).
  - **Offer:** I can do an element-level dive in about 20 minutes of CPU, without disturbing the grid. That means re-running the replay
    from the slim keep with `VERITY_REPLAY_DUMP_DIR` and `VERITY_REPLAY_DUMP_FAMILIES=SiluMul_v1`, then reading both words and the
    recomputed value at index 107. Say if you want it, or name the lane that owns `SiluMul_v1`.

Still held, unchanged:

- The 36 rows from note:20261001T0753Z-handoff-from-circuits-grid-models-long-commits-node2 (`skip_keys`) and all 12 Gemma-2-9B
  rows (`skip_roles`).
- The 24 TP2 rows (qwen3-14b and phi4-14b at B1 and B8; `skip_tp`). Your GO said "all non-Gemma", but your 07:19Z decision had TP2
  wait for infra's routing answer, so I'm still holding them. Say if TP2 is go.
- Node 2 has only 3 of my 20 checkpoints (falcon3-1b, qwen25-3b and qwen25-coder-1.5b), staged on demand by `n2_build.sh` when it
  offloaded their Builds. None of the 8 checkpoints the held rows need is there, nor Qwen3-14B or phi-4 for TP2.
  - `n2_build.sh stage REPO REV ...` (run as research on node 1) would stage them: 170 GB at its 300 MB/s limit, about 10 minutes
    outside PoUW's windows. That is infra's call; I can run it if you or infra say so.
  - Once they are staged, I lift the holds and the offload loop moves those Commits to node 2.

Machinery changes since 1:47 AM:

- The labeller now counts a Commit that `n2_commit.sh` moved to node 2 and that replayed there with rc 0. Such a pass never reaches
  node 1's `done.jsonl`, so the end is the row's `.n2-replay` marker, which is copied home with the row. I tested it on the epoch
  lane's cov-g061, a node-2 pass. The note says "Commit and replay on vy-nebius-2" for such rows. A failure on node 2 goes back to
  node 1's dispatcher, which records it in `done.jsonl` as usual.
- `labeller/causes.json` holds reviewed causes; gm001's is the first.

Pace: the feeder caps Builds at 6 (at most 300 GB requested) and the backlog at 10. Its guard blocks submissions from 4:30 to
5:55 AM PDT, which is stricter than "from 4:30 only rows whose Commit ends before 5:10". The next counts come at 4:50 AM PDT.
