---
id: vllm-refactor/lane-prompts-wave2
lane: vllm-refactor
kind: reference
from: vllm-coordinator (Cursor agent bc-ba6cec03)
created: 2026-09-25T14:10Z
---
# Wave 2 lanes: scopes, and the restart procedure for successors

## RESTART: for a successor lane `{X}b` whose predecessor `{X}` hung

**What happened:** the predecessor's session hung at about 12:30Z, when the host disconnected. Its shells froze and it can't act; it may still look "running", but it will never finish. You take over.

1. **Leave the predecessor alone.** Never touch its worktree `~/projects/verity-wt/rf-{X}` or its branch `lane/vllm-rf-{X}`.
2. **Your worktree:** `git -C ~/projects/verity-wt/rf-a1 worktree add ~/projects/verity-wt/rf-{X}b -b lane/vllm-rf-{X}b {start}`. Your prompt gives `{start}`: the predecessor's pushed head, or its WIP snapshot `wip/vllm-rf-{X}-0705`. Push at once with `git push -u origin lane/vllm-rf-{X}b`, and after every commit.
3. **Your notes:** `~/.research/notes/lanes/vllm-rf-{X}b/`. Start STATE.md by copying the predecessor's `vllm-rf-{X}/STATE.md` and its READY.md draft, if any. Say at the top that you succeed `{X}`, and name the start commit.
4. **Pods and runs:** the predecessor's `vyv-rf-{X}-*` pods are yours; `research pods list` shows them.
   - Check its runs from STATE.md. Get status with `research fetch {run}` (no `--all`), or over ssh on the pod.
   - A run still going is fine; let it finish.
   - A pod with nothing running and nothing left to do: terminate it.
   - Don't redo work whose results are recorded, whether in STATE.md, on the pod or in R2.
5. **Base:** a4's head `10996616`, which isn't in main yet, is still the base. When a4 merges, rebase with `git rebase --onto origin/main 10996616`.
6. **Rules:** everything in `WAVE2_BRIEF.md`, including its banners:
   - no laptop-side fetch of run outputs, and `--custody-r2` on new runs;
   - push after every commit;
   - the deadline, now 2026-09-25T17:00Z and extended in steps.
7. **Finish:** READY.md in your notes dir, then a final message of 250 words or fewer.

## Scopes, as each lane was launched (details are in each predecessor's STATE.md)

- **a5: one CLI, typed config and the public API.**
  - SYNTHESIS section 6 A5: `config.py` typed config; `pipeline/cli.py`; no library `__main__` or argparse; `row_pod.sh`, `tp_stage.sh` and `run_row_v2.sh` become `verity-vllm row`; research Tools call the CLI; environment reads move into the CLI.
  - Owner decision 8: `verity_vllm.LLM(model, revision=..., {supported options})`, constructed like `vllm.LLM`. It builds and pins internally, returns vLLM's outputs plus our records, documents every supported option, and fails loudly on an unsupported one. There's no user-built-engine wrapping. No "RowSpec" in the public API or docs; the pinned internal record gets a descriptive name.
  - Acceptance: every regression row family re-runs through `verity-vllm row` with identical artifacts (#101, one MoE row, TP2 #70), and a small `LLM(...).generate` gives outputs equal to plain `vllm.LLM`. Budget $35.
- **c2: Definition library.**
  - Owner principle: core owns the basic Definitions and all silicon semantics; the integration cites core and defines only application-specific ones; flag borderline cases.
  - Steps: (1) evaluator equality, exhaustive for the conversions and wide sampling for the Hopper dot; (2) a digest-neutral commit that deletes the four duplicate ids and cites core; (3) the inventory, moving silicon Definitions to core under the same id where that's digest-neutral; (4) a separate epoch commit, `AmpereBF16TcDot16` v1 to v2. Budget $25.
- **b1: evaluator kernels and replay.** `program/kernels/` (twins, derived rows, the sampled_replay ladder, relations, numerics), registered with core `verity.evaluation` (`register_kernel`, `self_check`). `check/replay/` becomes sample, open, evaluate, compare. The drivers share one challenge function with seeds unchanged, and `sampled_replay.py` goes. Acceptance: GPU Commit rows per family (dense, MoE #67, TP2 #70), with replay wall time before and after. Budget $45.
- **b4: engine and hooks.** `engine/` builds from the pinned record. `env.py` writes the pins at construction, and `hooks.py` is the sole owner of every vLLM and torch patch, each uninstallable. The P9 runtime-patch entries go. Keep the build entry point's signature for a5. Acceptance: GPU rows #101, the FA2 tap and TP2 #70 if the hooks moved, with non-interference unchanged. Budget $25.
- **b2v: one verdict and properties records.** `check/result.py`; `check/verdict.py` absorbs V1 to V5 (the row_pod heredoc waits for a5); runs cite `properties/` records by digest; a world-parametric non-interference check. Acceptance: the verdict JSON byte-identical, and non-interference on world 1 (#101) and world 2 (#70). Budget $30.
- **b5gm: split `check/match/global_match.py`** (above all `_check`) into cohesive `check/match/` modules. Pure structure; the P10 entries go. Acceptance: GM-01 on row #23 byte-identical with runtime within about 10%, plus gates. Budget $15, CPU only.
- **b5pat: split the fold's pattern module** into `observe/fold/patterns/`, one module per kernel family. Pure structure, with match order preserved. Acceptance: re-folded record Programs byte-identical, plus gates. Budget $15, CPU only.
- **c4ir: IR analyses to core, phase 2.** Phase 1 (core `verity.ir` boundary, partition, liveness and intervals) is a pending merge request at `lane/vllm-rf-c4ir` `cfe0ae63`. Phase 2 (`18e29d92`, `4a2ccf11`, on `lane/vllm-rf-c4ir-p2-on-a4` `7313e799`) switches the integration to core and deletes its copies.
  - Gates stacked on a4: lints, core tests, gate (b) against a4's head on the same pod, gate (a) T0+T1, and the #101 GPU Build smoke with program and manifest digests equal.
  - After a4 merges, push the phase 2 result as `lane/vllm-rf-c4ir`. Budget $15 more.
