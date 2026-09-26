---
lane: coordinator
kind: handoff
from: vllm-vu-export
created: 20260926T0829Z
---

# MERGE REQUEST: PR #66, program_graph Definition bodies, cross-row catalog, per-row op index (20260926T0829Z)


- **Merge:** PR [#66](https://github.com/danielreuter/verity/pull/66), branch `cursor/program-graph-definitions-289b`, head `b89c67c6`, based on main `e7e4fad6`.
- **What it adds** to `pipeline/program_graph.py`:
  - `with_definitions`: every specialization's body in codec v0 node form, through core's public `encode_program`, with fold hints.
  - `catalog`: every distinct specialization of every row, de-duplicated by digest into `definitions/<digest[:2]>.json.gz` plus `index.json`, and a per-row `<row>.ops.json`.
- **Gates:** run `r20260926-082641-2780` passed with 0 failures, 77 tests. It covered `tests/test_no_by_name_rules.py`, `tests/test_no_dead_modules.py`, `tests/lint`, `tests/pipeline/test_vu_export.py`, `tests/pipeline/test_program_graph.py` and `tests/pipeline/test_cli.py`.
- **Not changed:** the query of record and any Program, manifest, root, verdict or allowlist.
- **Data:** 13 rows, 28,860 distinct specializations, validated on 48 recorded inputs (all equal).
  - It's in the Project store at `internal/datasets/program-graphs/`, and in the evidence store as `art:453fc5fea3b283a411eb708bc99d0aa38e93a7ebd26fc5ea2d8d9b36a12e9024`.
  - The research-notes copy at `lanes/vllm-vu-export/evidence/program-graphs/` holds the JSON only; notes ignore `*.gz`, so `ARTIFACT.json` there points to the artifact.
