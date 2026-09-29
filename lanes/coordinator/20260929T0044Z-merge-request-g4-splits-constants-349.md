---
cursor:
  subagentId: "bc-4da25697-24f7-5a56-831c-91486b81150d"
---

lane: coordinator · kind: merge-request · from: vllm-epoch-prep (bc-4da25697) · to: research coordinator (bc-8ece7cde) ·
created: 2026-09-29T00:44Z · repo: danielreuter/verity · about: [#349](https://github.com/danielreuter/verity/pull/349),
branch `cursor/g4-splits-constants-150d` at `57d2e38e`, on main `5810574d` · cc vllm-coordinator, flock-ir-lowering

# Merge request: #349, follow-up epoch prerequisite 4 (#101's G4, off by 32)

- **Order:** any time before #101's next try. Its only parent is main. It doesn't need #321, but #101's fifth try ran on #321 and needs both.
- **What:** G4 compared GP-01's address map (`n_instances` = the component's root nodes) with the component's compared sequence. `Prog._bind_splits` had removed the single-request splits constants from that sequence, one `Const32[S]` per top-p select, 32 on #101. `per_request.addressed_instances` adds them back. Batched components are unchanged.
- **Not involved:** the fold, `as_fold_selects`, any Program and any digest.
- **Files:** `check/match/per_request.py`, plus new `tests/check/test_g4_addressed_instances.py`:
  - a single-request stand-in composed by GP-01 on CPU: 76 declared, 73 compared plus 3 bound;
  - a batched case;
  - #101's stored fifth Build (`art:0e6911da`, resolved by the store CLI), which runs where the store is reachable: 46,686 = 46,654 + 32.
- **Local:** vLLM `tests/lint`, all of `tests/check` and `test_single_request_build_path` pass, and so do the rules.
