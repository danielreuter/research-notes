---
id: vllm-refactor/wave2-brief
lane: vllm-refactor
kind: brief
from: vllm-coordinator (Cursor agent bc-ba6cec03)
created: 2026-09-25T08:20Z
---
# Wave 2 lanes (after A4): shared rules

> **Coordinator, 09:30Z: custody rule for the cloud switch-over.** Push your branch to origin after every commit, WIP included. If you have uncommitted work worth keeping, commit it now and push. The coordinator pushed snapshots of uncommitted work to wip/vllm-rf-{lane} for custody; they are not for merge, so ignore them.

Read this, then `LANE_BRIEF.md` for the older hard rules (laptop, style, crash-only). Where the two differ, this file wins. Then read `SYNTHESIS.md`: sections 4 and 5, section 6 for your lane, and the decision log at the end, which records all five owner decisions (2026-09-25).

## Base and branch
- **A4 hasn't merged yet.** Lane a4 has moved the whole package tree into the section 5.1 layout (`program/kernels/` is the owner's name for what 5.1 calls `program/backends/`). Its pushed head, `origin/lane/vllm-rf-a4` at **`10996616`**, is your base.
- **Create your worktree:** `git -C ~/projects/verity-wt/rf-a1 worktree add ~/projects/verity-wt/rf-{lane} -b lane/vllm-rf-{lane} 10996616`. Write `a4 base: 10996616` in your STATE.md.
- **When A4 merges** (`git merge-base --is-ancestor origin/lane/vllm-rf-a4 origin/main`, or the coordinator's STATE banner), rebase with `git rebase --onto origin/main {your a4 base} lane/vllm-rf-{lane}`, then push with `--force-with-lease`. If a4 has changed its branch since 10996616, the coordinator posts the new base in your STATE.md.
- **Other lanes** run at the same time, and the file ownership is below. Keep hunks in other lanes' files minimal, and never reformat or reorder code you aren't changing.
- **Push** after every commit: `git push -u origin lane/vllm-rf-{lane}`.

## Invariants
- No Program digest, manifest digest, commitment root, leaf id or regression verdict changes. Code-identity digests may change; record them before and after.
- Any change that must move a digest goes in its own commit, labeled for the re-baseline epoch (decision 4). Say so in READY.md, and don't make the rest of the lane depend on it.
- Lints and import contracts stay green, and no allowlist grows. If you remove a violation, delete its entry in the same commit.

## Gates, on pods, before READY.md
1. **Lints:** `python -m pytest integrations/vllm/tests/lint integrations/vllm/tests/test_no_by_name_rules.py integrations/vllm/tests/test_imports_resolve.py -q`, green at your head.
2. **Gate (b):** `OMP_NUM_THREADS=3 python -m pytest integrations/vllm/tests -ra -n 12 --dist loadfile`, at your head and at your base (a4's head, or main once A4 is in) side by side on the same pod.
   - Compare with `~/.research/notes/lanes/vllm-rf-a1/baseline-jdiff.py`: no new failure, error, skip or skip reason. List renamed tests.
   - Counts follow the host CPU (see f1's READY.md), so always compare on the same pod.
3. **Gate (a):** `VERITY_REGRESSION=1 VERITY_REGRESSION_TIERS=T0,T1 python -m pytest integrations/vllm/tests/regression -m regression`, on a cpu3m pod with 512 GB.
   - T1 `replay_partition` needs up to about 115 GB per process.
   - It must match `~/.research/notes/lanes/vllm-rf-a23b/gate_a-t0t1-base-72884c8a-samepod.xml.gz` test by test.
4. **Your lane's acceptance** from SYNTHESIS section 6, including the GPU rows it names. A GPU row is compared with its regression record: program_digest, manifest_digest, run root and verdict.

## Pods and money
- **Setup:** name pods `vyv-rf-{lane}-{purpose}`, and register each in `~/.research/machines.toml` with `guard = 90` (copy lane f1's `vyv-rf-f1-g1b` entry). Bootstrap with the recipe in `~/.research/notes/lanes/vllm-rf-a1/baseline.md`, plus `pytest-xdist==3.8.0`.
- **Long jobs:** run them through `research run --on {pod} --project verity --source {clean worktree} --cwd source -- ...`, so they're recorded and survive you. Kill by pid; never `pkill -f` over ssh.
- **Fixture keys:** mint a 3 h read-only key on the laptop and pipe it into your own pod. Fetch every row, then delete it at once (the baseline.md gate (a) recipe).
- **Budget:** your lane's budget is in your prompt. vLLM has $300 of new spend tonight, shared by all lanes. Terminate pods as soon as their runs are fetched (`research fetch --all`), and all of them at READY.
- **Deadline:** a daemon terminates every `vyv-` pod at the armed deadline. The coordinator extends it in steps of at most 4 h and posts it in your STATE.md; register results as they land.

## Laptop
- Allowed: git, rg, small text-rewriting scripts that don't import `verity_vllm` (`uvx --python 3.12 python x.py`), and the `research` launcher.
- Not allowed: pytest, torch, builds.
- About 7 GB of disk is free, and a guardian kills any Python process over 1 GB. Never touch another lane's worktree.

## Notes and finish
- Notes go in `~/.research/notes/lanes/vllm-rf-{lane}/`. Create STATE.md at the start, and update it at least every 20 minutes and at every milestone.
- STATE.md records commits, what's running (pods, run ids), what's next, open questions, and "Found, not fixed". The coordinator reads Open questions every 30 minutes.
- READY.md records the branch and head, the base, the gate evidence (commands, counts, run ids, XML paths beside it), what changed, what deliberately didn't, and "Found, not fixed".
- Final message to the coordinator: 250 words or fewer, with the head, the gates, the READY.md path, and blockers. No progress messages.

## File ownership in this wave
- **a5, one CLI and typed config:**
  - `config.py`, `pipeline/cli.py`, the public API in `verity_vllm/__init__.py` and its module, `pyproject` `[project.scripts]`;
  - the `argparse` and `__main__` blocks in library modules;
  - `ops/*.sh` that become subcommands;
  - `pipeline/research.py`.
- **c1, commitment scheme:** `commit/` (`scheme.py`, `committer/`, `openings.py`, `binding.py`) and the commit-throughput instrumentation.
- **c2, Definition library:** `program/registry/` and the core Definitions under `packages/verity/src/verity/ml/`.
- **b1, evaluator kernels and replay:** `program/kernels/`, `check/replay/`, and the replay drivers (`replay`, `stoch_recompute`, `compiled_kernel_check`, `difftest`).
- **b4, engine and hooks:** `engine/` (`build.py`, `env.py`, `driver.py`, `hooks.py`, `profiles/`, `rank_worker.py`). a5's `LLM` calls `engine`'s build entry point; b4 keeps that entry point's signature, or agrees a change with a5 through the coordinator.
- **b2v, one verdict:** `check/result.py`, `check/verdict.py` and the `commit_verdict` absorption, and `properties/`. The `row_pod.sh` heredoc waits for a5.
- **c4ir, IR analyses to core:** `query/` boundary and partition, `program/frontend/liveness`, and `packages/verity/src/verity/ir/`.
