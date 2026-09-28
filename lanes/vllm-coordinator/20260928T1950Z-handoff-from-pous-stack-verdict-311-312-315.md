---
id: 20260928T1950Z-handoff-from-pous-stack-verdict-311-312-315
campaign: verity
lane: vllm-coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# One verdict, please, for the vLLM protocol-options stack: #311, then #312 and #315

From the worker "Build composable vLLM protocol options" (bc-23d60f13). Daniel wants PoUW, POUS and sampled proofs on
`main` as vLLM protocol options, so the research coordinator can land the three in one train
(`lanes/coordinator/20260928T1950Z-handoff-from-pous-311-ready.md`).

- **#311:** https://github.com/danielreuter/verity/pull/311, the scaffold, final head `69153d43`.
  - The design is `20260928T1650Z-handoff-from-pous-composition-design.md` in this lane, revised through 18:20Z with
    PoUW's composition needs.
  - Every option is off by default, so the default Build, Match and Commit run the same code: the new calls return before
    any adapter is imported. `TargetProfile()` still digests to `86c255b3…`, and P10 doesn't grow.
- **#312, the POUS adapter** (bc-13eada34), and **#315, the PoUW adapter** (bc-dd22acf8), both stack on #311. Each
  merges in `69153d43` and re-runs `check`.
- **What I'd ask you to check:**
  - the one-call edits in `pipeline/commit.py` (`commit_guard`, `at_commit`, `weights_view`/`register_weights` at the
    replay, `into_verdict`) and `pipeline/tp/commit.py`, and the row knob in `pipeline/row.py`;
  - `protocol_options` placed in the `acquire` layer (P9);
  - the placeholder composed Commit: with POUS it writes `verdict.protocols.of_record = false`; with PoUW, sampled proofs
    is refused until PoUW's int7 linear has a Definition;
  - the default-path A/B on #101. I haven't run it, because it needs a pod.
- **Evidence:**
  - the vLLM tests under torch: `r20260928-190833-ed72`;
  - the recorded check: `r20260928-190929-b330`, which failed only on the clock-dependent `test_notes` test that #322
    fixes in D3.
- **Main `a8e72c81` itself fails `tests/test_no_dead_modules.py`:** #309's `program/registry/spec.py` isn't reached from
  any entry point. That's outside this stack.
- **Please reply here or in `lanes/pous/`:** a GO, GO-with-changes, or "not before X" for the three together.
