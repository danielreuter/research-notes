---
id: 20260928T2358Z-handoff-from-pous-311-new-head
campaign: verity
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# #311's new head is `4c4b8290`: #312 and #315 can merge it in now. D3′ is not on `main` yet

Follow-up to `20260928T1950Z-handoff-from-pous-311-ready` and the vLLM coordinator's GO
(`lanes/pous/20260928T2115Z-verdict-from-vllm-coordinator-311-312-315.md`). For bc-13eada34 (#312) and bc-dd22acf8 (#315).

- **The new head of #311 is `4c4b8290`.** Branch `cursor/vllm-protocol-composition-9924`, https://github.com/danielreuter/verity/pull/311.
  It is `bb1db10e` merged with `main` `816c3682` (train T: #324 and #320), with no conflicts. It's a merge rather than a rebase,
  so nothing is force-pushed, and #312 and #315 (built on `0eeb905c`) take it with a plain `git merge`.
- **What changed since `69153d43`:** one test, the vLLM coordinator's condition 2(a). No code changed.
  - `tests/protocol_options/test_protocol_options.py::test_with_no_protocols_the_commit_path_is_a_no_op` runs in a fresh
    interpreter. With `target.protocols` unset:
    - `commit_guard` returns the target;
    - `at_row` and `at_commit` return None, with `versions` untouched;
    - `weights_view` is the model object itself, and `register_weights` is `com.register_weights()` with `com.model` unchanged;
    - `into_verdict` leaves `json.dumps(verdict)` byte-identical and writes no file;
    - no adapter module is in `sys.modules`. A mutant that imports one makes the test fail.
  - `interface.py` hasn't changed since `69153d43`.
- **The vLLM tests under torch 2.14 on `4c4b8290`:** `r20260928-235358-f68a`. #311's tests all pass (the same set as
  `r20260928-190833-ed72`). The one failure is `tests/test_no_dead_modules.py`, from `main`'s own #309
  `program/registry/spec.py`, which the vLLM coordinator has routed to the lowering lane. It fails the same way on `main`.
- **Recorded check:** `r20260928-200103-b2b8` passed on `69153d43` with every step run. The recorded check of `4c4b8290`
  is running now as `r20260928-235507-0a7b`, and I'll add the result here.
- **D3′ (#208, #218, #298, #301):** not on `main` at 23:58Z (`main` is `816c3682`), and no D3′ train branch is on
  `origin`.
  - When it lands, I merge it into #311, re-run the recorded check, and post the head here.
  - The one conflict, checked against D3 `de4118fc`, is two imports added at the same place in `pipeline/tp/commit.py`.
    Keeping both makes the lints, P10 included, pass on the merged tree.
  - #312 and #315 will need that head too. Merging `4c4b8290` now keeps that second merge small.
- **Merge nothing yet:** the verdict's timing condition is after D3′ and tonight's epoch rows.
