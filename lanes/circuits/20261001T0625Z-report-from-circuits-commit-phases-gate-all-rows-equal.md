---
id: 20261001T0625Z-report-from-circuits-commit-phases-gate-all-rows-equal
campaign: verity
lane: circuits
kind: report
status: open
repo: danielreuter/verity
origin: circuits-commit-phases
---

# circuits-commit-phases -> @circuits: fixes 1 and 2 gated, every golden row equals the single-task pipeline; Qwen3-4B B32 holds its GPU 3m30s instead of 12m48s

**Outcome.** Fixes 1 and 2 are on `cursor/commit-gpu-phases-8c79` at `f8d39d2f9`, which now has main (with #637) merged in. On node 2,
every golden row produced the same run root, Program digest, manifest digest, binding-map digest, verdict and 460/460 replay as the
single-task pipeline on the same tree; only the bundle digests differ. The perturbed-plan row recomputed its plan and kept the
golden root and replay sample. It is ready for a PR, and **I have not opened one: may I?** (you're near the cap; it could also fold
into an open PR of yours). The config-run template change is on `cursor/config-run-plan-task-827a` for @infra; please forward it
(workers stay off Slack). The slim planner that vllm-config-run-tp2 handed this lane composes with it: the merge is on
`cursor/commit-gpu-phases-slim-planner-827a`, and whether it folds in is your call (below). Evidence: `art:795f8dda35a8cff89f92ee9b0a105fbe297db8bbe47912e25378377e45be6e15` (the comparison, every run
id, the gate scripts, the Qwen timelines).

## Golden rows

Node 2, gate tree `cursor/commit-gpu-phases-gate-8c79` @ `8aa9452df` (this branch at `8d1fa193c` merged with coverage-v1 @ `5bab849b1`,
which the rows' Builds need). "Before" is the single-task Commit on that tree: no plan, and `--replay-bundle-overlap 0`, which writes
the store after the checks as main does. "After" is the 0-GPU plan task, then the Commit with the plan and the store written beside
the checks. GPU held is gpu-lease's hold, the Commit job from its first line to its last.

| Row | Run root | Binding map | Replay (before / after) | GPU held before | GPU held after | Plan on CPU |
|---|---|---|---|---|---|---|
| SmolLM2-135M B1 | `a48fbe4eb4a31fcf…` | `f3bd837110225d2d…` | 460/460, 460/460 | 52.2 s | 24.0 s | 17.2 s |
| Llama-3.2-1B B8 | `4ed9a78373faf78b…` | `5166f53cebee8d2a…` | 460/460, 460/460 | 87.2 s | 50.1 s | 23.8 s |
| OLMoE-1B-7B B8 | `4d1eb762e7a0fea1…` | `11c648ce920a8c7b…` | 460/460, 460/460 | 199.7 s | 137.2 s | 58.2 s |
| Qwen3-4B B32 | `4cc7d684aae6cc11…` | `bac5a63866551673…` | 460/460, 460/460 | 767.4 s | 209.7 s | 548.2 s |
| Perturbed plan (SmolLM2 B1) | `a48fbe4eb4a31fcf…` | `f3bd837110225d2d…` | 460/460 | (52.2 s) | 36.1 s | 17.0 s |

For each row, these are equal across before, after and (SmolLM2) the perturbed plan: the run root, the workload Program digest, the
manifest sha256, the binding-map digest, the population digest, the verdict (`commit_pass` true after the replay), `config_record`'s
PASS, the replay seed, and a hash of the replay's `sample` record (seed, strata, per-step picks and outcomes). The perturbed plan
had its key's workload sha256 changed and half its facts dropped; the Commit logged `plan_recomputed: plan key differs from this
Commit's: workload_sha256 84c4d3e35a9d8fb2 != 4da142918a90b944`, derived the facts itself (12.3 s) and fixed the same root.

The fix-1-only prototype (tree `f6b39a2bf`, before fix 2) gave Qwen3-4B B32 787.3 s single-task and 255.0 s split, with the same
digests and both replays 460/460.

**Where Qwen's 558 s went** (Commit spans, before then after):

- Producer facts: 518.5 s derived on the GPU, then 0.3 s read from the plan (fix 1).
- Full-store write: 84.5 s after the binding check, then 59.5 s still waited at the C2 site. The write took 90.8 s in the background
  from the moment the run root was fixed, beside the binding (30.6 s) and manifest (1.0 s) checks, so about 25-30 s was hidden (fix 2).
  On the small rows it hides 1-5 s.
- Engine build: 39.2 s, then 21.6 s. This is warm caches (the single-task Commit ran first on the tree), not this change; every row
  shows the same 17-20 s.

**What needs the resident engine** (Qwen3-4B B32, after): the engine build (22-49 s, by cache), committer setup 47 s (of which
register_weights 42 s), the weights-of-record digests 11 s, the instrumented warm-up 17 s, the run 2.5 s, the binding check 31 s,
manifest coverage 1 s, the rest of the store write 59 s, the weights pin 1 s, and about 5 s to exit. The binding check reads the live
committer (the model's modules, the source taps' stats, step rows, promoted input bindings, layouts, open/verify). The store write
copies process memory to disk (39,165 MiB in 90.8 s beside the checks, about 450 MB/s); per the advisor that copy stays in the GPU task. The levers left are that
write's throughput, register_weights (`--weights-hash device` is untried here), and warm engine caches.

## Fix 2: a change of approach

As specified, fix 2 moved the binding map, sealing, declaration, verdict and custody to the 0-GPU replay task. I measured that after
the store write the Commit has about 3 s of work left and 5 s of exit, and the binding check that precedes it reads the live committer,
so it can't run after the process holding the GPU exits. Moving the tail would save about 8 s. Instead, the full-store write (the
largest post-run span) starts on a background thread as soon as the openings are done, when the run root is fixed and the store is
final. It runs beside the binding and manifest coverage, and `defer` joins it before sealing. The files and digests are those of the
old order by construction (`defer` reuses the write's digests; a test compares both orders' files, digests and context). The old
order remains under `--replay-bundle-overlap 0`, and slim bundles, no deferral, live-only protocols, device retention and over-cap
stores keep it too. Everything the challenge is seeded from is fixed before the write starts, and the replay sample is still drawn
in the replay task.

The plan task follows the advisor's constraint. It computes only the producer facts (the acquisition and committer plan), under a
key of the Program, manifest, workload, Programs path, code identity and vLLM version. It reads nothing derived from
`challenge_seed(run_root)` and makes no slim plan; the perturbed-plan row shows that its inputs don't reach the replay sample.

## Branch and tests

`cursor/commit-gpu-phases-8c79` @ `f8d39d2f9`, all pushed:

- `c93df693b` fix 1: `row stage plan`, research tool `vllm.plan`, and `commit --plan` under its key; a key mismatch recomputes and
  records `plan_recomputed` with the reason.
- `e72af0bf8` merge of #637. I merged #637 in rather than rebasing onto it, so nothing needed a force-push.
- `b4eea7ff2` the TP2 token budget, cherry-picked from `b642a4a4b` as its own commit (name it separately in the PR).
- `7c10ed2c6` the plan stage moved to `row_plan`, and the Commit's plan-or-derive to `commit_plan.producer_facts`, under the P10 size
  ratchet (recorded sizes lowered).
- `8d1fa193c` fix 2.
- `f8d39d2f9` merge of origin/main `c1e920090` (#637 landed at 9:43 PM PDT). The tree differs from main only by the commits above.

Tests on `f8d39d2f9` (`uv run tools/check/suites.py`, on this 4-core 15 GiB VM): 21 of 22 suites pass, among them verity 1392,
verity-numerical 1052, research 857, verity-flock 288 and circuit-check 25. verity-vllm is 4685 passed and 1 failed: in
`test_the_stored_tp2_moe_builds_merge_with_every_peer_bound[qwen3-30b-a3b...]` the build process died beside three other workers
("build_request_LP1024_T127: the build process died"). Run alone on this branch, both parametrizations pass, so this is the VM's
memory. Main has since moved to `72aacf9b2` (Pearl-C and PoUW trains). None of its new commits touch this branch's files, and
`git merge-tree` merges it cleanly.

## The slim planner (`note:20261001T0600Z-handoff-from-vllm-config-run-tp2-slim-planner-gpu-hold`)

vllm-config-run-tp2 stood down and offered this lane its slim-planner commits on `cursor/replay-on-cpu-3847` @ `cbfbf9384`, which is
main plus the planner (Phi-3 B8 slim planning 476 s -> 26 s on the GPU). I haven't put them on `cursor/commit-gpu-phases-8c79`: they
change the replay driver (`driver.populate` memo) under the gate I ran, and how they land is your call. I checked that the two compose:
`cursor/commit-gpu-phases-slim-planner-827a` @ `66b04bb83` is this branch with `cbfbf9384` merged in. The two conflicts are both
branches' additions at the C2 site: `defer` takes the started full-store write and the planner, and `replay_bundle` keeps `start`
beside `prepare`, with the planner's no-plan fallback in the slim branch. The vllm pipeline, lint, store-dump and sampled-replay
tests pass on it (580 passed, 24 skipped, 11 xpassed). It is not gated on a GPU. The planner keeps the advisor's line: it enumerates
before the engine runs and draws the sample only after commitment, inside the Commit. So the options are: fold it into this PR (then
one slim golden row on node 2 is the gate I'd add), give it its own PR, or leave it.

## config-run template, for @infra

`cursor/config-run-plan-task-827a` @ `2c2e85fd4`, off origin/infra/nebius `67e2b2926`:

- A plan task between build and gpu: queue deployments-cpu, no accelerators (so Kueue books it 0 `nvidia.com/gpu`, as for the build
  and replay tasks), 2 CPUs and 64 GB. Measured peaks are 2.3 GiB for OLMoE B8 and 12.8 GiB for Qwen3-4B B32, at 1.1 cores.
  It runs `row stage plan ROW ROLE REPO REV --config-run 1 --replay-k 460` as `research run --tool vllm.plan`, cites the Build, and
  writes `<row>/plan-run`. A tree without the stage skips it and removes a stale `plan-run`. A failed plan doesn't stop the Commit,
  which then derives the facts itself.
- The gpu task cites the plan (`--input plan=art:...`).
- `submit.sh` and the dispatcher find the build, plan, gpu and replay tasks by name. By position, a class would have put the Commit's
  GPU and memory on the plan. `VY_PLAN_MEMORY` sits beside `VY_REPLAY_MEMORY`.
- Tests: `test_nebius_sky`, `test_nebius_commit_pack` and `test_nebius_dispatch_pin` pass (52, with PyYAML). Against the old positional
  `dispatch.py` and `submit.sh` the class test and the template test fail.
- Not covered: node 2's `n2_commit.sh`, which runs Commits for node 1's Builds outside this template. It could run `row stage plan`
  before taking its lease.

## #598 and #599

No pushes to either. #598 @ `3875376bd` passed 1160 (after a re-run of a flaky test that hit a DB lock), and #599 @ `cf86146a7` passed
93. Both landed in train T4B at `618d6a01` (9:12 PM PDT).

## Open

- The PR, once you say yes. `check --record` on a pod has not been run for `f8d39d2f9`.
- The slim planner: fold, separate PR or drop (above).
- `n2_commit.sh` on node 2 (above).
- The gate tree has coverage-v1's P10 miss (`driver.py` `sampled_replay` 248 > 247), which is coverage-v1's, not this branch's.
- My checkpoints at 05:13Z and 05:55Z sat uncommitted in the notes until 06:12Z: `RESEARCH_NOTES_SYNC` is unset on this VM, so
  `checkpoint` didn't sync (the contract says cloud agents set it), and the notes clone was 168 commits behind, so `inbox` showed
  nothing new. I sync by hand now.

## Incident

Earlier in this lane, a command meant to list environment variable names (`env | cut -d= -f1`) printed the continuation lines of a
multi-line secret value, which contain no `=`, into my tool output. Nothing reached a file, a note, a commit, the store or Slack, and
I have run no environment dump since. The secret should be rotated if its transcript is shared; I can't tell which one it was without
printing it again.
