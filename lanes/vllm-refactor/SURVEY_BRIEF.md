---
id: vllm-refactor/survey-brief
lane: vllm-refactor
kind: brief
status: active
created: 2026-09-24T15:45Z
---
# Code-smell survey of the Verity x vLLM integration: shared brief

Four read-only surveyors each audit one slice of `integrations/vllm/`, so the refactor can be grounded in evidence. They all use the category ids below, so their reports can be merged.

## Where and how
- **Repo:** `/Users/danielreuter/projects/verity`, checked out at `f0810a11` (branch `lane/vllm-cleanup-2`).
- **Don't modify the checkout.** The owner is browsing it. Don't edit files, switch branches, or run `git checkout` or `git stash`.
- **Don't run Python or tests.** The laptop is short on disk and memory. Reading files and running `rg`, `git grep`, `git log` and `wc` are fine.
- **Verity core** lives at `packages/verity/src/verity/`:
  - `ir/`: defs, refs, types, codec, layout, program, evaluate, query, query_ast.
  - `verification/`: query, statement (Obligation, Statement, KindProgram), binding, typed_obligation, trust, target, plan, lowering, gateset, programs.
  - `commitments/`: leaves, merkle, indexed, multiproof, poseidon2_babybear.
  - `ml/tc/`: models, relation, instructions, term, total.
- **The integration should use core's abstractions, not copy them.** Known facts:
  - The integration imports core's IR heavily (`verity.ir.defs`, `refs`, `types`, `codec`). Only 3 files import `verity.verification.*`, and none imports `verity.commitments`.
  - `verity_vllm/commit/hashing.py` duplicates `verity/commitments/leaves.py`: same framing, same `leaf_hash` and `node_hash`.
  - There are at least two numpy twin libraries: `check/twins.py` and `program/registry/derived_rows.py`.
  - 73 of 286 modules end in a `__main__` block.
  - `ops/row_pod.sh` (1,147 lines of bash) orchestrates 19 `python -m` modules and reads 108 environment variables.

## Smell taxonomy (category ids)
1. **CORE-DUP:** reimplements something verity core already provides. Cite both sides.
2. **INTERNAL-DUP:** two or more implementations of one job inside the integration.
3. **VERSION-RESIDUE:** versions, phases or experiment names in file, function, class, flag or env-var names: v1, v2, `_fast`, `_new`, legacy, `poc_`, m1, b1, B0/B1/B7 case names, W11, L5, C2, G1..G8, `capture_v1`, `v1_bridge`, tier a/b/c. Separate LEGIT versioned identifiers that are hashed data (Definition names like `Gemm_v1`, schema ids like `runtime-correspondence/v1`) from residue in code names.
4. **HARDCODING:** model names, layer counts, TP degrees, GPU or architecture names, row numbers in library logic. `program/registry/quarantine/` is meant to hold the by-name residue; report anything model-specific outside it.
5. **SCRIPT/ENV/PATH:**
   - `if __name__ == "__main__"` or argparse in library modules.
   - `os.environ` reads in library code.
   - Default paths relative to the working directory.
   - `Path(__file__).parents[N]` arithmetic.
   - Hardcoded machine paths (`/workspace`, `/vault`, `/vol`, `out/...`).
6. **LAYERING:** imports in the wrong direction (e.g. query imports check), and library code reading `tests/` or the top-level data directories (`data/`, `fixtures/`, `manifests/`, `docs/data/`).
7. **GOD-MODULE:** oversized or multi-responsibility modules. For each module over about 800 lines, list the distinct jobs it does.
8. **DEAD:** no importers or callers. Other forms: proof-of-concept leftovers, references to paths that no longer exist, NOT_YET tables, commented-out code.
   - Before claiming "unused", check absolute imports, relative imports (`from . import x`, `from .x import`), dynamic imports and importlib, `python -m verity_vllm.x` in shell scripts and tests, and string references.
   - Label each DEAD claim with confidence (high, medium or low) and what you searched.
9. **NAMING:** one word with several meanings (gate, profile, fixture, manifest, record, oracle, twin, relation, verdict, spec, case, role, kappa), or names that don't say the job.
10. **DOCS:** docstrings written as lab notebooks (board ids like M-0356, lane names, dates, decision numbers like F-r17b-39) instead of explaining what the code does and why. Also stale docs.
11. **FALLBACKS:** silent fallback chains, broad try/except that swallows errors, env overrides that change behavior.
12. **OTHER-WEIRD:** anything else surprising. Examples: monkeypatching vLLM or torch internals, global mutable state (including registration side effects at import), subprocess orchestration inside library code, giant literal tables, copy-paste blocks, magic constants.

## Deliverables
1. **Full report** at `/Users/danielreuter/.research/notes/lanes/vllm-refactor/survey-<slice>.md`. Write it progressively, one section per module group as you finish it, so a crash doesn't lose your work. Include:
   - **Per subpackage:** one sentence on the job it actually does vs what its name suggests, and a module list with line counts and a one-line job for each.
   - **Findings** grouped by category id. Each gets `file:line`, a one-line explanation and a severity (high, medium or low). Give counts per category.
   - **Slice-specific maps** from your prompt.
   - **Disposition table:** for every module in your slice, one of keep, merge into X, move to X, delete, or replace with core Y, with a one-line reason.
2. **Return a compact summary** of at most about 450 words:
   - counts per category;
   - the 12 most important findings, with `file:line`;
   - your slice-specific maps, a few lines each;
   - the path of the full report.
