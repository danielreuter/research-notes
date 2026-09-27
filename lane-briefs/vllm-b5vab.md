---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

# Lane brief: vllm-rf-b5vab (split `engine/vllm_adapter.py`), successor of b5va

**Launch as** a Cursor cloud agent in `danielreuter/verity`, base branch `main`, with this prompt:

> You are vLLM refactor lane `vllm-rf-b5vab`, the successor of `vllm-rf-b5va` (its session ended at the 9:03 AM PT
> laptop restart, before its first commit). First read `/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/internal/lane-briefs/cloud-lane-setup.md`
> and do its section 1. Then read `/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/internal/lane-briefs/vllm-cloud-common.md`
> (it overrides the setup page for vLLM lanes), then your brief
> `/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/internal/lane-briefs/vllm-b5vab.md`. Write your first checkpoint
> (`research notes checkpoint vllm-rf-b5vab open "..."`) within 10 minutes.

(This lane isn't `b5vb`/`b5vc`: those split `vllm_bindings.py`.)

## Predecessor and scope
- b5va: agent bc-649f6a27. No commits, no pods. Its STATE.md (`$RESEARCH_NOTES/lanes/vllm-rf-b5va/STATE.md`) holds the
  scope, plus the 15:02Z banner about b4b's move.
- Scope (`LANE_PROMPTS_WAVE2.md` "b5va"): split `integrations/vllm/verity_vllm/engine/vllm_adapter.py` (about 1,913 lines
  at b4b) into cohesive `engine/` modules, one per job.
  - The moves are verbatim, proved by an AST/source script (b5patb's `tools/verify_split.py` approach).
  - `load_workload` and everything it calls stay in `vllm_adapter.py`: four tests extract it by path, and lane
    `vllm-rf-gc` owns those tests.
  - `build_engine` and `engine_kwargs_for` keep their signatures (a5's `verity_vllm.LLM` calls `build_engine`); it has 39
    importers.
  - No allowlist grows; the P10 entries leave the ratchet. Pure structure.
- Acceptance: lints; gate (b) against b4b's head on one pod; gate (a) T0+T1 equal to a23b's base; the #101 GPU Build
  smoke equal to the record.

## Branch
`lane/vllm-rf-b5vab` from **`5c05ff6d`** (`origin/lane/vllm-rf-b4b`, b4 rebased on c1). b5va's `2908cca1` start is obsolete.
If lane `vllm-rf-b4c` commits on top of `5c05ff6d`, it tells you; then rebase with `git rebase --onto <new> 5c05ff6d`
before your first push, or with `--force-with-lease` after, and say so in a checkpoint. The merge request goes after b4's.

## Pods (handed to you; don't touch them before the handoff arrives in your notes directory)
- `vyv-rf-b4b-cpu` (cjzaq3ploo8kok, $1.28/h) from `vllm-rf-b4c`: gate (b) at your head. b4c's head XML at `5c05ff6d`
  on the same pod is your base, so you needn't rerun the base unless b4c's head moved.
- `vyv-rf-b4b-g1` (nplcyinf9r2si8, 1x L40S, $1.09/h) from `vllm-rf-b4c`: the #101 smoke. The record is program
  `ccc21347…`, manifest `90f81868…`, run root `7adcef49…`.
- `vyv-rf-c4ir-reg` (oh3k08zb07i38u, cpu3m 32 vCPU / 256 GB, $1.76/h, fixtures in `/workspace/research/store`) from
  `vllm-rf-c4irc`, after its gate (a), expected at about 10:15 AM PT: your gate (a). Point your tree at the pod store as
  the common rules say; `inputs/reg_gate_a.sh` in c4ir's run dir is a working recipe. This pod runs gate (a) slowly
  (about 5 h), so start it as soon as your head is final.
- Until the pods come, work on the VM: map the module's jobs, importers, the tests that read it by path, monkeypatch
  uses and allowlist entries. Design and write the split, and verify it statically.
- If a pod hasn't come by 18:30Z (11:30 AM PT), say so in a handoff to the coordinator, not a new pod.

## Budget
$16 of new spend.
