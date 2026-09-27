---
cursor:
  subagentId: "bc-4b90ecda-24d7-5c3a-8a26-e025e49aa6b0"
---

# G1..G8 artifact keys (epoch worktree)

Worktree: `/workspace-wt/epoch` (read-only). Scope: `integrations/vllm`.

## 1. Exact keys (two parallel namespaces, same strings)

**Not filenames.** Artifacts are `gates.json`, `card.json`, `holdouts.json`, `global_match.json`. The numeric-ish keys live *inside* them.

### A. Acceptance gates (`gates.json` / `card.gates` / `holdouts.json`)

Canonical ids: `"G1"`..`"G7"`, plus structural `"G8"` (and integrity `"R1"`, out of G1..G8).

| Key | Human label already in `GATE_NAMES` |
|-----|-------------------------------------|
| G1 | observation fidelity |
| G2 | semantic closure |
| G3 | root closure |
| G4 | primitive exactness |
| G5 | composition exactness |
| G6 | canonicality + regression |
| G7 | holdout generalization |
| G8 | VU partition |

```112:121:/workspace-wt/epoch/integrations/vllm/verity_vllm/check/gates.py
GATES = ("G1", "G2", "G3", "G4", "G5", "G6", "G7")
GATE_NAMES = {
    "G1": "observation fidelity", "G2": "semantic closure", "G3": "root closure", "G4": "primitive exactness",
    "G5": "composition exactness", "G6": "canonicality + regression", "G7": "holdout generalization",
}
HOLDOUT_GATES = ("G1", "G2", "G3", "G4", "G5", "G6")
STRUCTURAL_GATES = ("G8",)
GATE_NAMES["G8"] = "VU partition"
```

Dict key write: `gates_json` → `"gates": {r.id: r.to_json() ...}` at `gates.py:1208`; file `gates.json` via `ARTIFACTS["gates"]` (`gates.py:174`) / `write_gates` (`:1216-1219`).

### B. GM-01 Match checks (`global_match.json` → `checks[].id` / `failed_checks`)

Same `"G1"`..`"G8"` strings, **different meanings** (from `NamedCheck(..., "G*", "…")`):

| Key | `what` prefix |
|-----|---------------|
| G1 | requests_declared (`declaration.py:360`) |
| G2 | requests_observed (`attribution.py:77`) |
| G3 | subcircuits_x09 (`per_request.py:56`) |
| G4 | identity_map (`per_request.py:57`) |
| G5 | shared_state (`per_request.py:58`) |
| G6 | chronology (`chronology.py:31`) |
| G7 | vu_population (`engine_steps.py:19`) |
| G8 | within_step_order (`engine_steps.py:72`) |

Emitted as JSON `"id"` by `NamedCheck.done` (`match_run.py:22-23`). Timing phase marks (separate lowercase keys in `phases`): `g1`,`g2`,`g3_g4_g5_per_request`,`g6`,`g7`,`g8` (`global_match.py:228-240`).

**GM-01 / GP-01** are protocol labels, not the G1..G8 dict keys.

## 2. Writers and readers (file:line)

### Writers

| What | Where |
|------|--------|
| Acceptance gate ids | `@_gate("G1")`…`"G8"` `gates.py:495,612,663,735,828,927,967,1001`; `_gate` sets `r.id` `:452` |
| `gates.json` | `gates_json` `:1205-1208`, `write_gates` `:1216-1219`; caller `pipeline/match.py:566` |
| `card.gates` | `report.py:430` `{r.id: r.to_json()}` → `write_card` |
| Holdout gate subset | `properties/holdout.py:89` filters with `HOLDOUT_GATES` |
| Match check ids | NamedCheck sites above; `failed_checks` from `checks[].id` `global_match.py:242-244` |
| Regression pin of Match checks | `tests/regression/checks/global_match_checks.py:42-43` → `checks: {c["id"]: {status, n_problems}}` into `expected/*.json` via `rebaseline.py` |

### Readers

| What | Where |
|------|--------|
| Card / report | `report.py:315,357-358,389,461-462,558,604` (`gates.get("G8")` etc.) |
| Experiment VU block | `pipeline/experiment.py:257` `gates["gates"]["G8"]` |
| Holdout assemble | `holdout.py:86-90` (via `HOLDOUT_GATES`) |
| Gate G7 over holdouts | `gates.py:986-989` reads nested `holdouts[].gates` |
| Match tests | `tests/check/test_global_match.py` (heavy `_check(res,"G*")`); `test_global_match_multi_weight_nodes.py:81+`; `tests/pipeline/test_global_program_regress.py:721+` |
| Acceptance gate tests | `tests/check/test_gates_fixtures.py` (pins `G.GATES`, `gate(...,"G1")`…); `tests/pipeline/test_run_config_dry_run.py:198` |
| Lint allowlist | `tests/lint/allowlists/p04_one_result.json` (many `detail: "G*"`); `test_p04_one_result.py:102-108` |
| Regression expected | **13** files under `tests/regression/expected/` — each pins `global_match_checks.checks.G1`..`G8` (≈83 `"G[1-8]"` hits total). **No** acceptance-gate `gates.json` G keys in expected/. |
| Rebaseline tool | `tests/regression/rebaseline.py` + `checks/global_match_checks.py` (rewrites those pins) |
| `integrations/vllm/tools/` | **no** `"G[1-8]"` hits |

## 3. SYNTHESIS (`/tmp/ep/lanes_vllm-refactor_SYNTHESIS.md`)

- **C3** (line 588): “the G1 to G8 artifact keys get names” (with profile-id cleanup); after B4; GPU; Decision 4.
- **Decision 4 / Epoch** (78, 590, 617): one `rebaseline.py write` batches digest/root/key renames including “G1 to G8 key renames”.
- **P11** (385): no `G1` in module/function/class/flag/env names; names should “say the job”.
- **T3** (224): counts 420 `G1`–`G8` tokens in 58 files.
- **No concrete replacement map** (no `G1 → requests_declared` etc.). Closest proposed names are already in-code: `GATE_NAMES` values (acceptance) and NamedCheck `what` prefixes (Match). Those two namespaces must not be collapsed blindly.

## 4. Rename size

- ~**484** quoted `"G[1-8]"` hits in **~31** `.py`/`.json` files under `integrations/vllm` (SYNTHESIS’s broader 420/58 includes comments/docs).
- Hot path: ~10 production files (`gates.py`, match/{declaration,attribution,per_request,chronology,engine_steps,global_match,match_run}.py, `report.py`, `holdout.py`, `experiment.py`).
- Tests dominate: `test_global_match.py` (~123), `test_gates_fixtures.py` (~97), lint allowlist (37), plus 13 expected JSON + rebaseline.
- Estimate: **~30–40 files, ~500–700 line touches** if both namespaces rename; Match-only (C3 “artifact keys” + expected/) is smaller (~15 files, ~200 touches + 13 JSON rebaselines). Need distinct name sets for acceptance vs Match.
