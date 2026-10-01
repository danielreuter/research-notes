---
id: 20261001T0618Z-handoff-from-circuits-build-speed-pr-639-grant
campaign: circuits-build-speed
lane: circuits
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits-build-speed (bc-d2d56312-a75e-56c6-a829-45a5135a3752)
---

# circuits-build-speed: #639 is open and marked ready at 1c2487ef8, and waits for your grant. The reference-row Build takes 196 s on the branch against 291 s on main, with every digest equal

The PR is [#639](https://github.com/danielreuter/verity/pull/639), from `cursor/build-speed-8c79` at `1c2487ef8ac07826ad4bb2a05fb0b226c4b0ea88`. `research queue ready 639 --by circuits-build-speed` is recorded at that head.

The branch is merged with `main` (`03dddbc23`), not rebased, because my rules forbid force-pushing a pushed branch. Every timing below comes from back-to-back runs through the queue on vy-nebius-1, at 16 CPUs:

| Row | main | branch | Runs (main, branch) |
|---|---|---|---|
| Llama-3.2-1B B8 1024/128 | 291 s | 196 s | r20261001-055617-3f39, r20261001-060202-d606 |
| Llama-3.2-1B B1 256/32 | 112 s | 65 s | r20261001-060607-e264, r20261001-060949-3298 |

Every program, correspondence, workload and manifest digest is equal between `main` and the branch, and to the `e3ea0c9a0` baseline. Only the artifact identity differs, because `build.py` is a construction source. Peak memory on the reference row goes from 15.1 to 18.7 GB, because the manifest now builds beside the compose.

**Left for the merge:**
- your grant at `1c2487ef8`;
- a passing `check` of that head.

Locally, the touched tests give 61 passed. The full vllm suite I ran before the merge with main had one failure, `test_tp_moe_members`: the 15 GB agent VM ran out of memory. That test takes the explicit-digest path, which the branch doesn't change. The rerun on the merged tree is in progress.

**Next:** I'm measuring the 4k-context row (`llama32-1b` L40S B1 4096/512, r20261001-061206-423c), for the attention references' quadratic term and a manifest word-check cache keyed by Program digest. That work goes on a new branch, so #639's head and its grant stay put.
