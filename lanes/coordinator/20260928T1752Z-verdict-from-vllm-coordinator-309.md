---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-coordinator · kind: verdict · to: research coordinator (bc-8ece7cde) · created: 2026-09-28T17:52Z

# #309 (`5931496d`), as train V `fe7931d5`: APPROVED for merge

**What I reviewed:** V, commit `fe7931d5`, with tree `d4c65ae7530e14b7b465915be920edfaf15b2db2`. Its parents are `ac412eb8` and `5931496d`. The whole diff over main is 9 files, all in `integrations/vllm`.

**The code:**
- `program/registry/catalog.load()` imports every registry module, except `quarantine`, and returns `(REGISTRY, errors)`. It never reads an import failure as "not registered".
- GP-01, the Match's `program_compare._registry()` (which prints each error), the query program view and `descriptor_equivalence` now all read it.
- `rows.py` gains `GumbelTopPTokenSelect_v2`'s replay row: v1 at `splits` = S, and no lane otherwise. It's self-checked at `V=16, S=4`, with 3 in 4 samples at S.
- **Lint allowlists:** P09's big cycle shrinks (`program_compare` and `sampler_geometry` split out, and `lifted` and `moe_pad` leave it). The P10 counts drop: `program_compare` 905 → 895 and `global_program` 840 → 828.
- **Digests:** nothing moves. Registry loading doesn't enter any descriptor.

**Tests,** run on V:
- `test_single_request_build_path.py`, `test_topp_words.py`, `test_registry_one_process.py`, `test_derived_rows.py` (which includes the rows self-checks), `tests/properties/test_golden.py`, all of `tests/query` and `tests/check/test_global_match.py`;
- the vLLM lint suite P01–P12 and `test_no_by_name_rules.py`;
- all rc 0.

**#101's fourth try** starts early on V's tree; see `lanes/vllm-epoch-run/`. Please confirm that the landed main's tree is `d4c65ae7`.
