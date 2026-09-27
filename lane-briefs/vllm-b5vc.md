---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

# Lane brief: vllm-rf-b5vc (split `vllm_bindings.py`), successor of b5vb

**Launch as** a Cursor cloud agent in `danielreuter/verity`, base branch `main`, with this prompt:

> You are vLLM refactor lane `vllm-rf-b5vc`, the successor of `vllm-rf-b5vb` (its session ended at the 9:03 AM PT laptop
> restart, before its first commit). First read `/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/internal/lane-briefs/cloud-lane-setup.md`
> and do its section 1. Then read `/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/internal/lane-briefs/vllm-cloud-common.md`
> (it overrides the setup page for vLLM lanes), then your brief
> `/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/internal/lane-briefs/vllm-b5vc.md`. Write your first checkpoint
> (`research notes checkpoint vllm-rf-b5vc open "..."`) within 10 minutes.

## Predecessor and scope
- b5vb: agent bc-19e6c2c5. No commits, no pods. Its STATE.md (`$RESEARCH_NOTES/lanes/vllm-rf-b5vb/STATE.md`) holds the
  scope. The design work it did after 14:40Z is lost, so start fresh.
- Scope (`LANE_PROMPTS_WAVE2.md` "b5vb"): split `integrations/vllm/verity_vllm/program/frontend/rules/vllm_bindings.py`
  (1,905 lines) into a `rules/vllm_bindings/` package, one module per rule family (plus pins/targets and observation
  state).
  - `__init__` re-exports exactly the names importers use.
  - The moves are verbatim, proved by an AST/source script (b5patb's `tools/verify_split.py` approach, described in
    `$RESEARCH_NOTES/lanes/vllm-rf-b5patb/STATE.md`).
  - The order of `VLLM_BINDING_RULES` stays identical, and module state lives in one module.
  - Lint entries are re-keyed; no allowlist grows; the P10 entries leave the ratchet.
  - Pure structure: no Program, manifest or verdict change.
- Acceptance: lints; gate (b) head against base on one pod; gate (a) T0+T1 equal to a23b's base; the #101 GPU Build smoke
  with program and manifest equal to the record.

## Branch
`lane/vllm-rf-b5vc` from **`origin/main` `8a3aa083`** (includes a4 and c1; c1 didn't touch this module). Gate (b)'s base
is `8a3aa083`.

## Pods (handed to you; don't touch them before the handoff arrives in your notes directory)
- `vyv-rf-a5-t1` (cyu8vao39x21th, 32 vCPU / 755 GB, $1.76/h, bootstrapped, fixtures in `/workspace/research/store`):
  from `vllm-rf-a5c`, after its gate (a) and re-gate, expected at about 10:30–11:00 AM PT. Use it for gate (a), with
  your own copy of `/workspace/a5/gate_a.sh` under `/workspace/b5vc/`, and for gate (b), head and base.
- `vyv-rf-a5-g1` (4w1vzyvmibdvdf, 1x L40S, $1.09/h, bootstrapped): from `vllm-rf-a5c`, after its #101 smoke. Use it
  for your #101 smoke. The record is program `ccc21347…`, manifest `90f81868…`, run root `7adcef49…`.
- Until then, work on the VM: read the module, its importers, the tests that monkeypatch it and its allowlist entries.
  Design the split, write it, and verify it statically (pyflakes and the AST check need no torch).
- If a pod hasn't come by 18:30Z (11:30 AM PT), say so in a handoff to the coordinator, not a new pod.

## Budget
$16 of new spend (gate (a) about 3 h on t1, gate (b) about 1.5 h, #101 about 45 min).
