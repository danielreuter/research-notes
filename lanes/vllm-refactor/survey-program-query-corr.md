---
id: vllm-refactor/survey-program-query-corr
lane: vllm-refactor
kind: survey
status: in-progress
created: 2026-09-24
checkout: f0810a11 (lane/vllm-cleanup-2)
slice: integrations/vllm/verity_vllm/{program,query,correspondence}
---
# Survey: program/, query/, correspondence/

Read-only survey against `/Users/danielreuter/projects/verity` at `f0810a11`. No Python was run. Evidence is `rg`, `git grep`, `git log`, `wc` and reading.

Paths below are relative to `integrations/vllm/verity_vllm/` unless they start with `packages/` (verity core, `packages/verity/src/verity/`) or another top-level directory.

## Slice size

| Subpackage | .py files | .py lines | other files |
|---|---:|---:|---|
| `program/` | 119 | 36,252 | 4 `.cu` probes, 3 `.cpp` models, 2 table files (`mufu_tanh_sm89.json`, 450 KB `.xzblocks`) |
| `query/` | 14 | 6,613 | none |
| `correspondence/` | 13 | 5,602 | none |
| total | 146 | 48,467 | |

Global counts over the slice (before per-module detail):
- 18 modules end in `if __name__ == "__main__":` and 17 import `argparse`.
- 11 modules read `os.environ` (plus `vllm_meta.py`, which *writes* 5 env vars with `setdefault` at import).
- verity core imports: mostly `verity.ir.{defs,refs,types,codec}`. Only `query/module_body.py`, `query/program_view.py`, `query/v1_bridge.py` import `verity.verification.query`; `correspondence/capture_identities_program.py` imports `verity.verification.{programs,typed_obligation}`. Nothing imports `verity.commitments` or `verity.verification.plan`.

(Sections below are appended as each module group is finished.)
