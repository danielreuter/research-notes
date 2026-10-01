---
id: 20261001T0225Z-handoff-from-vllm-config-run-tp2-572-merged-heads
campaign: overnight-sep30
lane: circuits
kind: handoff
status: open
repo: danielreuter/verity
origin: vllm-config-run-tp2 (bc-35ab914e), answering note:20261001T0144Z-handoff-from-circuits-merge-572-into-598-URGENT
cursor:
  subagentId: "bc-35ab914e-d276-5d3b-bab0-9f87a3ef3847"
---

# @circuits: #572 (`9288c339`) is merged into both PRs; new heads #598 `ea302d4c5`, #599 `cf86146a7`

- **#598** `cursor/replay-on-cpu-3847` @ **`ea302d4c5`**: #572 merged, then #599 merged.
- **#599** `cursor/replay-deferred-bundle-3847` @ **`cf86146a7`**: #572 merged too, because #599 alone conflicted with #572 in `p10_size.json`.
- `git merge-tree` shows each head merges cleanly on `9288c339`, and #599 is an ancestor of #598.

**How the conflicts were resolved (both behaviours kept):**
- `check/replay/evaluate.py`: `_evaluate_row` takes #572's `row=` and my `plan=`. Interior rows pass both. A plan returns before #572's delegate dispatch, so planning never evaluates.
- `pipeline/commit.py`: #572 changed the inline C2 block, which #598 moved into `pipeline/c2_replay.py`. I ported the change there: the replay runs under `pouw_circuit.replayed(protocols, …)`, with `protocols` now on `C2.Site`.
  - New rule: a run composed with `pouw:ncp-v2` never defers (`C2.live_only`). Its circuit replay reads the live run, so it replays in process.
- `p10_size.json`: recounted with the test; `commit.main` is 1434 on #598 and 1762 on #599.

**Tests:** these suites pass on #598 (`tests/check`, `tests/pipeline`, `tests/lint`, `tests/commit/test_store_dump.py`) and on #599 (`tests/lint`, `tests/pipeline/test_replay_bundle.py`, `tests/pipeline/test_config_run.py`, `tests/commit/test_store_dump.py`).

**Next:** cut the plan's 476 s of GPU hold (your 0149Z order, goal ≤ 60 s added). I'll profile first.
