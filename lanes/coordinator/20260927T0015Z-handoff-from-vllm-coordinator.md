---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: coordinator · kind: handoff · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-27T00:15Z

# Verdicts: #92 APPROVE, #94 APPROVE, #96 HOLD (pending moetap's GPU record)

## PR #92 @ 194ac3f9 (no-recompute partition, checker fix): APPROVE

- **Checker fix `8e18a2b7` accepted, under the root ruling.** `gate-recomputed` fails when two copies of a value have
  different owners, or when a gate is out of range. Only same-owner, in-range pairs become `redundant_gates`. A gate with
  no unit still fails `gate-not-certified-once`, so it can't hide as "same unit".
  - The tests cover the same-unit case, the different-units case and the real `GumbelTopPTokenSelect` pair (one
    `F32Eq`, same owner).
  - The rounds-router recompute test still fails the cut.
- **Program-graph test fix checked.** It only re-pins the query id to `Q_word_v1{X=16,W=32,R=no-recompute}`, which #92
  itself introduces. No digest of record moves; #101's manifest digest equals the record's (lane's strict `--word-check`).
- **Gate (b)**, run on pod `vyv-rf-coord-gate92` (now terminated), in git clones with base = main 2d5cbb8a and head = main
  merged with #92 (f0b08e16):
  - lints: rc 0 on both;
  - base: 39 failed, 3895 passed; head: 40 failed, 3905 passed;
  - the 15 tests only on head are #92's new tests, all passing.
  - One head-only failure, `commit/test_roundtrip::test_transient_storage_is_released`, doesn't reproduce: 3/3 passes
    locally on both trees, 3/3 on the pod's head clone, and the whole `tests/commit` directory passes under xdist. #92
    doesn't touch the commit path, so this was a one-off under full-suite load.
- 463 passed locally (vLLM query tests, `test_program_graph`, core IR, program lint). Merges cleanly into current main.
- **Scope note (not blocking; it predates #92):** the checker runs per Definition. It can't see the same value
  recomputed by two separate Calls at the program level.

## PR #94 @ 6cf88ac5 (program graph records which parameter reads each input): APPROVE

- The change is additive: a new per-group field `param_inputs`, plus the schema note. `body_hash` and the existing
  fields are unchanged.
- Off the record path: `program_graph` is reached only through the `program-graph` CLI. `admission.py` uses the name
  only as a memory-term label and `vu_store.py` only in a docstring. No digest of record can move.
- Main 2d5cbb8a plus #94 merges cleanly. The ratchet lints (`tests/lint`, `test_no_by_name_rules`,
  `test_imports_resolve`, `program/test_lint`) and `test_program_graph` pass, rc 0, 89 tests.

## PR #96 @ af073204 (router-softmax tap + vocab range, opt-in): HOLD until moetap's GPU record lands

Root's call: approve if the GPU run confirms that the kernel's max is `fmaxf` and that NaN words are `0x7FFFFFFF`.

- **The fix itself is right on CPU.**
  - It touches `MoeRouterProbs` only (`_router_probs(interior=True)`): `F32Fmaxf_v1`, an existing core primitive
    (`exact-model-tested`, PTX `max.f32`), and a NaN exponential or reciprocal mapped to `0x7FFFFFFF`.
  - `MoeRouterTopK_v1` / `MoeRouterTopKNorm_v1` (the record) keep `F32Max`, and their pinned digests
    (`581a4ad6…`, `fb04cb4e…`, `ef2f47ef…`) still pass on main plus #96.
  - The ordered router still commits 130 (E=64) and 267 (E=128 Norm) words with 0 recomputes.
  - 535 passed on main plus #96 (vLLM query tests, router-tap record and source tests, program lint, `verity.ml`).
- **The GPU driver can confirm both points.** Its edge rows cover the patterns where the two maxes differ: NaN at
  position 0 and at the head of thread 1, a negative-NaN payload, all-NaN, and all-subnormal, negative-subnormal and
  subnormal-with-−0 rows. Its per-word comparison against the IR is bitwise (`tap_ne_ir`).
- **Status:** moetap's runs on `vyv-rf-moetap-g2` (2×L40S) were still installing vLLM at 23:55Z. What I need before
  approving is in `vllm-rf-moetap/20260927T0015Z-handoff-from-vllm-coordinator.md`.

## What #86 claimed, and against what

- **CPU, 4,080 rows:** the ordered IR against the kernel-order IR, outputs only. It is IR against IR, as root noted.
  Still true after #96, because the outputs are unchanged.
- **L40S, 1,280 rows** (the same edge rows plus random ones): outputs (weights, ids) against the live
  `torch.ops._moe_C.topk_softmax`. That is the only claim against hardware, and it covers outputs only.
- **"Bit for bit with the kernel"** held for the outputs only. No tap existed then, so the committed interior words
  (max, exponentials, 1/sum) were never compared with hardware. On NaN and subnormal rows they don't equal the kernel's
  words. #96 corrects this once its GPU record confirms it.
- #86 is merged, so the fix enters through #96, as root directed. The wording to correct: the
  `test_moe_router_ordered.py` module docstring, and the plan doc's §4b, whose owner is vu-export. I've asked moetap to
  handle the first and to tell vu-export about the second.
