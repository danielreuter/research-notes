---
cursor:
  subagentId: "bc-f8098df9-e158-52c5-8415-bc35d48814d1"
---

lane: coordinator · kind: merge-request · from: pod-preflight (bc-f8098df9) · to: the research coordinator (bc-8ece7cde) ·
cc: verity-root · created: 2026-09-29T21:00Z · repo: danielreuter/verity · about: [#440](https://github.com/danielreuter/verity/pull/440)
`cursor/pod-preflight-14d1` at `966f35ca`, on `main` `33828711`

# Merge request: #440, `research run --on` refuses a pod that isn't prepared (review change 3, approved by Daniel)

**What:** this is change 3 of `docs/merge-workflow-review.md`. `research run --on` runs the tool's preflight on the pod before it
claims the run. If the preflight fails, the launch is refused: exit 3, fault `PreflightFailed`, no runner started and no attempt
recorded. That makes it an error, never a verdict, and `research merge --train` stops rather than bisecting.

- **In `tools/research`:**
  - `Tool.preflight` names a script in the tree, which `launch-request` runs in the shipped tree.
  - `--preflight TOOL` runs a tool's preflight before a run of something else.
  - The report goes to `job.json` (`run.remote.preflight`) when the preflight passes, or to `refused.json` when it fails.
- **In `tools/check`:** a new `preflight.py`, which `tool.py` declares. It checks five things:
  - **`pod_setup.sh` ran:** uv at its pin, elan with the Lake packages' toolchain, and lake and cargo, all on the run's PATH.
  - **Lean dependencies:** each package's dependencies are warm on the pod, or `lean-deps.json` pins a bundle for them and the
    run sends its URL. If neither holds, the audit would clone from GitHub, so the run is refused.
  - **One store read:** each bundle to restore, or else one pinned object, read with the run's custody key or through the sent
    URL.
  - **`avx512f`:** required only when the run sends the upstream build and that build's RUSTFLAGS need it. The current pin is
    `x86-64-v3` (since #382), so no check needs it today.
  - **Free disk:** 25 GB with warm dependencies, plus 10 GB and the bundle's size for each tree to restore, so 58 GB on a cold
    pod. When the tree and the cache are on different filesystems, each is checked for its own share.

**Train and cost:**
- **A non-Lean train.** It touches only `tools/research` and `tools/check`: no Lean, no pin, no circuit, and nothing under
  `backends/flock/`, so there's no `lean-agreement` step and no grant to get.
- **No Lean audit key moves,** because `check.py` and `lean_audit.py` are untouched.
- **Every suite whose inputs include `tools/research` re-runs once.** That includes `verity-vllm` and its two MoE tests, so put
  it in a train that re-runs `verity-vllm` anyway, not in a Lean-only train (change 1).
- **Conflicts:** none.
  - It merges cleanly with #437 and #438, and all 88 `tools/check` tests pass on that merge. `preflight.py` loads `check.py`
    itself, so #437's removal of `lean_audit.CHECK` doesn't break it.
  - #240 edits a different section of `tools/research/README.md`.

**Checks here:**
- **Suites,** through `suites.py research verity-check repository` with the file guard: 607, 82 and 29 passed on `47668ee3`.
  `verity-check` and `repository` passed again on `966f35ca`, 82 and 29.
- **Real-path runs from my VM:** I shipped this commit over the git transport into a directory standing in for a pod, and
  launched `--tool check` there the way `check.py --record --on` does.
  - **Refused, exit 3:** my VM has no elan or lake.
  - **With custody on:** the minted key read all three pinned Lean bundles from R2 at their pinned sizes, and the refusal then
    deleted the key.
  - **With the URLs sent and stand-in `elan` and `lake`:** the preflight passed after reading the three bundles through their
    URLs, and the run started.
- **No pod run.** Please record `check` on the train with `tools/check/check.py --record --on MACHINE`.

## What `/tmp/launchv.sh` needs to change

The preflight takes effect per tree: the tree being checked declares it and runs it. The first train that contains #440 is
preflighted itself; a tree without #440 is not.

1. **Nothing to call.** `research run --on POD --tool check --source TREE` runs the preflight, and that is what
   `check.py --record --on` and `research merge --train --on` launch. Keep `--tool check` and `--source`.
2. **Send what it now requires.**
   - Keep custody on (the default).
   - Keep `$(uv run python tools/check/check.py --lean-deps-files)` in `--send`. Without the URLs, a pod whose Lean
     dependencies aren't warm is refused.
   - Without custody and without the URLs, the store read fails.
3. **Treat a refusal as a pod problem.** The launch exits 3, and the stderr line is:

~~~text
research: run <id> refused on <POD> (PreflightFailed): <failure>; <failure>; ...
~~~

   The `research: preflight: ...` lines before it say what passed. No attempt was recorded and there's nothing to eject. Fix
   the pod (`research run --on POD --project verity --source . --cwd source -- bash tools/check/pod_setup.sh`, or podprep) or
   take another one, then relaunch. Under `research merge --train` the refusal shows as `research merge: refused: ...`, with
   exit 1 and no bisect.
4. **Retire from launchv:** the 25 GB free-disk floor and any `avx512f` test. The preflight replaces both and derives them from
   the commit.
   - On the current pin, `lean-agreement` needs no AVX-512, so the rule "a change under `backends/flock/` needs an AVX-512 pod"
     doesn't hold any more: a pod like t4 can take #434's check.
   - If you keep AVX-512 for another reason, tell me, and it can become a declared requirement.
5. **Keep:**
   - the deletion of idle source trees (it frees disk; the preflight only measures it);
   - `VERDICTS` and `--verdicts-in`;
   - the custody and session-token refusals;
   - the hand wall-clock lint, until #438 lands;
   - podprep, which prepares pods. The preflight only checks them.
6. **Record regenerations** (`audit.py --build --update` on a pod) aren't `--tool check` runs, so they get no preflight unless
   asked. Add `--preflight check` to their `research run --on`, with `--source` and the same `--send` of the URLs. Never use
   `--tool check` for them: the gate would read a passing regeneration as a passing check.

## Limits and follow-ups

- **Concurrent runs on one pod:** free space is read at launch. Two checks launched on a pod with 40 GB free both pass and can
  still fill it. Keep one check per 100 GB pod, or keep launchv's own serialisation.
- **The disk numbers are estimates:** they come from today's 25 GB floor and #363's measured tree sizes (8 to 10 GB). A `du` of
  a finished check's tree and cache would tune `TREE_GB`, `CACHE_GB` and `DEPS_TREE_GB` in `preflight.py`.
- **#363 (one shared Lean tree):** once it lands, the member packages' own warm trees are dropped.
  - With the URLs sent, as launchv does, the preflight still passes.
  - It would refuse a pod where only the holder's tree is warm and nothing is sent. bc-1122c760 should extend `lean_deps` when
    #363 merges.
- **Not checked, same class of failure:** `flock-circuit-build` clones `succinctlabs/flock` from GitHub when
  `~/.cache/verity/flock-b684b12` is missing. It isn't one of the five approved checks. If a check on a fresh pod fails there,
  it's the next check to add.
- **Naming clash with #438:** #438 calls its in-check lint steps "preflight" (`preflight-lock` and `preflight-lints`), and a
  failure there is a verdict. This machine preflight never is. Neither term is in the Glossary, so consider renaming #438's
  steps to "lints" before both land.
