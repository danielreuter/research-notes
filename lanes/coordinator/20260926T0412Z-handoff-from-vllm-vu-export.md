---
lane: coordinator
kind: handoff
from: vllm-vu-export
created: 2026-09-26T04:12Z
---

# MERGE REQUEST: PR #53, the hierarchical VU store and program_graph (vllm-vu-export, 04:12Z)


- **Merge:** PR [#53](https://github.com/danielreuter/verity/pull/53), branch `cursor/vllm-vu-store-289b`, head `11d453e0`. It's marked ready and CI is green (GitGuardian, the only check). It merges cleanly onto main (`git merge-tree`); `origin/main` has already been merged into the branch.
- **What it is:** the follow-up to #42 (merged 02:29Z) that Daniel asked for.
  - `pipeline/vu_store.py`:
    - The hierarchical store: units inside their Program, with content-addressed values.
    - GEMM weights as a fixed seeded row sample, with the whole slice referenced by checkpoint hash.
    - `extract(where=, module=, weights=)`, so flat input sets are a query output and the default query reproduces the #42 sets.
  - `pipeline/program_graph.py`: the Program as a graph, with modules, Call groups, edges and fold hashes.
  - Two #42 fixes: a keyed stratum order, and a serial export under 20% memory headroom (the vLLM coordinator's OOM-ordering follow-up).
  - `verity-vllm vu-store` and `program-graph` commands, and the store kind `vllm-vu-store/v1`.
- **Gates:** run `r20260926-040026-4968` on `vyv-vu-export-g2` at `11d453e0`, with 0 failures and 0 errors. It covered `tests/pipeline/test_vu_export.py`, `tests/pipeline/test_program_graph.py`, `tests/lint` (every ratchet, P10 sizes unchanged), `tests/check/test_sampled_replay*.py`, `tests/pipeline/test_cli.py` and `tests/pipeline/test_row*.py`.
- **Behaviour changes:**
  - The default-on export (#42) now writes `store/` and then the flat `sets/` derived from it.
  - The draw order changes, because strata are visited in keyed order. Exports drawn before this fix differ.
  - When memory is tight, the export runs serially.
- **Not changed:** any Program, manifest, root, verdict, allowlist, the tables spec or Table 2.
- **Found, not fixed:** TP rows (`pipeline/tp/commit.py`) have no export hook. Evaluating GateSets over the descriptor Program is still open; `where` uses the NameSel grammar.
