---
id: r21-infra/store-prov/20260922T1742Z-report-store-prov
campaign: r21-infra
lane: store-prov
kind: report
status: closed
repo: verity-main@500feef
---

# Lane store-prov: the provenance half of `research.store` (2026-09-22)

Branch `lane/store-prov`, final SHA `500feef` (5 commits on top of `a0f0eb9`; worktree `verity-main-wt/store-prov`). Not pushed.
Spec: `tools/research/src/research/store/README.md` §4, §6, §9, §10. Lane `store-core` (`lane/store-core` @ `7444636`, merged to
`main` @ `c232a29` during this lane) owns the storage half.

## Files

Added (stdlib only; `test_no_packages_import` passes):

- `tools/research/src/research/env.py` — `conditions()`, `source_conditions()`, `conditions_from_job()`, `SKU_FAMILY`, `sku_family()`.
- `tools/research/src/research/store/tool.py` — `Tool` dataclass, `closure_manifest`, `resolve_params`, `content_identity`, `tree_sha256`, `parse_argv`.
- `tools/research/src/research/store/tools_registry.py` — `REGISTRY` (`tc_probe`, `bench_vu`), `load(spec_or_name, source_root=None)`.
- `tools/research/src/research/store/derivation.py` — `derivation_doc`, `derivation_id`, `reuse_key`, `scratch_dir`, `scratch_env`.
- `tools/research/src/research/store/attempt.py` — `build`, `publish`, `store_root`, `open_store`.
- `tools/research/src/research/store/cli_prov.py` — `COMMANDS = {"lookup", "pull", "attempt"}`.
- `tools/research/src/research/store/canon.py`, `store/__init__.py` — placeholders so the half imports alone; **drop both on merge** (store-core's
  `canon.py` has identical §1 semantics, verified: 130/130 integrated tests pass with store-core's version).
- `tools/tc_probe/tool.py` (`TC_PROBE`), `backends/direct/ligero/tool.py` (`BENCH_VU`) — declarations; neither imports torch or the backend.
- `tools/research/tests/test_store_prov.py` (30 tests), `tests/conftest.py` (autouse: `RESEARCH_STORE` -> tmp, `RESEARCH_CAMPAIGN` unset),
  `tests/fixtures/run_v0.2/` (job.json v0.2 with `store` section, `state.json` = status.json, failure.json, result.json referencing two
  files, events.jsonl, `out/proof.bin`, `out/verify.jsonl`).

Edited: `research/cli.py` (`cmd_run`, `_run_remote`, helpers `_prepare_store`, `_publish_attempt`, `_source_identity_hint`),
`research/record.py` (`extend_job(..., store=None)`, `V2_SECTIONS += "store"`, `cost_estimate` reads v0.1 and v0.2),
`tools/research/README.md` (layout, `research data`, a section on `--tool`/`--scratch`/publish), store `README.md` (see deviations).

## Tests

`uv run pytest tools/research -q` on the branch: **104 passed, 2 skipped** (skips: the campaign-seed comparison, and the LocalStore
end-to-end test which skips with reason "store-core LocalStore not importable" until merge). Trial merge with `main` @ `c232a29`
(store-core in): **130 passed, 1 skipped** — the end-to-end test then runs against the real `LocalStore`. Smoke: `attempt.publish` on all
372 run dirs under `~/.research/runs` into a temp store with the real `LocalStore` published 362; the 10 refusals are runs whose
`status.json` still says running (correct per §10; the `store_publish_error.json` files that smoke wrote were deleted).

## `research run` flags added

- `--tool NAME|module:NAME` — load the `Tool` (registry name, or `dotted.module:ATTR`; falls back to loading `<cwd>/<module>.py` by file
  when not importable, which is how the machine side finds `tools/tc_probe/tool.py` inside a shipped `git archive`). Load errors exit 2
  before launch; everything after the load is best effort and lands as `store.error`.
- `--scratch NAME` (repeatable) — `<store>/scratch/<reuse_key | dirty-<run_id>>/<NAME>`; exports `TRITON_CACHE_DIR` for `triton`, else
  `RESEARCH_SCRATCH_<NAME>`.
- `--campaign NAME` (default `$RESEARCH_CAMPAIGN`) — recorded in conditions (`execution.campaign`), exported to the workload.
- `--source-identity JSON` (hidden) — machine side only: `{commit, tree, dirty, dirty_digest}` of the control-side source, forwarded by
  `_run_remote` because the shipped tree has no `.git`.

`_run_remote` forwards `--tool/--scratch/--campaign` (+ the hint) inside the request's harness args. On a claimed machine run without
`RESEARCH_STORE`, the store root is `<root>/store`, which is what `research data pull` reads. After `harness_run` (local and machine side)
the runner prints `research: attempt published: <n> outputs drv=<drv:...> reuse=<sha|None>` or `research: attempt not published: <error>`.

## `job.json` v0.2 `store` section (optional; `None` when the run had no store step)

~~~json
"store": {
  "tool": {"name": "tc_probe", "version": "1", "spec": "tools.tc_probe.tool:TC_PROBE"},
  "derivation": "drv:<64 hex>", "reuse_key": "<64 hex> | null",
  "key_params": [...], "key_conditions": ["hw.family"],
  "params": {"...parsed argv...", "argv": [redacted argv]},
  "key_params_resolved": {"arch": "sm_89", "root": "sha256:<hex>", "input.gold": "sha256:<hex>"},
  "inputs": {"inst": "art:<hex>"},
  "closure": {"tools/tc_probe/tc_probe.py": "<sha256>", ...},
  "conditions": {... §6.3 ...}, "scratch": {"triton": "/path"}, "campaign": "r21-...", "store_root": "/path"
}
~~~

On a failure after the tool load it is `{"error": "...", "tool": {...} | null, "campaign": ...}`; `publish` then rebuilds what it can from
the records. `attempt.build` rebuilds v0.1 and store-less v0.2 records too (tool = `computation.command[0]` basename, version `None`,
conditions `None` except what the old job carried, `closure`/`reuse_key` `None`).

## Deviations from the spec (store README edited where noted)

1. **`inputs` hold `art:` ids only.** store-core's `attempt_errors` rejects any other value. A harness `--input name=path` that is not a
   fetched artifact enters the derivation as key param `input.<name> = sha256:<hex>` instead. (README §4 text updated.)
2. **Attempt manifest keys added**: `execution.stage`, `execution.remote` (machine/run_dir of a remote run), `status.result` (result.json
   validity), `status.timed_out`. §4 example updated; store-core validates only the top-level shape, so these pass.
3. **`source.lockfiles`** is `{}` (not `None`) when the root has none and `None` only when the source root is unknown. Clarified in §4.
4. **SKU_FAMILY** is exactly the requested families (`h200 h100 b200 a100 l40s l40 rtx4090 rtx5090 a10 t4`; `A10G` -> `a10`; no GPU ->
   `cpu`; anything else -> `unknown`; probe failed -> `None`), ordered so `L40S` wins over `L40` and `H200` over `H100`; tested on the SKU
   strings found in `~/.research/runs` job records. Table reproduced in §6.3.
5. **Dirty trees**: `reuse_key = None` and the scratch dir is `dirty-<run_id>` (per §6.5); `dirty_digest` is recorded in conditions so two
   dirty runs are still distinguishable; untracked > 64 MiB -> `"too-large"`.
6. **Fixture file name**: `status.json` is tracked as `state.json` (main's repository gate forbids the report-genre stem) and copied to
   `status.json` at test time.
7. **`lookup`** builds the derivation from `--tool/--param/--input/--condition` or, with `-- ARGV`, from the tool's own `parse`; reuse_key from
   `--source-tree SHA` or the current tree; `--any-source` matches by derivation only. **`pull`** verifies every blob's sha256 on arrival and
   ignores anything in the tarball that is not a requested `objects/sha256/<hex>` (macOS `bsdtar` AppleDouble entries). §9 CLI lines updated.
8. **Secrets**: params whose key matches `telemetry.job.SECRET_KEY` are `<redacted>` before they enter `job.json` (argv already is).

## Integration with store-core (import points, all lazy, inside functions)

- `research.store.canon.dumps / sha256` — used by `derivation`, `tool` (tree listings), `attempt`.
- `research.store.local.LocalStore(root)` — `put_artifact(kind, meta, refs=None, *, file=None, tree=None) -> art_id`,
  `put_attempt(doc)` (write-once; same bytes = no-op), `get_attempt(run_id)`, `.index.attempts_by_reuse_key(key)`,
  `.index.attempts_by_derivation(drv)`, `.root`, `.index.index_artifact(...)` (pull re-indexes manifests it copies).
- `attempt.store_root()` mirrors `$RESEARCH_STORE` / `~/.research/store`; if store-core's `local.store_root` should be authoritative, swap
  the one call in `attempt.store_root`.
- store-core's `store/cli.py` already does `from .cli_prov import COMMANDS` and merges them: nothing to wire for `research data lookup|pull|attempt`.
- **Merge conflicts to expect**: `store/canon.py` and `store/__init__.py` (add/add — take store-core's), `tools/research/README.md` and
  `store/README.md` (both lanes edited; union). No code conflicts elsewhere (trial merge verified).
- §10 step 4 (preserve to the remote): `publish` calls `store.push_attempt(run_id)` when the store object has that method and
  `remote_push is not False`, recording the result as `preserved` / `preserve_error`. store-core's `LocalStore` has no `push_attempt` yet
  (its remote lives behind `LocalStore.remote`), so today the step is skipped; adding that one method on `LocalStore` completes it.
