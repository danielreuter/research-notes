---
cursor:
  subagentId: "bc-9916bbb1-de98-5d21-a511-aafa5255c78f"
---

lane: vllm-coordinator · kind: handoff · from: flock-ir-lowering (bc-9916bbb1) · created: 2026-09-28T17:21Z · re:
`lanes/flock-ir-lowering/20260928T1652Z-note-from-vllm-coordinator-101-program-view.md`

# #101's manifest-step failure: fixed in #309 (stacked on #297), with the research coordinator as urgent

- **The head:** [#309](https://github.com/danielreuter/verity/pull/309), `5931496d`, on #297's `81fd1414`.
- **The sweep for a fourth site:** every lookup on the Build, manifest, Match and Commit paths is in the PR's audit table.
  - Four module lists missed #231's modules: GP-01, the Match's `program_compare._registry()`, the query layer's program view (the
    manifest, word check, cross-call, program graph, serving view) and `descriptor_equivalence`. All now read one catalogue that
    loads every registry module.
  - The Commit's replay had no evaluator for `GumbelTopPTokenSelect_v2`. It would have counted the sampler's Calls as "no registered
    evaluator", a form (B) gap. It now has one, self-checked against the Definition.
- **Run on CPU on #101's stored Build (`art:2d65d5d7…`)**, each step in a fresh interpreter:
  - GP-01 composes (23,256,312,239 gates), and the Match's registry decodes the result.
  - `manifest build` with the row's policy flags and the default `--word-check 16/32`: the program view resolves every Call and the
    word check runs over all of them.
  - A **strict** pass isn't possible on this 15 GB VM. At the default limit the one violation is `GumbelTopPTokenSelect_v2
    {V=128256,S=32}: too-large, 32 Call(s)`, and cutting that Call needs about 60 GB.
  - The query's program view resolves all 334 specs, and every family has a Commit replay evaluator.
- **Launch the fourth try with** `VERITY_QWORD_MAX_GATES=GumbelTopPTokenSelect_v2=110000000` in the row's environment. The row
  driver's `manifest build` command carries no gate flag, and the environment reaches it. The same variable covers
  `program-graph --word`.
- **Not tested on CPU:** the Match and the Commit at full size, which need the GPU capture.
