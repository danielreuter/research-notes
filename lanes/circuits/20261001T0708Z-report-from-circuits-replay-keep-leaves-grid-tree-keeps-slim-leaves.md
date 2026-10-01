---
id: 20261001T0708Z-report-from-circuits-replay-keep-leaves-grid-tree-keeps-slim-leaves
campaign: verity
lane: circuits
kind: report
status: open
repo: danielreuter/verity
origin: circuits-replay-keep-leaves
---

# circuits-replay-keep-leaves -> @circuits: node 1's grid tree keeps every decided replay's leaves (slim keep) before the bundle goes; proof row queued

**Outcome.** Node 1's `/workspace/research/trees/cursor-coverage-v1-2622` is at `4764da87e` (clean, synced 12:01 AM PDT). Every replay
task that starts from now on works like this:

- It records what its 460 picks read.
- After a decided replay (pass or fail), it writes `commit/replay_slim_p<pair>/` and publishes it as a preserved
  `vllm-replay-slim/v1` typed output of the replay's `research run`.
- The row deletes the full bundle only after `slim.json` exists. A crashed replay, or a decided replay that left no keep, keeps the
  bundle.

Running tasks keep their own `job_tree.sh` copies, and the bundle format is unchanged, so a bundle sealed on the old tree replays on
the new one. The proof row, SmolLM2-135M B1 greedy 256/32, was submitted at 12:05 AM PDT; its result follows in a second report.

## Branches

| branch | head | what |
|---|---|---|
| `cursor/replay-keep-leaves-b3b0` (off main) | `913ea442f` | the change and its tests. The name ends `-b3b0`, not `-8c79`: my VM only lets me create `-b3b0` branches. **No PR yet: may I open it?** |
| `cursor/coverage-v1-2622` | `4764da87e` | 7 `-x` cherry-picks on `5bab849b1` (fast-forward, no force), plus one run-branch commit that reflows `sampled_replay`'s signature so P10 stays at 247 lines |

The coverage port carries main's prerequisites:

- `sampled_replay(plan=True)`
- `store_dump.touched` and the slim `dump(touched=)`
- a dumped store dumps again
- the bundle-discard rule (a failed Commit and a decided replay delete the bundle; a crashed replay keeps it)

Two resolutions differ from main:

- `driver.py`: coverage's `replay_draw` stays in the signature.
- `c2_replay.py`: coverage has no `protocols` or `plan` arguments in `evaluate`, so only `Site.reads` and the re-plan were ported.

The vLLM `tests/lint`, `tests/pipeline`, `tests/commit/test_store_dump.py` and `tests/check/test_sampled_replay.py` pass on the port,
as does research's `test_store_vllm_tools.py`.

## What the keep is

`commit/replay_slim_p<pair>/` holds:

- `store/`: a slim `store_dump` with only the byte ranges and Merkle nodes that the picks' openings read. A read it lacks refuses
  by name; it never returns zeros.
- `weights/`: the bundle's `tree.json` and `extra/*.bin`, the buffers and engine constants that no checkpoint holds.
- `binding_map.json` and `context.json`.
- `slim.json`, which records:
  - the run root, the Program digest (and each Program's), and the binding map's sha256
  - the bundle manifest's sha256
  - the Commit's pass
  - `picked` (460) and the picks as `[request_id, step, i, op_path]`
  - each file's sha256 and size, and `dump_sha256` (the sha256 of the canonical JSON of that file map)

The picks' reads are collected by making the replay's own draw again in-process after the replay (`sampled_replay(plan=True)`, read
only, before the Programs are freed): its forked evaluators' reads never reach the parent. The keep is written only when that draw
names exactly the replay's `picked`. It is written before `record()` rewrites the Commit's record, so a failure while keeping leaves
the replay retryable. It adds no GPU time; the extra CPU is one serial plan over 460 picks.

## @infra must change one template line (they own it)

`config-run.yaml`'s replay task (line 355 in `config-run@66fd197aefc5`) deletes the bundles on rc 0 whether a keep exists or not:

```sh
if [ "$rc" = 0 ] && [ -s "$SWEEP_DIR/$ROW/config_record.json" ]; then rm -rf "$SWEEP_DIR/$ROW"/commit/replay_bundle_p*; fi
```

Proposed:

```sh
if [ "$rc" = 0 ] && [ -s "$SWEEP_DIR/$ROW/config_record.json" ] && ls "$SWEEP_DIR/$ROW"/commit/replay_slim_p*/slim.json > /dev/null 2>&1; then
  rm -rf "$SWEEP_DIR/$ROW"/commit/replay_bundle_p*
fi
```

On the new tree, the row deletes the bundle itself, and only after the keep exists. The line only matters for an older tree, or for a
keep that failed. Its glob never matches `replay_slim_p*`, and it runs after `research run` has already published the keep, so it
doesn't block the grid. The gpu task's line 248 (a failed Commit deletes its bundle) is right as it is. I'm sending this to @infra on
Slack.
