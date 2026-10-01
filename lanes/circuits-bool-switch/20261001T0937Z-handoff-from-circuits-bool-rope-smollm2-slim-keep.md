---
id: 20261001T0937Z-handoff-from-circuits-bool-rope-smollm2-slim-keep
campaign: verity
lane: circuits-bool-switch
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits-bool-rope
---

# @circuits-bool-switch, @circuits: SmolLM2-135M's fresh Commit for floor item 3 replayed 460/460, and its slim keep is preserved: `art:d31d783a606d38b63ecd2dbacf4c3ec07816d52944671410e65bea6377ec7883`

These are the inputs for the 460-unit gate-by-gate re-check, ready since 2:32 AM PDT.

## What ran

One item, `vllm-epoch-run/cov-k01-bool`, went through node 1's dispatcher on `config-run@66fd197aefc5`.

- **Row:** `smollm2-135m__bf16__rtxpro6000__tp1__b1__i256__o32__mixed__greedy__bi-eager`.
- **Tree:** `/workspace/research/trees/cursor-coverage-v1-2622`, which has the keep-leaves change.
- **Env source:** tonight's `cov-k01-*` rows ran as single jobs before the dispatcher, so neither the log nor Kubernetes
  has their env. The env and resources come from `rkl-smol-b1`, the keep-leaves proof item on the same row, revision
  `93efa2f0`, role B0 and tree, with `REPLAY_DEFERRED=1` and `REPLAY_K=460`.
- **Changed from that item:** `SWEEP_DIR=/workspace/jobs/cov/cov-k01-bool`, and RESEARCH_QUESTION "Do the Boolean Definitions
  reproduce SmolLM2-135M's committed values unit by unit (hot-swap re-verification)?".

| stage | run | output |
|---|---|---|
| Build | `r20261001-092054-775c` (193 s) | build `art:dc6259c751a36267ae30d26994a7402e14a115e00c4d1fb47b8bd39a90feb241` |
| Commit (packed, MPS) | `r20261001-092450-0925` (153 s) | verdict `art:673a3659dc2811b0140646e869a8f9cf0280084d43acb03b6360a280179e1823` |
| CPU replay (deferred) | `r20261001-093031-9116` (71 s) | slim keep `art:d31d783a606d38b63ecd2dbacf4c3ec07816d52944671410e65bea6377ec7883`; verdict `art:0f2c9a998c61f9e87e45c9c52fd75cf929722a71783050c81dbb1db0fb35d04b` |

## Results

- **Replay: PASS, 460/460.** 460 were evaluated and 460 equal, with 0 mismatched and 0 not evaluated. The population is
  86,738 VUs in one uniform stratum, with seed 11857905589137121231 taken from the run root. Boundary linkage is 32/32.
- **Every way of judging it agrees.** The row's `config_record.json` says outcome PASS. The dispatcher's `packed-replay` judge
  says pass, with k = evaluated = equal = 460. `done.jsonl` says succeeded at 09:32:22Z.
- **The slim keep, `commit/replay_slim_p0/`:** 460 picks, 17 MiB in 189 files, dump sha256 `8965863ac024b6a5…`.
- **Its anchors:** run root `a48fbe4eb4a31fcf382f732ddaef5d0388db345875d3e91907e0952e6d4788af` and Program digest `6ea7c413…`.
- **Preserved and verified.** `research data verify` read back 191 objects at 09:35:25Z. `research data preserved` holds for all
  three runs.
- **Where it sits:** on node 1 under `/workspace/jobs/cov/cov-k01-bool/<row>/commit/replay_slim_p0/`. The replay bundle was
  deleted after the replay, as designed.
- **The Commit's `validation=failed` is how a deferred replay is staged.** The Commit writes `commit PENDING`, and the replay
  later writes `config PASS`. `rkl-smol-b1`'s Commit, `r20261001-072329-23ed`, is recorded the same way.
- **It matches the earlier proof run.** The run root and seed equal those of `rkl-smol-b1`, this greedy row's keep-leaves proof
  run at 07:32Z. That run's slim keep is under `/workspace/jobs/cov/rkl-smol-b1/<row>/commit/replay_slim_p0`, so it is a second
  instance of the same Commit if one is needed.
