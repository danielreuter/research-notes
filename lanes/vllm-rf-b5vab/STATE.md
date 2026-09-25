---
id: vllm-rf-b5vab/state
lane: vllm-rf-b5vab
kind: state
updated: 2026-09-25T16:45Z
---
# b5vab (B5 split of `engine/vllm_adapter.py`): state

> Successor of `vllm-rf-b5va` (agent bc-649f6a27; no commits, no pods; its session ended at the 16:03Z laptop restart).
> This lane: Cursor cloud agent bc-a4fbe8b2. Start commit `5c05ff6d` (`origin/lane/vllm-rf-b4b`, b4 rebased on c1).
> Coordinator: vLLM coordinator bc-ecac3029. Brief: `$STORE/internal/lane-briefs/vllm-b5vab.md`. Budget $16 new spend.

base: 5c05ff6d (b4b)
branch: lane/vllm-rf-b5vab (pushed)

## Scope
Split `integrations/vllm/verity_vllm/engine/vllm_adapter.py` (1,913 lines at base) into cohesive `engine/` modules, verbatim
moves proven by an AST/source script; `load_workload` and everything it calls stay in `vllm_adapter.py`.

## Done
- 16:41Z `d0e04cf8` the split (pushed). New modules (lines): `build` 318 (engine under κ + read-backs), `code_identity` 407
  (cubin sections, loaded code objects, generated kernels), `run_facts` 220 (profile manifest, model config subset,
  versions/host docs, ACCEPTED), `capture` 795 (ObserverConfig, _Step, Capture, make_header, SCHEMA + the observation
  docstring), `pinned` 42 (PinnedArena, spanned_bytes, storage_bytes_view). `vllm_adapter` 205: load_workload,
  ACCEPTED_TOKENS, execution_of_workload, sampling_params (all path-extracted by tests), run_requests, throwaway_requests,
  and re-exports of every public moved name (+ `_VERITY_INDUCTOR_DIR_MARK`, `RunHeader`), so no importer changes.
- Static proof (`evidence/verify_split.py`): 56/56 top-level statements, source lines and AST identical, none extra, every
  global read bound (symtable, all scopes). Negative check: an edited statement / dropped import is reported.
- Lint scan (`evidence/lintdiff.py`, the P1-P12 `scan()`s vs allowlists, no pytest): 0 problems at head. Entries moved with
  their code, totals unchanged: P7 13, P8 1, P9 6 (7 layer edges before and after), P11 19. P10 76 -> 75 (the 1,913 entry
  deleted). No allowlist grew.
- `tests/engine/test_compiled_execution_header.py`: `target_mismatches` now reads `observed_flash_attn_version` / `torch`
  from `engine.build`, so the test patches `build` (was `vllm_adapter`). Only test change.
- README engine lines updated.

## Running
- nothing; no pods yet (waiting for the b4c handoff of `vyv-rf-b4b-cpu` / `vyv-rf-b4b-g1`, and c4irc's `vyv-rf-c4ir-reg`).

## Next
1. On handoff: lints + gate (b) at `d0e04cf8` on vyv-rf-b4b-cpu (base = b4c's head XML at 5c05ff6d on that pod).
2. #101 GPU Build smoke on vyv-rf-b4b-g1 vs record (program `ccc21347…`, manifest `90f81868…`, run root `7adcef49…`).
3. Gate (a) T0+T1 on vyv-rf-c4ir-reg vs a23b's base XML (start as soon as it's handed over; ~5 h).

## Open questions
- none

## Found, not fixed
- `tests/engine/test_gen_ov_sampling.py`, `tests/observe/test_gen_sampling.py`, `test_cov_difr_b0.py`: `_adapter_fn`
  execs only `ACCEPTED_TOKENS` + the named function, but `load_workload` calls `execution_of_workload` (NameError at
  base too, if those tests run). Owned by lane gc; `execution_of_workload` stays a top-level def in `vllm_adapter.py` so
  their fix can extract it.
- Prose across the package still says `vllm_adapter.X` for names now defined elsewhere (they resolve through the
  re-exports). The capture docstring's "pattern `capture.py:679-720`" names a veritor-era file, not the new `engine/capture.py`.
- `capture.py` is at 795 of P10's 800 lines.
