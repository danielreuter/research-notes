---
id: 20260928T1950Z-handoff-from-pous-311-ready
campaign: verity
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# #311 (vLLM protocol options scaffold) is ready: please land it in one train with #312 and #315

Follow-up to `20260928T1945Z-handoff-from-pous-merge-eta`. From the worker "Build composable vLLM protocol options"
(bc-23d60f13). Daniel wants the scaffold on `main`, with the adapters as their own PRs stacked on it:
- POUS is #312 (bc-13eada34, `cursor/vllm-pous-option-c934`);
- PoUW is #315 (bc-dd22acf8, `cursor/pouw-vllm-option-4f91`).

I've asked the vLLM coordinator for one verdict covering the three
(`lanes/vllm-coordinator/20260928T1950Z-handoff-from-pous-stack-verdict-311-312-315.md`).

- **PR:** https://github.com/danielreuter/verity/pull/311, branch `cursor/vllm-protocol-composition-9924`.
  - **Final head: `69153d43`.** It contains `main` `ac412eb8` and is marked ready for review.
  - Against today's `main`, `a8e72c81`, it merges clean (`git merge-tree`).
  - On that merged tree, `integrations/vllm/tests/lint`, `tests/protocol_options`, the import-resolution check and
    `test_target_profile` pass.
- **Contents:** everything is under `integrations/vllm/`:
  - `verity_vllm/protocol_options/`: the selector and composition, the adapter interface, and the sampled-proofs adapter;
  - `engine/hooks.py`: `Service` and tagged entries;
  - `config.parse_protocols`, `TargetProfile.protocols`, `LLM(protocols=…)` and the row knob `PROTOCOLS`;
  - one-call edits at the Commit's sites, and the TP Commit's guard.
  - It adds no circuits, no Definitions and no Lean.
- **Default path:** every option is off by default. With no protocols, no adapter is imported, and a subprocess test checks
  that. `TargetProfile()` still digests to `86c255b3…`. P10: `commit.py` `main` goes from 1,767 to 1,766 lines, and
  neither module grows.
- **The vLLM tests under torch:** `r20260928-190833-ed72` on `69153d43`, done rc 0, preserved on the remote. `check`
  doesn't collect these. It ran:
  - `tests/protocol_options`, `tests/engine/test_hooks.py`, `tests/pipeline/test_llm.py`, `test_row.py`, `test_cli.py`
    and `tests/program/test_target_profile.py`;
  - `tests/lint`, and the dead-module and import-resolution checks.
- **Recorded check: `r20260928-200103-b2b8` on `69153d43`, PASSED** (21:05Z, preserved on the remote). Every step ran:
  - pytest: 3,467 passed;
  - `circuit-check --all`: passed;
  - `lean-build` and `lean-unit-cut`: passed;
  - `lean-audit`: PASS for all four Lake packages (verifier, `level3`, `soundness`, `protocols/pous/lean`);
  - `lean-agreement`: skipped by name (no bundle).
- **The run before it,** `r20260928-190929-b330`, failed only on the clock-dependent
  `tools/research/tests/test_notes.py::test_relaunch_saves_the_work_supersedes_binds_the_successor_and_prints_its_launch_message`.
  That test fails on any tree between 19:00 and 20:00 UTC, and #322 in D3 fixes it.
- **Earlier failed checks on this head, none from #311:**
  - `r20260928-181350-9598`: `tests/test_instances_hw.py::test_hopper_recipes_match_the_relation_registry`. It runs only
    when torch is importable, and fails on `main` too when torch is present. I restored the environment with
    `uv sync --frozen`.
  - `r20260928-184207-bc3a`: the known race in `test_remote_local.py::test_exclusive_refuses_a_live_holder_and_reclaims_a_dead_one`.
- **Heads-up on `main` `a8e72c81`:** `integrations/vllm/tests/test_no_dead_modules.py` fails on `main` itself. #309 added
  `verity_vllm/program/registry/spec.py`, and no entry point reaches it. It isn't #311's, and it's in the vLLM
  coordinator's lints.
- **vLLM coordinator's review:** none has arrived. It was asked for at 16:35Z
  (`lanes/vllm-coordinator/20260928T1635Z-handoff-from-pous-compose-protocols.md`) and at 16:50Z
  (`…/20260928T1650Z-handoff-from-pous-composition-design.md`, revised through 18:20Z). Now there is one request for the
  whole stack.
- **Not run:** the #101 default-path A/B on a pod.
- **Merge:** `research merge cursor/vllm-protocol-composition-9924`, then #312 and #315 on top. Their owners merge in
  `69153d43` and re-run `check`.
- **Statement reviewer:** none needed.
- **Open questions for Daniel:** five, each with its built default, in the PR description.
