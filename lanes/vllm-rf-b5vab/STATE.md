---
id: vllm-rf-b5vab/state
lane: vllm-rf-b5vab
kind: state
updated: 2026-09-25T21:12Z
---
# b5vab (B5 split of `engine/vllm_adapter.py`): state

> Successor of `vllm-rf-b5va` (agent bc-649f6a27; no commits, no pods; its session ended at the 16:03Z laptop restart).
> This lane: Cursor cloud agent bc-a4fbe8b2. Start commit `5c05ff6d` (`origin/lane/vllm-rf-b4b`, b4 rebased on c1).
> Coordinator: vLLM coordinator bc-ecac3029. Brief: `$STORE/internal/lane-briefs/vllm-b5vab.md`. Budget $16 new spend.

base: 5c05ff6d (b4b)
branch: lane/vllm-rf-b5vab (pushed), head 3201c3f4

## Scope
Split `integrations/vllm/verity_vllm/engine/vllm_adapter.py` (1,913 lines at base) into cohesive `engine/` modules, verbatim
moves proven by an AST/source script; `load_workload` and everything it calls stay in `vllm_adapter.py`.

## Done
- 21:05Z gate (a) at `3201c3f4` = a23b base (158: 73 passed / 85 skipped; 2 known reworded skip reasons). c4ir-reg terminated. READY.md + merge request.
- 20:15Z #101 at `3201c3f4` on b4b-g1, run `r20260925-185918-5fec` (rc 0, PRESERVED): build/match/commit PASS; program
  `ccc21347…`, manifest `90f81868…` (7043), run root `7adcef49…`, commit PASS (all checks); non-interference PASS 992/992,
  tokens equal = record. The multiset of program/manifest/run-root/verdict values in the row dir is identical (md5) to b4c's
  `r101-9689a1ef` on the same pod (`evidence/r101-head-3201c3f4.txt`). b4b-g1 terminated 20:17Z.
- 18:58Z gate (b) at `3201c3f4` vs b4c `9689a1ef`, same pod (b4b-cpu), runs `r20260925-181128-fbe5` / `r20260925-181148-2918`:
  lints rc 0 both; 4063 tests both; 0 only-one-side, 0 new failures, 0 new skips / skip reasons; the 2 flaky gc-freeze tests
  failed->passed (`evidence/jdiff-gate_b-head-3201c3f4-vs-9689a1ef.txt`). All 3 gate (b) runs PRESERVED; b4b-cpu terminated 19:03Z.
- 18:10Z `3201c3f4` = merge of b4c `9689a1ef` (+ a5c `40b9e571`): conflicts only in README, p08, p10 (kept both sides' moves,
  dropped the vllm_adapter P10 entry). Lint scan 0 problems, split proof 56/56, every `va.X` in the tree is in the facade.
- Mint log: 18:17:52Z mint (ttl 3h, read-only, manifests/ + objects/sha256/) lost in a failed ssh pipe, never stored;
  18:18:43Z mint piped into `/root/r2ro.env` on vyv-rf-b5vab-reg (45jkskzz61srvd), deleted there ~18:19Z when c4ir-reg
  (fixtures local) was handed over. That pod's run `r20260925-181454-8a8a` was killed by pid and the pod terminated 18:20Z
  (up ~12 min, ~$0.35).
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
- 16:53Z `42cf1781` = merge of b4c's head `5494e29f` (5c05ff6d + main 38a8d35d) into the lane; clean. Lint scan 0 problems
  and the split proof 56/56 hold at `42cf1781`. Pushed.
- 16:57Z handoff to the coordinator: head final for gate (a); asked for a fixture-holding pod (c4ir-reg not coming soon).

## Running
- nothing; all pods terminated.

## Next
- none: READY.md written, merge request sent to the coordinator; FINAL.

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
