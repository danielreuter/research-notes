---
cursor:
  subagentId: "bc-700087cc-a225-5dd8-acb2-02bfa467d05e"
---

# One-stage audit inventory (`origin/main` + PR #108)

Read-only on `origin/main` (`8515c79e…`). PR #108 adds `pipeline/serving_view.py` only.

## 1. Serving commitments

**Live scheme:** `verity.commitments.vllm_v1` via `commit/scheme.py` (`NAME="vllm-v1"`), **SHA-256**. **frame-v3:** not on the live path. **hm96:** opt-in (`commit/hiding.py` `LeafSchemeRule`, `hm96-sha256/v1`); default = unsalted position leaves (`Opening.salt` empty). `vllm-v1-sha512` exists in core; live digests are 32 B.

**Compute sites:** `commit/committer/native_host.py` `NativeHostCommitter` — `pos_leaf`/chunk leaves → `fold_levels` → `step_root` (~L1470+) → `finalize`/`run_root` (~L2043). Production prefers `native_collect` (same scheme). Weights: `register_weights` → `weights_root` (~L1200). Hidden: `stream_root`/`thread_root`. Harness: `pipeline/commit.py`.

**Roots:** **step root** = `step_root(program_digest, ctx_digest, geo_digest, layout_digest, n, merkle_root)` (`StepCommitment`); **run root** = `run_root(program_digest, geo_digest, step_roots)` per run/rank; **weights root** separate (binding map `registered-input`). Manifest digests are separate (`query/manifest/format.py`). **Partition digest in any root: not found** (only census JSON under `integrations/vllm/data/census/`).

## 2. Registration

**Explicit register-roots-with-verifier: not found.** Closest: Commit artifacts — `runs.jsonl.run_root`, `binding_map_p*.json` (`run_root`, `program_digest`, map `digest`, entry `step_root`), `declaration_*.json`, `verdict.json` (`run_roots`), `weights_of_record.json`. Required-value manifest (`pipeline/manifest.py`, schema `verity-sweep/required-manifest/v1`) is Value population + `manifest_digest`, not a root registry. `ops/known_roots.json` = canary pins; `release_json.py` = ship identity. PROTOCOL.md step 1 names registration; **audit driver + registration log + beacon client “Not here yet.”**

**Draws** (`commit/challenge.py`, `LEGACY=True`): positions/identities from **run_root** (+ map digest/salt); non-legacy uses `derive(source, …)` with beacon/auditor `source`. Replay: `legacy_replay_seed(challenge, run_root)` or `root_seed`; non-legacy `replay_key` → `vu_key(source, {run_root})`. VU export: `selection_key(run_root)` via `derive` — labeled benchmark selection, not verifier challenge.

## 3. Openings

`Committer.open` → `Opening(step, index, value, path, identity, salt)` (`acquire/committer_api.py`); verify via leaf → `fold_path` → `step_root` → run root. Checks: `commit/opened.py` `OpenedReader` (`open_range`/`verify_range`). Replay: `check/replay/opening.py` `CommittedStore`. Fold VU index: `check/replay/vu_query.py`.

**Drawn unit → I/O + Merkle vs registered root:** partial — binding map + store open VU words; leaf openings verify vs **run root**. **Not found:** packaged proof-unit → Flock statement + Merkle multiproof vs a verifier-registered root.

**Export:** `pipeline/vu_export.py`/`vu_store.py` write flat LE ports + `manifest.json` (relation/ports/digests/provenance root) after bit-exact replay. `verity_flock.boolean_export` lowers a **program graph** for the visualizer — not served leaf openings.

## 4. Smallest served row

Cited: `#4` SmolLM2-135M, `#73` Qwen3-4B, `#74` FP8, `#101` stoch/attention (`tests/regression/…`). Canaries in `ops/known_roots.json`. Checkpoints: **B0 SmolLM2-135M** smallest; then PYTHIA160M, QWEN05, SMOL360, TINYLLAMA, …

**CPU:** `manifest.build`/`program_graph` from `instances.json.gz`; `commit_offline`/`commit_block_offline`. Synthetic pad e2e: `tests/program/padded_commit_tiny.py` (not a served row). **Not found:** fixture replaying a full tiny *served* Commit without GPU. PR #108 `serving_view` rearranges Build Programs as served (CPU).

## 5. Draw-by-index / population

| Mechanism | Population |
|-----------|------------|
| `law.select_replay_units` / `select_verification_units` | RU index; VU `0..n_v-1`; `derive` domains `ru-sample/v1`, `vu-sample/v1` |
| `challenge.stratum_picks` | strata as RUs, `p=1`, `k=per_stratum` |
| `replay/population` + `sample` | executed-prefix VUs by `(spec, request, phase)` |
| `vu_export.select` | same pool under `selection_key(run_root)` |
| `query/word.partition`/`units` | per-Call word units (gate cut) |
| `vu_query` | fold-Program local VUs by index |

vLLM C2: one post-commit challenge, strata as RUs at `p=1`; default draws still LEGACY/root-derived.

## GAPS for one-stage e2e

- No verifier registration log/root handoff (only Commit artifacts / `known_roots` / `--expect-root`).
- Draws LEGACY/root-keyed; not verifier-owned randomness independent of prover root (beacon API exists, off by default; audit driver not here).
- Live **vllm-v1 SHA-256** (no hm96) vs often-assumed SHA-512 + HM96 re-baseline/Flock M0.
- Partition digest not bound into roots.
- No e2e: register → draw → open → Flock prove → Lean verify → **`IntegrityProfile`** (vLLM emits `verdict.json`; `TwoStageLaw.profile` only in protocol tests).
- `vu_export`/`boolean_export` not audit openings packages.
- Smallest real row B0; no tiny served-Commit fixture on CPU.
- One-stage protocol code **not found** (only two-stage law + vLLM p=1 specialization).
