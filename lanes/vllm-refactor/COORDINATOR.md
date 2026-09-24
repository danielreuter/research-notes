---
id: vllm-refactor/coordinator-state
lane: vllm-refactor
kind: state
updated: 2026-09-24T17:45Z
---
# vllm-refactor: coordinator state (resume from here)

## Where things stand
- **Survey:** done, 673 findings. The synthesis is `SYNTHESIS.md` in this directory; its gate text and A4 ordering were corrected by the coordinator.
- **Owner decisions** (17:20Z), all as recommended:
  - merge cleanup-2 into main and branch from main;
  - start Phase 0 and A1 to A3 now;
  - value checks over opened values inside Commit now, with a separate verifier later;
  - delete CMT-1, `engine_rs` and the dead PoC paths;
  - refuse world > 2.
- **Merge:** `lane/vllm-cleanup-2` went into `main` at `72884c8a` (17:24Z, `--no-ff`). The only extra changes relative to cleanup-2 are in `tools/research`. No references to the removed package paths remain outside the integration.
- **Budget and deadline:**
  - The CAP file on `vy-control-verity` is 600. Spend was $238.67 when it was raised; the tally has run since 2026-09-23 under tag `2026-09-23-vyv-rebuild`.
  - The rate cap is $45/h.
  - The deadline daemon terminates `vyv-` pods at 03:00Z.
- **Watcher:** the other coordinator's notes watcher excludes `vllm*` lanes, which is why the refactor lanes are named `vllm-rf-*`.

## Lanes (local subagents launched from chat eb746331; the brief is `LANE_BRIEF.md`)
| lane | scope | agent id | branch | notes dir |
|---|---|---|---|---|
| a1 | baseline and guardrail lints | 0071dbd5-fc85-40a2-b188-0ff3b70d93a3 | lane/vllm-rf-a1 | ~/.research/notes/lanes/vllm-rf-a1 |
| a23 | dead code, data and paths | 910daceb-3d03-4c35-abd4-3ef36049a9a6 | lane/vllm-rf-a23 | …/vllm-rf-a23 |
| f1 | D1 opened-value replay | ca142d03-cbdd-4db6-921c-ad007244aa4b | lane/vllm-rf-f1 | …/vllm-rf-f1 |
| f24 | D5, D6, D7, D10, D11, D13 | 1d5dba5f-1f4a-44b3-b2b7-01aa308edc91 | lane/vllm-rf-f24 | …/vllm-rf-f24 |
| f3 | D3, D4, D14, D15 | 4d8eb3fd-689f-4551-a6ef-9439c59c06e6 | lane/vllm-rf-f3 | …/vllm-rf-f3 |
| f56 | D16, D17 | fec8581f-4b57-4899-81f1-ead76e01ceee | lane/vllm-rf-f56 | …/vllm-rf-f56 |

The canvas agent (742f18e5-2fc5-4a71-b848-36d442816381) is building a canvas of the survey and plan.

## If a lane dies
Relaunch a fresh generalPurpose subagent with the same prompt, plus: "RESTART: read your STATE.md first and continue from it." The prompts are in chat eb746331. Each one is a short scope paragraph that points at `LANE_BRIEF.md` and its `SYNTHESIS.md` sections.

## Merging
The order is a1, then a23, then the f-lanes as their READY.md files appear. For each lane:
1. Check the gate evidence in READY.md against the baseline.
2. Merge `--no-ff` into main from a scratch worktree (`git worktree add --detach /tmp/rf-merge origin/main`).
3. Push only if main hasn't moved.
4. Tell the remaining lanes to rebase.

## Next phases (not started)
- **A4, re-home into the 12-package tree:** after the Phase 0 lanes merge.
- **A5, one CLI and typed config:** after A4.
- **Phase 2:** B1 to B5.
- **Phase 3:** C1 to C4, behind decisions 1, 3, 4 and 5, which are still open.
